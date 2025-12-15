# Image Generation Flow - How Story Becomes Images

## Complete Flow Diagram

```
Script Text
    ↓
[Script Parser] → Extracts scenes with visual notes
    ↓
[LLM Translator] → Converts to FIBO JSON parameters
    ↓
[FIBO Engine] → Builds enhanced prompt from description + FIBO params
    ↓
[BRIA API Client] → Calls BRIA API endpoint
    ↓
[BRIA AI API] → Generates image
    ↓
[Download & Process] → Returns PIL Image
    ↓
[Storyboard] → Combines into storyboard frames
```

## Step-by-Step Process

### 1. Script Parsing
**File**: `backend/core/script_parser.py`

- Input: Raw script text (e.g., "EXT. CITY STREET - NIGHT")
- Output: List of `Scene` objects with:
  - Scene number
  - Location
  - Description
  - Visual notes (shot_type, lighting, color, etc.)

**Example**:
```python
Scene(
    number=1,
    location="EXT. CITY STREET - NIGHT",
    description="Wide establishing shot. Rain-soaked street, neon signs.",
    visual_notes={"shot_type": "wide", "lighting": "night"}
)
```

### 2. FIBO Translation
**File**: `backend/core/llm_translator.py`

- Input: Scene description + visual notes
- Output: FIBO JSON parameters

**Example Output**:
```json
{
  "camera": {
    "angle": "eye_level",
    "fov": 60,
    "movement": "static"
  },
  "lighting": {
    "time_of_day": "night",
    "style": "dramatic",
    "intensity": 0.3
  },
  "color": {
    "palette": "desaturated",
    "saturation": 0.4
  }
}
```

### 3. Prompt Building
**File**: `backend/core/bria_client.py` → `build_fibo_prompt()`

- Combines scene description with FIBO parameters
- Creates enhanced prompt for BRIA API

**Example**:
```
Input: "Wide establishing shot. Rain-soaked street, neon signs."
FIBO Params: {camera: {fov: 60}, lighting: {time_of_day: "night"}}

Output Prompt:
"Wide establishing shot. Rain-soaked street, neon signs, Camera: wide shot, Lighting: night, dramatic lighting"
```

### 4. BRIA API Call
**File**: `backend/core/bria_client.py` → `generate_image()`

**Current Endpoint**: `https://platform.bria.ai/api/v2/generate`

**Request**:
```python
POST https://platform.bria.ai/api/v2/generate
Headers:
  api_token: <your_api_token>
  Content-Type: application/json
Body:
{
  "prompt": "Wide establishing shot. Rain-soaked street, neon signs, Camera: wide shot, Lighting: night, dramatic lighting",
  "negative_prompt": "vibrant colors, saturated",
  "width": 1920,
  "height": 1080,
  "sync": false
}
```

**Expected Response** (Async):
```json
{
  "request_id": "abc123...",
  "status_url": "https://platform.bria.ai/api/v2/status/abc123..."
}
```

**Then Poll Status**:
```python
GET https://platform.bria.ai/api/v2/status/{request_id}
```

**Final Response**:
```json
{
  "status": "COMPLETED",
  "result": {
    "image_url": "https://...",
    "seed": 12345,
    "prompt": "..."
  }
}
```

### 5. Image Download
**File**: `backend/core/bria_client.py` → `_download_image()`

- Downloads image from `image_url`
- Converts to PIL Image object
- Returns to FIBO Engine

### 6. Storyboard Assembly
**File**: `backend/core/fibo_engine.py` → `create_storyboard()`

- Combines all frames into Storyboard object
- Each frame contains:
  - Scene number
  - Generated image (PIL Image)
  - FIBO parameters
  - HDR version (if enabled)

## Current Issue

### Problem
The endpoint `https://platform.bria.ai/api/v2/generate` is returning **HTML** (the website) instead of **JSON** (the API).

**Error**: `Expecting value: line 1 column 1 (char 0)`
- This happens when trying to parse HTML as JSON
- The response starts with `<!doctype html>` instead of `{`

### Root Cause
The endpoint URL is incorrect. The BRIA API endpoint is likely:
- Different for each account
- Not at `platform.bria.ai/api/v2`
- Needs to be found in your BRIA dashboard

### Solution
1. **Check BRIA Dashboard**: https://platform.bria.ai
2. **Find API Documentation**: Look for "Base URL" or "API Endpoint"
3. **Update `.env`**: Set `BRIA_API_BASE_URL` to correct endpoint
4. **Restart Backend**: Restart server to load new endpoint

## Endpoint Details

### Current Configuration
```bash
BRIA_API_BASE_URL=https://platform.bria.ai/api/v2
```

### Actual Endpoint Called
```
POST https://platform.bria.ai/api/v2/generate
```

### What Should Happen
1. Request sent to endpoint
2. Returns `request_id` and `status_url`
3. Poll status endpoint until `COMPLETED`
4. Download image from `result.image_url`
5. Return PIL Image

### What's Actually Happening
1. Request sent to endpoint
2. Returns HTML page (not JSON)
3. Code tries to parse HTML as JSON
4. Error: "Expecting value: line 1 column 1 (char 0)"
5. Falls back to error placeholder image

## Files Involved

1. **`backend/api/main.py`** - API endpoint `/api/generate-storyboard`
2. **`backend/core/fibo_engine.py`** - Main generation logic
3. **`backend/core/llm_translator.py`** - FIBO JSON translation
4. **`backend/core/bria_client.py`** - BRIA API client
5. **`backend/core/script_parser.py`** - Script parsing

## Next Steps

1. ✅ Find correct endpoint in BRIA dashboard
2. ✅ Update `BRIA_API_BASE_URL` in `.env`
3. ✅ Restart backend server
4. ✅ Test storyboard generation
5. ✅ Images should now generate correctly!




