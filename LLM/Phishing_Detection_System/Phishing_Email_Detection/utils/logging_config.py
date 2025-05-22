import logging
import os
from pathlib import Path

def setup_logging():
    """
    Sets up the logging configuration for the application.
    Logs messages to the console and to a file.
    """
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
    log_dir = PROJECT_ROOT / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_filepath = log_dir / 'app.log'

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)

        # File Handler
        file_handler = logging.FileHandler(log_filepath)
        file_handler.setLevel(logging.INFO)
        file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        file_handler.setFormatter(file_format)
        logger.addHandler(file_handler)