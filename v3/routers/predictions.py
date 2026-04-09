"""
routers/predictions.py
"""
from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
import services.prediction_service as svc

router = APIRouter(prefix="/prediction", tags=["Predictions"])


@router.get("/daily-nakshatra")
@log_api_call("/prediction/daily-nakshatra")
def daily_nakshatra(nakshatra: int, dob: str, lang: str = "en",
                    api_id: Optional[str] = Query(None, alias="api_key")):
    try:
        return {"status": 200, "response": svc.get_nakshatra_prediction(nakshatra, dob, lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/prediction/daily-nakshatra")}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/daily-sun")
@log_api_call("/prediction/daily-sun")
def daily_sun(zodiac: int, date: str, lang: str = "en",
              split: bool = False,
              prediction_type: Literal["big","small"] = Query("big", alias="type"),
              api_id: Optional[str] = Query(None, alias="api_key")):
    try:
        return {"status": 200,
                "response": svc.get_sun_prediction(zodiac, date, prediction_type, lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/prediction/daily-sun")}
    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
