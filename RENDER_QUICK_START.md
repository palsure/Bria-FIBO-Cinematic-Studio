# Render Quick Start Guide

## Quick Deployment Steps

### 1. Sign Up / Login
- Go to https://render.com
- Sign up or log in with GitHub/GitLab/Bitbucket

### 2. Create New Web Service

**Via Dashboard:**
1. Click "New +" → "Web Service"
2. Connect your Git repository
3. Fill in:
   - **Name**: `fibo-backend`
   - **Region**: Choose closest to you
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: (leave empty)
   - **Environment**: `Python 3`
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && uvicorn api.main:app --host 0.0.0.0 --port $PORT`

### 3. Add Environment Variables

In the "Environment" section, add:
- `BRIA_API_TOKEN` = `your_bria_api_key_here`
- `USE_LOCAL_BRIA` = `false`

### 4. Deploy

Click "Create Web Service" and wait for deployment (~5-10 minutes).

### 5. Get Your Backend URL

After deployment, you'll get a URL like:
```
https://fibo-backend.onrender.com
```

### 6. Test

```bash
curl https://fibo-backend.onrender.com/api/health
```

Should return: `{"status": "healthy"}`

### 7. Update Frontend

In your Vercel frontend deployment, add environment variable:
- `VITE_API_URL` = `https://fibo-backend.onrender.com`

Or update the frontend code to use the Render URL.

## Using render.yaml (Alternative)

If you've added `render.yaml` to your repo:

1. Go to Render Dashboard
2. Click "New +" → "Blueprint"
3. Connect your repository
4. Render will auto-detect and use `render.yaml`
5. Add `BRIA_API_TOKEN` in the environment variables section
6. Click "Apply"

## Important Notes

### Free Tier
- ⚠️ Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30-50 seconds (cold start)
- **Solution**: Use a cron job or monitoring service to ping `/api/health` every 10 minutes

### Keep Service Alive (Free Tier)

You can use a free service like:
- **UptimeRobot**: https://uptimerobot.com (free, pings every 5 minutes)
- **Cron-job.org**: https://cron-job.org (free cron jobs)
- Set up to ping: `https://your-app.onrender.com/api/health`

### Paid Plans
- **Starter ($7/month)**: Always on, no spin-down
- **Professional ($25/month)**: Production-ready with auto-scaling

## Troubleshooting

**Service won't start?**
- Check logs in Render Dashboard
- Verify `startCommand` uses `$PORT` (not hardcoded port)
- Ensure all dependencies are in `requirements.txt`

**Import errors?**
- Check that `backend/` structure is correct
- Verify Python path in your code
- Check logs for specific import errors

**Timeout errors?**
- Free tier has request timeouts
- Consider upgrading for longer timeouts
- Optimize slow endpoints

## Next Steps

1. ✅ Backend deployed to Render
2. ⬜ Update frontend to use Render backend URL
3. ⬜ Test full application
4. ⬜ Set up health check pings (if using free tier)
5. ⬜ Configure custom domain (optional)

## Support

- Render Docs: https://render.com/docs
- Render Community: https://community.render.com

