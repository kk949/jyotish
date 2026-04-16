"""
routers/panchang.py
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
from services.panchang_service import get_panchang, get_muhurta
import logging

logger  = logging.getLogger(__name__)
router  = APIRouter(prefix="/panchang", tags=["Panchang"])


@router.get("/daily")
@log_api_call("/panchang/daily")
def daily_panchang(date: str, lat: float, lon: float, tz: float,
                   lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": get_panchang(date, lat, lon, tz, lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/panchang/daily")}
    except Exception as e:
        import traceback
        raise HTTPException(500, f"Panchang error: {e}\n{traceback.format_exc()}")


@router.get("/muhurta")
@log_api_call("/panchang/muhurta")
def muhurta_times(date: str, lat: float, lon: float, tz: float,
                  lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": get_muhurta(date, lat, lon, tz),
                "remaining_api_calls": get_remaining_calls(api_id, "/panchang/muhurta")}
    except Exception as e:
        import traceback
        raise HTTPException(500, f"Muhurta error: {e}\n{traceback.format_exc()}")
