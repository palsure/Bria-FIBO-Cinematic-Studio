# BRIA AI API Integration

This project uses [BRIA AI API](https://docs.bria.ai) for image generation, leveraging BRIA's enterprise-grade visual AI capabilities.

## Overview

BRIA AI API provides:
- **High-quality image generation** from text prompts
- **Enterprise-grade safety** and compliance
- **Commercial use** with full indemnity
- **Asynchronous processing** with status polling
- **Rate limiting** based on plan type

## Setup

### 1. Get BRIA API Token

1. Register at [BRIA AI Platform](https://bria.ai)
2. Navigate to API section in dashboard
3. Generate your API token
4. Copy the token

### 2. Configure Environment

Add to `backend/.env`:

```bash
BRIA_API_TOKEN=your_bria_api_token_here
```

### 3. API Plans and Rate Limits

| Plan Type        | Rate Limit                          |
| ---------------- | -------------------------------------- |
| Free Trial       | 10 requests per minute, per endpoint   |
| Starter          | 60 requests per minute, per endpoint   |
| Pro & Enterprise | 1000 requests per minute, per endpoint |

## How It Works

### 1. Prompt Enhancement

The system converts FIBO JSON parameters into enhanced prompts:

**Input:**
```json
{
  "camera": {"angle": "high", "fov": 60},
  "lighting": {"time_of_day": "golden_hour", "style": "soft"},
  "color": {"palette": "warm"}
}
```

**Output Prompt:**
```
Wide establishing shot. Rain-soaked street, neon signs.
Camera: high angle, wide shot
Lighting: golden hour, soft lighting
Color palette: warm
```

### 2. Image Generation

The BRIA API client:
1. Sends request to BRIA API with enhanced prompt
2. Handles async requests with status polling
3. Downloads generated image
4. Returns PIL Image object

### 3. Error Handling

- **Rate Limits**: Automatic retry with exponential backoff
- **API Errors**: Graceful fallback to placeholder images
- **Timeout**: Configurable max wait time (default: 300s)

## Code Structure

### BRIA Client (`backend/core/bria_client.py`)

```python
from backend.core.bria_client import BRIAAPIClient

# Initialize client
client = BRIAAPIClient(api_token="your_token")

# Generate image synchronously
image = client.generate_image_sync(
    prompt="A cinematic scene",
    width=1920,
    height=1080
)

# Or use async with status polling
response = client.generate_image(prompt="...", sync=False)
status = client.wait_for_completion(response["request_id"])
```

### FIBO Generator Integration

The `FIBOGenerator` class automatically uses BRIA API:

```python
from backend.core.fibo_engine import FIBOGenerator

generator = FIBOGenerator(
    api_token="your_token",  # Optional, uses env var if not provided
    hdr_enabled=True,
    image_width=1920,
    image_height=1080
)

# Generate frame with FIBO parameters
frame = generator.generate_frame(
    scene_description="Wide shot of city street",
    fibo_params={
        "camera": {"angle": "high", "fov": 60},
        "lighting": {"time_of_day": "golden_hour"}
    }
)
```

## API Endpoints Used

### Image Generation
- **Endpoint**: `POST https://engine.bria.ai/api/v2/generate`
- **Method**: Synchronous or Asynchronous
- **Parameters**:
  - `prompt`: Text prompt (enhanced with FIBO parameters)
  - `negative_prompt`: What to avoid
  - `width`: Image width (default: 1920)
  - `height`: Image height (default: 1080)
  - `sync`: Boolean (default: false for async)

### Status Check
- **Endpoint**: `GET https://engine.bria.ai/api/v2/status/{request_id}`
- **Status Values**:
  - `IN_PROGRESS`: Processing
  - `COMPLETED`: Success, image_url available
  - `ERROR`: Failed, error details in response
  - `UNKNOWN`: Unexpected error

## Best Practices

### 1. Rate Limiting

Implement retry logic with exponential backoff:

```python
import time
import random

def generate_with_retry(client, prompt, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.generate_image_sync(prompt)
        except Exception as e:
            if "429" in str(e) and attempt < max_retries - 1:
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                time.sleep(wait_time)
                continue
            raise
```

### 2. Async Processing

For batch generation, use async mode:

```python
# Submit multiple requests
requests = []
for scene in scenes:
    response = client.generate_image(prompt=scene.prompt, sync=False)
    requests.append(response["request_id"])

# Poll all requests
results = []
for request_id in requests:
    status = client.wait_for_completion(request_id)
    results.append(status["result"]["image_url"])
```

### 3. Error Handling

Always handle API errors gracefully:

```python
try:
    image = client.generate_image_sync(prompt)
except ValueError as e:
    # Missing API token
    print(f"Configuration error: {e}")
except TimeoutError as e:
    # Request timeout
    print(f"Timeout: {e}")
except Exception as e:
    # Other errors
    print(f"API error: {e}")
    # Use fallback/placeholder
```

## Troubleshooting

### API Token Not Working
- Verify token in BRIA dashboard
- Check token is set in `.env` file
- Ensure no extra spaces in token

### Rate Limit Errors
- Upgrade plan for higher limits
- Implement request queuing
- Use async mode for better throughput

### Timeout Issues
- Increase `max_wait` parameter
- Check network connectivity
- Verify API service status

## Resources

- [BRIA AI API Documentation](https://docs.bria.ai)
- [BRIA AI Platform](https://bria.ai)
- [API Access Registration](https://bria.ai) - Get your API token
- [Rate Limits Documentation](https://docs.bria.ai)

## Support

For BRIA API issues:
- Email: support@bria.ai
- Check API status in dashboard
- Review error messages in API responses




