"""
Storyboard Data Structure and Export Functions
"""

from typing import List, Optional
from dataclasses import dataclass
from .fibo_engine import Frame
import os


@dataclass
class Storyboard:
    """Represents a complete storyboard"""
    frames: List[Frame]
    
    def to_dict(self) -> dict:
        """Convert storyboard to dictionary for API response"""
        return {
            "frames": [frame.to_dict() for frame in self.frames],
            "frame_count": len(self.frames)
        }
    
    def export_pdf(self, output_path: str):
        """Export storyboard as PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.lib.units import inch
            from reportlab.platypus import SimpleDocTemplate, Image as RLImage, Spacer, Paragraph, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.enums import TA_CENTER
            from io import BytesIO
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Create custom style for scene numbers
            scene_style = styles['Heading2']
            scene_style.alignment = TA_CENTER
            
            # Layout: 2 frames per page
            frames_per_page = 2
            
            for i, frame in enumerate(self.frames):
                # Add page break if needed (except for first frame)
                if i > 0 and i % frames_per_page == 0:
                    story.append(PageBreak())
                
                # Add scene number header
                scene_text = f"Scene {frame.scene_number}"
                story.append(Paragraph(scene_text, scene_style))
                story.append(Spacer(1, 0.1*inch))
                
                # Add frame image
                img_buffer = BytesIO()
                frame.image.save(img_buffer, format='PNG')
                img_buffer.seek(0)
                
                # Calculate image dimensions maintaining aspect ratio
                img_width = 6 * inch
                aspect_ratio = frame.image.height / frame.image.width
                img_height = img_width * aspect_ratio
                
                # Limit height to fit on page
                max_height = 4 * inch
                if img_height > max_height:
                    img_height = max_height
                    img_width = img_height / aspect_ratio
                
                img = RLImage(img_buffer, width=img_width, height=img_height)
                story.append(img)
                
                # Add spacing after image
                story.append(Spacer(1, 0.2*inch))
            
            doc.build(story)
            print(f"PDF exported to {output_path}")
            return True
            
        except ImportError as e:
            error_msg = "reportlab not installed. Install with: pip install reportlab"
            print(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = f"Error exporting PDF: {e}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def export_hdr(self, output_dir: str, format: str = "exr"):
        """Export frames as HDR images"""
        os.makedirs(output_dir, exist_ok=True)
        
        for frame in self.frames:
            if frame.hdr_image is not None:
                output_path = os.path.join(
                    output_dir, 
                    f"scene_{frame.scene_number:03d}.{format}"
                )
                
                if format == "exr":
                    try:
                        import OpenEXR
                        import Imath
                        
                        # Convert to OpenEXR format
                        # This is a simplified version
                        # Full implementation would handle RGB channels properly
                        print(f"HDR export to {output_path} (placeholder)")
                        # TODO: Implement full OpenEXR export
                        
                    except ImportError:
                        print("OpenEXR not installed. Install with: pip install OpenEXR")
                else:
                    # Fallback to TIFF 16-bit
                    from PIL import Image
                    hdr_img = Image.fromarray(frame.hdr_image, mode='I;16')
                    output_path = output_path.replace('.exr', '.tiff')
                    hdr_img.save(output_path)
                    print(f"HDR exported to {output_path}")
    
    def export_animatic(self, output_path: str, duration_per_frame: float = 3.0):
        """Export storyboard as animatic video"""
        try:
            import cv2
            import numpy as np
            
            if not self.frames:
                raise ValueError("No frames to export")
            
            # Get frame dimensions
            first_frame = self.frames[0].image
            width, height = first_frame.size
            
            # Video writer with H.264 codec (better compatibility)
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 1.0 / duration_per_frame if duration_per_frame > 0 else 1.0
            out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not out.isOpened():
                # Fallback to imageio if OpenCV fails
                return self._export_animatic_imageio(output_path, duration_per_frame)
            
            for frame in self.frames:
                # Convert PIL to OpenCV format
                img_array = np.array(frame.image)
                # Handle RGBA images
                if img_array.shape[2] == 4:
                    # Convert RGBA to RGB
                    img_rgb = img_array[:, :, :3]
                    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                else:
                    img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
                
                # Write frame multiple times for duration
                frames_to_write = max(1, int(fps * duration_per_frame))
                for _ in range(frames_to_write):
                    out.write(img_bgr)
            
            out.release()
            print(f"Animatic exported to {output_path}")
            return True
            
        except ImportError:
            # Fallback to imageio
            print("opencv-python not available, using imageio fallback")
            return self._export_animatic_imageio(output_path, duration_per_frame)
        except Exception as e:
            error_msg = f"Error exporting animatic with OpenCV: {e}"
            print(error_msg)
            # Try imageio as fallback
            try:
                return self._export_animatic_imageio(output_path, duration_per_frame)
            except Exception as e2:
                raise Exception(f"{error_msg}. Fallback also failed: {e2}") from e
    
    def _export_animatic_imageio(self, output_path: str, duration_per_frame: float = 3.0):
        """Export animatic using imageio (fallback method)"""
        try:
            import imageio
            import numpy as np
            
            if not self.frames:
                raise ValueError("No frames to export")
            
            # Prepare frames
            frames_data = []
            for frame in self.frames:
                # Convert PIL to numpy array
                img_array = np.array(frame.image)
                # Handle RGBA
                if img_array.shape[2] == 4:
                    img_array = img_array[:, :, :3]  # Remove alpha channel
                frames_data.append(img_array)
            
            # Calculate fps
            fps = 1.0 / duration_per_frame if duration_per_frame > 0 else 1.0
            
            # Write video
            imageio.mimwrite(output_path, frames_data, fps=fps, codec='libx264', quality=8)
            print(f"Animatic exported to {output_path} using imageio")
            return True
            
        except ImportError as e:
            error_msg = "imageio or imageio-ffmpeg not installed. Install with: pip install imageio imageio-ffmpeg"
            print(error_msg)
            raise ImportError(error_msg) from e
        except Exception as e:
            error_msg = f"Error exporting animatic with imageio: {e}"
            print(error_msg)
            raise Exception(error_msg) from e
    
    def generate_ai_animatic(self, bria_client, output_path: str, 
                            duration_per_frame: float = 3.0):
        """
        Generate AI-powered animatic using BRIA video generation
        
        Args:
            bria_client: BRIAAPIClient instance
            output_path: Output video path
            duration_per_frame: Duration per frame in seconds
        """
        try:
            import requests
            
            # Generate video for each frame
            video_urls = []
            for frame in self.frames:
                # Convert frame to base64
                frame_base64 = bria_client.image_to_base64(frame.image)
                
                # Build prompt from frame parameters
                prompt = self._build_video_prompt(frame)
                
                # Generate video from frame
                video_url = bria_client.generate_video_sync(
                    prompt=prompt,
                    image_url=f"data:image/png;base64,{frame_base64}",
                    duration=duration_per_frame,
                    fps=24,
                    width=frame.image.width,
                    height=frame.image.height
                )
                video_urls.append(video_url)
            
            # Download and concatenate videos
            # Note: This is a simplified version - full implementation would
            # use ffmpeg or similar to concatenate video segments
            print(f"Generated {len(video_urls)} video segments")
            print(f"AI animatic segments ready. Full concatenation requires ffmpeg.")
            
        except Exception as e:
            print(f"Error generating AI animatic: {e}")
            # Fallback to regular animatic
            self.export_animatic(output_path, duration_per_frame)
    
    def _build_video_prompt(self, frame) -> str:
        """Build video generation prompt from frame"""
        params = frame.params
        prompt_parts = []
        
        # Add camera movement
        camera = params.get("camera", {})
        if camera.get("movement") and camera["movement"] != "static":
            prompt_parts.append(f"Camera {camera['movement'].replace('_', ' ')}")
        
        # Add lighting
        lighting = params.get("lighting", {})
        if lighting.get("time_of_day"):
            prompt_parts.append(f"{lighting['time_of_day'].replace('_', ' ')} atmosphere")
        
        return ", ".join(prompt_parts) if prompt_parts else "Cinematic scene"
    
    def enhance_frames(self, bria_client, upscale_factor: int = 2):
        """
        Enhance storyboard frames using BRIA upscaling
        
        Args:
            bria_client: BRIAAPIClient instance
            upscale_factor: Upscale factor (2, 4, etc.)
        """
        for frame in self.frames:
            try:
                # Convert to base64
                frame_base64 = bria_client.image_to_base64(frame.image)
                
                # Upscale image
                upscaled = bria_client.upscale_image(
                    image_url=f"data:image/png;base64,{frame_base64}",
                    scale_factor=upscale_factor,
                    sync=True
                )
                
                # Update frame with upscaled image
                frame.image = upscaled
                print(f"Enhanced frame {frame.scene_number}")
            except Exception as e:
                print(f"Error enhancing frame {frame.scene_number}: {e}")

