# BRIA API Key Configuration

## Quick Setup

1. **Get your API key** from BRIA dashboard:
   - Go to Organization Settings > API Keys
   - Copy your **Production** key (recommended)

2. **Add to .env file**:
   ```bash
   # Edit .env file
   nano .env
   
   # Update this line:
   BRIA_API_TOKEN=your_actual_production_key_here
   ```

3. **Test configuration**:
   ```bash
   python3 test_bria_key.py
   ```

4. **Restart server** (if running):
   ```bash
   python3 main.py
   ```

## Key Types

- **Production** ✅ - Use this for FIBO Studio
- **Staging** - For testing
- **ComfyUI** - For ComfyUI only
- **MCP** - For MCP server only

## Verification

After setup, you should see:
```
✅ BRIA_API_TOKEN found: xxxxx...xxxx
✅ BRIA API client initialized successfully
🎉 Your API key is configured correctly!
```

## Troubleshooting

**"BRIA_API_TOKEN is still set to placeholder"**
- Make sure you replaced `your_bria_api_token_here` with actual key
- Check for typos or extra spaces

**"BRIA_API_TOKEN not found"**
- Verify `.env` file exists in `backend/` directory
- Check the line starts with `BRIA_API_TOKEN=`

**API errors**
- Verify key is active in BRIA dashboard
- Check you have credits/usage available
- Ensure you're using Production key

## Security

- ✅ `.env` is git-ignored (safe to commit code)
- ⚠️ Never commit actual API keys
- ⚠️ Never share keys publicly




