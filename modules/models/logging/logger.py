import os
import logging
from pathlib import Path
from datetime import datetime

def ensure_log_directory(log_dir: str = "logs") -> str:
    """
    Ensure that the log directory exists, create it if it doesn't.
    
    Args:
        log_dir (str): The directory path where logs should be stored. Defaults to 'logs'.
        
    Returns:
        str: The absolute path to the log directory
    """
    log_path = Path(log_dir).absolute()
    log_path.mkdir(parents=True, exist_ok=True)
    return str(log_path)

def get_logger(name: str, log_dir: str = "logs", log_level: int = logging.INFO) -> logging.Logger:
    """
    Get a logger with a file handler that writes to a log file in the specified directory.
    Creates the log directory and file if they don't exist.
    
    Args:
        name (str): The name of the logger
        log_dir (str): The directory to store log files. Defaults to 'logs'.
        log_level (int): The logging level. Defaults to logging.INFO.
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Ensure log directory exists
    log_path = ensure_log_directory(log_dir)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Don't add handlers if they're already added
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Create file handler
    log_file = os.path.join(log_path, f"{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Add handler to logger
    logger.addHandler(file_handler)
    
    return logger
