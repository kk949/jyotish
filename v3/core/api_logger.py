"""
core/api_logger.py
------------------
Drop-in replacement for the old api_logger.py.

Changes from original:
  1. Uses core.database.get_connection() pool — no new socket per call.
  2. Fixed bug: sql variable referenced before assignment in get_api_usage_stats.
  3. Uses settings.API_DAILY_LIMIT instead of hard-coded 500_000.
  4. Remaining-calls helper extracted so routers can call it without repeating SQL.
"""

from functools import wraps
import json
import logging
import traceback
from datetime import datetime
from typing import Optional

from fastapi import HTTPException

from core.database import get_connection
from core.config import settings

logger = logging.getLogger(__name__)


# ── decorator ─────────────────────────────────────────────────────────────────

def log_api_call(endpoint_name: str):
    """
    Decorator that:
      1. Requires a valid, active api_id query parameter.
      2. Inserts an api_logs row before the call.
      3. Updates that row with the response (or error) after the call.

    Usage:
        @router.get("/something")
        @log_api_call("/something")
        def my_endpoint(..., api_id: Optional[str] = Query(None)):
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            api_id   = kwargs.get("api_id")
            log_id   = None
            user_id  = None

            if not api_id:
                logger.error("Request rejected — api_id not provided")
                raise HTTPException(status_code=401, detail="API ID is required")

            try:
                with get_connection() as conn:
                    cur = conn.cursor()

                    # ── 1. Authenticate ───────────────────────────────────────
                    cur.execute(
                        "SELECT id, status FROM users WHERE app_id = %s", (api_id,)
                    )
                    user = cur.fetchone()

                    if not user:
                        raise HTTPException(status_code=401, detail="Invalid API ID")

                    user_id = user[0]
                    status  = user[1] if len(user) > 1 else "active"

                    if status != "active":
                        raise HTTPException(
                            status_code=403,
                            detail="API ID is inactive. Please contact support.",
                        )

                    # ── 2. Insert initial log row ─────────────────────────────
                    payload = {
                        k: v for k, v in kwargs.items()
                        if k not in ("api_id", "password", "token")
                    }
                    cur.execute(
                        """INSERT INTO api_logs
                               (user_id, api_endpoint, request_payload, status_code, created_at)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (user_id, endpoint_name,
                         json.dumps(payload, default=str), 200, datetime.now()),
                    )
                    conn.commit()
                    log_id = cur.lastrowid

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Pre-call DB error in {endpoint_name}: {e}\n{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=f"Internal error: {e}")

            # ── 3. Execute the actual endpoint ────────────────────────────────
            try:
                response = func(*args, **kwargs)
            except HTTPException as http_ex:
                _update_log(log_id, http_ex.status_code,
                            {"error": http_ex.detail}, endpoint_name)
                raise
            except Exception as e:
                _update_log(log_id, 500,
                            {"error": str(e), "trace": traceback.format_exc()[:1000]},
                            endpoint_name)
                logger.error(f"Error in {endpoint_name}: {e}\n{traceback.format_exc()}")
                raise HTTPException(status_code=500, detail=str(e))

            # ── 4. Update log row with success response ───────────────────────
            _update_log(log_id, 200, response, endpoint_name)
            logger.info(f"{endpoint_name} OK — user_id={user_id}")
            return response

        return wrapper
    return decorator


def _update_log(log_id: Optional[int], status_code: int,
                response_body, endpoint_name: str) -> None:
    """Update the api_logs row created at the start of the call."""
    if not log_id:
        return
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                """UPDATE api_logs
                      SET status_code = %s, response_payload = %s, updated_at = %s
                    WHERE id = %s""",
                (status_code,
                 json.dumps(response_body, default=str),
                 datetime.now(),
                 log_id),
            )
            conn.commit()
    except Exception as e:
        logger.error(f"Could not update log {log_id} for {endpoint_name}: {e}")


# ── helpers used by routers to attach remaining_api_calls ─────────────────────

def get_remaining_calls(api_id: Optional[str], endpoint: str,
                        date: Optional[datetime] = None) -> int:
    """
    Returns calls remaining today for this user+endpoint.
    Falls back to the daily limit if api_id is absent or the query fails,
    so legitimate errors don't silently block users.
    """
    if not api_id:
        return settings.API_DAILY_LIMIT

    ref_date = (date or datetime.now()).strftime("%Y-%m-%d")

    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
            user = cur.fetchone()
            if not user:
                return 0

            cur.execute(
                """SELECT COUNT(*) FROM api_logs
                    WHERE user_id = %s
                      AND api_endpoint = %s
                      AND DATE(created_at) = %s""",
                (user[0], endpoint, ref_date),
            )
            used = cur.fetchone()[0]
            return max(0, settings.API_DAILY_LIMIT - int(used))
    except Exception as e:
        logger.error(f"get_remaining_calls error: {e}")
        return settings.API_DAILY_LIMIT


# ── standalone utilities (kept for backward compatibility) ────────────────────

def get_user(api_id: str):
    if not api_id:
        return None
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, status, created_at FROM users WHERE app_id = %s", (api_id,)
            )
            user = cur.fetchone()
        if not user:
            return None
        if len(user) > 1 and user[1] != "active":
            raise HTTPException(status_code=403, detail="API ID is inactive")
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_user error: {e}")
        return None


def validate_api_key(api_id: str) -> bool:
    if not api_id:
        return False
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT COUNT(*) FROM users WHERE app_id = %s AND status = 'active'",
                (api_id,),
            )
            return cur.fetchone()[0] > 0
    except Exception as e:
        logger.error(f"validate_api_key error: {e}")
        return False


def get_api_usage_stats(api_id: str, endpoint: str = None, days: int = 30):
    if not api_id:
        return None
    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
            user = cur.fetchone()
            if not user:
                return None
            user_id = user[0]

            # ── fixed: sql defined before it is used ──────────────────────────
            if endpoint:
                sql = """
                    SELECT COUNT(*) as total,
                           SUM(status_code = 200) as ok,
                           SUM(status_code != 200) as failed,
                           DATE(created_at) as day
                      FROM api_logs
                     WHERE user_id = %s AND api_endpoint = %s
                       AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                     GROUP BY DATE(created_at)
                     ORDER BY day DESC
                """
                cur.execute(sql, (user_id, endpoint, days))
            else:
                sql = """
                    SELECT COUNT(*) as total,
                           SUM(status_code = 200) as ok,
                           SUM(status_code != 200) as failed,
                           DATE(created_at) as day
                      FROM api_logs
                     WHERE user_id = %s
                       AND created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                     GROUP BY DATE(created_at)
                     ORDER BY day DESC
                """
                cur.execute(sql, (user_id, days))

            rows = cur.fetchall()

        total_calls = sum(r[0] for r in rows)
        total_ok    = sum(r[1] or 0 for r in rows)
        total_fail  = sum(r[2] or 0 for r in rows)

        return {
            "api_id"     : api_id,
            "endpoint"   : endpoint or "all",
            "period_days": days,
            "daily_usage": [
                {"date": str(r[3]), "total_calls": r[0],
                 "successful_calls": r[1], "failed_calls": r[2]}
                for r in rows
            ],
            "summary": {
                "total_calls"     : total_calls,
                "successful_calls": total_ok,
                "failed_calls"    : total_fail,
                "success_rate"    : (
                    f"{total_ok / total_calls * 100:.2f}%" if total_calls else "0%"
                ),
            },
        }
    except Exception as e:
        logger.error(f"get_api_usage_stats error: {e}")
        return None


def check_rate_limit(api_id: str, endpoint: str,
                     limit_per_day: int = None) -> dict:
    limit = limit_per_day or settings.API_DAILY_LIMIT
    if not api_id:
        return {"allowed": True, "remaining": limit, "limit": limit}

    try:
        with get_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
            user = cur.fetchone()
            if not user:
                return {"allowed": False, "remaining": 0, "limit": limit,
                        "error": "Invalid API ID"}

            cur.execute(
                """SELECT COUNT(*) FROM api_logs
                    WHERE user_id = %s AND api_endpoint = %s
                      AND DATE(created_at) = CURDATE()""",
                (user[0], endpoint),
            )
            used      = cur.fetchone()[0]
            remaining = max(0, limit - used)
            return {
                "allowed"   : remaining > 0,
                "remaining" : remaining,
                "limit"     : limit,
                "used_today": used,
            }
    except Exception as e:
        logger.error(f"check_rate_limit error: {e}")
        return {"allowed": True, "remaining": limit, "limit": limit, "error": str(e)}
