import json
import os

def config():
    # Load from JSON
    with open(os.path.join(os.path.dirname(__file__), "db_config.json")) as f:
        db_config = json.load(f)

    return db_config
