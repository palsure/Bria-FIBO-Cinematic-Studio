# FIBO Studio Architecture

## Project Structure

```
fibo/
├── backend/                 # Backend API (FastAPI)
│   ├── api/               # API routes and endpoints
│   │   └── main.py        # FastAPI application
│   ├── core/              # Core business logic
│   │   ├── script_parser.py      # Script parsing
│   │   ├── llm_translator.py     # LLM translation
│   │   ├── fibo_engine.py        # FIBO generation
│   │   └── storyboard.py         # Storyboard data structure
│   ├── main.py            # Backend entry point
│   └── requirements.txt  # Backend dependencies
│
├── frontend/              # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/    # React components
│   │   │   ├── ScriptUpload.jsx
│   │   │   └── StoryboardViewer.jsx
│   │   ├── App.jsx        # Main app
│   │   └── main.jsx       # Entry point
│   ├── package.json       # Frontend dependencies
│   └── vite.config.js    # Vite configuration
│
├── examples/              # Example scripts
└── docs/                  # Documentation
```

## Architecture Overview

### Backend (FastAPI)

**API Layer** (`backend/api/`)
- RESTful API endpoints
- Request/response models
- File upload handling
- CORS configuration

**Core Logic** (`backend/core/`)
- Script parsing and scene extraction
- Natural language to JSON translation
- FIBO image generation
- Consistency engine
- Storyboard data structures

### Frontend (React)

**Components**
- `ScriptUpload`: Script input (file upload or text)
- `StoryboardViewer`: Display generated storyboard frames

**Features**
- Real-time storyboard generation
- Interactive parameter visualization
- PDF and animatic export
- Responsive design

## API Endpoints

### Script Processing
- `POST /api/parse-script` - Parse script content
- `POST /api/upload-script` - Upload and parse script file

### Storyboard Generation
- `POST /api/generate-storyboard` - Generate storyboard from script
- `POST /api/export-pdf` - Export storyboard as PDF
- `POST /api/export-animatic` - Export storyboard as video

## Data Flow

1. **Script Input** → Frontend uploads/pastes script
2. **Script Parsing** → Backend extracts scenes and visual notes
3. **LLM Translation** → Natural language → FIBO JSON
4. **FIBO Generation** → Generate images with consistency
5. **Storyboard Assembly** → Combine frames into storyboard
6. **Export** → PDF, video, or HDR formats

## Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Pydantic**: Data validation
- **Pillow**: Image processing
- **OpenCV**: Video generation
- **ReportLab**: PDF generation

### Frontend
- **React**: UI framework
- **Vite**: Build tool
- **Axios**: HTTP client
- **CSS**: Styling

## Development Workflow

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Full Stack
1. Start backend: `cd backend && python main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Access: `http://localhost:3000`

## Environment Variables

### Backend (.env)
```
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
FIBO_MODEL_PATH=./models/fibo
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

## Deployment

### Backend
- Deploy FastAPI with uvicorn/gunicorn
- Set up environment variables
- Configure CORS for production domain

### Frontend
- Build: `npm run build`
- Deploy static files to CDN/hosting
- Update API URL in environment




