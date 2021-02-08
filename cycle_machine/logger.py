import os
import logging
from cycle_machine import config

_loggers = {}

def get_logger_for(logger_name: str):
    if logger_name not in _loggers:
        log_file_handler = logging.FileHandler(config.LOG_DIR + os.path.sep + logger_name + '.log')
        log_file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        log_file_handler.setFormatter(log_file_formatter)

        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(log_file_handler)

        _loggers[logger_name] = logger

    return _loggers[logger_name]
