"""
Vercel Serverless Function Handler for FastAPI
Minimal handler to avoid Vercel's handler inspection issues
"""

import sys
from pathlib import Path

# Setup paths
_current_file = Path(__file__).resolve()
_backend_dir = _current_file.parent.parent / "backend"

if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

# Lazy initialization - don't create anything at module level
# that Vercel might try to inspect
_app_instance = None
_mangum_instance = None

def _get_app():
    """Lazy load FastAPI app"""
    global _app_instance
    if _app_instance is None:
        from api.main import app
        _app_instance = app
    return _app_instance

def _get_mangum():
    """Lazy load Mangum adapter"""
    global _mangum_instance
    if _mangum_instance is None:
        from mangum import Mangum
        app = _get_app()
        _mangum_instance = Mangum(app, lifespan="off")
    return _mangum_instance

# Export a simple function handler
# This should avoid Vercel's class inspection
def handler(event, context):
    """Vercel serverless function handler"""
    mangum = _get_mangum()
    return mangum(event, context)
