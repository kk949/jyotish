"""
core/config.py
--------------
Single source of truth for all configuration.
Values are read from environment variables / .env file.
Import `settings` anywhere — never read os.getenv() directly in other files.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Database ──────────────────────────────────────────────────────────────
    DB_HOST    : str = "localhost"
    DB_PORT    : int = 3306
    DB_USER    : str = "root"
    DB_PASSWORD: str = ""
    DB_NAME    : str = "jyotish"
    DB_TIMEOUT : int = 5
    DB_POOL_SIZE: int = 10          # max simultaneous DB connections
    DB_POOL_NAME: str = "jyotish_pool"

    # ── API limits ────────────────────────────────────────────────────────────
    API_DAILY_LIMIT: int = 500_000  # calls per user per day

    # ── App ───────────────────────────────────────────────────────────────────
    APP_TITLE  : str = "Jyotish API"
    APP_VERSION: str = "2.0.0"
    LOG_LEVEL  : str = "INFO"
    LOG_DIR    : str = "logs"
    LOG_MAX_BYTES : int = 10 * 1024 * 1024   # 10 MB
    LOG_BACKUP_COUNT: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"            # silently ignore unknown env vars


@lru_cache()                        # instantiated once for the whole process
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
