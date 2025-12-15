# BRIA AI Features Used in FIBO Studio

This document outlines the specific BRIA AI API features and capabilities utilized in the FIBO Studio project.

## 🎯 Primary Feature: Image Generation

### **1. Image Generation Using Bria Models** ✅
**Status**: Fully Implemented

The project uses BRIA's pre-trained models to generate high-quality images from text prompts.

**Implementation:**
- **Endpoint**: `POST https://engine.bria.ai/api/v2/generate`
- **Location**: `backend/core/bria_client.py` → `generate_image()`
- **Usage**: Core image generation for storyboard frames

**Features Used:**
- Text-to-image generation from prompts
- Custom image dimensions (width/height)
- Negative prompts for better control
- Multiple image generation support (`num_images` parameter)

**Code Example:**
```python
# From backend/core/bria_client.py
def generate_image(self, prompt: str, 
                  negative_prompt: Optional[str] = None,
                  width: int = 1024,
                  height: int = 1024,
                  num_images: int = 1,
                  sync: bool = False,
                  **kwargs) -> Dict:
```

---

### **2. Asynchronous Request Processing** ✅
**Status**: Fully Implemented

BRIA API V2 processes requests asynchronously by default. The project implements full async support with status polling.

**Implementation:**
- **Status Endpoint**: `GET https://engine.bria.ai/api/v2/status/{request_id}`
- **Location**: `backend/core/bria_client.py` → `check_status()`, `wait_for_completion()`
- **Status States Handled**:
  - `IN_PROGRESS` - Request accepted and processing
  - `COMPLETED` - Request finished successfully
  - `ERROR` - Processing failed
  - `UNKNOWN` - Unexpected error

**Features Used:**
- Async request submission
- Status polling with configurable intervals
- Automatic completion detection
- Error state handling
- Timeout management (default: 300 seconds)

**Code Example:**
```python
# Async workflow
response = client.generate_image(prompt="...", sync=False)
request_id = response["request_id"]
status = client.wait_for_completion(request_id, max_wait=300)
```

---

### **3. Synchronous Image Generation** ✅
**Status**: Fully Implemented

The project supports both sync and async modes, with automatic fallback.

**Implementation:**
- **Location**: `backend/core/bria_client.py` → `generate_image_sync()`
- **Behavior**: Tries sync first, falls back to async if needed
- **Returns**: PIL Image object directly

**Features Used:**
- Synchronous API calls (`sync=True`)
- Automatic async fallback
- Direct image download and conversion
- PIL Image object return

---

### **4. Prompt Enhancement with FIBO Parameters** ✅
**Status**: Fully Implemented

Unique feature: Converts structured FIBO JSON parameters into enhanced text prompts for BRIA API.

**Implementation:**
- **Location**: `backend/core/bria_client.py` → `build_fibo_prompt()`
- **Converts**:
  - Camera parameters (angle, FOV, movement) → Camera descriptions
  - Lighting parameters (time_of_day, style) → Lighting descriptions
  - Color parameters (palette, saturation) → Color descriptions
  - Composition parameters (framing) → Composition descriptions

**Example Transformation:**
```json
// Input FIBO JSON
{
  "camera": {"angle": "high", "fov": 60, "movement": "push_in"},
  "lighting": {"time_of_day": "golden_hour", "style": "soft"},
  "color": {"palette": "warm"}
}

// Output Enhanced Prompt
"Wide establishing shot. Rain-soaked street, neon signs.
Camera: high angle, wide shot, push in
Lighting: golden hour, soft lighting
Color palette: warm"
```

---

### **5. Negative Prompt Generation** ✅
**Status**: Fully Implemented

Automatically generates negative prompts from FIBO parameters to improve image quality.

**Implementation:**
- **Location**: `backend/core/fibo_engine.py` → `_build_negative_prompt()`
- **Logic**: Inverts color/lighting parameters to avoid unwanted elements

**Example:**
- If `color.palette = "desaturated"` → Negative: "vibrant colors, saturated"
- If `lighting.style = "dramatic"` → Negative: "flat lighting, even lighting"

---

## 🔧 API Infrastructure Features

### **6. Authentication** ✅
**Status**: Fully Implemented

- **Method**: API token in request headers
- **Header**: `api_token: <your_api_token>`
- **Location**: `backend/core/bria_client.py` → `__init__()`
- **Source**: Environment variable `BRIA_API_TOKEN`

---

### **7. Rate Limiting Awareness** ✅
**Status**: Documented and Handled

The project is aware of BRIA's rate limits and includes documentation:

| Plan Type        | Rate Limit                          |
| ---------------- | -------------------------------------- |
| Free Trial       | 10 requests per minute, per endpoint   |
| Starter          | 60 requests per minute, per endpoint   |
| Pro & Enterprise | 1000 requests per minute, per endpoint |

**Implementation:**
- Error handling for 429 (Too Many Requests) responses
- Documentation for retry logic with exponential backoff
- Best practices guide in `BRIA_INTEGRATION.md`

---

### **8. Error Handling** ✅
**Status**: Fully Implemented

Comprehensive error handling for all API scenarios:

- **Missing API Token**: Clear error message
- **Rate Limit Errors**: Graceful handling
- **API Errors**: Exception catching with detailed messages
- **Timeout Errors**: Configurable timeout with clear errors
- **Network Errors**: Request exception handling
- **Fallback Mode**: Placeholder images if API unavailable

**Implementation:**
- `backend/core/bria_client.py` - All methods include try/except
- `backend/core/fibo_engine.py` - Fallback to placeholder images

---

## 📊 Feature Summary Table

| BRIA AI Feature | Status | Implementation | Location |
|----------------|--------|---------------|----------|
| **Image Generation** | ✅ Implemented | Core feature | `bria_client.py` |
| **Async Processing** | ✅ Implemented | Full support | `bria_client.py` |
| **Sync Processing** | ✅ Implemented | With fallback | `bria_client.py` |
| **Status Polling** | ✅ Implemented | Automatic | `bria_client.py` |
| **Prompt Enhancement** | ✅ Implemented | FIBO→Prompt | `bria_client.py` |
| **Negative Prompts** | ✅ Implemented | Auto-generated | `fibo_engine.py` |
| **Authentication** | ✅ Implemented | Token-based | `bria_client.py` |
| **Error Handling** | ✅ Implemented | Comprehensive | Both files |
| **Rate Limiting** | ✅ Documented | Best practices | `BRIA_INTEGRATION.md` |

---

## ✅ NEWLY IMPLEMENTED BRIA FEATURES

### **1. Image Editing Suite** ✅
**Status**: Fully Implemented

Comprehensive image editing capabilities for fine-tuning storyboard frames:

#### **Reimagine API** ✅
- **Purpose**: Maintain image outline/depth while changing materials, colors, textures, lighting
- **Use Case**: Style variations, lighting adjustments, color grading tweaks
- **Location**: `backend/core/bria_client.py` → `reimagine_image()`
- **Example**: Adjust lighting from "day" to "golden hour" while keeping composition

#### **Generative Fill (GenFill)** ✅
- **Purpose**: Add, modify, or replace objects in images
- **Use Case**: Add characters, props, or elements to storyboard frames
- **Location**: `backend/core/bria_client.py` → `generative_fill()`
- **Example**: Add a character to an empty scene

#### **Eraser API** ✅
- **Purpose**: Remove unwanted elements from images
- **Use Case**: Remove unwanted objects, clean up frames
- **Location**: `backend/core/bria_client.py` → `erase_object()`
- **Example**: Remove a prop that doesn't match the scene

#### **Background Replacement** ✅
- **Purpose**: Replace image background with AI-generated background
- **Use Case**: Change scene locations, adjust environments
- **Location**: `backend/core/bria_client.py` → `replace_background()`
- **Example**: Change background from "city street" to "forest"

#### **Image Upscaling** ✅
- **Purpose**: Increase image resolution with AI enhancement
- **Use Case**: Enhance storyboard frames for high-resolution exports
- **Location**: `backend/core/bria_client.py` → `upscale_image()`
- **Example**: Upscale 1920x1080 to 3840x2160 (4K)

**API Endpoint**: `POST /api/edit-frame`

---

### **2. Video Generation** ✅
**Status**: Fully Implemented

Generate AI-powered videos from storyboard frames for enhanced animatics.

**Features:**
- Text-to-video generation
- Image-to-video generation (from storyboard frames)
- Custom duration, FPS, resolution
- Automatic video concatenation

**Location**: 
- `backend/core/bria_client.py` → `generate_video()`, `generate_video_sync()`
- `backend/core/storyboard.py` → `generate_ai_animatic()`

**Use Case**: Create dynamic animatics with camera movements and transitions

**API Endpoint**: `POST /api/generate-ai-animatic`

---

### **3. Video Editing** ✅
**Status**: Implemented

Edit generated videos with background replacement, object removal, and enhancement.

**Location**: `backend/core/bria_client.py` → `edit_video()`

**Features:**
- Background replacement in videos
- Object removal
- Video enhancement

---

### **4. Storyboard Enhancement** ✅
**Status**: Implemented

Batch enhance all storyboard frames using upscaling.

**Location**: `backend/core/storyboard.py` → `enhance_frames()`

**API Endpoint**: `POST /api/enhance-storyboard`

---

## 🚫 BRIA Features NOT Used (Available but Not Implemented)

The following BRIA AI features are available but not currently used:

1. **Train Your Own Tailored Models** - Not needed (using pre-trained models)
   - *Could be useful for maintaining consistent visual style across projects*

2. **Product Shot Editing** - Not applicable to storyboards
   - *Focused on cinematic scenes, not product photography*

3. **Ads Generation** - Not the use case
   - *Focused on pre-visualization, not advertising*

**Note**: These features could be added in future iterations if needed.

---

## 🎨 How BRIA Features Enhance FIBO Studio

### 1. **Enterprise-Grade Quality**
- BRIA's trained models provide professional-quality images
- Full commercial use with indemnity
- Consistent, predictable results

### 2. **Structured Control**
- FIBO JSON parameters → Enhanced prompts
- Deterministic control over visual elements
- Maintains consistency across frames

### 3. **Scalability**
- Async processing for batch generation
- Rate limit awareness
- Efficient resource usage

### 4. **Reliability**
- Comprehensive error handling
- Fallback mechanisms
- Status tracking and monitoring

---

## 📚 Documentation References

- **BRIA API Docs**: [https://docs.bria.ai](https://docs.bria.ai)
- **Integration Guide**: `BRIA_INTEGRATION.md`
- **API Client Code**: `backend/core/bria_client.py`
- **FIBO Engine**: `backend/core/fibo_engine.py`

---

## 🔮 Future Enhancements

Potential BRIA features to add:

1. **Video Generation**: For animatic creation
2. **Image Editing**: Fine-tune generated frames
3. **Tailored Models**: Train on specific visual styles
4. **Batch Processing**: Optimize for large scripts

---

## Summary

**Primary BRIA AI Feature Used**: **Image Generation Using Bria Models**

**Supporting Features**:
- Asynchronous request processing
- Status polling and monitoring
- Prompt enhancement from FIBO JSON
- Comprehensive error handling
- Authentication and rate limiting awareness

The project leverages BRIA AI's core image generation capabilities with custom enhancements for cinematic pre-visualization workflows.

