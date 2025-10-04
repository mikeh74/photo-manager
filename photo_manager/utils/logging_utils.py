"""
Logging utilities for the photo manager.
"""

import logging
import sys

from photo_manager.config import config


def setup_logging(log_level: str | None = None) -> logging.Logger:
    """
    Set up logging configuration.

    Args:
        log_level: Override default log level

    Returns:
        Configured logger instance
    """
    # Use provided level or config default
    level = log_level or config.log_level

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Set up console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Set up file handler if log file is configured
    handlers = [console_handler]
    if config.log_file:
        try:
            # Ensure log directory exists
            config.log_file.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(config.log_file)
            file_handler.setFormatter(formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not set up file logging: {e}")

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        handlers=handlers,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    return logging.getLogger("photo_manager")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
