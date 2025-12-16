"""
FIBO Generation Engine
Handles image generation using FIBO with JSON control via BRIA AI API
"""

from typing import List, Dict, Optional
from PIL import Image
import numpy as np
from dataclasses import dataclass
import os
import base64
from io import BytesIO
from .bria_client import BRIAAPIClient

# Lazy import of local model to avoid blocking startup
BRIA_LOCAL_AVAILABLE = False
BRIALocalClient = None
try:
    from .bria_local import BRIALocalClient as _BRIALocalClient, BRIA_LOCAL_AVAILABLE as _BRIA_LOCAL_AVAILABLE
    BRIALocalClient = _BRIALocalClient
    BRIA_LOCAL_AVAILABLE = _BRIA_LOCAL_AVAILABLE
except Exception as e:
    # Silently fail - local model not available
    pass

# Optional torch import (not required for BRIA API usage)
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


@dataclass
class Frame:
    """Represents a generated storyboard frame"""
    scene_number: int
    image: Image.Image
    params: Dict
    hdr_image: Optional[np.ndarray] = None  # 16-bit HDR data
    
    def to_dict(self) -> Dict:
        """Convert frame to dictionary for API response"""
        # Convert image to base64
        img_buffer = BytesIO()
        self.image.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return {
            "scene_number": self.scene_number,
            "image": f"data:image/png;base64,{img_base64}",
            "params": self.params
        }


class ConsistencyEngine:
    """Maintains visual consistency across frames"""
    
    def __init__(self):
        self.frame_history: List[Dict] = []
        self.lighting_state: Optional[Dict] = None
        self.color_state: Optional[Dict] = None
        
    def maintain_consistency(self, current_params: Dict, 
                           previous_params: Optional[Dict] = None) -> Dict:
        """
        Adjust parameters to maintain visual continuity
        
        Args:
            current_params: Current frame parameters
            previous_params: Previous frame parameters (if any)
            
        Returns:
            Adjusted parameters for consistency
        """
        if previous_params is None:
            # First frame - no consistency needed
            self.lighting_state = current_params.get("lighting", {}).copy()
            self.color_state = current_params.get("color", {}).copy()
            return current_params
        
        adjusted_params = current_params.copy()
        
        # Maintain lighting continuity (gradual transitions)
        if "lighting" in adjusted_params and self.lighting_state:
            adjusted_params["lighting"] = self._interpolate_lighting(
                self.lighting_state,
                adjusted_params["lighting"]
            )
        
        # Maintain color grading consistency
        if "color" in adjusted_params and self.color_state:
            adjusted_params["color"] = self._interpolate_color(
                self.color_state,
                adjusted_params["color"]
            )
        
        # Smooth camera transitions
        if "camera" in adjusted_params and previous_params.get("camera"):
            adjusted_params["camera"] = self._smooth_camera_transition(
                previous_params["camera"],
                adjusted_params["camera"]
            )
        
        # Update state
        self.lighting_state = adjusted_params.get("lighting", {}).copy()
        self.color_state = adjusted_params.get("color", {}).copy()
        self.frame_history.append(adjusted_params)
        
        return adjusted_params
    
    def _interpolate_lighting(self, prev: Dict, curr: Dict) -> Dict:
        """Interpolate lighting parameters for smooth transitions"""
        # Simple interpolation - can be enhanced
        interpolated = prev.copy()
        
        for key in ["intensity", "color_temperature"]:
            if key in curr and key in prev:
                # 70% previous, 30% new for smooth transition
                interpolated[key] = 0.7 * prev[key] + 0.3 * curr[key]
        
        # Update other parameters
        for key in curr:
            if key not in ["intensity", "color_temperature"]:
                interpolated[key] = curr[key]
        
        return interpolated
    
    def _interpolate_color(self, prev: Dict, curr: Dict) -> Dict:
        """Interpolate color parameters for consistency"""
        interpolated = prev.copy()
        
        for key in ["saturation", "contrast"]:
            if key in curr and key in prev:
                interpolated[key] = 0.8 * prev[key] + 0.2 * curr[key]
        
        # Keep palette if similar, otherwise transition
        if curr.get("palette") == prev.get("palette"):
            interpolated["palette"] = curr["palette"]
        else:
            # Gradual transition
            interpolated["palette"] = curr["palette"]
        
        return interpolated
    
    def _smooth_camera_transition(self, prev: Dict, curr: Dict) -> Dict:
        """Smooth camera parameter transitions"""
        interpolated = prev.copy()
        
        # Smooth FOV transitions
        if "fov" in curr and "fov" in prev:
            fov_diff = curr["fov"] - prev["fov"]
            if abs(fov_diff) > 10:  # Significant change
                # Gradual transition
                interpolated["fov"] = prev["fov"] + fov_diff * 0.3
            else:
                interpolated["fov"] = curr["fov"]
        
        # Smooth elevation/rotation
        for key in ["elevation", "rotation"]:
            if key in curr and key in prev:
                diff = curr[key] - prev[key]
                if abs(diff) > 5:
                    interpolated[key] = prev[key] + diff * 0.3
                else:
                    interpolated[key] = curr[key]
        
        # Update other camera parameters
        for key in curr:
            if key not in ["fov", "elevation", "rotation"]:
                interpolated[key] = curr[key]
        
        return interpolated


class FIBOGenerator:
    """Generates images using BRIA AI API with FIBO JSON control"""
    
    def __init__(self, api_token: Optional[str] = None,
                 hdr_enabled: bool = True,
                 image_width: int = 1920,
                 image_height: int = 1080,
                 use_local_model: bool = True):
        """
        Initialize FIBO generator with BRIA model
        
        Args:
            api_token: BRIA API token (optional, for API mode)
            hdr_enabled: Enable HDR/16-bit output
            image_width: Generated image width (default: 1920)
            image_height: Generated image height (default: 1080)
            use_local_model: Use local BRIA-4B-Adapt model (default: True)
        """
        self.hdr_enabled = hdr_enabled
        self.image_width = image_width
        self.image_height = image_height
        self.consistency_engine = ConsistencyEngine()
        self.use_local_model = use_local_model
        
        # Initialize BRIA client (local model or API)
        self.bria_client = None
        self.bria_local_client = None
        
        local_model_loaded = False
        if use_local_model and BRIA_LOCAL_AVAILABLE and BRIALocalClient:
            try:
                print("🔄 Attempting to use local BRIA-4B-Adapt model...")
                self.bria_local_client = BRIALocalClient()
                print("✅ Local BRIA model initialized")
                local_model_loaded = True
            except Exception as e:
                print(f"⚠️  Failed to load local model: {e}")
                print("🔄 Falling back to API mode...")
                self.bria_local_client = None
                local_model_loaded = False
        
        # Initialize BRIA API client if local model not available or failed
        if not local_model_loaded:
            try:
                if api_token:
                    self.bria_client = BRIAAPIClient(api_token=api_token)
                    print("✅ BRIA API client initialized")
                else:
                    print("⚠️  No BRIA API token provided. Using placeholder mode.")
                    self.bria_client = None
            except Exception as e:
                print(f"Warning: Failed to initialize BRIA API client: {e}. Using placeholder mode.")
                self.bria_client = None
    
    def generate_frame(self, scene_description: str, 
                      fibo_params: Dict, 
                      scene_number: int = 1) -> Frame:
        """
        Generate a single storyboard frame
        
        Args:
            scene_description: Text description of the scene
            fibo_params: FIBO JSON parameters
            scene_number: Scene number for tracking
            
        Returns:
            Generated Frame object
        """
        # Maintain consistency with previous frames
        previous_params = None
        if self.consistency_engine.frame_history:
            previous_params = self.consistency_engine.frame_history[-1]
        
        adjusted_params = self.consistency_engine.maintain_consistency(
            fibo_params, previous_params
        )
        
        # Generate image using FIBO
        # TODO: Implement actual FIBO generation
        # This is a placeholder structure
        image = self._generate_with_fibo(scene_description, adjusted_params)
        
        # Generate HDR version if enabled
        hdr_image = None
        if self.hdr_enabled:
            hdr_image = self._generate_hdr(image, adjusted_params)
        
        return Frame(
            scene_number=scene_number,
            image=image,
            params=adjusted_params,
            hdr_image=hdr_image
        )
    
    def _generate_with_fibo(self, description: str, params: Dict) -> Image.Image:
        """
        Generate image using BRIA AI API with FIBO parameters
        
        Args:
            description: Scene description
            params: FIBO JSON parameters
            
        Returns:
            Generated PIL Image
        """
        # Check if we have any BRIA client available
        if not self.bria_local_client and not self.bria_client:
            # Fallback to placeholder if no BRIA client available
            print("Warning: BRIA not configured. Using placeholder image.")
            placeholder = Image.new('RGB', (self.image_width, self.image_height), color='#2a2a2a')
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(placeholder)
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            except:
                font = ImageFont.load_default()
            text = "BRIA Not Configured"
            bbox = draw.textbbox((0, 0), text, font=font)
            x = (self.image_width - (bbox[2] - bbox[0])) // 2
            y = (self.image_height - (bbox[3] - bbox[1])) // 2
            draw.text((x, y), text, fill='#ffa500', font=font)
            return placeholder
        
        # Build enhanced prompt from description and FIBO parameters
        if self.bria_local_client:
            prompt = self.bria_local_client.build_fibo_prompt(description, params)
        elif self.bria_client:
            prompt = self.bria_client.build_fibo_prompt(description, params)
        else:
            prompt = description  # Fallback
        
        # Build negative prompt from parameters
        negative_prompt = self._build_negative_prompt(params)
        
        try:
            # Generate image using local model or API
            if self.bria_local_client:
                # Use local BRIA-4B-Adapt model
                image = self.bria_local_client.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=self.image_width,
                    height=self.image_height,
                    num_inference_steps=50,
                    guidance_scale=5.0
                )
            elif self.bria_client:
                # Use BRIA API
                model_id = os.getenv("BRIA_MODEL_ID")
                kwargs = {}
                if model_id:
                    kwargs["model_id"] = model_id
                
                image = self.bria_client.generate_image_sync(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    width=self.image_width,
                    height=self.image_height,
                    **kwargs
                )
            else:
                raise Exception("No BRIA client available (neither local nor API)")
            
            return image
        except Exception as e:
            import traceback
            error_msg = f"Error generating image with BRIA API: {e}"
            print(f"\n{'='*60}")
            print(f"BRIA API ERROR:")
            print(f"{error_msg}")
            print(f"{'='*60}")
            print(f"Full traceback:\n{traceback.format_exc()}")
            print(f"{'='*60}\n")
            
            # Check if it's a connection/DNS error
            if "nodename" in str(e) or "servname" in str(e) or "Failed to establish" in str(e):
                print("⚠️  DNS/Connection Error - Check:")
                print("   1. Internet connection")
                print("   2. BRIA API endpoint URL (check dashboard)")
                print("   3. Firewall/proxy settings")
                print("   4. Try setting BRIA_API_BASE_URL in .env")
            elif "401" in str(e) or "403" in str(e) or "Unauthorized" in str(e):
                print("⚠️  Authentication Error - Check:")
                print("   1. BRIA_API_TOKEN in .env is correct")
                print("   2. API key is active in BRIA dashboard")
                print("   3. API key has proper permissions")
            
            # Create error placeholder with message
            error_img = Image.new('RGB', (self.image_width, self.image_height), color='#2a2a2a')
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(error_img)
            
            # Try to use a font, fallback to default if not available
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
                small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
            except:
                font = ImageFont.load_default()
                small_font = ImageFont.load_default()
            
            # Draw error message
            error_text = "BRIA API Error"
            error_detail = str(e)[:50] + "..." if len(str(e)) > 50 else str(e)
            
            # Get text dimensions for centering
            bbox = draw.textbbox((0, 0), error_text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (self.image_width - text_width) // 2
            y = (self.image_height - text_height) // 2 - 20
            
            # Draw main error text
            draw.text((x, y), error_text, fill='#ff6b6b', font=font)
            
            # Draw detail text
            bbox_detail = draw.textbbox((0, 0), error_detail, font=small_font)
            detail_width = bbox_detail[2] - bbox_detail[0]
            x_detail = (self.image_width - detail_width) // 2
            draw.text((x_detail, y + text_height + 10), error_detail, fill='#aaa', font=small_font)
            
            return error_img
    
    def _build_negative_prompt(self, params: Dict) -> str:
        """
        Build negative prompt from FIBO parameters
        
        Args:
            params: FIBO JSON parameters
            
        Returns:
            Negative prompt string
        """
        negative_parts = []
        
        # Add color-related negatives
        color = params.get("color", {})
        if color.get("palette") == "desaturated":
            negative_parts.append("vibrant colors, saturated")
        elif color.get("palette") == "vibrant":
            negative_parts.append("muted colors, desaturated")
        
        # Add lighting-related negatives
        lighting = params.get("lighting", {})
        if lighting.get("style") == "dramatic":
            negative_parts.append("flat lighting, even lighting")
        elif lighting.get("style") == "soft":
            negative_parts.append("harsh lighting, dramatic shadows")
        
        return ", ".join(negative_parts) if negative_parts else None
    
    def _generate_hdr(self, image: Image.Image, params: Dict) -> np.ndarray:
        """
        Convert image to HDR format (16-bit)
        
        Args:
            image: PIL Image
            params: FIBO parameters for HDR processing
            
        Returns:
            16-bit HDR image as numpy array
        """
        # Convert to numpy array
        img_array = np.array(image, dtype=np.float32) / 255.0
        
        # Apply HDR processing based on parameters
        # Enhance dynamic range
        if "lighting" in params:
            intensity = params["lighting"].get("intensity", 0.7)
            img_array = img_array * (intensity * 1.5)  # Expand dynamic range
        
        # Convert to 16-bit
        hdr_array = (img_array * 65535).astype(np.uint16)
        
        return hdr_array
    
    def create_storyboard(self, scenes: List,
                         translator,
                         custom_params: Optional[Dict] = None) -> 'Storyboard':
        """
        Generate storyboard from multiple scenes with parallel processing
        
        Args:
            scenes: List of Scene objects
            translator: LLMTranslator instance
            custom_params: Optional custom FIBO parameters to override defaults
            
        Returns:
            Storyboard object
        """
        import sys
        from pathlib import Path
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        backend_dir = Path(__file__).parent.parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))
        from core.storyboard import Storyboard
        
        def deep_merge(base, override):
            """Deep merge two dictionaries"""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result

        # Function to process a single scene and generate parameters
        def process_scene(scene, previous_params=None):
            try:
                # Translate scene to FIBO JSON
                fibo_params = translator.translate_to_json(
                    scene.description,
                    scene.visual_notes
                )
                
                # Merge custom parameters if provided
                if custom_params:
                    fibo_params = deep_merge(fibo_params, custom_params)
                
                # Apply consistency engine to maintain visual continuity
                adjusted_params = self.consistency_engine.maintain_consistency(
                    fibo_params, previous_params
                )
                
                return {
                    "scene": scene,
                    "params": adjusted_params
                }
            except Exception as e:
                print(f"Error preparing scene {scene.number}: {e}")
                return None

        # Step 1: Prepare parameters sequentially to maintain consistency
        # This ensures visual continuity across frames
        prepared_data = []
        previous_params = None
        for scene in scenes:
            scene_data = process_scene(scene, previous_params)
            if scene_data:
                prepared_data.append(scene_data)
                previous_params = scene_data["params"]
                # Update consistency engine history
                self.consistency_engine.frame_history.append(previous_params)

        # Step 2: Generate images in parallel
        # This is the slow part that we want to parallelize
        def generate_image_for_scene(data):
            try:
                # Generate frame (consistency already applied in params)
                # We need to bypass consistency checking in generate_frame since we already did it
                image = self._generate_with_fibo(data["scene"].description, data["params"])
                
                # Generate HDR version if enabled
                hdr_image = None
                if self.hdr_enabled:
                    hdr_image = self._generate_hdr(image, data["params"])
                
                frame = Frame(
                    scene_number=data["scene"].number,
                    image=image,
                    params=data["params"],
                    hdr_image=hdr_image
                )
                
                # Store scene description in frame params for later retrieval
                frame.params['scene_description'] = data["scene"].description
                return frame
            except Exception as e:
                print(f"Error generating frame for scene {data['scene'].number}: {e}")
                # Create a placeholder frame on error
                placeholder = Image.new('RGB', (self.image_width, self.image_height), color='#2a2a2a')
                from PIL import ImageDraw, ImageFont
                draw = ImageDraw.Draw(placeholder)
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
                except:
                    font = ImageFont.load_default()
                draw.text((10, 10), f"Error: Scene {data['scene'].number}", fill='#ff0000', font=font)
                return Frame(
                    scene_number=data["scene"].number,
                    image=placeholder,
                    params={'error': str(e), 'scene_description': data["scene"].description}
                )

        # Use parallel processing for image generation
        # Limit concurrent requests to avoid overwhelming the API
        max_workers = min(len(prepared_data), 5)  # Max 5 concurrent requests
        frames = [None] * len(prepared_data)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(generate_image_for_scene, data): i 
                for i, data in enumerate(prepared_data)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    frame = future.result()
                    frames[index] = frame
                except Exception as e:
                    print(f"Exception generating frame: {e}")
                    frames[index] = None
        
        # Filter out Nones and ensure frames are in correct order
        frames = [f for f in frames if f is not None]
        
        return Storyboard(frames)

