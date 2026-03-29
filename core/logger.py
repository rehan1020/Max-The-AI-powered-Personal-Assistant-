"""Logger module using loguru.

Replaces standard logging with loguru for better output.
"""

import sys
from pathlib import Path

try:
    import config
    LOGS_DIR = config.LOGS_DIR
    LOG_LEVEL = config.LOG_LEVEL
except Exception:
    LOGS_DIR = Path("logs")
    LOG_LEVEL = "INFO"

LOGS_DIR.mkdir(parents=True, exist_ok=True)

try:
    from loguru import logger
except ImportError:
    import logging
    logger = logging.getLogger("max")
    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S"
    ))
    logger.addHandler(handler)
    file_handler = logging.FileHandler(LOGS_DIR / "max.log")
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s"
    ))
    logger.addHandler(file_handler)
else:
    logger.remove()

    logger.add(
        lambda msg: print(msg, end=""),
        level="INFO",
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
    )

    logger.add(
        LOGS_DIR / "max_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        rotation="1 day",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}"
    )

    logger.add(
        LOGS_DIR / "max_error_{time:YYYY-MM-DD}.log",
        level="ERROR",
        rotation="1 day",
        retention="30 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{line} | {message}"
    )

    logger.configure(
        extra={"platform": "unknown"}
    )

__all__ = ["logger"]
