import logging
from pathlib import Path
import time
from functools import wraps
import json

def log_func_name_duration(func):
    """
    Decorator to log the duration of function execution.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger = logging.getLogger(func.__module__)
        logger.info(f"Function `{func.__name__}` executed in {duration:.2f} seconds.")
        return result
    return wrapper


def setup_logging():
    """
    Configures logging for the application:
    - Logs to both console and a file.
    - Ensures no duplicate handlers are added.
    """
    logger = logging.getLogger()
    if logger.hasHandlers():
        return  # Prevent adding handlers multiple times

    logger.setLevel(logging.INFO)

    # Create logs directory
    project_root = Path(__file__).resolve().parents[1]
    log_dir = project_root / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'app.log'

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)


def log_dict_pretty(logger, data: dict, level=logging.INFO, msg: str = ""):
    formatted = json.dumps(data, indent=2)
    logger.log(level, f"{msg}\n{formatted}")

