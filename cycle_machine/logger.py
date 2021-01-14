import logging

_log_file_handler = logging.FileHandler('c:/work/sw-delta-ai-cycles/logs/info.log')
_log_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_log_file_handler.setFormatter(_log_file_formatter)

logger = logging.getLogger('delta-engine')
logger.setLevel(logging.INFO)
logger.addHandler(_log_file_handler)
