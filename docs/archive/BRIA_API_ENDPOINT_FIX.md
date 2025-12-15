# BRIA API Endpoint Issue - Fix Required

## Problem Identified

The DNS test shows that **`engine.bria.ai` and `api.bria.ai` cannot be resolved**, while `bria.ai` resolves correctly. This means:

❌ **The API endpoint URLs in the code are incorrect**

## Current Status

- ✅ `bria.ai` resolves to `199.60.103.113`
- ✅ Can connect to `https://bria.ai`
- ❌ `engine.bria.ai` - DNS resolution fails
- ❌ `api.bria.ai` - DNS resolution fails

## Solution

You need to find the **correct API endpoint** from your BRIA dashboard:

### Steps:

1. **Log into BRIA Dashboard**
   - Visit: https://platform.bria.ai
   - Or: https://bria.ai (check for API documentation link)

2. **Find API Endpoint**
   - Go to **API Documentation** or **Settings**
   - Look for **Base URL** or **API Endpoint**
   - It might be:
     - `https://api.bria.ai/v2` (different subdomain)
     - `https://bria.ai/api/v2` (main domain with path)
     - `https://platform.bria.ai/api/v2` (platform subdomain)
     - Or a completely different URL

3. **Update `.env` File**
   ```bash
   cd backend
   nano .env
   ```
   
   Add or update:
   ```bash
   BRIA_API_BASE_URL=https://correct-endpoint-here/v2
   ```

4. **Restart Backend**
   ```bash
   # Stop current server (Ctrl+C)
   python3 main.py
   ```

## Alternative: Check BRIA Documentation

1. Visit: https://docs.bria.ai
2. Look for "API Endpoint" or "Base URL" in the documentation
3. Check authentication section for endpoint details

## Testing

After updating the endpoint, test it:

```bash
cd backend
python3 core/bria_client_debug.py
```

This will test the new endpoint and show if it works.

## Current Error Placeholders

Until the endpoint is fixed, frames will show **error placeholders** with messages like:
- "BRIA API Error"
- "BRIA API Not Configured"

These are better than gray boxes because they show what's wrong.

## Network Issue

If you can't resolve any BRIA subdomains:

1. **Try different DNS servers:**
   ```bash
   # macOS
   networksetup -setdnsservers Wi-Fi 8.8.8.8 1.1.1.1
   ```

2. **Check firewall/proxy settings**
   - Corporate networks might block subdomains
   - VPN might interfere with DNS

3. **Contact BRIA Support**
   - Email: support@bria.ai
   - Ask for the correct API endpoint URL for your account

## Next Steps

1. ✅ Check BRIA dashboard for correct endpoint
2. ✅ Update `BRIA_API_BASE_URL` in `.env`
3. ✅ Restart backend server
4. ✅ Test storyboard generation
5. ✅ Frames should now generate correctly!




