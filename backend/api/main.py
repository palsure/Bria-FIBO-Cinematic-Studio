"""
FastAPI Main Application
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
from datetime import datetime
import os
import tempfile
import shutil
from pathlib import Path
import sys
from io import BytesIO
import base64
# PIL Image imported lazily when needed to speed up startup

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Lazy imports - don't import heavy modules at startup
# This significantly speeds up application startup time

app = FastAPI(
    title="FIBO Studio API",
    description="AI-Powered Cinematic Pre-Visualization Pipeline",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy initialization of services - only create when needed
# This prevents blocking server startup
_script_processor = None
_llm_translator = None

def get_script_processor():
    """Lazy initialization of script processor"""
    global _script_processor
    if _script_processor is None:
        from core.script_parser import ScriptProcessor
        _script_processor = ScriptProcessor()
    return _script_processor

def get_llm_translator(provider="bria"):
    """Lazy initialization of LLM translator"""
    # Always create new instance if provider changes
    # This allows different providers per request
    from core.llm_translator import LLMTranslator
    return LLMTranslator(provider=provider)

# Initialize FIBO generator lazily (only when needed)
# This prevents blocking server startup if model loading takes time
fibo_generator = None

def get_fibo_generator():
    """Lazy initialization of FIBO generator"""
    global fibo_generator
    if fibo_generator is None:
        bria_api_token = os.getenv("BRIA_API_TOKEN")
        # Default to False for Vercel (local models too large for serverless)
        # Set USE_LOCAL_BRIA=true explicitly if you want local models
        use_local = os.getenv("USE_LOCAL_BRIA", "false").lower() == "true"
        try:
            from core.fibo_engine import FIBOGenerator
            fibo_generator = FIBOGenerator(
                api_token=bria_api_token,
                hdr_enabled=True,
                image_width=1920,
                image_height=1080,
                use_local_model=use_local
            )
        except Exception as e:
            print(f"Warning: Failed to initialize FIBO generator: {e}")
            # Create a minimal generator that will use placeholder mode
            from core.fibo_engine import FIBOGenerator
            fibo_generator = FIBOGenerator(
                api_token=None,
                hdr_enabled=True,
                image_width=1920,
                image_height=1080,
                use_local_model=False
            )
    return fibo_generator

# Output directory - lazy initialization for faster startup
_OUTPUT_DIR = None

def get_output_dir():
    """Get output directory, creating it if needed"""
    global _OUTPUT_DIR
    if _OUTPUT_DIR is None:
        # Try local directory first, fallback to /tmp
        output_dir = Path("./outputs")
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            # Quick write test
            test_file = output_dir / ".write_test"
            test_file.touch()
            test_file.unlink()
            _OUTPUT_DIR = output_dir
        except (OSError, PermissionError):
            # Fallback to /tmp
            _OUTPUT_DIR = Path("/tmp/outputs")
            _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return _OUTPUT_DIR

# For backward compatibility, create OUTPUT_DIR variable
OUTPUT_DIR = get_output_dir()


# Request/Response Models
class ScriptParseRequest(BaseModel):
    content: str


class SceneResponse(BaseModel):
    number: int
    location: str
    description: str
    visual_notes: Dict[str, str]
    characters: List[str]


class FrameResponse(BaseModel):
    scene_number: int
    image: str  # base64 encoded
    params: Dict


class StoryboardResponse(BaseModel):
    frames: List[FrameResponse]
    frame_count: int
    script_content: Optional[str] = None


class GenerateRequest(BaseModel):
    script_content: str
    llm_provider: Optional[str] = "bria"  # Default to BRIA/FIBO
    hdr_enabled: Optional[bool] = True
    custom_params: Optional[Dict] = None  # Custom FIBO parameters


class ExportPDFRequest(BaseModel):
    """Request model for exporting PDF - can use existing frames or regenerate"""
    frames: Optional[List[Any]] = None  # Use existing frames if provided (faster) - accepts any format
    script_content: Optional[str] = None  # Fallback to regeneration if frames not provided
    llm_provider: Optional[str] = None
    hdr_enabled: Optional[bool] = None
    custom_params: Optional[Dict[str, Any]] = None
    
    class Config:
        # Allow extra fields to be more flexible
        extra = "allow"


class EditFrameRequest(BaseModel):
    frame_index: int
    edit_type: str  # "reimagine", "genfill", "eraser", "background", "upscale"
    prompt: Optional[str] = None
    mask_url: Optional[str] = None
    scale_factor: Optional[int] = 2


class EnhanceStoryboardRequest(BaseModel):
    storyboard_data: Dict
    upscale_factor: Optional[int] = 2


# API Routes
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "FIBO Studio API", "status": "running"}


@app.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


@app.post("/api/parse-script", response_model=List[SceneResponse])
async def parse_script(request: ScriptParseRequest):
    """
    Parse script content and extract scenes
    
    Args:
        request: Script content as string
        
    Returns:
        List of parsed scenes
    """
    try:
        script_processor = get_script_processor()
        scenes = script_processor.parse_script_content(request.content)
        
        return [
            SceneResponse(
                number=scene.number,
                location=scene.location,
                description=scene.description,
                visual_notes=scene.visual_notes,
                characters=scene.characters
            )
            for scene in scenes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/upload-script", response_model=List[SceneResponse])
async def upload_script(file: UploadFile = File(...)):
    """
    Upload and parse script file
    
    Args:
        file: Script file (.txt, .fdx, .fountain)
        
    Returns:
        List of parsed scenes
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp_file:
            shutil.copyfileobj(file.file, tmp_file)
            tmp_path = tmp_file.name
        
        # Parse script
        script_processor = get_script_processor()
        scenes = script_processor.parse_script(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return [
            SceneResponse(
                number=scene.number,
                location=scene.location,
                description=scene.description,
                visual_notes=scene.visual_notes,
                characters=scene.characters
            )
            for scene in scenes
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-storyboard", response_model=StoryboardResponse)
async def generate_storyboard(request: GenerateRequest):
    """
    Generate storyboard from script content
    
    Args:
        request: Generation request with script content and options
        
    Returns:
        Generated storyboard with frames
    """
    try:
        # Parse script
        script_processor = get_script_processor()
        scenes = script_processor.parse_script_content(request.script_content)
        
        if not scenes:
            raise HTTPException(status_code=400, detail="No scenes found in script")
        
        # Initialize translator with specified provider
        translator = get_llm_translator(provider=request.llm_provider)
        
        # Generate storyboard with custom parameters if provided
        generator = get_fibo_generator()
        if request.custom_params:
            # Override default parameters with custom ones
            storyboard = generator.create_storyboard(scenes, translator, custom_params=request.custom_params)
        else:
            storyboard = generator.create_storyboard(scenes, translator)
        
        # Convert to response format
        frame_responses = [
            FrameResponse(
                scene_number=frame.scene_number,
                image=frame.to_dict()["image"],
                params=frame.params
            )
            for frame in storyboard.frames
        ]
        
        return StoryboardResponse(
            frames=frame_responses,
            frame_count=len(frame_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/export-pdf")
async def export_pdf(request: ExportPDFRequest):
    """
    Export storyboard as PDF - uses existing frames if provided (fast), otherwise regenerates
    
    Args:
        request: Export request with frames or script content
        
    Returns:
        PDF file download
    """
    try:
        from PIL import Image
        from io import BytesIO
        import base64
        from core.fibo_engine import Frame
        from core.storyboard import Storyboard
        
        # Extract values from request
        frames = request.frames if hasattr(request, 'frames') else None
        script_content = request.script_content if hasattr(request, 'script_content') else None
        llm_provider = request.llm_provider if hasattr(request, 'llm_provider') else "bria"
        hdr_enabled = request.hdr_enabled if hasattr(request, 'hdr_enabled') else True
        custom_params = request.custom_params if hasattr(request, 'custom_params') else None
        
        # Validate that either frames or script_content is provided
        if not frames and not script_content:
            raise HTTPException(status_code=400, detail="Either 'frames' or 'script_content' must be provided")
        
        # If frames are provided, use them directly (fast path)
        if frames and len(frames) > 0:
            # Convert frame dictionaries to Frame objects
            frame_objects = []
            for frame_data in frames:
                # Handle both dict and object formats
                if isinstance(frame_data, dict):
                    image_data = frame_data.get("image", "")
                    scene_number = frame_data.get("scene_number", 0)
                    params = frame_data.get("params", {})
                else:
                    # If it's a FrameResponse object, convert to dict
                    image_data = frame_data.image if hasattr(frame_data, 'image') else ""
                    scene_number = frame_data.scene_number if hasattr(frame_data, 'scene_number') else 0
                    params = frame_data.params if hasattr(frame_data, 'params') else {}
                
                if not image_data:
                    continue
                
                # Remove data URL prefix if present
                if isinstance(image_data, str) and image_data.startswith("data:image"):
                    image_data = image_data.split(",")[1]
                
                try:
                    # Decode base64 to PIL Image
                    img_bytes = base64.b64decode(image_data)
                    img = Image.open(BytesIO(img_bytes))
                    
                    # Create Frame object
                    frame = Frame(
                        scene_number=scene_number,
                        image=img,
                        params=params if params else {}
                    )
                    frame_objects.append(frame)
                except Exception as e:
                    print(f"Error processing frame {scene_number}: {e}")
                    continue
            
            if not frame_objects:
                raise HTTPException(status_code=400, detail="No valid frames could be processed")
            
            # Create storyboard from existing frames
            storyboard = Storyboard(frame_objects)
        else:
            # Fallback: Generate storyboard from script (slower)
            if not script_content:
                raise HTTPException(status_code=400, detail="Either frames or script_content must be provided")
            
            script_processor = get_script_processor()
            scenes = script_processor.parse_script_content(script_content)
            translator = get_llm_translator(provider=llm_provider or "bria")
            generator = get_fibo_generator()
            
            # Generate storyboard with custom parameters if provided
            if custom_params:
                storyboard = generator.create_storyboard(scenes, translator, custom_params=custom_params)
            else:
                storyboard = generator.create_storyboard(scenes, translator)
        
        # Export PDF
        pdf_path = get_output_dir() / "storyboard.pdf"
        result = storyboard.export_pdf(str(pdf_path))
        
        # Check if PDF was created successfully
        if not pdf_path.exists():
            raise HTTPException(
                status_code=500, 
                detail="PDF export failed. reportlab may not be installed. Install with: pip install reportlab"
            )
        
        return FileResponse(
            path=str(pdf_path),
            media_type="application/pdf",
            filename="storyboard.pdf"
        )
    except HTTPException:
        raise
    except ValueError as e:
        # Pydantic validation errors
        raise HTTPException(status_code=422, detail=f"Validation error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export error: {str(e)}")


@app.post("/api/export-animatic")
async def export_animatic(request: GenerateRequest, duration: float = 3.0):
    """
    Generate storyboard and export as animatic video
    
    Args:
        request: Generation request
        duration: Duration per frame in seconds
        
    Returns:
        Video file download
    """
    try:
        # Generate storyboard
        script_processor = get_script_processor()
        scenes = script_processor.parse_script_content(request.script_content)
        translator = get_llm_translator(provider=request.llm_provider)
        generator = get_fibo_generator()
        
        # Generate storyboard with custom parameters if provided
        if request.custom_params:
            storyboard = generator.create_storyboard(scenes, translator, custom_params=request.custom_params)
        else:
            storyboard = generator.create_storyboard(scenes, translator)
        
        # Export animatic
        video_path = get_output_dir() / "animatic.mp4"
        storyboard.export_animatic(str(video_path), duration_per_frame=duration)
        
        # Check if video was created successfully
        if not video_path.exists():
            raise HTTPException(
                status_code=500,
                detail="Animatic export failed. Check if opencv-python and imageio-ffmpeg are installed."
            )
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename="animatic.mp4"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Animatic export error: {str(e)}")


class RegenerateSceneRequest(BaseModel):
    scene_number: int
    scene_description: str
    params: Dict
    script_content: Optional[str] = None


@app.post("/api/regenerate-scene")
async def regenerate_scene(request: RegenerateSceneRequest):
    """
    Regenerate a single scene with new parameters
    
    Args:
        request: Scene regeneration request with new parameters
        
    Returns:
        Regenerated frame
    """
    try:
        generator = get_fibo_generator()
        
        # Generate frame with new parameters
        frame = generator.generate_frame(
            request.scene_description,
            request.params,
            request.scene_number
        )
        
        # Convert to response format
        return FrameResponse(
            scene_number=frame.scene_number,
            image=frame.to_dict()["image"],
            params=frame.params
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/edit-frame")
async def edit_frame(request: EditFrameRequest, storyboard_data: Dict):
    """
    Edit a single storyboard frame using BRIA AI editing features
    
    Args:
        request: Edit request with frame index and edit type
        storyboard_data: Storyboard data from previous generation
        
    Returns:
        Edited frame
    """
    try:
        from core.bria_client import BRIAAPIClient
        
        bria_client = BRIAAPIClient(api_token=os.getenv("BRIA_API_TOKEN"))
        
        # Get frame from storyboard data
        frames = storyboard_data.get("frames", [])
        if request.frame_index >= len(frames):
            raise HTTPException(status_code=400, detail="Invalid frame index")
        
        frame = frames[request.frame_index]
        image_url = frame.get("image")  # base64 data URI
        
        # Extract base64 from data URI
        if image_url.startswith("data:image"):
            image_base64 = image_url.split(",")[1]
            image_url = f"data:image/png;base64,{image_base64}"
        
        # Perform edit based on type
        if request.edit_type == "reimagine":
            edited_image = bria_client.reimagine_image(
                image_url=image_url,
                prompt=request.prompt or "Enhance the scene",
                sync=True
            )
        elif request.edit_type == "genfill":
            edited_image = bria_client.generative_fill(
                image_url=image_url,
                prompt=request.prompt or "Add elements",
                mask_url=request.mask_url,
                sync=True
            )
        elif request.edit_type == "eraser":
            edited_image = bria_client.erase_object(
                image_url=image_url,
                mask_url=request.mask_url,
                prompt=request.prompt,
                sync=True
            )
        elif request.edit_type == "background":
            edited_image = bria_client.replace_background(
                image_url=image_url,
                background_prompt=request.prompt or "New background",
                sync=True
            )
        elif request.edit_type == "upscale":
            edited_image = bria_client.upscale_image(
                image_url=image_url,
                scale_factor=request.scale_factor or 2,
                sync=True
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown edit type: {request.edit_type}")
        
        # Convert to base64 for response
        img_buffer = BytesIO()
        edited_image.save(img_buffer, format='PNG')
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
        return FrameResponse(
            scene_number=frame.get("scene_number", request.frame_index + 1),
            image=f"data:image/png;base64,{img_base64}",
            params=frame.get("params", {})
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-ai-animatic")
async def generate_ai_animatic(request: GenerateRequest, duration: float = 3.0):
    """
    Generate AI-powered animatic using BRIA video generation
    
    Args:
        request: Generation request with script content
        duration: Duration per frame in seconds
        
    Returns:
        Video file download
    """
    try:
        from core.bria_client import BRIAAPIClient
        
        # Generate storyboard first
        script_processor = get_script_processor()
        scenes = script_processor.parse_script_content(request.script_content)
        translator = get_llm_translator(provider=request.llm_provider)
        generator = get_fibo_generator()
        storyboard = generator.create_storyboard(scenes, translator)
        
        # Initialize BRIA client
        bria_client = BRIAAPIClient(api_token=os.getenv("BRIA_API_TOKEN"))
        
        # Generate AI animatic
        video_path = get_output_dir() / "ai_animatic.mp4"
        storyboard.generate_ai_animatic(bria_client, str(video_path), duration)
        
        return FileResponse(
            path=str(video_path),
            media_type="video/mp4",
            filename="ai_animatic.mp4"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/enhance-storyboard")
async def enhance_storyboard(request: EnhanceStoryboardRequest):
    """
    Enhance storyboard frames using BRIA upscaling
    
    Args:
        request: Enhancement request with storyboard data
        
    Returns:
        Enhanced storyboard
    """
    try:
        from core.bria_client import BRIAAPIClient
        from core.storyboard import Storyboard
        from core.fibo_engine import Frame
        
        bria_client = BRIAAPIClient(api_token=os.getenv("BRIA_API_TOKEN"))
        
        # Reconstruct storyboard from data
        frames = []
        for frame_data in request.storyboard_data.get("frames", []):
            # Decode base64 image
            image_data = frame_data["image"].split(",")[1]
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            frame = Frame(
                scene_number=frame_data["scene_number"],
                image=image,
                params=frame_data["params"]
            )
            frames.append(frame)
        
        storyboard = Storyboard(frames)
        
        # Enhance frames
        storyboard.enhance_frames(bria_client, request.upscale_factor)
        
        # Convert to response format
        frame_responses = [
            FrameResponse(
                scene_number=frame.scene_number,
                image=frame.to_dict()["image"],
                params=frame.params
            )
            for frame in storyboard.frames
        ]
        
        return StoryboardResponse(
            frames=frame_responses,
            frame_count=len(frame_responses)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SaveSceneRequest(BaseModel):
    scene_number: int
    image: str  # base64 encoded
    params: Dict
    description: Optional[str] = None
    name: Optional[str] = None
    timestamp: Optional[str] = None


@app.post("/api/save-scene")
async def save_scene(request: SaveSceneRequest):
    """
    Save a scene to the library
    
    Args:
        request: Scene data to save
        
    Returns:
        Success message with saved scene info
    """
    try:
        # Create saved scenes directory
        saved_dir = get_output_dir() / "saved_scenes"
        try:
            saved_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Fallback to /tmp if OUTPUT_DIR is read-only
            saved_dir = Path("/tmp/outputs/saved_scenes")
            saved_dir.mkdir(parents=True, exist_ok=True)
        
        scene_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        scene_data = {
            "id": scene_id,
            "scene_number": request.scene_number,
            "params": request.params,
            "description": request.description or request.params.get("scene_description", ""),
            "name": request.name or f"Scene {request.scene_number}",
            "timestamp": request.timestamp or timestamp,
            "image": request.image
        }
        
        # Save to file
        scene_file = saved_dir / f"{scene_id}.json"
        with open(scene_file, 'w') as f:
            json.dump(scene_data, f, indent=2)
        
        return {
            "status": "success",
            "message": f"Scene {request.scene_number} saved successfully",
            "scene_id": scene_id,
            "file": str(scene_file.name)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/saved-scenes")
async def list_saved_scenes():
    """
    List all saved scenes
    
    Returns:
        List of saved scenes
    """
    try:
        saved_dir = get_output_dir() / "saved_scenes"
        saved_dir.mkdir(exist_ok=True)
        
        scenes = []
        
        # Read all JSON files in saved_scenes directory
        for file_path in saved_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    scene_data = json.load(f)
                    scene_name = scene_data.get("name")
                    # Ensure name is a string or None (not empty string)
                    if scene_name and isinstance(scene_name, str) and scene_name.strip():
                        scene_name = scene_name.strip()
                    else:
                        scene_name = None
                    
                    scenes.append({
                        "id": scene_data.get("id", file_path.stem),
                        "scene_number": scene_data.get("scene_number", 0),
                        "name": scene_name,
                        "description": scene_data.get("description", ""),
                        "params": scene_data.get("params", {}),
                        "timestamp": scene_data.get("timestamp"),
                        "thumbnail": scene_data.get("image")
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Sort by timestamp (newest first)
        scenes.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        
        return {
            "status": "success",
            "scenes": scenes,
            "count": len(scenes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/saved-scene/{scene_id}")
async def get_saved_scene(scene_id: str):
    """
    Get a specific saved scene
    
    Args:
        scene_id: ID of the scene
        
    Returns:
        Scene data
    """
    try:
        saved_dir = get_output_dir() / "saved_scenes"
        scene_file = saved_dir / f"{scene_id}.json"
        
        if not scene_file.exists():
            raise HTTPException(status_code=404, detail="Scene not found")
        
        with open(scene_file, 'r') as f:
            scene_data = json.load(f)
        
        return {
            "status": "success",
            "scene": scene_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/saved-scene/{scene_id}")
async def delete_saved_scene(scene_id: str):
    """
    Delete a saved scene
    
    Args:
        scene_id: ID of the scene to delete
        
    Returns:
        Success message
    """
    try:
        saved_dir = get_output_dir() / "saved_scenes"
        scene_file = saved_dir / f"{scene_id}.json"
        
        if not scene_file.exists():
            raise HTTPException(status_code=404, detail="Scene not found")
        
        scene_file.unlink()
        
        return {
            "status": "success",
            "message": "Scene deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class SaveStoryboardRequest(BaseModel):
    name: Optional[str] = None
    frames: List[Dict]  # Accept frames as dictionaries
    script_content: Optional[str] = None


@app.post("/api/save-storyboard")
async def save_storyboard(request: SaveStoryboardRequest):
    """
    Save a complete storyboard
    
    Args:
        request: Storyboard data to save
        
    Returns:
        Success message with saved storyboard info
    """
    try:
        # Create saved storyboards directory
        saved_dir = get_output_dir() / "saved_storyboards"
        try:
            saved_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            # Fallback to /tmp if OUTPUT_DIR is read-only
            saved_dir = Path("/tmp/outputs/saved_storyboards")
            saved_dir.mkdir(parents=True, exist_ok=True)
        
        
        storyboard_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        storyboard_data = {
            "id": storyboard_id,
            "name": request.name or f"Storyboard {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            "frames": request.frames,  # Already dictionaries
            "frame_count": len(request.frames),
            "script_content": request.script_content,
            "created_at": timestamp,
            "updated_at": timestamp,
            "thumbnail": request.frames[0].get("image") if request.frames else None
        }
        
        # Save to file
        storyboard_file = saved_dir / f"{storyboard_id}.json"
        with open(storyboard_file, 'w') as f:
            json.dump(storyboard_data, f, indent=2)
        
        return {
            "status": "success",
            "message": "Storyboard saved successfully",
            "storyboard_id": storyboard_id,
            "file": str(storyboard_file.name)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/saved-storyboards")
async def list_saved_storyboards():
    """
    List all saved storyboards
    
    Returns:
        List of saved storyboards
    """
    try:
        saved_dir = get_output_dir() / "saved_storyboards"
        saved_dir.mkdir(exist_ok=True)
        
        from pathlib import Path
        
        storyboards = []
        
        # Read all JSON files in saved_storyboards directory
        for file_path in saved_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    storyboard_data = json.load(f)
                    # Only include essential info for list view
                    storyboards.append({
                        "id": storyboard_data.get("id", file_path.stem),
                        "name": storyboard_data.get("name", "Unnamed Storyboard"),
                        "frame_count": storyboard_data.get("frame_count", 0),
                        "created_at": storyboard_data.get("created_at"),
                        "updated_at": storyboard_data.get("updated_at"),
                        "thumbnail": storyboard_data.get("thumbnail")
                    })
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue
        
        # Sort by created_at (newest first)
        storyboards.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return {
            "status": "success",
            "storyboards": storyboards,
            "count": len(storyboards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/saved-storyboard/{storyboard_id}")
async def get_saved_storyboard(storyboard_id: str):
    """
    Get a specific saved storyboard
    
    Args:
        storyboard_id: ID of the storyboard
        
    Returns:
        Storyboard data
    """
    try:
        saved_dir = get_output_dir() / "saved_storyboards"
        storyboard_file = saved_dir / f"{storyboard_id}.json"
        
        if not storyboard_file.exists():
            raise HTTPException(status_code=404, detail="Storyboard not found")
        
        with open(storyboard_file, 'r') as f:
            storyboard_data = json.load(f)
        
        # Convert to StoryboardResponse format with name and id
        response_data = StoryboardResponse(
            frames=[
                FrameResponse(
                    scene_number=frame.get("scene_number", i + 1),
                    image=frame.get("image", ""),
                    params=frame.get("params", {})
                )
                for i, frame in enumerate(storyboard_data.get("frames", []))
            ],
            frame_count=storyboard_data.get("frame_count", 0),
            script_content=storyboard_data.get("script_content")
        )
        # Add name and id to response
        response_dict = response_data.dict()
        response_dict["name"] = storyboard_data.get("name", "Unnamed Storyboard")
        response_dict["id"] = storyboard_data.get("id", storyboard_id)
        return response_dict
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/saved-storyboard/{storyboard_id}")
async def delete_saved_storyboard(storyboard_id: str):
    """
    Delete a saved storyboard
    
    Args:
        storyboard_id: ID of the storyboard
        
    Returns:
        Success message
    """
    try:
        saved_dir = get_output_dir() / "saved_storyboards"
        storyboard_file = saved_dir / f"{storyboard_id}.json"
        
        if not storyboard_file.exists():
            raise HTTPException(status_code=404, detail="Storyboard not found")
        
        storyboard_file.unlink()
        
        return {
            "status": "success",
            "message": "Storyboard deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

