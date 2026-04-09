"""
routers/dosha.py
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
import services.dosha_service as svc

router = APIRouter(tags=["Dosha"])


@router.get("/mangal-dosh")
@log_api_call("/mangal-dosh")
def mangal_dosh(dob: str, tob: str, lat: float, lon: float, tz: float,
                lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_mangal_dosh(dob,tob,lat,lon,tz,lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/mangal-dosh")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/pitra-dosh")
@log_api_call("/pitra-dosh")
def pitra_dosh(dob: str, tob: str, lat: float, lon: float, tz: float,
               lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_pitra_dosh(dob,tob,lat,lon,tz,lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/pitra-dosh")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/kaalsarp-dosha")
@log_api_call("/kaalsarp-dosha")
def kaalsarp_dosh(dob: str, tob: str, lat: float, lon: float, tz: float,
                  lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_kaalsarp_dosh(dob,tob,lat,lon,tz,lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/kaalsarp-dosha")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/papasamaya")
@log_api_call("/papasamaya")
def papasamaya(dob: str, tob: str, lat: float, lon: float, tz: float,
               lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200, "response": svc.get_papasamaya(dob,tob,lat,lon,tz,lang),
                "remaining_api_calls": get_remaining_calls(api_id, "/papasamaya")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
