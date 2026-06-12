import sys
from pathlib import Path

# Add app/backend to path
root_dir = Path(__file__).parent
backend_dir = root_dir / "app" / "backend"
sys.path.append(str(backend_dir))

# Import the FastAPI app from main.py
from main import app
