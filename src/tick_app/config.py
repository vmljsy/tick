import os
from pathlib import Path

# Define the base directory for the application's data
TICK_DATA_DIR = Path(os.path.expanduser("~")) / ".tick"

# Ensure the data directory exists
os.makedirs(TICK_DATA_DIR, exist_ok=True)

# Define the path to the SQLite database file
DATABASE_PATH = TICK_DATA_DIR / "tick.db"
