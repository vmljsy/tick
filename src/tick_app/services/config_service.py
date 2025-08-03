import json
from typing import Any, Dict, Optional
from ..config import CONFIG_PATH

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

    def get(self, key: str, default: Any = None) -> Any:
        return self._config.get(key, default)

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
