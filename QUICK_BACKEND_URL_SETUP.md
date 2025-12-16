# Quick Setup: Backend URL in Vercel Frontend

## 🚀 Quick Steps

### 1. Get Your Render Backend URL
After deploying to Render, you'll have a URL like:
```
https://fibo-backend.onrender.com
```

### 2. Set Environment Variable in Vercel

**Via Dashboard:**
1. Go to: https://vercel.com/dashboard
2. Select your **frontend project**
3. Go to **Settings** → **Environment Variables**
4. Click **Add New**
5. Enter:
   - **Key**: `VITE_API_URL`
   - **Value**: `https://your-render-backend.onrender.com`
   - **Environment**: Select **Production**, **Preview**, and **Development**
6. Click **Save**

**Via CLI:**
```bash
cd frontend
vercel env add VITE_API_URL
# Enter: https://your-render-backend.onrender.com
# Select: Production, Preview, Development
```

### 3. Redeploy Frontend

**Via Dashboard:**
- Go to **Deployments** → Click **⋯** → **Redeploy**

**Via CLI:**
```bash
vercel --prod
```

### 4. Verify

Open your Vercel frontend and check browser console:
- API calls should go to your Render backend
- No CORS errors
- Health check should work

## 📝 Current Frontend Configuration

The frontend already uses this pattern:
```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 
  (import.meta.env.DEV ? 'http://localhost:8000' : '')
```

**Behavior:**
- ✅ If `VITE_API_URL` is set → Uses that URL
- ✅ If not set + Development → Uses `http://localhost:8000`
- ✅ If not set + Production → Uses empty string (relative paths won't work)

## ⚠️ Important

1. **Must Redeploy**: Environment variables are baked in at build time
2. **VITE_ Prefix**: Only variables starting with `VITE_` are exposed to client
3. **HTTPS Required**: Use HTTPS URLs for production (Render provides this)

## ✅ Checklist

- [ ] Backend deployed to Render
- [ ] Render backend URL copied
- [ ] `VITE_API_URL` added in Vercel
- [ ] Value set to Render backend URL
- [ ] Frontend redeployed
- [ ] Tested API connection

## 🔍 Troubleshooting

**API calls failing?**
- Check `VITE_API_URL` is set correctly
- Verify Render backend is running
- Check CORS settings (should allow all origins)

**Environment variable not working?**
- Must redeploy after adding variable
- Check variable name is exactly `VITE_API_URL`
- Verify it's set for the correct environment

