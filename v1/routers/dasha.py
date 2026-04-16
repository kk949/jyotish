"""
routers/dasha.py
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
import services.dasha_service as svc
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/dasha", tags=["Dasha"])

# ── helper to avoid repeating try/except boilerplate ─────────────────────────
def _ok(data, api_id, endpoint):
    return {"status": 200, "response": {**data, "calculation_date": str(datetime.now())},
            "remaining_api_calls": get_remaining_calls(api_id, endpoint)}


# ── Vimshottari ───────────────────────────────────────────────────────────────

@router.get("/vimshottari/current")
@log_api_call("/dasha/vimshottari/current")
def current_mahadasha(dob: str, tob: str, lat: float, lon: float, tz: float,
                      lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"current_mahadasha": svc.get_current_mahadasha(dob,tob,lat,lon,tz)},
                   api_id, "/dasha/vimshottari/current")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/full")
@log_api_call("/dasha/vimshottari/full")
def full_mahadasha(dob: str, tob: str, lat: float, lon: float, tz: float,
                   lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"current_mahadasha": svc.get_full_mahadasha(dob,tob,lat,lon,tz)},
                   api_id, "/dasha/vimshottari/full")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/all")
@log_api_call("/dasha/vimshottari/all")
def all_mahadashas(dob: str, tob: str, lat: float, lon: float, tz: float,
                   lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok(svc.get_all_mahadashas(dob,tob,lat,lon,tz),
                   api_id, "/dasha/vimshottari/all")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/antardasha")
@log_api_call("/dasha/vimshottari/antardasha")
def antardashas(dob: str, tob: str, lat: float, lon: float, tz: float,
                mahadasha_lord: Optional[str] = None,
                lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok(svc.get_antardashas(dob,tob,lat,lon,tz,mahadasha_lord),
                   api_id, "/dasha/vimshottari/antardasha")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/paryantardasha")
@log_api_call("/dasha/vimshottari/paryantardasha")
def paryantardashas(dob: str, tob: str, lat: float, lon: float, tz: float,
                    mahadasha_lord: Optional[str] = None,
                    antardasha_lord: Optional[str] = None,
                    lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok(svc.get_paryantardashas(dob,tob,lat,lon,tz,mahadasha_lord,antardasha_lord),
                   api_id, "/dasha/vimshottari/paryantardasha")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/predictions/{planet}")
@log_api_call("/dasha/vimshottari/predictions/{planet}")
def planet_predictions(planet: str, api_id: Optional[str] = Query(None)):
    try:
        return {"status": 200,
                "response": {"planet": planet,
                             "predictions": svc.get_mahadasha_predictions(planet)},
                "remaining_api_calls": get_remaining_calls(api_id,
                                       "/dasha/vimshottari/predictions/{planet}")}
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/vimshottari/specific/{planet}")
@log_api_call("/dasha/vimshottari/specific/{planet}")
def specific_dasha(planet: str, dob: str, tob: str, lat: float, lon: float,
                   tz: float, lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"planet": planet,
                    "dasha_details": svc.get_specific_dasha(dob,tob,lat,lon,tz,planet)},
                   api_id, "/dasha/vimshottari/specific/{planet}")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


# ── Chara ─────────────────────────────────────────────────────────────────────

@router.get("/chara/current")
@log_api_call("/dasha/chara/current")
def chara_current(dob: str, tob: str, lat: float, lon: float, tz: float,
                  lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"current_chara_dasha": svc.get_chara_current(dob,tob,lat,lon,tz)},
                   api_id, "/dasha/chara/current")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/chara/main")
@log_api_call("/dasha/chara/main")
def chara_main(dob: str, tob: str, lat: float, lon: float, tz: float,
               lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        periods = svc.get_chara_main(dob,tob,lat,lon,tz)
        return _ok({"chara_dasha_main_periods": periods, "total_periods": len(periods)},
                   api_id, "/dasha/chara/main")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/chara/sub/{sign}")
@log_api_call("/dasha/chara/sub/{sign}")
def chara_sub(sign: str, dob: str, tob: str, lat: float, lon: float, tz: float,
              lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"main_sign": sign, "sub_periods": svc.get_chara_sub(dob,tob,lat,lon,tz,sign)},
                   api_id, "/dasha/chara/sub/{sign}")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


# ── Yogini ────────────────────────────────────────────────────────────────────

@router.get("/yogini/main")
@log_api_call("/dasha/yogini/main")
def yogini_main(dob: str, tob: str, lat: float, lon: float, tz: float,
                lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        periods = svc.get_yogini_main(dob,tob,lat,lon,tz)
        return _ok({"yogini_dasha_main_periods": periods, "total_periods": len(periods),
                    "total_cycle_years": 36},
                   api_id, "/dasha/yogini/main")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/yogini/sub/{lord}")
@log_api_call("/dasha/yogini/sub/{lord}")
def yogini_sub(lord: str, dob: str, tob: str, lat: float, lon: float, tz: float,
               lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        return _ok({"main_lord": lord, "sub_periods": svc.get_yogini_sub(dob,tob,lat,lon,tz,lord)},
                   api_id, "/dasha/yogini/sub/{lord}")
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
