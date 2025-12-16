"""
BRIA-4B-Adapt Local Model Integration
Uses the Hugging Face model for local image generation
Reference: https://huggingface.co/briaai/BRIA-4B-Adapt
"""
import os
from typing import Optional, Dict
from PIL import Image
import torch
from huggingface_hub import hf_hub_download
import sys
from pathlib import Path

# Try to import the BRIA pipeline
try:
    # Download required files if not present
    backend_dir = Path(__file__).parent.parent
    local_dir = str(backend_dir)
    
    # Download pipeline files
    try:
        from pipeline_bria import BriaPipeline
    except ImportError:
        print("📥 Downloading BRIA-4B-Adapt pipeline files...")
        hf_hub_download(
            repo_id="briaai/BRIA-4B-Adapt",
            filename='pipeline_bria.py',
            local_dir=local_dir
        )
        hf_hub_download(
            repo_id="briaai/BRIA-4B-Adapt",
            filename='transformer_bria.py',
            local_dir=local_dir
        )
        hf_hub_download(
            repo_id="briaai/BRIA-4B-Adapt",
            filename='bria_utils.py',
            local_dir=local_dir
        )
        from pipeline_bria import BriaPipeline
    
    BRIA_LOCAL_AVAILABLE = True
except Exception as e:
    print(f"⚠️  BRIA Local model not available: {e}")
    BRIA_LOCAL_AVAILABLE = False
    BriaPipeline = None


class BRIALocalClient:
    """Client for local BRIA-4B-Adapt model inference"""
    
    def __init__(self, device: Optional[str] = None):
        """
        Initialize local BRIA model
        
        Args:
            device: Device to run on ('cuda', 'cpu', or None for auto)
        """
        if not BRIA_LOCAL_AVAILABLE:
            raise ImportError("BRIA-4B-Adapt model not available. Install dependencies first.")
        
        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        print(f"🚀 Loading BRIA-4B-Adapt model on {self.device}...")
        
        try:
            # Load the pipeline
            self.pipe = BriaPipeline.from_pretrained(
                "briaai/BRIA-4B-Adapt",
                torch_dtype=torch.bfloat16 if self.device == "cuda" else torch.float32,
                trust_remote_code=True
            )
            self.pipe.to(device=self.device)
            print(f"✅ BRIA-4B-Adapt model loaded successfully")
        except Exception as e:
            raise Exception(f"Failed to load BRIA-4B-Adapt model: {e}")
    
    def generate_image(self, prompt: str,
                      negative_prompt: Optional[str] = None,
                      width: int = 1024,
                      height: int = 1024,
                      num_inference_steps: int = 50,
                      guidance_scale: float = 5.0,
                      seed: Optional[int] = None,
                      **kwargs) -> Image.Image:
        """
        Generate image using local BRIA-4B-Adapt model
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Negative prompt (what to avoid)
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            num_inference_steps: Number of inference steps (default: 50)
            guidance_scale: Guidance scale (default: 5.0)
            seed: Random seed for reproducibility
            **kwargs: Additional parameters
            
        Returns:
            PIL Image object
        """
        # Default negative prompt from BRIA documentation
        if negative_prompt is None:
            negative_prompt = (
                "Logo,Watermark,Text,Ugly,Morbid,Extra fingers,"
                "Poorly drawn hands,Mutation,Blurry,Extra limbs,"
                "Gross proportions,Missing arms,Mutated hands,"
                "Long neck,Duplicate,Mutilated,Mutilated hands,"
                "Poorly drawn face,Deformed,Bad anatomy,"
                "Cloned face,Malformed limbs,Missing legs,"
                "Too many fingers"
            )
        
        # Validate resolution (should be ~1M pixels)
        total_pixels = width * height
        if total_pixels < 800000 or total_pixels > 1500000:
            print(f"⚠️  Warning: Resolution {width}x{height} ({total_pixels} pixels) "
                  f"may not be optimal. Recommended: ~1M pixels (e.g., 1024x1024)")
        
        # Set up generator with seed
        generator = None
        if seed is not None:
            generator = torch.Generator(self.device).manual_seed(seed)
        
        try:
            # Generate image
            print(f"🎨 Generating image: {prompt[:50]}...")
            images = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                height=height,
                width=width,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator,
                **kwargs
            ).images
            
            return images[0]
        except Exception as e:
            raise Exception(f"Image generation failed: {e}")
    
    def build_fibo_prompt(self, scene_description: str, fibo_params: Dict) -> str:
        """
        Build enhanced prompt from scene description and FIBO parameters
        
        Args:
            scene_description: Scene description
            fibo_params: FIBO JSON parameters
            
        Returns:
            Enhanced prompt string
        """
        prompt_parts = [scene_description]
        
        # Add camera information
        camera = fibo_params.get("camera", {})
        if camera:
            angle = camera.get("angle", "")
            fov = camera.get("fov", "")
            movement = camera.get("movement", "")
            
            camera_desc = []
            if angle and angle != "eye_level":
                camera_desc.append(f"{angle} angle")
            if fov:
                if fov < 30:
                    camera_desc.append("close-up shot")
                elif fov < 50:
                    camera_desc.append("medium shot")
                else:
                    camera_desc.append("wide shot")
            if movement and movement != "static":
                camera_desc.append(f"{movement.replace('_', ' ')}")
            
            if camera_desc:
                prompt_parts.append(f"Camera: {', '.join(camera_desc)}")
        
        # Add lighting information
        lighting = fibo_params.get("lighting", {})
        if lighting:
            time_of_day = lighting.get("time_of_day", "")
            style = lighting.get("style", "")
            
            lighting_desc = []
            if time_of_day:
                lighting_desc.append(time_of_day.replace("_", " "))
            if style:
                lighting_desc.append(f"{style} lighting")
            
            if lighting_desc:
                prompt_parts.append(f"Lighting: {', '.join(lighting_desc)}")
        
        # Add color information
        color = fibo_params.get("color", {})
        if color:
            palette = color.get("palette", "")
            if palette and palette != "neutral":
                prompt_parts.append(f"Color palette: {palette}")
        
        # Add composition
        composition = fibo_params.get("composition", {})
        if composition:
            framing = composition.get("framing", "")
            if framing:
                prompt_parts.append(f"Framing: {framing}")
        
        return ", ".join(prompt_parts)





