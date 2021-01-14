import os
import logging
from cycle_machine import config

_log_file_handler = logging.FileHandler(config.LOG_DIR + os.path.sep + 'info.log')
_log_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_log_file_handler.setFormatter(_log_file_formatter)

logger = logging.getLogger('delta-engine')
logger.setLevel(logging.INFO)
logger.addHandler(_log_file_handler)
