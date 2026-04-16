"""
routers/horoscope.py
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
import services.prediction_service as svc
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/horoscope", tags=["Horoscope"])


@router.get("/daily")
@log_api_call("/horoscope/daily")
def daily_horoscope(zodiac: int, date: str, lang: str = "en",
                    api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_daily_horoscope(zodiac, date),
                "remaining_api_calls": get_remaining_calls(api_id, "/horoscope/daily")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/weekly")
@log_api_call("/horoscope/weekly")
def weekly_horoscope(zodiac: int, start_date: str, lang: str = "en",
                     api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_weekly_horoscope(zodiac, start_date),
                "remaining_api_calls": get_remaining_calls(api_id, "/horoscope/weekly")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/monthly")
@log_api_call("/horoscope/monthly")
def monthly_horoscope(zodiac: int, month: int, year: int, lang: str = "en",
                      api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_monthly_horoscope(zodiac, month, year),
                "remaining_api_calls": get_remaining_calls(api_id, "/horoscope/monthly")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
