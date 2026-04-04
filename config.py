import json
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


def get_credentials_info() -> dict:
    env_creds = os.environ.get("GOOGLE_CREDENTIALS")
    if not env_creds:
        raise RuntimeError(
            "GOOGLE_CREDENTIALS environment variable is not set. "
            "Set it to the JSON content of your service account credentials."
        )
    try:
        return json.loads(env_creds)
    except json.JSONDecodeError as e:
        raise ValueError("GOOGLE_CREDENTIALS is not valid JSON") from e
