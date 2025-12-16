"""
Vercel Serverless Function Handler for FastAPI
This file serves as the entry point for Vercel's serverless functions
"""

import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the FastAPI app
from api.main import app

# Use Mangum to adapt FastAPI (ASGI) to Vercel's serverless format
# Mangum handles the conversion from AWS Lambda/Vercel events to ASGI
from mangum import Mangum

# Create Mangum handler - this adapts FastAPI to work with Vercel's serverless runtime
# lifespan="off" disables lifespan events which can cause issues in serverless environments
handler = Mangum(app, lifespan="off")

