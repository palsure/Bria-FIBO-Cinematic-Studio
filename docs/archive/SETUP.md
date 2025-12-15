# Setup Guide

## Complete Setup Instructions

### 1. Clone and Navigate

```bash
git clone <your-repo-url>
cd fibo
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../backend/env.example .env
# Edit .env and add:
# - OPENAI_API_KEY or ANTHROPIC_API_KEY (for LLM translation)
# - BRIA_API_TOKEN (required - get from https://bria.ai)
```

### 3. Frontend Setup

```bash
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 4. Download FIBO Model (Optional)

If using local FIBO model:

```bash
# Follow instructions from huggingface.co/briaai
# Set FIBO_MODEL_PATH in backend/.env
```

### 5. Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
python main.py
```

Backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Frontend will start on `http://localhost:3000`

### 6. Access the Application

Open your browser and navigate to:
- Frontend: `http://localhost:3000`
- Backend API Docs: `http://localhost:8000/docs`

## Troubleshooting

### Backend Issues

**Import Errors:**
- Make sure you're in the `backend/` directory
- Check that all dependencies are installed: `pip install -r backend/requirements.txt`

**API Key Errors:**
- Verify `.env` file exists in `backend/` directory
- Check that API keys are set correctly

**Port Already in Use:**
- Change port in `backend/main.py`: `uvicorn.run(app, port=8001)`

### Frontend Issues

**Cannot Connect to API:**
- Verify backend is running on port 8000
- Check `VITE_API_URL` in `frontend/.env`

**Module Not Found:**
- Run `npm install` again
- Delete `node_modules` and reinstall

**Build Errors:**
- Clear cache: `rm -rf node_modules/.vite`
- Reinstall: `npm install`

## Development Tips

1. **Hot Reload**: Both frontend and backend support hot reload
2. **API Testing**: Use `http://localhost:8000/docs` for interactive API testing
3. **Logs**: Check terminal output for errors
4. **Environment**: Always activate virtual environment for backend

## Production Build

### Backend
```bash
cd backend
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend
```bash
cd frontend
npm run build
# Serve dist/ directory with nginx or similar
```

