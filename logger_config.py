"""Logging configuration module."""

import logging
import logging.handlers
import sys
from pathlib import Path
from config import Config


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "app.log",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> None:
    """
    Configure application logging with console and file handlers.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep
    """
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / log_file
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
    
    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Console handler (INFO level, simple format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler (detailed format, all levels)
    file_handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=max_bytes,
        backupCount=backup_count
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    logger.info("Logging configured successfully")


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class ContextFilter(logging.Filter):
    """Add context information to log records."""
    
    def __init__(self, context: dict = None):
        """
        Initialize context filter.
        
        Args:
            context: Dictionary of context values to add to logs
        """
        super().__init__()
        self.context = context or {}
    
    def filter(self, record):
        """Add context to log record."""
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


def add_context_filter(logger: logging.Logger, context: dict) -> None:
    """
    Add context filter to a logger.
    
    Args:
        logger: Logger instance
        context: Dictionary of context values
    """
    filter_instance = ContextFilter(context)
    logger.addFilter(filter_instance)
