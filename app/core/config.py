import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"
STATIC_DIR = APP_DIR / "static"
TEMP_DIR = APP_DIR / "temp"
OUTPUT_DIR = APP_DIR / "outputs"

# Ensure essential directories exist
for directory in [TEMP_DIR, OUTPUT_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# App Metadata
VERSION = "0.1.0"
APP_NAME = "Local Timer Renderer"
DEFAULT_PORT = 8001
