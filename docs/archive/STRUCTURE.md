# Project Structure

## Complete Directory Tree

```
fibo/
├── backend/                      # Backend API (FastAPI)
│   ├── api/                     # API layer
│   │   ├── __init__.py
│   │   └── main.py              # FastAPI application & routes
│   ├── core/                    # Core business logic
│   │   ├── __init__.py
│   │   ├── script_parser.py    # Script parsing & scene extraction
│   │   ├── llm_translator.py   # Natural language → JSON translation
│   │   ├── fibo_engine.py      # FIBO generation & consistency
│   │   └── storyboard.py        # Storyboard data structure
│   ├── __init__.py
│   ├── main.py                  # Backend entry point
│   └── requirements.txt         # Backend Python dependencies
│
├── frontend/                     # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/          # React components
│   │   │   ├── ScriptUpload.jsx      # Script input component
│   │   │   ├── ScriptUpload.css
│   │   │   ├── StoryboardViewer.jsx  # Storyboard display
│   │   │   └── StoryboardViewer.css
│   │   ├── App.jsx              # Main app component
│   │   ├── App.css
│   │   ├── main.jsx             # React entry point
│   │   └── index.css            # Global styles
│   ├── index.html
│   ├── package.json             # Frontend dependencies
│   ├── vite.config.js           # Vite configuration
│   ├── .gitignore
│   └── README.md
│
├── examples/                     # Example files
│   └── sample_script.txt        # Sample script for testing
│
├── docs/                         # Documentation (if needed)
│
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules
│
├── README.md                     # Main project documentation
├── PROJECT_PROPOSAL.md          # Project proposal
├── IMPLEMENTATION_GUIDE.md       # Technical implementation guide
├── QUICK_START.md                # Quick start guide
├── SETUP.md                      # Detailed setup instructions
├── ARCHITECTURE.md               # Architecture documentation
├── STRUCTURE.md                  # This file
└── WHY_THIS_PROJECT.md           # Competitive analysis
```

## Module Separation

### Backend (`backend/`)

**API Layer** (`backend/api/`)
- `main.py`: FastAPI application
  - RESTful endpoints
  - Request/response models
  - File upload handling
  - CORS configuration

**Core Logic** (`backend/core/`)
- `script_parser.py`: Parse scripts, extract scenes and visual notes
- `llm_translator.py`: Convert natural language to FIBO JSON
- `fibo_engine.py`: Generate images with FIBO, maintain consistency
- `storyboard.py`: Storyboard data structure and export functions

**Entry Point** (`backend/main.py`)
- Starts FastAPI server with uvicorn
- Development mode with auto-reload

### Frontend (`frontend/`)

**Components** (`frontend/src/components/`)
- `ScriptUpload.jsx`: Script input (file upload or text)
- `StoryboardViewer.jsx`: Display generated storyboard frames

**App** (`frontend/src/`)
- `App.jsx`: Main application component
- `main.jsx`: React entry point
- `index.css`: Global styles

**Configuration**
- `vite.config.js`: Vite build configuration with API proxy
- `package.json`: Dependencies and scripts

## File Responsibilities

### Backend Files

| File | Purpose |
|------|---------|
| `backend/api/main.py` | FastAPI routes and endpoints |
| `backend/core/script_parser.py` | Script parsing logic |
| `backend/core/llm_translator.py` | LLM translation service |
| `backend/core/fibo_engine.py` | FIBO generation engine |
| `backend/core/storyboard.py` | Storyboard data and exports |
| `backend/main.py` | Server startup |

### Frontend Files

| File | Purpose |
|------|---------|
| `frontend/src/App.jsx` | Main app component |
| `frontend/src/components/ScriptUpload.jsx` | Script input UI |
| `frontend/src/components/StoryboardViewer.jsx` | Storyboard display |
| `frontend/vite.config.js` | Build configuration |

## API Endpoints

All endpoints are in `backend/api/main.py`:

- `GET /` - Health check
- `GET /health` - Health status
- `POST /api/parse-script` - Parse script content
- `POST /api/upload-script` - Upload and parse script file
- `POST /api/generate-storyboard` - Generate storyboard
- `POST /api/export-pdf` - Export PDF
- `POST /api/export-animatic` - Export animatic video

## Data Flow

1. **Frontend** → User uploads/pastes script
2. **Frontend** → POST to `/api/generate-storyboard`
3. **Backend API** → Calls `ScriptProcessor.parse_script_content()`
4. **Backend Core** → `LLMTranslator.translate_to_json()`
5. **Backend Core** → `FIBOGenerator.create_storyboard()`
6. **Backend Core** → Returns `Storyboard` object
7. **Backend API** → Converts to JSON response
8. **Frontend** → Displays storyboard frames

## Development Workflow

### Backend Development
```bash
cd backend
python main.py  # Starts on localhost:8000
```

### Frontend Development
```bash
cd frontend
npm run dev  # Starts on localhost:3000
```

### Full Stack
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:3000`
- API Docs: `http://localhost:8000/docs`

## Dependencies

### Backend (`backend/requirements.txt`)
- FastAPI, uvicorn
- torch, transformers, diffusers
- openai, anthropic
- pillow, numpy, opencv-python
- reportlab, OpenEXR

### Frontend (`frontend/package.json`)
- react, react-dom
- react-router-dom
- axios
- vite, @vitejs/plugin-react

## Environment Variables

### Backend (`.env` in `backend/`)
```
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
FIBO_MODEL_PATH=./models/fibo
```

### Frontend (`.env` in `frontend/`)
```
VITE_API_URL=http://localhost:8000
```




