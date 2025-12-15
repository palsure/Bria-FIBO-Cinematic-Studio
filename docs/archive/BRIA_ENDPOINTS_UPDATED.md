# BRIA API Endpoints Updated

## ✅ Changes Applied

### Base URL Updated
- **Old**: `https://platform.bria.ai/api/v2` (returned HTML)
- **New**: `https://engine.prod.bria-api.com/v2` (correct API endpoint)

### Image Generation Endpoint
- **Old**: `POST /generate`
- **New**: `POST /text-to-image/tailored/{model_id}`

### Video Generation Endpoint  
- **Old**: `POST /video/generate`
- **New**: `POST /video/generate/tailored/image-to-video`

## Configuration

### `.env` File
```bash
BRIA_API_BASE_URL=https://engine.prod.bria-api.com/v2
BRIA_MODEL_ID=your_model_id_here  # Optional - check dashboard
```

## Model ID

The image generation endpoint requires a `model_id`. You can:

1. **Set in `.env`**:
   ```bash
   BRIA_MODEL_ID=your_model_id_here
   ```

2. **Or pass when calling**:
   ```python
   client.generate_image(prompt="...", model_id="your_model_id")
   ```

3. **Find in Dashboard**:
   - Log into https://platform.bria.ai
   - Check API documentation for available models
   - Look for model IDs in your account settings

## Available Endpoints (from Dashboard)

### Image Generation
- `POST /text-to-image/tailored/{model_id}`
- `POST /text-to-image/tailored/{model_id}/{checkpoint_step}`
- `POST /text-to-vector/tailored/{model_id}`
- `POST /tailored-gen/restyle_portrait`

### Video Generation
- `POST /video/generate/tailored/image-to-video`

## Testing

After updating, test the connection:

```bash
cd backend
python3 -c "
from core.bria_client import BRIAAPIClient
client = BRIAAPIClient()
print(f'Base URL: {client.BASE_URL}')
print(f'Image endpoint: {client.BASE_URL}/text-to-image/tailored/{{model_id}}')
"
```

## Next Steps

1. ✅ Base URL updated to `https://engine.prod.bria-api.com/v2`
2. ⚠️  **Set `BRIA_MODEL_ID` in `.env`** (if required)
3. ✅ Restart backend server
4. ✅ Test storyboard generation

The endpoint should now work correctly!




