import json
import os


def load_config(project_name):
    config_path = os.path.join("configs", f"{project_name}.json")

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, "r") as f:
        return json.load(f)