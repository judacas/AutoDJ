"""
Logging configuration for AutoDJ project.
Provides consistent logging setup across all modules.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    console_output: bool = True,
) -> logging.Logger:
    """
    Set up a logger with consistent formatting across the project.

    Args:
        name: Logger name (usually __name__)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional path to log file
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        try:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            # Log the error to the console
            error_msg = f"Failed to set up file logging at '{log_file}': {e}"
            temp_console_handler = logging.StreamHandler(sys.stderr)
            temp_console_handler.setLevel(logging.ERROR)
            temp_console_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
            logger.addHandler(temp_console_handler)
            logger.error(error_msg)
            logger.removeHandler(temp_console_handler)
    
    return logger


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module with default AutoDJ configuration.

    Args:
        module_name: Usually __name__ of the calling module

    Returns:
        Configured logger instance
    """
    return setup_logger(
        name=module_name,
        level=logging.INFO,
        log_file="logs/autodj.log",
        console_output=True
    )