"""
core/database.py
----------------
MySQL connection pool — created once at startup, shared across all requests.

Usage:
    from core.database import get_connection

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(...)
        conn.commit()
    # connection automatically returned to pool here

Never call mysql.connector.connect() anywhere else in the project.
"""

import mysql.connector
from mysql.connector import pooling
from urllib.parse import urlparse
from contextlib import contextmanager
import logging

from core.config import settings

logger = logging.getLogger(__name__)


def _sanitize_host(host: str) -> str:
    """Strip http/https prefix that sometimes ends up in env vars."""
    if not host:
        return "localhost"
    host = host.strip()
    if host.startswith(("http://", "https://")):
        return urlparse(host).hostname or host
    return host


# ── Pool created once when this module is first imported ──────────────────────
def _create_pool() -> pooling.MySQLConnectionPool:
    return pooling.MySQLConnectionPool(
        pool_name       = settings.DB_POOL_NAME,
        pool_size       = settings.DB_POOL_SIZE,
        host            = _sanitize_host(settings.DB_HOST),
        port            = settings.DB_PORT,
        user            = settings.DB_USER,
        password        = settings.DB_PASSWORD,
        database        = settings.DB_NAME,
        connection_timeout = settings.DB_TIMEOUT,
        autocommit      = False,
    )

try:
    _pool = _create_pool()
    logger.info(f"MySQL connection pool '{settings.DB_POOL_NAME}' created "
                f"(size={settings.DB_POOL_SIZE})")
except Exception as e:
    logger.critical(f"Failed to create MySQL connection pool: {e}")
    _pool = None


@contextmanager
def get_connection():
    """
    Context manager that borrows a connection from the pool and
    returns it automatically when the with-block exits.

        with get_connection() as conn:
            cur = conn.cursor()
            ...
    """
    conn = None
    try:
        if _pool is None:
            raise RuntimeError("Database connection pool is not initialized")
        conn = _pool.get_connection()
        yield conn
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        raise
    finally:
        if conn and conn.is_connected():
            conn.close()   # returns to pool, does NOT close the underlying socket


# ── Backward-compat shim so old code that calls get_db_connection()
#    keeps working without changes during the migration period. ─────────────────
def get_db_connection():
    """
    Deprecated — use `get_connection()` context manager instead.
    Kept for backward compatibility with api_logger and any other
    callers that haven't been migrated yet.
    """
    if _pool is None:
        raise RuntimeError("Database connection pool is not initialized")
    return _pool.get_connection()
