import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(log_path: Path, name: str = None) -> logging.Logger:
    """Unified logger setup. Configures root logger if name is None.
    
    Uses RotatingFileHandler to prevent disk space issues in production.
    """
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # If name is None, we configure the root logger
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if setup_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Silence noisy third-party loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    # Standardized format: [TIME] [LEVEL] [MODULE] - MESSAGE
    # Increased name padding to 30 for better visual coherence with long module names
    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-7s  %(name)-30s  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 1. Rotating File Handler (Max 5MB per file, keep 3 backups)
    fh = RotatingFileHandler(log_path, maxBytes=5 * 1024 * 1024, backupCount=3)
    fh.setFormatter(fmt)
    logger.addHandler(fh)

    # 2. Console Handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    return logger
