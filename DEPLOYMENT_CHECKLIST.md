# Vercel Deployment Checklist

## Pre-Deployment Setup

### 1. Environment Variables
Set these in Vercel Project Settings → Environment Variables:

- ✅ `BRIA_API_TOKEN` - Your BRIA API token (REQUIRED)
- ✅ `USE_LOCAL_BRIA` - Set to `false` (local models disabled for serverless)
- ✅ `PYTHON_VERSION` - Optional, defaults to 3.9

### 2. Verify Files Are Present
- ✅ `vercel.json` - Vercel configuration
- ✅ `api/index.py` - Serverless function handler
- ✅ `api/requirements.txt` - Python dependencies (optimized for serverless)
- ✅ `frontend/package.json` - Frontend dependencies
- ✅ `frontend/vite.config.js` - Frontend build config

### 3. Project Structure
```
fibo/
├── api/
│   ├── index.py          # Vercel serverless handler
│   └── requirements.txt  # Python deps (serverless-optimized)
├── backend/
│   ├── api/main.py       # FastAPI app
│   └── core/             # Business logic
├── frontend/
│   └── ...               # React app
└── vercel.json           # Vercel config
```

## Deployment Steps

### Option 1: Deploy via Vercel Dashboard
1. Push code to your Git repository
2. Go to Vercel Dashboard
3. Import project (if not already connected)
4. Set environment variables
5. Deploy

### Option 2: Deploy via Vercel CLI
```bash
# Install Vercel CLI
npm install -g vercel

# Login
vercel login

# Deploy
vercel

# For production
vercel --prod
```

## Post-Deployment Verification

### 1. Check Health Endpoint
Visit: `https://your-domain.vercel.app/api/health`
Expected: `{"status": "healthy"}`

### 2. Check Root API Endpoint
Visit: `https://your-domain.vercel.app/api/`
Expected: `{"message": "FIBO Studio API", "status": "running"}`

### 3. Test Frontend
Visit: `https://your-domain.vercel.app/`
- Should load the React frontend
- API calls should work (check browser console)

### 4. Check Function Logs
- Go to Vercel Dashboard → Your Project → Functions
- Check for any errors in `api/index.py` logs

## Common Issues & Solutions

### Issue: Function Timeout
**Solution**: Vercel has a 10s timeout on free tier. Consider:
- Using BRIA API (already configured)
- Optimizing image processing
- Using Vercel Pro for longer timeouts

### Issue: Module Not Found
**Solution**: 
- Check `api/requirements.txt` includes all needed packages
- Verify imports in `backend/core/` modules
- Check function logs for specific missing module

### Issue: CORS Errors
**Solution**: 
- Backend already configured with `allow_origins=["*"]`
- Check browser console for specific CORS errors
- Verify frontend is making requests to correct domain

### Issue: Large Function Size
**Solution**: 
- Heavy dependencies (torch, transformers) are excluded
- If still too large, consider:
  - Removing unused dependencies
  - Using Vercel Pro for larger function sizes
  - Splitting into multiple functions

### Issue: Environment Variables Not Working
**Solution**:
- Verify variables are set in Vercel Dashboard
- Redeploy after adding/changing variables
- Check variable names match exactly (case-sensitive)

## Testing Locally Before Deploy

```bash
# Test backend locally
cd backend
python main.py

# Test frontend locally
cd frontend
npm run dev

# Test API endpoint
curl http://localhost:8000/api/health
```

## Notes

- Local BRIA models are disabled (too large for serverless)
- Heavy ML dependencies are excluded from `api/requirements.txt`
- File storage is ephemeral - saved scenes/storyboards won't persist across deployments
- Consider using external storage (S3, etc.) for production

