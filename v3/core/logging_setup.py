"""
core/logging_setup.py
---------------------
Call configure_logging() once from api.py at startup.
All other modules just do: logger = logging.getLogger(__name__)
"""

import logging
import os
from logging.handlers import RotatingFileHandler

from core.config import settings


def configure_logging() -> None:
    os.makedirs(settings.LOG_DIR, exist_ok=True)

    fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    handlers = [
        RotatingFileHandler(
            os.path.join(settings.LOG_DIR, "api.log"),
            maxBytes    = settings.LOG_MAX_BYTES,
            backupCount = settings.LOG_BACKUP_COUNT,
        ),
        logging.StreamHandler(),
    ]

    logging.basicConfig(
        level    = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format   = fmt,
        handlers = handlers,
    )
