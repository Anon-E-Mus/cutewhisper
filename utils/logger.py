"""
Logging Configuration Module - Sets up application-wide logging
"""

import logging
from pathlib import Path
import sys


def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    Configure application logging with both file and console handlers

    Args:
        log_level: Logging level (default: INFO)
        log_to_file: Whether to log to file (default: True)

    Returns:
        Logger instance for the main application
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers
    root_logger.handlers.clear()

    # Console handler (always enabled)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_to_file:
        log_file = log_dir / "cutewhisper.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels for noisy libraries
    logging.getLogger('faster_whisper').setLevel(logging.WARNING)
    logging.getLogger('sounddevice').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)

    # Return main application logger
    logger = logging.getLogger('CuteWhisper')
    logger.info(f"Logging initialized (Level: {logging.getLevelName(log_level)})")

    return logger
