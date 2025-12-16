# Starting the Application Locally

## Quick Start Commands

### Terminal 1 - Backend
```bash
cd backend
python3 main.py
```
Backend runs on: `http://localhost:8000`

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```
Frontend runs on: `http://localhost:5173` or `http://localhost:3000`

## Stop Services

### Stop Backend
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### Stop Frontend
```bash
# Kill process on port 3000 or 5173
lsof -ti:3000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Stop All
```bash
# Kill all related processes
pkill -f "uvicorn|vite|python.*main.py"
```

## Verify Services

### Check Backend
```bash
curl http://localhost:8000/api/health
# Should return: {"status": "healthy"}
```

### Check Frontend
Open browser: `http://localhost:5173`

## Environment Variables

Make sure you have a `.env` file in `backend/`:
```bash
cd backend
cp env.example .env
# Edit .env and add your BRIA_API_TOKEN
```

## Troubleshooting

### Port Already in Use
```bash
# Find and kill process
lsof -ti:8000 | xargs kill -9
lsof -ti:5173 | xargs kill -9
```

### Backend Not Starting
- Check if Python dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists with `BRIA_API_TOKEN`
- Check logs for errors

### Frontend Not Starting
- Check if Node dependencies are installed: `npm install`
- Verify port 5173 or 3000 is available
- Check console for errors

