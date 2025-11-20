import os
from pathlib import Path
from typing import Optional

# Define the base directory for the application's data
TICK_DATA_DIR = Path(os.path.expanduser("~")) / ".tick"

# Ensure the data directory exists
os.makedirs(TICK_DATA_DIR, exist_ok=True)

# Define the path to the SQLite database file
DATABASE_PATH = TICK_DATA_DIR / "tick.db"

# Define the path to the configuration file
CONFIG_PATH = TICK_DATA_DIR / "config.json"

DEFAULT_TIMEZONE = "UTC"

def get_user_timezone() -> str:
    from .services.config_service import config_service
    return config_service.get("timezone", DEFAULT_TIMEZONE)
