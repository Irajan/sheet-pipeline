import os
from pathlib import Path

import yaml


def load_config() -> dict:
    config_path = os.environ.get("CONFIG_PATH", "config.yaml")
    
    app_dir = Path(__file__).parent
    config_file = app_dir / config_path
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_file}")
    
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


def get_credentials_path() -> str:
    config = load_config()
    app_dir = Path(__file__).parent
    cred_path = config.get("credentials_path", "credentials.json")
    return str(app_dir / cred_path)
