import os
import sys

from configparser import ConfigParser
def get_config() -> ConfigParser:
    config = ConfigParser()
    # repo defaults
    if not os.path.exists(os.path.join(sys.path[0], 'config.ini')):
        raise FileNotFoundError(f"config.ini not found in {sys.path[0]}")
    config.read(os.path.join(sys.path[0], 'config.ini'))
    return config


