# Frame Generation Issue - Fix Guide

## Problem
Frames are showing as gray placeholders instead of generated images.

## Root Cause
BRIA API calls are failing, likely due to:
1. **Incorrect API endpoint URL** - The endpoint might be different for your account
2. **Network/DNS issues** - Connection to BRIA API servers failing
3. **API key format** - Key might need different format or headers

## Solutions

### 1. Check Your BRIA Dashboard for Correct Endpoint

The API endpoint URL might be different for your account. Check:

1. Log into your BRIA dashboard: https://platform.bria.ai
2. Go to **API Documentation** or **Settings**
3. Find the **Base URL** or **API Endpoint**
4. Update `backend/.env`:

```bash
BRIA_API_BASE_URL=https://your-actual-endpoint-here/v2
```

### 2. Verify API Key Format

Check your API key in the dashboard:
- Copy the **full key** (including any prefixes)
- Ensure no extra spaces
- Check if it needs to be in a specific header format

### 3. Test API Connection

Run the debug script:

```bash
cd backend
python3 core/bria_client_debug.py
```

This will test different endpoint URLs and show which one works.

### 4. Check Network Connectivity

Test if you can reach BRIA servers:

```bash
# Test DNS resolution
nslookup engine.bria.ai

# Test HTTPS connection
curl -I https://engine.bria.ai
```

### 5. Check Backend Logs

When generating a storyboard, check the backend terminal for detailed error messages. The improved error handling will show:
- Connection errors
- Authentication errors
- API response errors

### 6. Alternative: Use BRIA API Documentation

Check the official BRIA API docs for your account:
- Visit: https://docs.bria.ai
- Look for "API Endpoint" or "Base URL"
- Check authentication method (header name, format)

## Common Issues

### DNS Resolution Failure
**Error**: `nodename nor servname provided, or not known`

**Fix**:
- Check internet connection
- Try different DNS servers (8.8.8.8, 1.1.1.1)
- Check firewall/proxy settings
- Verify endpoint URL is correct

### Authentication Error
**Error**: `401 Unauthorized` or `403 Forbidden`

**Fix**:
- Verify API key is correct
- Check key is active in dashboard
- Ensure key has proper permissions
- Check header format (might need `Authorization: Bearer <token>` instead of `api_token`)

### Rate Limiting
**Error**: `429 Too Many Requests`

**Fix**:
- Wait before retrying
- Upgrade your BRIA plan
- Implement request queuing

## Next Steps

1. **Check BRIA Dashboard** for correct endpoint URL
2. **Update `.env`** with correct `BRIA_API_BASE_URL`
3. **Restart backend server**
4. **Test again** - errors will now be clearly logged
5. **Check backend terminal** for detailed error messages

## Getting Help

If issues persist:
- Check BRIA API documentation: https://docs.bria.ai
- Contact BRIA support: support@bria.ai
- Check backend logs for specific error messages
- Verify your API key and endpoint in BRIA dashboard




