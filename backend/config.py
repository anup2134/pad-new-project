import os
from pathlib import Path
from dotenv import load_dotenv

# Get the directory where this config.py file is located (backend directory)
backend_dir = Path(__file__).parent
env_path = backend_dir / '.env'

# Load .env file from the backend directory
load_dotenv(dotenv_path=env_path)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# Define directories relative to project root
project_root = backend_dir.parent
UPLOAD_DIR = str(project_root / "uploads")
AUDIO_DIR = str(project_root / "audio")

# Ensure directories exist
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
