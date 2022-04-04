import os
import logging
import json


def setup_logging(default_path="logging.json", default_level=logging.INFO, env_key = "LOG_CFG"):
    if not os.path.exists('log'):
        os.makedirs('log')
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, "r") as f:
            config = json.load(f)
            logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
