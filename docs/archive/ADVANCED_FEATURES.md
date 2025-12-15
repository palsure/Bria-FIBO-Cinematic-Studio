# Advanced BRIA AI Features Guide

This guide covers the newly implemented advanced BRIA AI features for FIBO Studio.

## 🎨 Image Editing Features

### 1. Reimagine

Transform images while maintaining composition and depth.

**Use Cases:**
- Adjust lighting (day → night, golden hour → blue hour)
- Change color grading (warm → cool, saturated → desaturated)
- Modify materials and textures
- Style variations

**API Example:**
```python
from backend.core.bria_client import BRIAAPIClient

client = BRIAAPIClient()

# Reimagine a frame with different lighting
edited = client.reimagine_image(
    image_url="data:image/png;base64,...",
    prompt="Change to golden hour lighting, warm color palette",
    sync=True
)
```

**Frontend Usage:**
```javascript
// POST /api/edit-frame
{
  "frame_index": 0,
  "edit_type": "reimagine",
  "prompt": "Change to golden hour lighting"
}
```

---

### 2. Generative Fill (GenFill)

Add, modify, or replace objects in images.

**Use Cases:**
- Add characters to scenes
- Insert props or set pieces
- Modify existing objects
- Fill empty spaces

**API Example:**
```python
# Add a character to a scene
edited = client.generative_fill(
    image_url="data:image/png;base64,...",
    prompt="Add a mysterious figure in the shadows",
    sync=True
)
```

**Frontend Usage:**
```javascript
{
  "frame_index": 1,
  "edit_type": "genfill",
  "prompt": "Add a character walking in the background"
}
```

---

### 3. Eraser

Remove unwanted elements from images.

**Use Cases:**
- Remove unwanted props
- Clean up frames
- Remove background elements
- Fix composition issues

**API Example:**
```python
# Remove an object
edited = client.erase_object(
    image_url="data:image/png;base64,...",
    prompt="Remove the car in the background",
    sync=True
)
```

**Frontend Usage:**
```javascript
{
  "frame_index": 2,
  "edit_type": "eraser",
  "prompt": "Remove the unwanted prop"
}
```

---

### 4. Background Replacement

Replace image backgrounds with AI-generated backgrounds.

**Use Cases:**
- Change scene locations
- Adjust environments
- Fix background issues
- Create location variations

**API Example:**
```python
# Replace background
edited = client.replace_background(
    image_url="data:image/png;base64,...",
    background_prompt="Rain-soaked city street at night with neon signs",
    sync=True
)
```

**Frontend Usage:**
```javascript
{
  "frame_index": 0,
  "edit_type": "background",
  "prompt": "Rain-soaked city street at night"
}
```

---

### 5. Image Upscaling

Increase image resolution with AI enhancement.

**Use Cases:**
- Enhance storyboard frames for high-res exports
- Prepare frames for 4K/8K workflows
- Improve image quality for presentations

**API Example:**
```python
# Upscale 2x
upscaled = client.upscale_image(
    image_url="data:image/png;base64,...",
    scale_factor=2,  # 2x, 4x, etc.
    sync=True
)
```

**Frontend Usage:**
```javascript
{
  "frame_index": 0,
  "edit_type": "upscale",
  "scale_factor": 2
}
```

---

## 🎬 Video Generation

### AI-Powered Animatics

Generate dynamic videos from storyboard frames with camera movements and transitions.

**Features:**
- Image-to-video generation
- Custom duration per frame
- Configurable FPS (default: 24)
- Automatic video generation

**API Example:**
```python
from backend.core.bria_client import BRIAAPIClient
from backend.core.storyboard import Storyboard

client = BRIAAPIClient()
storyboard = Storyboard(frames)

# Generate AI animatic
storyboard.generate_ai_animatic(
    client,
    output_path="animatic.mp4",
    duration_per_frame=3.0
)
```

**Frontend Usage:**
```javascript
// POST /api/generate-ai-animatic
{
  "script_content": "...",
  "llm_provider": "openai",
  "duration": 3.0
}
```

**Benefits:**
- Dynamic camera movements
- Smooth transitions
- Professional animatics
- Better than static frame sequences

---

## 🎥 Video Editing

Edit generated videos with various transformations.

**Features:**
- Background replacement in videos
- Object removal
- Video enhancement

**API Example:**
```python
# Edit video background
result = client.edit_video(
    video_url="https://...",
    edit_type="background",
    prompt="Replace with forest background",
    sync=True
)
```

---

## 📊 Batch Operations

### Enhance Entire Storyboard

Upscale all frames in a storyboard at once.

**API Example:**
```python
storyboard.enhance_frames(
    bria_client,
    upscale_factor=2  # 2x upscaling
)
```

**Frontend Usage:**
```javascript
// POST /api/enhance-storyboard
{
  "storyboard_data": { /* previous storyboard */ },
  "upscale_factor": 2
}
```

---

## 🔄 Workflow Examples

### Complete Storyboard Workflow

1. **Generate Storyboard**
   ```javascript
   POST /api/generate-storyboard
   ```

2. **Edit Individual Frames**
   ```javascript
   POST /api/edit-frame
   {
     "frame_index": 0,
     "edit_type": "reimagine",
     "prompt": "Adjust to golden hour"
   }
   ```

3. **Enhance All Frames**
   ```javascript
   POST /api/enhance-storyboard
   {
     "storyboard_data": storyboard,
     "upscale_factor": 2
   }
   ```

4. **Generate AI Animatic**
   ```javascript
   POST /api/generate-ai-animatic
   {
     "script_content": "...",
     "duration": 3.0
   }
   ```

---

## 💡 Best Practices

### Image Editing
- Use **reimagine** for lighting/color adjustments
- Use **genfill** for adding elements
- Use **eraser** for removing unwanted objects
- Use **background** for location changes
- Use **upscale** for final export preparation

### Video Generation
- Use appropriate duration per frame (2-5 seconds)
- Consider FPS based on final output (24fps for film, 30fps for video)
- Generate videos in batches for efficiency

### Performance
- Use async mode for batch operations
- Cache edited frames to avoid regeneration
- Upscale only when needed (final export)

---

## 🎯 Use Cases

### Pre-Production
1. Generate initial storyboard
2. Edit frames to match director's vision
3. Enhance frames for client presentation
4. Generate AI animatic for review

### Production
1. Use enhanced frames as reference
2. Export high-res frames for crew
3. Generate animatics for planning

### Post-Production
1. Use storyboards as reference
2. Match final footage to storyboard style
3. Create comparison materials

---

## 📚 API Reference

### Edit Frame
- **Endpoint**: `POST /api/edit-frame`
- **Request**: `EditFrameRequest`
- **Response**: `FrameResponse`

### Generate AI Animatic
- **Endpoint**: `POST /api/generate-ai-animatic`
- **Request**: `GenerateRequest` + `duration`
- **Response**: Video file download

### Enhance Storyboard
- **Endpoint**: `POST /api/enhance-storyboard`
- **Request**: `EnhanceStoryboardRequest`
- **Response**: `StoryboardResponse`

---

## 🔗 Resources

- [BRIA AI API Documentation](https://docs.bria.ai)
- [Image Editing Guide](BRIA_INTEGRATION.md)
- [API Client Code](backend/core/bria_client.py)




