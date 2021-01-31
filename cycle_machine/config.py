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
SOLUTION_DIR = config['default']['solution_dir']

MONGO_DB_HOSTNAME = None
MONGO_DB_DBNAME = None
MONGO_DB_PORT = None

if 'mongodb' in config:
    MONGO_DB_HOSTNAME = config['mongodb']['hostname']
    MONGO_DB_PORT = int(config['mongodb']['port'])
    MONGO_DB_DBNAME = config['mongodb']['dbname']


if not os.path.exists(CACHE_DIR):
    os.path.makedirs(CACHE_DIR)

OANDA_ACCOUNT = None
OANDA_AUTH_TOKEN = None

if 'oanda' in config:
    OANDA_ACCOUNT = config['oanda']['account-id']
    OANDA_AUTH_TOKEN = config['oanda']['auth-token']

FINNHUB_AUTH_TOKEN = None

if 'finnhub' in config:
    FINNHUB_AUTH_TOKEN = config['finnhub']['auth-token']
