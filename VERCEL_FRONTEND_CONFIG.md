# Configuring Backend URL in Vercel Frontend

## Current Configuration

The frontend is already configured to use environment variables. All components use:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')
```

This means:
- **Development**: Uses `http://localhost:8000` (if `VITE_API_URL` not set)
- **Production**: Uses empty string (relative paths) if `VITE_API_URL` not set
- **With VITE_API_URL**: Uses the environment variable value

## Step 1: Get Your Render Backend URL

After deploying to Render, you'll get a URL like:
```
https://fibo-backend.onrender.com
```

## Step 2: Set Environment Variable in Vercel

### Option A: Via Vercel Dashboard (Recommended)

1. Go to **Vercel Dashboard** → Your Frontend Project
2. Click **Settings** → **Environment Variables**
3. Click **Add New**
4. Add:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-render-backend.onrender.com` (your Render backend URL)
   - **Environment**: Select all (Production, Preview, Development)
5. Click **Save**

### Option B: Via Vercel CLI

```bash
# Set for all environments
vercel env add VITE_API_URL production preview development

# When prompted, enter your Render backend URL:
# https://your-render-backend.onrender.com
```

## Step 3: Redeploy Frontend

After adding the environment variable:

1. **Via Dashboard**: Go to **Deployments** → Click **Redeploy** on latest deployment
2. **Via CLI**: 
   ```bash
   vercel --prod
   ```

## Step 4: Verify Configuration

After redeployment, check:

1. Open your Vercel frontend URL
2. Open browser DevTools → Console
3. Check Network tab for API calls
4. API calls should go to your Render backend URL

## Testing

### Test API Connection

Open browser console on your Vercel frontend and run:
```javascript
fetch(`${import.meta.env.VITE_API_URL || ''}/api/health`)
  .then(r => r.json())
  .then(console.log)
```

Should return: `{"status": "healthy"}`

## Environment Variable Format

### For Render Backend
```
VITE_API_URL=https://fibo-backend.onrender.com
```

### For Local Development (Optional)
Create `frontend/.env.local`:
```
VITE_API_URL=http://localhost:8000
```

### For Different Environments

You can set different values for different environments:

- **Production**: `https://fibo-backend.onrender.com`
- **Preview**: `https://fibo-backend-staging.onrender.com` (if you have staging)
- **Development**: `http://localhost:8000`

## Important Notes

1. **VITE_ Prefix**: Vite only exposes environment variables prefixed with `VITE_` to the client
2. **Rebuild Required**: After changing environment variables, you must redeploy
3. **CORS**: Ensure your Render backend has CORS configured (already done in your code)
4. **HTTPS**: Use HTTPS URLs for production (Render provides this automatically)

## Troubleshooting

### API Calls Failing

1. **Check Environment Variable**:
   - Verify `VITE_API_URL` is set in Vercel
   - Check it's set for the correct environment (Production/Preview)

2. **Check Backend URL**:
   - Verify Render backend is running
   - Test backend directly: `curl https://your-backend.onrender.com/api/health`

3. **Check CORS**:
   - Backend should allow your Vercel domain
   - Your backend already has `allow_origins=["*"]` which should work

4. **Check Browser Console**:
   - Look for CORS errors
   - Check Network tab for failed requests

### Environment Variable Not Working

1. **Redeploy**: Environment variables are baked in at build time
2. **Check Variable Name**: Must be `VITE_API_URL` (with `VITE_` prefix)
3. **Check Build Logs**: Verify variable is being used in build

## Quick Setup Checklist

- [ ] Deploy backend to Render
- [ ] Get Render backend URL
- [ ] Add `VITE_API_URL` in Vercel Dashboard
- [ ] Set value to Render backend URL
- [ ] Redeploy frontend on Vercel
- [ ] Test API connection
- [ ] Verify all endpoints work

## Example Configuration

```
Vercel Frontend: https://fibo-frontend.vercel.app
Render Backend:  https://fibo-backend.onrender.com

Environment Variable in Vercel:
VITE_API_URL = https://fibo-backend.onrender.com
```

After redeployment, frontend will call:
- `https://fibo-backend.onrender.com/api/health`
- `https://fibo-backend.onrender.com/api/generate-storyboard`
- etc.

