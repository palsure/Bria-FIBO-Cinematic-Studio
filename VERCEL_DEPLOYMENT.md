# Vercel Deployment Guide

This guide explains how to deploy the FIBO Studio application to Vercel.

## Prerequisites

1. A Vercel account
2. Your BRIA API token
3. Git repository connected to Vercel

## Deployment Steps

### 1. Environment Variables

Set the following environment variables in your Vercel project settings:

- `BRIA_API_TOKEN`: Your BRIA API token
- `USE_LOCAL_BRIA`: Set to `false` (local models are too large for serverless)
- `PYTHON_VERSION`: `3.9` (optional, defaults to 3.9)

### 2. Project Structure

The project is configured as follows:

- **Frontend**: Located in `frontend/` directory, built with Vite
- **Backend API**: Located in `api/index.py`, handles all `/api/*` routes
- **Backend Core**: Located in `backend/core/`, contains business logic

### 3. Vercel Configuration

The `vercel.json` file is configured to:
- Build the frontend from `frontend/` directory
- Route all `/api/*` requests to the Python serverless function at `api/index.py`
- Serve the frontend static files from `frontend/dist/`

### 4. API Routes

All API routes are handled by the FastAPI application:
- `/api/parse-script` - Parse script content
- `/api/generate-storyboard` - Generate storyboard
- `/api/save-storyboard` - Save storyboard
- `/api/saved-storyboards` - List saved storyboards
- And more...

### 5. Frontend Configuration

The frontend is configured to use relative API paths in production:
- Development: Uses `http://localhost:8000`
- Production: Uses relative paths (same domain)

## Troubleshooting

### Backend Not Responding

1. Check Vercel function logs in the dashboard
2. Verify environment variables are set correctly
3. Ensure `BRIA_API_TOKEN` is set
4. Check that `mangum` is installed (required for ASGI adapter)

### CORS Issues

The backend is configured to allow all origins (`allow_origins=["*"]`). If you encounter CORS issues:
- Check that the CORS middleware is properly configured
- Verify the frontend is making requests to the correct domain

### Build Failures

1. Check that all dependencies are listed in `api/requirements.txt`
2. Verify Python version compatibility (3.9+)
3. Check build logs for specific error messages

### Large Dependencies

Some dependencies (like `torch`, `transformers`) are very large and may cause deployment issues:
- Consider using lighter alternatives if possible
- Vercel has a 50MB limit for serverless functions
- You may need to use Vercel's larger function size limits

## Notes

- The backend uses Mangum to adapt FastAPI (ASGI) to Vercel's serverless format
- Local BRIA models are disabled by default (too large for serverless)
- File storage (saved scenes/storyboards) is ephemeral in serverless - consider using external storage for production

