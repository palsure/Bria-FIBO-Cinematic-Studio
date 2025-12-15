# How to Start the Application

## Quick Start

### Backend (Terminal 1)
```bash
cd backend
python3 main.py
```
Backend runs on: **http://localhost:8000**

### Frontend (Terminal 2)
```bash
cd frontend
npm install  # First time only
npm run dev
```
Frontend runs on: **http://localhost:3000**

## Access Points

- **Frontend UI**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Testing Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### Parse Script
```bash
curl -X POST http://localhost:8000/api/parse-script \
  -H "Content-Type: application/json" \
  -d '{"content": "EXT. CITY STREET - NIGHT\n\nWide shot..."}'
```

### Generate Storyboard (requires BRIA API token)
```bash
curl -X POST http://localhost:8000/api/generate-storyboard \
  -H "Content-Type: application/json" \
  -d '{
    "script_content": "EXT. CITY STREET - NIGHT\n\nWide shot...",
    "llm_provider": "openai",
    "hdr_enabled": true
  }'
```

## Troubleshooting

### Backend won't start
1. Install dependencies: `pip install -r backend/requirements.txt`
2. Check `.env` file exists in `backend/` directory
3. Verify Python 3.9+ is installed

### Frontend won't start
1. Install dependencies: `cd frontend && npm install`
2. Check Node.js 18+ is installed
3. Verify port 3000 is available

### Port already in use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```




