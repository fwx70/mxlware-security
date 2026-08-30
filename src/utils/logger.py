import logging
import sys
from pathlib import Path

import config

def setup_logging():
    """Setup logging configuration"""
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger("discord_bot")
    logger.setLevel(config.LOG_LEVEL)
    
    # File handler
    fh = logging.FileHandler(config.LOG_FILE)
    fh.setLevel(config.LOG_LEVEL)
    
    # Console handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(config.LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

def get_protection_logger(name):
    """Get a logger for protection systems"""
    log_dir = Path(config.LOG_FILE).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(config.LOG_LEVEL)
    
    # Only add handlers if they don't exist
    if not logger.handlers:
        # File handler - separate log file for protection systems
        fh = logging.FileHandler(log_dir / f"protection_{name.lower()}.log")
        fh.setLevel(config.LOG_LEVEL)
        
        # Console handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(config.LOG_LEVEL)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger
