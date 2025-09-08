import json
import os
def config():
    with open("db_config.json") as f:
        db_config = json.load(f)
        db_config['password'] = os.environ.get('sql_pass')
        return db_config