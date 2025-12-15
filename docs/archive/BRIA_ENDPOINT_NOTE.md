# BRIA API Endpoint Configuration

## Important Note

The BRIA API endpoint URL needs to be obtained from your **BRIA dashboard**. The endpoint may vary by account or region.

## How to Find Your Endpoint

1. **Log into BRIA Dashboard**
   - Visit: https://platform.bria.ai
   - Sign in with your account

2. **Find API Documentation**
   - Look for "API Documentation" or "API Settings"
   - Check for "Base URL" or "API Endpoint"
   - The endpoint might be shown in code examples

3. **Common Endpoint Formats**
   - `https://api.platform.bria.ai/v2`
   - `https://engine.platform.bria.ai/v2`
   - `https://platform.bria.ai/api/v2` (returns HTML, not API)
   - Or a custom endpoint for your account

4. **Update `.env` File**
   ```bash
   cd backend
   nano .env
   ```
   
   Add:
   ```bash
   BRIA_API_BASE_URL=https://your-correct-endpoint-here/v2
   ```

5. **Restart Backend**
   ```bash
   # Stop server (Ctrl+C)
   python3 main.py
   ```

## Testing

Use the endpoint finder script:
```bash
cd backend
python3 find_bria_endpoint.py
```

This will test common endpoints and show which one works.

## Current Status

The endpoint `https://platform.bria.ai/api/v2` returns HTML (the website) instead of the API. You need to find the correct API endpoint from your BRIA dashboard.

## Contact BRIA Support

If you can't find the endpoint:
- Email: support@bria.ai
- Check: https://docs.bria.ai
- Ask for the correct API endpoint URL for your account




