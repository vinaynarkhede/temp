"""
Logging configuration for Distributed Compute Marketplace.

Provides centralized logging setup with file rotation and console output.
"""

import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


# Default log directory
DEFAULT_LOG_DIR = "logs"

# Log file settings
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5  # Keep 5 backup files

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(
    name: str,
    log_dir: Optional[str] = None,
    level: Optional[int] = None
) -> logging.Logger:
    """
    Setup and configure a logger with file and console handlers.

    Creates a logger with:
    - Rotating file handler (10MB max, 5 backups)
    - Console handler for stdout
    - Appropriate log level based on environment

    Args:
        name: Logger name (typically module name)
        log_dir: Directory for log files (default: logs/)
        level: Logging level (default: based on ENVIRONMENT variable)

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(__name__)
        >>> logger.info("Application started")
    """
    # Get logger
    logger = logging.getLogger(name)

    # Determine log level
    if level is None:
        environment = os.getenv("ENVIRONMENT", "development")
        level = logging.DEBUG if environment == "development" else logging.INFO

    # If logger already has handlers with the same configuration, return it
    # This makes the function idempotent for the same configuration
    if logger.handlers and logger.level == level:
        return logger

    # Clear existing handlers if reconfiguring
    if logger.handlers:
        # Close file handlers properly before removing
        for handler in logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
        logger.handlers.clear()

    logger.setLevel(level)

    # Determine log directory
    if log_dir is None:
        log_dir = os.getenv("LOG_DIR", DEFAULT_LOG_DIR)

    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)

    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)

    # File handler (rotating)
    log_file = log_path / f"{name.replace('.', '_')}.log"
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=LOG_FILE_MAX_BYTES,
        backupCount=LOG_FILE_BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Prevent propagation to root logger (avoid duplicate logs)
    logger.propagate = False

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.

    This is a convenience wrapper around setup_logging() that uses
    default settings. Suitable for most use cases.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance

    Example:
        >>> from src.utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Module initialized")
    """
    return setup_logging(name)


def configure_root_logger() -> None:
    """
    Configure the root logger for the entire application.

    This should be called once at application startup to ensure
    consistent logging across all modules.

    Example:
        >>> from src.utils.logging_config import configure_root_logger
        >>> configure_root_logger()
    """
    root_logger = logging.getLogger()

    # Clear existing handlers
    root_logger.handlers.clear()

    # Set up root logger
    setup_logging("root")
