# BRIA API 404 Error - Fix Guide

## Problem
All BRIA API endpoints are returning **404 Not Found**, indicating the endpoint format is incorrect.

## Current Configuration
- Base URL: `https://engine.prod.bria-api.com/v2`
- Endpoint: `/text-to-image/tailored/{model_id}`
- Model ID: `default` (or from `BRIA_MODEL_ID` env var)

## Possible Solutions

### 1. Check Your BRIA Dashboard
The endpoint format may be account-specific. Check:
- Log into https://platform.bria.ai
- Go to API Documentation or Settings
- Look for the **exact endpoint format** for your account
- Note the **base URL** and **endpoint path**

### 2. Verify Model ID
The `model_id` in the endpoint must be a **real model ID** from your account:
- Check your BRIA dashboard for available models
- Set `BRIA_MODEL_ID` in `.env` to your actual model ID
- Example: `BRIA_MODEL_ID=your-actual-model-id-here`

### 3. Try Alternative Endpoint Formats
The API might use a different format. Try updating `BRIA_API_BASE_URL` in `.env`:

```bash
# Option 1: Without /v2
BRIA_API_BASE_URL=https://engine.prod.bria-api.com

# Option 2: Different base URL
BRIA_API_BASE_URL=https://api.bria.ai/v2

# Option 3: Account-specific endpoint
BRIA_API_BASE_URL=https://your-account.bria-api.com/v2
```

### 4. Check API Documentation
Your BRIA account might have:
- Different endpoint structure
- Different authentication method
- Account-specific base URLs

## Quick Fix Steps

1. **Get correct endpoint from dashboard:**
   ```bash
   # Log into BRIA dashboard
   # Find API documentation
   # Copy the exact endpoint format
   ```

2. **Update .env:**
   ```bash
   cd backend
   nano .env
   # Update BRIA_API_BASE_URL with correct base URL
   # Set BRIA_MODEL_ID to your actual model ID
   ```

3. **Test the endpoint:**
   ```bash
   python3 test_bria_endpoint.py
   ```

4. **Restart backend:**
   ```bash
   pkill -f "python.*main.py"
   python3 main.py
   ```

## Diagnostic Output
When you generate a storyboard, check the backend logs for:
```
🔍 BRIA API Call:
   URL: https://engine.prod.bria-api.com/v2/text-to-image/tailored/default
   Model ID: default
```

This shows exactly what URL is being called. Compare it with your BRIA dashboard documentation.




