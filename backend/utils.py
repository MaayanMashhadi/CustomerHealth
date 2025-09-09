import json
import os
def config():
    with open("../db_config.json") as f:
        db_config = json.load(f)
        return db_config