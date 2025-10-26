"""

    Logging module to have all logging in one place!

"""
import logging
import os

from logging import config


def init():
    logging.getLogger(app_name)


def critical(msg, *args, **kwargs):
    logger.critical(msg, *args, **kwargs)


def debug(msg, *args, **kwargs):
    logger.debug(msg, *args, **kwargs)


def error(msg, *args, **kwargs):
    logger.error(msg, *args, **kwargs)


def info(msg, *args, **kwargs):
    logger.info(msg, *args, **kwargs)


def warning(msg, *args, **kwargs):
    logger.warning(msg, *args, **kwargs)


def find_log_dir(project):

    # Find where to output logs (projects 'logs' directory if found, or current directory's 'logs' directory if not.
    found_proj_dir = os.getcwd()
    while True:
        if found_proj_dir.split('/')[-1] == project:
            return found_proj_dir
        else:
            found_proj_dir = '/'.join(found_proj_dir.split('/')[:-1])
        if len(found_proj_dir.split('/')[:-1]) == 1:
            return os.getcwd()

# Configuration
app_name = 'starlight'
log_path = find_log_dir(app_name) + '/logs'

# Start
os.makedirs(log_path, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s.%(msecs)03d %(message)s",
            "old_datefmt": "%Y-%m-%d %H:%M:%S",
            "datefmt": "%H:%M:%S"
        }
    },
    "handlers": {
        "stdout": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "verbose",
            "level": "CRITICAL"
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "verbose",
            "filename": f"{log_path}/{app_name}.log",
            "encoding": "utf-8",
            "level": "DEBUG"
        }
    },
    "loggers": {
        app_name: {
            "handlers": [
                "stdout",
                "file"
            ],
            "level": "DEBUG"
        },
        "paramiko": {
            "handlers": [
                "stdout",
                "file"
            ],
            "level": "CRITICAL"
        }
    }
}

config.dictConfig(LOGGING)
logger = logging.getLogger(app_name)
