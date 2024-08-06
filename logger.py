"""Handles log messages"""

import logging


def exclude_http_requests(record):
    """Excludes logs that contain 'HTTP Request'"""
    return "HTTP Request" not in record.getMessage()


logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a file handler for the log file
file_handler = logging.FileHandler("application.log")
file_handler.setLevel(logging.INFO)

# Create a formatter and set it for the file handler
formatter = logging.Formatter(
    fmt="{asctime} - {levelname} - {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)

# Add the custom filter to the file handler
file_handler.addFilter(exclude_http_requests)

# Add the file handler to the root logger
logger.addHandler(file_handler)


def log_message(level, msg, *args):
    """
    Logs a message at the specified level.
    Args:
        level (str): The log level (e.g., 'info', 'warning', 'error').
        msg (str): The log message.
        *args: Arguments to format the message.
    """

    if level == "info":
        logger.info(msg, *args)
    elif level == "warning":
        logger.warning(msg, *args)
    elif level == "error":
        logger.error(msg, *args)
