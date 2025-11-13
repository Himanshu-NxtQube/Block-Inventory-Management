import os
import json
import yaml

# Paths
BASE_DIR      = os.getcwd()
CLIENTS_FILE  = os.path.join(BASE_DIR, "configs", "clients.json")
COMMON_FILE   = os.path.join(BASE_DIR, "configs", "common.yaml")

# Load clients registry once
with open(CLIENTS_FILE, "r") as f:
    _clients_list = json.load(f)

# Build lookup: user_id -> config_path
_USER_ID_TO_PATH = {
    client["user_id"]: client["config_path"]
    for client in _clients_list
}

# Load common.yaml once (if it exists)
_common_config = {}
if os.path.isfile(COMMON_FILE):
    with open(COMMON_FILE, "r") as f:
        _common_config = yaml.safe_load(f) or {}

# Global config placeholder
CONFIG = None

def deep_merge(base: dict, override: dict) -> dict:
    result = base.copy()
    for k, v in override.items():
        if isinstance(v, dict) and k in result and isinstance(result[k], dict):
            result[k] = deep_merge(result[k], v)
        else:
            result[k] = v
    return result


def set_config(user_id: str|int):
    """
    Load the client-specific YAML, merge it with common.yaml (common first),
    and store in CONFIG.
    """
    global CONFIG

    if isinstance(user_id, str):
        user_id = int(user_id)

    try:
        client_path = _USER_ID_TO_PATH[user_id]
    except KeyError:
        raise ValueError(f"No client found for user_id: {user_id}")

    # Load client-specific YAML
    full_path = os.path.join(BASE_DIR, client_path)
    if not os.path.isfile(full_path):
        raise FileNotFoundError(f"Config file not found: {full_path}")

    with open(full_path, "r") as f:
        client_config = yaml.safe_load(f) or {}

    # Merge: common settings overridden by client-specific
    # merged = {**_common_config, **client_config}
    merged = deep_merge(_common_config, client_config)

    CONFIG = merged

def get_config():
    """
    Retrieve the merged config. Must call set_config() first.
    """
    if CONFIG is None:
        raise RuntimeError("Config has not been set. Call set_config(user_id) first.")
    return CONFIG

