# Quick Start Guide

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js 18+
- FIBO model from Hugging Face
- API keys (OpenAI or Anthropic)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys:
# - BRIA_API_TOKEN (required - get from https://bria.ai)
# - OPENAI_API_KEY or ANTHROPIC_API_KEY (for LLM translation)
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

### 3. Start Backend Server

```bash
cd backend
python main.py
```

Backend will run on `http://localhost:8000`

### 4. Start Frontend Development Server

```bash
cd frontend
npm run dev
```

Frontend will run on `http://localhost:3000`

### 5. Use the Application

1. Open `http://localhost:3000` in your browser
2. Upload a script file or paste script content
3. Click "Generate Storyboard"
4. View the generated storyboard
5. Export as PDF or animatic video

## 📝 Usage

### Web Interface

1. **Upload Script**: Click "Upload Script File" or paste script content
2. **Configure Options**: 
   - Select LLM provider (OpenAI, Anthropic, or Local)
   - Enable/disable HDR output
3. **Generate**: Click "Generate Storyboard"
4. **View Results**: Storyboard frames will display with parameters
5. **Export**: Click "Export PDF" or "Export Animatic" to download

### API Usage

#### Parse Script
```bash
curl -X POST http://localhost:8000/api/parse-script \
  -H "Content-Type: application/json" \
  -d '{"content": "EXT. CITY STREET - NIGHT\n\nWide shot..."}'
```

#### Generate Storyboard
```bash
curl -X POST http://localhost:8000/api/generate-storyboard \
  -H "Content-Type: application/json" \
  -d '{
    "script_content": "EXT. CITY STREET - NIGHT\n\nWide shot...",
    "llm_provider": "openai",
    "hdr_enabled": true
  }'
```

### Python API (Backend)

```python
from backend.core.script_parser import ScriptProcessor
from backend.core.llm_translator import LLMTranslator
from backend.core.fibo_engine import FIBOGenerator

# Parse script
processor = ScriptProcessor()
scenes = processor.parse_script_content("script content here")

# Initialize translator
translator = LLMTranslator(provider="openai")

# Initialize generator (requires BRIA API token)
generator = FIBOGenerator(
    api_token="your_bria_token",  # or set BRIA_API_TOKEN env var
    hdr_enabled=True
)

# Generate storyboard
storyboard = generator.create_storyboard(scenes, translator)

# Export
storyboard.export_pdf("storyboard.pdf")
storyboard.export_animatic("animatic.mp4")
storyboard.export_hdr("./hdr_outputs/")
```

## 🎬 Script Format

FIBO Studio supports scripts in plain text format with scene markers:

```
EXT. LOCATION - TIME

Scene description with visual directions.
Camera movements, lighting, and color notes.

CLOSE-UP: More detailed description.
```

**Example:**
```
EXT. CITY STREET - NIGHT

Wide establishing shot. Rain-soaked street, neon signs.
Camera slowly pushes in.

CLOSE-UP: Figure's face. Dramatic side lighting. Desaturated colors.
```

## 🔧 Next Steps

1. **Get BRIA API Token**: Register at [bria.ai](https://bria.ai) and get your API token
2. **Configure Environment**: Add `BRIA_API_TOKEN` to `backend/.env`
3. **Test Generation**: Upload a script and generate your first storyboard
4. **Enhance Script Parser**: Add support for Final Draft (.fdx) format
5. **Add Nuke Export**: Implement Nuke script generation
6. **Improve Consistency**: Enhance multi-frame consistency engine

## 📚 Documentation

- [Project Proposal](PROJECT_PROPOSAL.md) - Full project overview
- [Implementation Guide](IMPLEMENTATION_GUIDE.md) - Technical details
- [README](README.md) - Project documentation

## 🆘 Troubleshooting

**Issue: "BRIA API token not found"**
- Register at [bria.ai](https://bria.ai) to get your API token
- Add `BRIA_API_TOKEN` to `backend/.env` file
- Verify token is correct (no extra spaces)

**Issue: "LLM translation failed"**
- Check API key in `.env`
- Verify API quota/credits
- Falls back to rule-based translation if LLM fails

**Issue: "HDR export not working"**
- Install OpenEXR: `pip install OpenEXR Imath`
- Or use TIFF format: change `.exr` to `.tiff` in export

## 💡 Tips

1. **Start Simple**: Test with a short 2-3 scene script first
2. **Use LLM**: Better results with OpenAI/Anthropic than rule-based
3. **HDR for Production**: Enable HDR for professional workflows
4. **Consistency Matters**: The consistency engine is key to good results

