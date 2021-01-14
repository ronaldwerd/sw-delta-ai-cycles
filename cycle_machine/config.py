import configparser
import os

_CONFIG_PATH_ORDER = [os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '.' + os.path.sep + 'config.ini',
                      os.path.dirname(os.path.abspath(__file__)) + os.path.sep + '..' + os.path.sep + 'config.ini']
_config_path = None

for p in _CONFIG_PATH_ORDER:
    if os.path.isfile(p):
        _config_path = p
        break

if _config_path is None:
    print("Unable to find config.ini")
    exit(1)

config = configparser.ConfigParser()
config.read(_config_path)


CACHE_DIR = config['default']['cache_dir']
LOG_DIR = config['default']['log_dir']


if not os.path.exists(CACHE_DIR):
    os.path.makedirs(CACHE_DIR)

