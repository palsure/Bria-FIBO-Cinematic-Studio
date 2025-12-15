# BRIA API Key Setup Guide

## Quick Setup

### Option 1: Using Setup Script (Recommended)
```bash
cd backend
./setup_api_key.sh
```
Enter your API key when prompted (it will be hidden for security).

### Option 2: Manual Setup
1. Copy your BRIA API key from the dashboard
2. Edit `backend/.env` file:
   ```bash
   cd backend
   nano .env  # or use your preferred editor
   ```
3. Update or add this line:
   ```bash
   BRIA_API_TOKEN=your_actual_api_key_here
   ```

### Option 3: Environment Variable
```bash
export BRIA_API_TOKEN=your_actual_api_key_here
cd backend
python3 main.py
```

## API Key Types

Based on your BRIA dashboard, you have these key types available:

- **Production**: For production use
- **Staging**: For testing/development
- **ComfyUI**: For ComfyUI integration
- **MCP**: For MCP server integration

**For FIBO Studio, use the Production key** for best results.

## Verification

After setting up your API key, test it:

```bash
cd backend
python3 -c "from core.bria_client import BRIAAPIClient; client = BRIAAPIClient(); print('✅ API key configured correctly')"
```

## Security Notes

⚠️ **Important:**
- Never commit `.env` file to git (it's already in `.gitignore`)
- Never share your API key publicly
- Use different keys for development and production
- Rotate keys if compromised

## Troubleshooting

### "BRIA_API_TOKEN is required"
- Make sure `.env` file exists in `backend/` directory
- Check that `BRIA_API_TOKEN=...` line is present
- Verify no extra spaces around the `=` sign

### "BRIA API request failed"
- Verify API key is correct
- Check your BRIA account has active credits
- Ensure you're using the correct key type (Production recommended)

### Key Not Working
- Check key is active in BRIA dashboard
- Verify key hasn't been revoked
- Try creating a new key if needed

## Next Steps

Once your API key is configured:

1. **Restart Backend Server** (if running):
   ```bash
   # Stop current server (Ctrl+C)
   cd backend
   python3 main.py
   ```

2. **Test Storyboard Generation**:
   - Open http://localhost:3000
   - Use the pre-populated sample script
   - Click "Generate Storyboard"
   - Should now work with BRIA API!

3. **Check API Usage**:
   - Monitor usage in BRIA dashboard
   - Check rate limits based on your plan

## Rate Limits

Based on your BRIA plan:
- **Free Trial**: 10 requests/minute
- **Starter**: 60 requests/minute  
- **Pro/Enterprise**: 1000 requests/minute

The application handles rate limits automatically with retry logic.




