#!/bin/bash
# Install BRIA-4B-Adapt local model dependencies

echo "📥 Installing BRIA-4B-Adapt local model dependencies..."
echo ""

cd "$(dirname "$0")"

# Install base requirements
pip install -q huggingface-hub accelerate

# Download BRIA pipeline files
echo "📥 Downloading BRIA-4B-Adapt pipeline files..."
python3 << EOF
from huggingface_hub import hf_hub_download
import os

backend_dir = os.path.dirname(os.path.abspath(__file__))

files = [
    'pipeline_bria.py',
    'transformer_bria.py',
    'bria_utils.py'
]

for filename in files:
    print(f"Downloading {filename}...")
    try:
        hf_hub_download(
            repo_id="briaai/BRIA-4B-Adapt",
            filename=filename,
            local_dir=backend_dir
        )
        print(f"✅ {filename} downloaded")
    except Exception as e:
        print(f"❌ Failed to download {filename}: {e}")

print("\n✅ BRIA-4B-Adapt setup complete!")
print("\nNote: The model weights will be downloaded automatically on first use.")
print("This may take several minutes depending on your internet connection.")
EOF

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use the local model, set in .env:"
echo "  USE_LOCAL_BRIA=true"
echo ""
echo "The model will be downloaded automatically on first use."




