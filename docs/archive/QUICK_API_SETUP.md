# Quick API Key Setup

## 🚀 Fast Setup (3 Steps)

### Step 1: Copy Your Production API Key
From your BRIA dashboard, copy your **Production** API key (recommended for FIBO Studio).

### Step 2: Add to .env File
```bash
cd backend
nano .env  # or use your preferred editor (vim, code, etc.)
```

Find this line:
```
BRIA_API_TOKEN=your_bria_api_token_here
```

Replace with your actual key:
```
BRIA_API_TOKEN=your_actual_production_key_here
```

Save and exit (Ctrl+X, then Y, then Enter for nano).

### Step 3: Verify Setup
```bash
python3 test_bria_key.py
```

You should see: ✅ BRIA API client initialized successfully

## 🎯 Which Key to Use?

- **Production** ✅ - Recommended for FIBO Studio
- **Staging** - For testing/development
- **ComfyUI** - Only if using ComfyUI integration
- **MCP** - Only if using MCP server

## 🔄 Restart Server

After adding your key, restart the backend:

```bash
# Stop current server (Ctrl+C if running)
cd backend
python3 main.py
```

## ✅ Test It

1. Open http://localhost:3000
2. The sample script should be pre-filled
3. Click "Generate Storyboard"
4. It should now work with your BRIA API key!

## 🔒 Security

- ✅ `.env` is already in `.gitignore` (won't be committed)
- ✅ Never share your API key
- ✅ Use Production key for best results




