import json
from typing import Any, Dict, Optional
from ..config import CONFIG_PATH

# Define default configuration values and their descriptions
DEFAULT_CONFIGS = {
    "debug_mode": {"value": "false", "description": "Enable or disable debug logging and profiling (true/false)."},
    "log_file_path": {"value": "~/.tick/.logs/app.log", "description": "Absolute path to the log file."},
    "log_file_max_bytes": {"value": "10485760", "description": "Maximum size of a log file before rotation (in bytes)."},
    "log_file_backup_count": {"value": "5", "description": "Number of backup log files to keep."},
    "log_level": {"value": "INFO", "description": "Minimum logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL). Overrides debug_mode for file logging."},
}

class ConfigService:
    def __init__(self):
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r') as f:
                return json.load(f)
        return {}

    def _save_config(self):
        with open(CONFIG_PATH, 'w') as f:
            json.dump(self._config, f, indent=4)

    def get(self, key: str) -> Any:
        # First, try to get the value from the loaded config
        value = self._config.get(key)
        if value is not None:
            return value
        
        # If not found, try to get it from default configs
        default_entry = DEFAULT_CONFIGS.get(key)
        if default_entry:
            return default_entry["value"]
        
        return None # Return None if key is not found anywhere

    def set(self, key: str, value: Any):
        self._config[key] = value
        self._save_config()

    def delete(self, key: str):
        if key in self._config:
            del self._config[key]
            self._save_config()

    def all(self) -> Dict[str, Any]:
        return self._config

config_service = ConfigService()
