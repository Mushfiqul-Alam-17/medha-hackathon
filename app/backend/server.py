import sys
from pathlib import Path

# Add current folder to path
backend_dir = Path(__file__).parent
sys.path.append(str(backend_dir))

# Import the FastAPI app from main.py
from main import app
