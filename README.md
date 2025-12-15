# 🎬 FIBO Studio

> AI-Powered Cinematic Pre-Visualization Pipeline. Powered by Bria FIBO and JSON-Native Visual Generation

Transform scripts into professional storyboards with AI-powered visual consistency using BRIA AI's FIBO technology.

## ✨ Features

### Core Functionality
- **2-Step Workflow**: Streamlined script-to-storyboard generation
  - **Step 1: Scripting** - Upload or paste your script, automatically generates storyboard
  - **Step 2: Scene Generation and Editing** - Review and edit generated scenes with full parameter control
- **Script Parsing**: Automatic scene extraction from scripts
- **AI-Powered Generation**: BRIA FIBO API integration for high-quality image generation
- **Scene Management**: Save and manage individual scenes and complete storyboards
- **Parameter Customization**: Full control over camera, lighting, color, and composition
- **Scene Editing**: Edit individual scenes with parameter adjustments and regeneration

### Export Options
- **PDF Export**: Professional storyboard PDFs
- **Animatic Export**: Video animatics from storyboard sequences
- **HDR/16-bit Support**: Professional-grade outputs

### User Interface
- **Tab Navigation**: Create Storyboard, My Storyboards, My Scenes
- **In-App Notifications**: Non-intrusive toast notifications for all actions
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Modern, professional UI

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- BRIA API Key ([Get one here](https://bria.ai))

### Installation

#### Backend Setup

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env and add your BRIA API key:
# BRIA_API_TOKEN=your_api_key_here
```

#### Frontend Setup

```bash
cd frontend

# Install Node dependencies
npm install
```

### Running the Application

#### Development Mode

**Terminal 1 - Backend:**
```bash
cd backend
KMP_DUPLICATE_LIB_OK=TRUE python main.py
```
Backend runs on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on `http://localhost:5173` (Vite default) or `http://localhost:3000`

#### Production Mode

**Backend:**
```bash
cd backend
KMP_DUPLICATE_LIB_OK=TRUE uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm run build
# Serve the dist/ directory with your web server
```

## 📁 Project Structure

```
fibo/
├── backend/                 # Backend API (FastAPI)
│   ├── api/
│   │   └── main.py         # FastAPI application & endpoints
│   ├── core/               # Core business logic
│   │   ├── script_parser.py      # Script parsing logic
│   │   ├── llm_translator.py     # LLM translation
│   │   ├── fibo_engine.py        # FIBO generation engine
│   │   ├── bria_client.py        # BRIA API client
│   │   └── storyboard.py         # Storyboard export logic
│   ├── main.py             # Backend entry point
│   ├── requirements.txt    # Python dependencies
│   ├── .env                # Environment variables (create from env.example)
│   └── outputs/            # Generated outputs
│       ├── saved_storyboards/
│       └── saved_scenes/
│
├── frontend/               # Frontend (React + Vite)
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── CreateStoryboard.jsx    # Main storyboard creation
│   │   │   ├── StoryboardViewer.jsx    # Storyboard display & editing
│   │   │   ├── ParameterCustomization.jsx  # Parameter controls
│   │   │   ├── SavedStoryboards.jsx    # Saved storyboards list
│   │   │   ├── SavedScenes.jsx         # Saved scenes list
│   │   │   └── Notification.jsx       # Toast notifications
│   │   ├── App.jsx         # Main app component
│   │   └── main.jsx        # Entry point
│   ├── package.json
│   └── vite.config.js
│
└── README.md
```

## 🎬 Usage Guide

### Creating a Storyboard

1. **Navigate to "Create Storyboard" tab**
2. **Step 1: Scripting**
   - Paste your script in the text area, OR
   - Click "Upload Script File" to upload a text file
   - The storyboard will automatically generate after script parsing
3. **Step 2: Scene Generation and Editing**
   - Review generated scenes
   - Click "✏️ Edit Scene" on any scene to customize parameters
   - Adjust camera, lighting, color, and composition settings
   - Click "Apply Changes" to regenerate the scene
   - Enable HDR/16-bit if needed
4. **Save Your Work**
   - Enter a storyboard name and click "Save Storyboard"
   - After saving, the name is displayed with an edit option
   - Individual scenes can be saved to "My Scenes" tab

### Managing Storyboards

- **My Storyboards**: View all saved storyboards, load them for editing, or delete them
- **My Scenes**: View all saved individual scenes, view details, or delete them

### Exporting

- **Export PDF**: Generate a professional PDF storyboard
- **Export Animatic**: Create a video animatic from the storyboard

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **BRIA AI API**: Enterprise-grade image generation
- **ReportLab**: PDF generation
- **OpenCV**: Video/animatic generation
- **Pydantic**: Data validation

### Frontend
- **React 18**: UI framework
- **Vite**: Build tool and dev server
- **Axios**: HTTP client for API calls

## 📡 API Endpoints

### Storyboard Generation
- `POST /api/parse-script` - Parse script content
- `POST /api/upload-script` - Upload script file
- `POST /api/generate-storyboard` - Generate storyboard from scenes

### Storyboard Management
- `POST /api/save-storyboard` - Save a storyboard
- `GET /api/saved-storyboards` - List all saved storyboards
- `GET /api/saved-storyboard/{id}` - Get a specific storyboard
- `DELETE /api/saved-storyboard/{id}` - Delete a storyboard

### Scene Management
- `POST /api/save-scene` - Save an individual scene
- `GET /api/saved-scenes` - List all saved scenes
- `GET /api/saved-scene/{id}` - Get a specific scene
- `DELETE /api/saved-scene/{id}` - Delete a scene

### Scene Editing
- `POST /api/regenerate-scene` - Regenerate a scene with new parameters

### Export
- `POST /api/export-pdf` - Export storyboard as PDF
- `POST /api/export-animatic` - Export storyboard as animatic video

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend/` directory:

```env
BRIA_API_TOKEN=your_bria_api_key_here
PORT=8000
```

### Frontend Configuration

The frontend automatically connects to `http://localhost:8000` by default. To change this, set the `VITE_API_URL` environment variable or update `vite.config.js`.

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

**BRIA API errors:**
- Verify your API key in `.env`
- Check BRIA API status at https://bria.ai
- Ensure you have API credits

**Module import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend Issues

**Port conflicts:**
- Vite will automatically use the next available port
- Check console for the actual port number

**API connection errors:**
- Ensure backend is running on port 8000
- Check CORS settings in backend
- Verify `VITE_API_URL` if using custom port

## 📚 Additional Documentation

- [Quick Start Guide](docs/QUICK_START.md) - Get up and running quickly
- [API Documentation](docs/API.md) - Complete API reference
- [Features Guide](docs/FEATURES.md) - Detailed feature documentation
- [Contributing Guide](CONTRIBUTING.md) - How to contribute

### External Resources
- [BRIA AI API Documentation](https://docs.bria.ai)
- [BRIA AI Platform](https://bria.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)

## 🤝 Contributing

This is a hackathon project. Contributions and feedback welcome!

## 📄 License

[Specify your license]

## 🔗 Resources

- [BRIA AI API Documentation](https://docs.bria.ai)
- [BRIA AI Platform](https://bria.ai)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [React Documentation](https://react.dev)

## 📧 Contact

[Your contact information]
