"""
A Python module that configures the logger for the application.

This module defines a dictionary-based logging configuration
(`logger_configuration`) and initializes the main application logger
(`app_logger`).
It provides a flexible setup for logging, supporting both console and
file outputs.

The logging configuration supports the following handlers:
1. `consoleHandler`: Logs INFO and higher-level messages to the console.
2. `infoFileHandler`: Logs INFO and higher-level messages to a file
   (logs/normal_activity.log).
3. `errorFileHandler`: Logs ERROR and higher-level messages to a file
   (logs/errors.log).

Details:
--------
Loggers:
  - `appLogger`: The main application logger for logging general messages.

Handlers:
  - `consoleHandler`: Logs INFO or higher messages to the console (stdout).
  - `infoFileHandler`: Logs INFO or higher messages to
  logs/normal_activity.log.
  - `errorFileHandler`: Logs ERROR or higher messages to logs/errors.log.

Formatters:
  - `fileFormatter`: Specifies the layout for messages written to files.
    It includes the timestamp, module, function name, log level, and message
     content.
  - `consoleFormatter`: Specifies the layout for messages logged to the
   console, including the log level and message content.

This module also automatically applies the logging configuration (`dictConfig`)
and exposes the globally available `app_logger` instance, which can be used
throughout the application.

Usage:
------
Simply import and use `app_logger` in your code:
    from core.logger import app_logger

    app_logger.info("This is an informational message.")
    app_logger.error("This is an error message.")
"""

import sys
from logging import getLogger
from logging.config import dictConfig

LEVEL: str = "level"
FILE_FORMAT: str = (
    "%(asctime)s - %(module)s.%(funcName)s - %(levelname)s - %(message)s"  # noqa: WPS323,E501
)
CONSOLE_FORMAT: str = "%(levelname)s - %(message)s"  # noqa: WPS323
DATE_FORMAT: str = "%Y-%m-%dT%H:%M:%S%Z"  # noqa: WPS323

logger_configuration = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "fileFormatter": {
            "format": FILE_FORMAT,
            "datefmt": DATE_FORMAT,
        },
        "consoleFormatter": {
            "format": CONSOLE_FORMAT,
            "datefmt": DATE_FORMAT,
        },
    },
    "handlers": {
        "consoleHandler": {
            "class": "logging.StreamHandler",
            LEVEL: "INFO",
            "formatter": "consoleFormatter",
            "stream": sys.stdout,
        },
        "infoFileHandler": {
            "class": "logging.FileHandler",
            LEVEL: "INFO",
            "formatter": "fileFormatter",
            "filename": "logs/normal_activity.log",
        },
        "errorFileHandler": {
            "class": "logging.FileHandler",
            LEVEL: "ERROR",
            "formatter": "fileFormatter",
            "filename": "logs/errors.log",
        },
    },
    "loggers": {
        "appLogger": {
            LEVEL: "DEBUG",
            "handlers": [
                "consoleHandler",
                "infoFileHandler",
                "errorFileHandler",
            ],
            "qualname": "appLogger",
            "propagate": False,
        },
    },
}

dictConfig(logger_configuration)
app_logger = getLogger("appLogger")
