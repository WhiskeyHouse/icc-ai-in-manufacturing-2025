import logging
import sys
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """Configure logging settings for the application"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO if not settings.DEBUG else logging.DEBUG)

    # Configure console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))
    root_logger.addHandler(console_handler)

    # Set specific log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Debug mode - set all app loggers to DEBUG
    if settings.DEBUG:
        for logger_name in logging.root.manager.loggerDict:
            if logger_name.startswith("app."):
                logging.getLogger(logger_name).setLevel(logging.DEBUG)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)
