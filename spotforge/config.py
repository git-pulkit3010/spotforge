# spotforge/config.py

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- API Keys ---
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Project Directories ---
PROJECT_ROOT = Path.cwd()
INPUTS_DIR = PROJECT_ROOT / "inputs"
PANELS_DIR = PROJECT_ROOT / "panels"
EXPORTS_DIR = PROJECT_ROOT / "exports"
CACHE_DIR = PROJECT_ROOT / "cache"

# Ensure directories exist
INPUTS_DIR.mkdir(exist_ok=True)
PANELS_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)
CACHE_DIR.mkdir(exist_ok=True)

# --- Generation Settings ---
DEFAULT_STYLE = "Warm Lifestyle"
MAX_PANELS = 6
ASPECT_RATIO = "16:9"
RESOLUTION = (1920, 1080)

# --- OpenRouter Settings ---
OPENROUTER_MODEL = "google/gemini-2.5-flash-image-preview"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- Preset Definitions ---
PRESETS = {
    "Minimal Studio": {
        "description": "Clean, simple background with strong product focus.",
        "lighting": "bright, even lighting",
        "background": "white or light grey seamless paper",
        "mood": "professional, minimalist"
    },
    "Warm Lifestyle": {
        "description": "Cozy, inviting scenes that tell a story.",
        "lighting": "warm, soft lighting, possibly golden hour",
        "background": "kitchen counter, living room, cozy blanket",
        "mood": "comfortable, inviting, homely"
    },
    "Outdoor Natural": {
        "description": "Natural settings with outdoor lighting.",
        "lighting": "natural daylight",
        "background": "park, garden, patio, trail",
        "mood": "fresh, energetic, adventurous"
    }
}

def validate_config():
    """Checks if essential configuration is present."""
    errors = []
    if not OPENROUTER_API_KEY:
        errors.append("OPENROUTER_API_KEY not found in environment variables (.env file).")
    return errors

config_errors = validate_config()
if config_errors:
    print("Configuration Errors:")
    for error in config_errors:
        print(f" - {error}")
    # raise ValueError("Critical configuration missing. Please check .env file and config.py")
