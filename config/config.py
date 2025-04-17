import json
import threading
import os
from typing import Any, Optional
from pathlib import Path


class Config:
    _instance: Optional["Config"] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(Config, cls).__new__(cls)
                    cls._instance._initialize_config()
        return cls._instance

    def _initialize_config(self):
        # Resolve the home directory and set the config file path
        self._config_file = os.path.join(os.path.expanduser("~"), ".voyagersdk", "config.json")
        self._load_config()

    def _load_config(self):
        """Load configuration from the JSON file."""
        try:
            with open(self._config_file, "r") as file:
                self._config = json.load(file)
        except FileNotFoundError:
            # If the file doesn't exist, initialize with default values
            self._config = {
                "mode": "LOCAL", # "LOCAL uses JWT Token, SERVICE uses Service Token"
                "service_token": None,
                "email": None,
                "auth_token": None,
                "refresh_token": None,
                "pipeline_cache": os.path.join(os.path.expanduser("~"), ".voyagersdk", "pipelines"),
                "default_file_group": os.environ.get("VOYAGER_FILE_GROUP", "b54d035d-f63c-4ea8-86fb-9dbc976bb7fe"),
                "base_url": os.environ.get("VOYAGER_URL", "http://voyager:5007")
            }
            self._dump_config()
            if not os.path.exists(self._config["pipeline_cache"]):
                Path(self._config["pipeline_cache"]).mkdir(parents=True, exist_ok=True)

    def _dump_config(self):
        """Save the current configuration to the JSON file."""
        with open(self._config_file, "w") as file:
            json.dump(self._config, file, indent=4)

    def __getattr__(self, name: str) -> Any:
        """Allow accessing configuration values as attributes."""
        if name in self._config:
            return self._config[name]
        raise AttributeError(f"'{name}' not found in configuration")

    def __setattr__(self, name: str, value: Any):
        """Allow modifying configuration values and dump changes to the file."""
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            with self._lock:
                self._config[name] = value
                self._dump_config()

    def __delattr__(self, name: str):
        """Prevent deletion of configuration values."""
        raise AttributeError("Cannot delete configuration values")