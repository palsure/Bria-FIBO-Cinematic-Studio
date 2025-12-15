# BRIA-4B-Adapt Local Model Integration

## Overview

The project now supports using the **BRIA-4B-Adapt** model locally instead of the BRIA API. This model is available from Hugging Face and provides high-quality text-to-image generation.

**Reference**: https://huggingface.co/briaai/BRIA-4B-Adapt

## Benefits

- ✅ **No API costs** - Run locally
- ✅ **No API rate limits** - Generate as many images as needed
- ✅ **Full control** - Customize inference parameters
- ✅ **Privacy** - All processing happens locally
- ✅ **Fine-tuning support** - Can train custom LoRAs

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install huggingface-hub accelerate
```

Or use the installation script:

```bash
cd backend
./install_bria_local.sh
```

### 2. Download Pipeline Files

The pipeline files will be downloaded automatically on first use, or you can download them manually:

```python
from huggingface_hub import hf_hub_download

hf_hub_download(
    repo_id="briaai/BRIA-4B-Adapt",
    filename='pipeline_bria.py',
    local_dir='.'
)
hf_hub_download(
    repo_id="briaai/BRIA-4B-Adapt",
    filename='transformer_bria.py',
    local_dir='.'
)
hf_hub_download(
    repo_id="briaai/BRIA-4B-Adapt",
    filename='bria_utils.py',
    local_dir='.'
)
```

### 3. Configure

Update `backend/.env`:

```bash
# Use local BRIA model (default: true)
USE_LOCAL_BRIA=true

# Optional: Device selection (cuda/cpu)
# BRIA_DEVICE=cuda
```

## Usage

The local model will be used automatically if:
1. `USE_LOCAL_BRIA=true` in `.env` (default)
2. The model is successfully loaded

The system will automatically:
- Download model weights on first use (~8GB)
- Use GPU if available (CUDA), otherwise CPU
- Fall back to API mode if local model fails

## Model Details

- **Model**: BRIA-4B-Adapt
- **Parameters**: 4 billion
- **License**: Commercial licensing available
- **Resolution**: Supports multiple aspect ratios (~1M pixels recommended)
- **Inference Steps**: 30-50 recommended
- **Guidance Scale**: 5.0 recommended

## Performance

- **GPU (CUDA)**: ~10-30 seconds per image
- **CPU**: ~2-5 minutes per image (not recommended for production)

## Fine-tuning

The model supports LoRA fine-tuning for custom styles/characters. See:
- https://huggingface.co/briaai/BRIA-4B-Adapt
- Training script: `train_lora.py` (download from Hugging Face)

## Troubleshooting

### Model Download Issues
- Check internet connection
- Ensure sufficient disk space (~10GB for model)
- Try manual download from Hugging Face

### CUDA Out of Memory
- Reduce image resolution
- Use CPU mode: Set `BRIA_DEVICE=cpu` in `.env`
- Close other GPU applications

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check that pipeline files are in `backend/` directory

## Switching Between Local and API

To use BRIA API instead:
```bash
# In backend/.env
USE_LOCAL_BRIA=false
BRIA_API_TOKEN=your_api_token
```

The system will automatically use the configured method.




