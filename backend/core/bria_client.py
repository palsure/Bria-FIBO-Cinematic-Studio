"""
BRIA AI API Client
Handles communication with BRIA AI API for image generation
Documentation: https://docs.bria.ai
"""

import requests
import time
import os
from typing import Dict, Optional
from PIL import Image
from io import BytesIO
import base64
from dotenv import load_dotenv

load_dotenv()


class BRIAAPIClient:
    """Client for BRIA AI API"""
    
    # BRIA API base URL - from BRIA dashboard
    # Production endpoints: https://engine.prod.bria-api.com/v2/ or /v1/
    BASE_URL = os.getenv("BRIA_API_BASE_URL", "https://engine.prod.bria-api.com/v2")
    
    # Image generation endpoint
    GENERATE_ENDPOINT = os.getenv("BRIA_GENERATE_ENDPOINT", "https://engine.prod.bria-api.com/v2/image/generate")
    
    # Default model ID for image generation (can be overridden)
    DEFAULT_MODEL_ID = os.getenv("BRIA_MODEL_ID", "default")
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize BRIA API client
        
        Args:
            api_token: BRIA API token (or from BRIA_API_TOKEN env var)
        """
        self.api_token = api_token or os.getenv("BRIA_API_TOKEN")
        if not self.api_token:
            raise ValueError("BRIA_API_TOKEN is required. Set it in .env or pass as parameter.")
        
        # BRIA API supports both "api_token" and "x-api-key" header formats
        # Try api_token first (BRIA standard), fallback to x-api-key if needed
        self.headers = {
            "api_token": self.api_token,
            "Content-Type": "application/json"
        }
        # Also support x-api-key format if needed
        # self.headers["x-api-key"] = self.api_token
    
    def generate_image(self, prompt: str, 
                      negative_prompt: Optional[str] = None,
                      width: int = 1024,
                      height: int = 1024,
                      num_images: int = 1,
                      sync: bool = False,
                      model_id: Optional[str] = None,
                      **kwargs) -> Dict:
        """
        Generate image using BRIA AI API
        
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Negative prompt (what to avoid)
            width: Image width (default: 1024)
            height: Image height (default: 1024)
            num_images: Number of images to generate (default: 1)
            sync: Whether to wait for completion (default: False for async)
            model_id: Model ID for tailored generation (default: from env or "default")
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with request_id and status_url (async)
            or image_url (sync)
        """
        # Use the image/generate endpoint
        url = self.GENERATE_ENDPOINT
        
        # Build payload for /image/generate endpoint
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "num_images": num_images,
            "sync": sync,
            **kwargs
        }
        
        # Add model_id if provided (some endpoints support it)
        if model_id and model_id != "default":
            payload["model_id"] = model_id
        
        if negative_prompt:
            payload["negative_prompt"] = negative_prompt
        
        # Debug: Log the URL being called
        print(f"\n🔍 BRIA API Call:")
        print(f"   URL: {url}")
        print(f"   Endpoint: /image/generate")
        if model_id and model_id != "default":
            print(f"   Model ID: {model_id}")
        print(f"   Headers: {list(self.headers.keys())}")
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # Log response structure for debugging
            if "image_url" in result:
                print(f"   ✓ Sync response: image_url received")
            elif "request_id" in result:
                print(f"   ✓ Async response: request_id = {result.get('request_id')}")
            elif "image" in result or "data" in result:
                print(f"   ✓ Direct image data in response")
            
            return result
        except requests.exceptions.HTTPError as e:
            error_detail = ""
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                except:
                    error_detail = e.response.text
                
                # Enhanced error message with URL info
                error_msg = f"BRIA API HTTP error {e.response.status_code}: {error_detail}"
                print(f"\n❌ Error Details:")
                print(f"   URL called: {url}")
                print(f"   Status: {e.response.status_code}")
                print(f"   Response: {error_detail}")
                
                # Suggest fixes for 404
                if e.response.status_code == 404:
                    print(f"\n💡 404 Not Found - Possible fixes:")
                    print(f"   1. Verify endpoint URL: {url}")
                    print(f"   2. Check BRIA_API_BASE_URL in .env matches your account")
                    print(f"   3. Verify BRIA_GENERATE_ENDPOINT if set in .env")
                    print(f"   4. Check BRIA dashboard for correct endpoint format")
                    print(f"   5. Ensure API key has proper permissions")
                
                raise Exception(error_msg)
            else:
                raise Exception(f"BRIA API HTTP error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API request failed: {str(e)}")
    
    def check_status(self, request_id: str) -> Dict:
        """
        Check status of an async request
        
        Args:
            request_id: Request ID from generate_image response
            
        Returns:
            Status dictionary with status, result, etc.
        """
        # Status endpoint might be different - try both patterns
        url = f"{self.BASE_URL}/status/{request_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API status check failed: {str(e)}")
    
    def wait_for_completion(self, request_id: str, 
                           max_wait: int = 300,
                           poll_interval: int = 2) -> Dict:
        """
        Wait for async request to complete
        
        Args:
            request_id: Request ID
            max_wait: Maximum wait time in seconds (default: 300)
            poll_interval: Polling interval in seconds (default: 2)
            
        Returns:
            Final status dictionary with result
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            status = self.check_status(request_id)
            
            if status.get("status") == "COMPLETED":
                return status
            elif status.get("status") == "ERROR":
                error = status.get("error", {})
                raise Exception(f"BRIA API error: {error.get('message', 'Unknown error')}")
            elif status.get("status") == "UNKNOWN":
                raise Exception(f"BRIA API unknown error. Request ID: {request_id}")
            
            # Status is IN_PROGRESS, continue polling
            time.sleep(poll_interval)
        
        raise TimeoutError(f"Request {request_id} did not complete within {max_wait} seconds")
    
    def generate_image_sync(self, prompt: str, 
                           negative_prompt: Optional[str] = None,
                           width: int = 1024,
                           height: int = 1024,
                           model_id: Optional[str] = None,
                           **kwargs) -> Image.Image:
        """
        Generate image synchronously and return PIL Image
        
        Args:
            prompt: Text prompt
            negative_prompt: Negative prompt
            width: Image width
            height: Image height
            **kwargs: Additional parameters
            
        Returns:
            PIL Image object
        """
        # Try sync first
        try:
            response = self.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                sync=True,
                model_id=model_id,
                **kwargs
            )
            
            if "image_url" in response:
                return self._download_image(response["image_url"])
            elif "image" in response:
                # Handle base64 encoded image directly
                return self._decode_base64_image(response["image"])
            elif "data" in response:
                # Handle base64 data URI
                image_data = response["data"]
                if isinstance(image_data, str) and image_data.startswith("data:image"):
                    return self._decode_base64_image(image_data.split(",")[1])
                return self._decode_base64_image(image_data)
        except Exception as e:
            print(f"⚠️  Sync generation failed: {e}, falling back to async")
            pass
        
        # Fallback to async
        response = self.generate_image(
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            sync=False,
            model_id=model_id,
            **kwargs
        )
        
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        # Wait for completion
        final_status = self.wait_for_completion(request_id)
        
        result = final_status.get("result", {})
        image_url = result.get("image_url")
        
        if not image_url:
            raise Exception("No image_url in result")
        
        return self._download_image(image_url)
    
    def _download_image(self, image_url: str) -> Image.Image:
        """
        Download image from URL and return PIL Image
        
        Args:
            image_url: URL of the image
            
        Returns:
            PIL Image object
        """
        try:
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            return Image.open(BytesIO(response.content))
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image: {str(e)}")
    
    def _decode_base64_image(self, image_data: str) -> Image.Image:
        """
        Decode base64 encoded image and return PIL Image
        
        Args:
            image_data: Base64 encoded image string
            
        Returns:
            PIL Image object
        """
        try:
            # Remove data URI prefix if present
            if isinstance(image_data, str) and "," in image_data:
                image_data = image_data.split(",")[1]
            
            image_bytes = base64.b64decode(image_data)
            return Image.open(BytesIO(image_bytes))
        except Exception as e:
            raise Exception(f"Failed to decode base64 image: {str(e)}")
    
    def build_fibo_prompt(self, scene_description: str, fibo_params: Dict) -> str:
        """
        Build BRIA prompt from scene description and FIBO parameters
        
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
    
    # ========== IMAGE EDITING FEATURES ==========
    
    def edit_image(self, image_url: str, 
                   prompt: str,
                   edit_type: str = "reimagine",
                   sync: bool = False,
                   **kwargs) -> Dict:
        """
        Edit an existing image using BRIA AI
        
        Args:
            image_url: URL or base64 of source image
            prompt: Description of desired changes
            edit_type: Type of edit - "reimagine", "genfill", "eraser", "background"
            sync: Whether to wait for completion
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with request_id or result
        """
        url = f"{self.BASE_URL}/edit"
        
        payload = {
            "image_url": image_url,
            "prompt": prompt,
            "edit_type": edit_type,
            "sync": sync,
            **kwargs
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API edit request failed: {str(e)}")
    
    def reimagine_image(self, image_url: str,
                       prompt: str,
                       sync: bool = False) -> Image.Image:
        """
        Reimagine an image - maintain outline/depth, change materials/colors/textures/lighting
        
        Args:
            image_url: URL or base64 of source image
            prompt: Description of desired changes
            sync: Whether to wait for completion
            
        Returns:
            Edited PIL Image
        """
        response = self.edit_image(
            image_url=image_url,
            prompt=prompt,
            edit_type="reimagine",
            sync=sync
        )
        
        if sync and "image_url" in response:
            return self._download_image(response["image_url"])
        
        # Async handling
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        final_status = self.wait_for_completion(request_id)
        result = final_status.get("result", {})
        image_url = result.get("image_url")
        
        if not image_url:
            raise Exception("No image_url in result")
        
        return self._download_image(image_url)
    
    def generative_fill(self, image_url: str,
                       prompt: str,
                       mask_url: Optional[str] = None,
                       sync: bool = False) -> Image.Image:
        """
        Add, modify, or replace objects in an image using Generative Fill
        
        Args:
            image_url: URL or base64 of source image
            prompt: Description of object to add/modify
            mask_url: Optional mask image URL (if None, uses prompt to determine area)
            sync: Whether to wait for completion
            
        Returns:
            Edited PIL Image
        """
        payload = {
            "image_url": image_url,
            "prompt": prompt,
            "edit_type": "genfill"
        }
        
        if mask_url:
            payload["mask_url"] = mask_url
        
        response = self.edit_image(
            image_url=image_url,
            prompt=prompt,
            edit_type="genfill",
            sync=sync,
            mask_url=mask_url
        )
        
        if sync and "image_url" in response:
            return self._download_image(response["image_url"])
        
        # Async handling
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        final_status = self.wait_for_completion(request_id)
        result = final_status.get("result", {})
        image_url = result.get("image_url")
        
        if not image_url:
            raise Exception("No image_url in result")
        
        return self._download_image(image_url)
    
    def erase_object(self, image_url: str,
                    mask_url: Optional[str] = None,
                    prompt: Optional[str] = None,
                    sync: bool = False) -> Image.Image:
        """
        Remove unwanted elements from an image using Eraser API
        
        Args:
            image_url: URL or base64 of source image
            mask_url: Optional mask image URL indicating what to remove
            prompt: Optional text description of what to remove
            sync: Whether to wait for completion
            
        Returns:
            Edited PIL Image with objects removed
        """
        payload = {
            "image_url": image_url,
            "edit_type": "eraser"
        }
        
        if mask_url:
            payload["mask_url"] = mask_url
        if prompt:
            payload["prompt"] = prompt
        
        response = self.edit_image(
            image_url=image_url,
            prompt=prompt or "",
            edit_type="eraser",
            sync=sync,
            mask_url=mask_url
        )
        
        if sync and "image_url" in response:
            return self._download_image(response["image_url"])
        
        # Async handling
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        final_status = self.wait_for_completion(request_id)
        result = final_status.get("result", {})
        image_url = result.get("image_url")
        
        if not image_url:
            raise Exception("No image_url in result")
        
        return self._download_image(image_url)
    
    def replace_background(self, image_url: str,
                          background_prompt: str,
                          sync: bool = False) -> Image.Image:
        """
        Replace image background with AI-generated background
        
        Args:
            image_url: URL or base64 of source image
            background_prompt: Description of desired background
            sync: Whether to wait for completion
            
        Returns:
            Image with new background
        """
        response = self.edit_image(
            image_url=image_url,
            prompt=background_prompt,
            edit_type="background",
            sync=sync
        )
        
        if sync and "image_url" in response:
            return self._download_image(response["image_url"])
        
        # Async handling
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        final_status = self.wait_for_completion(request_id)
        result = final_status.get("result", {})
        image_url = result.get("image_url")
        
        if not image_url:
            raise Exception("No image_url in result")
        
        return self._download_image(image_url)
    
    def upscale_image(self, image_url: str,
                     scale_factor: int = 2,
                     sync: bool = False) -> Image.Image:
        """
        Upscale image resolution using AI enhancement
        
        Args:
            image_url: URL or base64 of source image
            scale_factor: Upscale factor (2, 4, etc.)
            sync: Whether to wait for completion
            
        Returns:
            Upscaled PIL Image
        """
        url = f"{self.BASE_URL}/upscale"
        
        payload = {
            "image_url": image_url,
            "scale_factor": scale_factor,
            "sync": sync
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if sync and "image_url" in result:
                return self._download_image(result["image_url"])
            
            # Async handling
            request_id = result.get("request_id")
            if not request_id:
                raise Exception("No request_id in response")
            
            final_status = self.wait_for_completion(request_id)
            result_data = final_status.get("result", {})
            image_url = result_data.get("image_url")
            
            if not image_url:
                raise Exception("No image_url in result")
            
            return self._download_image(image_url)
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API upscale request failed: {str(e)}")
    
    # ========== VIDEO GENERATION FEATURES ==========
    
    def generate_video(self, prompt: str,
                      image_url: Optional[str] = None,
                      duration: float = 3.0,
                      fps: int = 24,
                      width: int = 1920,
                      height: int = 1080,
                      sync: bool = False,
                      **kwargs) -> Dict:
        """
        Generate video from text prompt or image
        
        Args:
            prompt: Text description for video generation
            image_url: Optional source image URL (for image-to-video)
            duration: Video duration in seconds (default: 3.0)
            fps: Frames per second (default: 24)
            width: Video width (default: 1920)
            height: Video height (default: 1080)
            sync: Whether to wait for completion
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with request_id or video_url
        """
        # Use correct endpoint: /video/generate/tailored/image-to-video
        url = f"{self.BASE_URL}/video/generate/tailored/image-to-video"
        
        payload = {
            "prompt": prompt,
            "duration": duration,
            "fps": fps,
            "width": width,
            "height": height,
            "sync": sync,
            **kwargs
        }
        
        if image_url:
            payload["image_url"] = image_url
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API video generation failed: {str(e)}")
    
    def generate_video_sync(self, prompt: str,
                           image_url: Optional[str] = None,
                           duration: float = 3.0,
                           fps: int = 24,
                           width: int = 1920,
                           height: int = 1080,
                           **kwargs) -> str:
        """
        Generate video synchronously and return video URL
        
        Args:
            prompt: Text description
            image_url: Optional source image
            duration: Video duration
            fps: Frames per second
            width: Video width
            height: Video height
            **kwargs: Additional parameters
            
        Returns:
            Video URL string
        """
        # Try sync first
        try:
            response = self.generate_video(
                prompt=prompt,
                image_url=image_url,
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                sync=True,
                **kwargs
            )
            
            if "video_url" in response:
                return response["video_url"]
        except Exception:
            pass
        
        # Fallback to async
        response = self.generate_video(
            prompt=prompt,
            image_url=image_url,
            duration=duration,
            fps=fps,
            width=width,
            height=height,
            sync=False,
            **kwargs
        )
        
        request_id = response.get("request_id")
        if not request_id:
            raise Exception("No request_id in response")
        
        # Wait for completion (longer timeout for video)
        final_status = self.wait_for_completion(request_id, max_wait=600)
        
        result = final_status.get("result", {})
        video_url = result.get("video_url")
        
        if not video_url:
            raise Exception("No video_url in result")
        
        return video_url
    
    def edit_video(self, video_url: str,
                  edit_type: str,
                  prompt: Optional[str] = None,
                  sync: bool = False,
                  **kwargs) -> Dict:
        """
        Edit video using BRIA AI (background replacement, object removal, etc.)
        
        Args:
            video_url: URL of source video
            edit_type: Type of edit - "background", "eraser", "enhance"
            prompt: Optional description of changes
            sync: Whether to wait for completion
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary with request_id or video_url
        """
        url = f"{self.BASE_URL}/video/edit"
        
        payload = {
            "video_url": video_url,
            "edit_type": edit_type,
            "sync": sync,
            **kwargs
        }
        
        if prompt:
            payload["prompt"] = prompt
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"BRIA API video edit failed: {str(e)}")
    
    # ========== UTILITY METHODS ==========
    
    def image_to_base64(self, image: Image.Image) -> str:
        """
        Convert PIL Image to base64 string (for API requests)
        
        Args:
            image: PIL Image object
            
        Returns:
            Base64 encoded string (without data URI prefix)
        """
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

