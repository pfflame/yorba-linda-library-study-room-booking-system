# Logging configuration
import logging
import sys
import json
from logging.handlers import RotatingFileHandler
import os

from config import settings

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineno": record.lineno
        }
        if record.exc_info:
            log_record['exc_info'] = self.formatException(record.exc_info)
        return json.dumps(log_record)

def setup_logger():
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(settings.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger = logging.getLogger("booking_system")
    logger.setLevel(settings.LOG_LEVEL)

    # Prevent duplicate handlers if logger is already configured
    if logger.hasHandlers():
        logger.handlers.clear()

    # File Handler
    file_handler = RotatingFileHandler(
        settings.LOG_FILE_PATH, 
        maxBytes=10*1024*1024, # 10 MB
        backupCount=5
    )
    if settings.LOG_FORMAT == 'json':
        file_formatter = JsonFormatter()
    else:
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    if settings.LOG_FORMAT == 'json':
        console_formatter = JsonFormatter()
    else:
        console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()