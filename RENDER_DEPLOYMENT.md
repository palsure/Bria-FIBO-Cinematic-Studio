# Render Deployment Guide for FIBO Studio

This guide explains how to deploy the FIBO Studio backend to Render, which has excellent support for FastAPI applications.

## Prerequisites

1. A Render account (sign up at https://render.com)
2. Your BRIA API token
3. Git repository (GitHub, GitLab, or Bitbucket)

## Deployment Steps

### 1. Prepare Your Repository

Ensure your repository has:
- `backend/` directory with your FastAPI app
- `backend/requirements.txt` with all dependencies
- `backend/api/main.py` with your FastAPI app

### 2. Create Render Configuration

Create a `render.yaml` file in your project root (see below for contents).

### 3. Deploy on Render

#### Option A: Using Render Dashboard

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your Git repository
4. Configure:
   - **Name**: `fibo-backend` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - **Root Directory**: Leave empty (or set to project root)

5. Add Environment Variables:
   - `BRIA_API_TOKEN` = your BRIA API key
   - `USE_LOCAL_BRIA` = `false`
   - `PORT` = `10000` (Render sets this automatically, but you can specify)

6. Click "Create Web Service"

#### Option B: Using render.yaml (Recommended)

1. Create `render.yaml` in your project root (see template below)
2. Go to Render Dashboard → "New +" → "Blueprint"
3. Connect your repository
4. Render will automatically detect and use `render.yaml`

### 4. Update Frontend API URL

After deployment, update your frontend to point to the Render backend URL:

```javascript
// In frontend/src/components/*.jsx files
const API_BASE_URL = import.meta.env.VITE_API_URL || 'https://your-render-app.onrender.com'
```

Or set `VITE_API_URL` environment variable in your frontend deployment.

## Render Configuration Files

### render.yaml

```yaml
services:
  - type: web
    name: fibo-backend
    env: python
    region: oregon  # or your preferred region
    plan: free  # or starter/professional
    buildCommand: cd backend && pip install -r requirements.txt
    startCommand: cd backend && uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: BRIA_API_TOKEN
        sync: false  # Set this manually in dashboard
      - key: USE_LOCAL_BRIA
        value: false
      - key: PYTHON_VERSION
        value: 3.9.18
    healthCheckPath: /api/health
    autoDeploy: true
```

### Alternative: Using Docker (Optional)

If you prefer Docker deployment, create `Dockerfile` in `backend/`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Then in Render:
- **Environment**: `Docker`
- **Dockerfile Path**: `backend/Dockerfile`
- **Docker Context**: `backend/`

## Environment Variables

Set these in Render Dashboard → Your Service → Environment:

| Variable | Value | Required |
|----------|-------|----------|
| `BRIA_API_TOKEN` | Your BRIA API key | Yes |
| `USE_LOCAL_BRIA` | `false` | Yes |
| `PORT` | `10000` (auto-set by Render) | Auto |
| `PYTHON_VERSION` | `3.9.18` or `3.10.x` | Optional |

## Post-Deployment

### 1. Get Your Backend URL

After deployment, Render will provide a URL like:
- `https://fibo-backend.onrender.com` (free tier)
- `https://fibo-backend-xxxx.onrender.com` (custom domain)

### 2. Test the Backend

```bash
# Health check
curl https://your-app.onrender.com/api/health

# Root endpoint
curl https://your-app.onrender.com/api/
```

### 3. Update Frontend

Update your frontend deployment (Vercel or elsewhere) to use the Render backend:

**Option A: Environment Variable**
- In Vercel Dashboard → Your Frontend Project → Environment Variables
- Add: `VITE_API_URL` = `https://your-render-app.onrender.com`

**Option B: Update Code**
- Update all `API_BASE_URL` references in frontend components
- Or use a config file

### 4. CORS Configuration

The backend already has CORS configured to allow all origins (`allow_origins=["*"]`), so your frontend should work without additional CORS setup.

## Render-Specific Considerations

### Free Tier Limitations
- **Spins down after 15 minutes of inactivity**
- First request after spin-down takes ~30-50 seconds (cold start)
- **Solution**: Use Render's paid plans for always-on service, or implement a health check ping

### Health Checks
Render automatically pings your health check endpoint to keep the service alive:
- Health check path: `/api/health`
- Interval: Every few minutes (on paid plans)

### Logs
- View logs in Render Dashboard → Your Service → Logs
- Real-time log streaming available
- Logs are retained for a limited time (varies by plan)

### Custom Domain
1. Go to Render Dashboard → Your Service → Settings → Custom Domains
2. Add your domain
3. Update DNS records as instructed
4. SSL certificates are automatically provisioned

## Troubleshooting

### Service Won't Start
- Check logs in Render Dashboard
- Verify `startCommand` is correct
- Ensure `PORT` environment variable is used (Render sets this automatically)

### Import Errors
- Verify all dependencies are in `requirements.txt`
- Check that Python path is correct in your code
- Ensure `backend/` structure is correct

### Timeout Issues
- Free tier has request timeout limits
- Consider upgrading to paid plan for longer timeouts
- Optimize your code for faster responses

### Database/Storage
- Render provides PostgreSQL (paid plans)
- For file storage, use external services (S3, etc.)
- `/tmp` directory is available but ephemeral

## Cost Comparison

### Render Free Tier
- ✅ Always free
- ⚠️ Spins down after inactivity
- ⚠️ Limited resources

### Render Starter ($7/month)
- ✅ Always on
- ✅ Better performance
- ✅ More resources

### Render Professional ($25/month)
- ✅ Production-ready
- ✅ Auto-scaling
- ✅ Better support

## Next Steps

1. Deploy backend to Render using the steps above
2. Update frontend to point to Render backend URL
3. Test the full application
4. Set up custom domain (optional)
5. Configure monitoring/alerts (optional)

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com
- Render Status: https://status.render.com

