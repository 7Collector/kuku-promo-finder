"""
Logging configuration with optional Rich formatting.
"""

import logging
import sys

logger = logging.getLogger("kuku")

def setup_logger(verbose: bool = False) -> logging.Logger:
    """Configures application logger."""
    level = logging.DEBUG if verbose else logging.INFO
    logger.setLevel(level)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
