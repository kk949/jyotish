"""
-----------------------
Safe, stateless wrapper around the AshtakaVarga computation.

Fixes applied here (do NOT change mod_ashtakavarga.py):
  1. State reset bug  — BhinnaAshtakaVargaPoints is re-initialised on every call
  2. Shallow copy bug — deepcopy used when storing into data.charts
  3. Guard            — raises clearly if D1 chart was never computed
  4. Thread safety    — a lock prevents concurrent calls from mixing state

Usage in api.py:
  from support.ashtakavarga_service import router as ashtaka_router
  app.include_router(ashtaka_router)
"""

import copy
import threading
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
import jyotishyamitra as jm
import support.mod_astrodata as data
import support.mod_general as gen
from support.mod_ashtakavarga import BAV_BinduMatrix   # reuse the matrix — don't redefine it
from api_logger import log_api_call
from database import get_db_connection

logger = logging.getLogger(__name__)

# ── thread lock so concurrent API calls don't share mutable module-level state ──
_lock = threading.Lock()

# ── FastAPI router (mirrors the pattern used in api.py) ─────────────────────────
router = APIRouter(prefix="/ashtakavarga", tags=["Ashtakavarga"])


###############################################################################
# INTERNAL: fixed computation                                                  #
###############################################################################

def _fresh_bav_points() -> dict:
    """Return a brand-new, zeroed BhinnaAshtakaVargaPoints dict every time."""
    return {
        "Sun"     : [0] * 12,
        "Moon"    : [0] * 12,
        "Mars"    : [0] * 12,
        "Mercury" : [0] * 12,
        "Jupiter" : [0] * 12,
        "Venus"   : [0] * 12,
        "Saturn"  : [0] * 12,
        "Total"   : [0] * 12,
    }


def _compute_ashtakavarga_safe() -> dict:
    """
    Bug-fixed computation of Bhinna + Sarva AshtakaVarga.

    Differences from the original mod_ashtakavarga.compute_AshtakaVargas():
      • State is never accumulated — fresh dict created on every call.
      • deepcopy used so data.charts["AshtakaVarga"] is fully independent.
      • Raises ValueError if D1 planets haven't been computed yet.
    """
    import support.mod_constants as c
    for pname, pdata in data.charts["D1"]["planets"].items():
        if pname in BAV_BinduMatrix and pdata.get("status") == c.INIT:
            raise ValueError(
                f"D1 chart not computed yet — planet '{pname}' still has INIT status. "
                "Call jm.generate_astrologicalData() before requesting AshtakaVarga."
            )

    bav = _fresh_bav_points()   # ← fix 1: no accumulated state

    for planet in BAV_BinduMatrix:
        planet_bav = bav[planet]
        for ref_planet, benefic_positions in BAV_BinduMatrix[planet].items():
            if ref_planet == "Ascendant":
                ref_house = 1
            else:
                ref_house = data.charts["D1"]["planets"][ref_planet]["house-num"]

            for nth in benefic_positions:
                index = gen.compute_nthsign(ref_house, nth) - 1
                planet_bav[index] += 1

    # Sarva AshtakaVarga (Total)
    for h in range(12):
        bav["Total"][h] = sum(bav[p][h] for p in
                              ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])

    # Store in charts with a DEEP copy so inner lists are independent ← fix 2
    data.charts["AshtakaVarga"] = copy.deepcopy(bav)
    return bav


###############################################################################
# PUBLIC: entry point used by the API endpoints                                #
###############################################################################

def get_ashtakavarga(dob: str, tob: str, lat: float, lon: float, tz: float) -> dict:
    """
    Compute and return AshtakaVarga for one birth chart.

    Parameters
    ----------
    dob : str   Date of birth  DD/MM/YYYY
    tob : str   Time of birth  HH:MM
    lat : float Latitude  (+N / -S)
    lon : float Longitude (+E / -W)
    tz  : float Timezone offset in decimal hours (e.g. 5.5 for IST)

    Returns
    -------
    dict with keys: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Total
    Each value is a list of 12 integers (points per rashi/sign).
    """
    try:
        day, month, year = dob.strip().split("/")
        hour, minute = tob.strip().split(":")
    except ValueError:
        raise ValueError("dob must be DD/MM/YYYY and tob must be HH:MM")

    with _lock:
        jm.input_birthdata(
            name      = "User",
            gender    = "Male",
            place     = "Birth Place",
            longitude = str(lon),
            lattitude = str(lat),
            timezone  = str(tz),
            year      = year,
            month     = month,
            day       = day,
            hour      = hour,
            min       = minute,
            sec       = "0",
        )

        result = jm.validate_birthdata()
        if result != "SUCCESS":
            raise ValueError(f"Birth data validation failed: {result}")

        birth_data = jm.get_birthdata()
        jm.generate_astrologicalData(birth_data, returnval="ASTRODATA_DICTIONARY")
        bav = _compute_ashtakavarga_safe()

    return bav


###############################################################################
# HELPER: remaining API calls — same pattern as every endpoint in api.py       #
###############################################################################

def _get_remaining_calls(api_id: Optional[str], endpoint: str, dob: Optional[str] = None) -> int:
    """
    Returns how many API calls the user has left today for this endpoint.
    Falls back to 500000 if api_id is absent or the DB lookup fails,
    exactly matching the behaviour of the existing endpoints in api.py.
    """
    remaining = 500000
    try:
        if api_id:
            # Derive today's date from dob string if provided, otherwise use now()
            if dob:
                try:
                    dt = datetime.strptime(dob, "%d/%m/%Y")
                except Exception:
                    dt = datetime.now()
            else:
                dt = datetime.now()

            conn = get_db_connection()
            cur  = conn.cursor()
            cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
            user = cur.fetchone()
            if user:
                uid   = user[0]
                today = dt.strftime("%Y-%m-%d")
                cur.execute(
                    "SELECT COUNT(*) FROM api_logs "
                    "WHERE user_id = %s AND api_endpoint = %s AND DATE(created_at) = %s",
                    (uid, endpoint, today),
                )
                used      = cur.fetchone()[0]
                remaining = max(0, 500000 - int(used))
            cur.close()
            conn.close()
    except Exception:
        remaining = 500000
    return remaining


###############################################################################
# HELPER: format raw BAV lists into labelled rashi dicts                       #
###############################################################################

_RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

def _to_rashi_map(points: list) -> list:
    return [{"rashi": _RASHIS[i], "rashi_num": i + 1, "points": points[i]}
            for i in range(12)]

def _format_bav_response(bav: dict) -> dict:
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    return {
        "bhinna_ashtakavarga": {p: _to_rashi_map(bav[p]) for p in planets},
        "sarva_ashtakavarga" : _to_rashi_map(bav["Total"]),
        "raw"                : bav,
    }


###############################################################################
# FASTAPI ENDPOINTS                                                            #
###############################################################################

@router.get("/")
@log_api_call("/ashtakavarga/")           # ← logs every call; api_id ties to the user record
def get_full_ashtakavarga(
    dob   : str,
    tob   : str,
    lat   : float,
    lon   : float,
    tz    : float,
    lang  : str = "en",
    api_id: Optional[str] = Query(None),  # ← authentication / usage tracking
):
    """
    Get complete Bhinna and Sarva AshtakaVarga for a birth chart.

    Parameters
    ----------
    dob    : Date of birth  DD/MM/YYYY
    tob    : Time of birth  HH:MM
    lat    : Latitude  (+N / -S)
    lon    : Longitude (+E / -W)
    tz     : Timezone offset in hours (e.g. 5.5 for IST)
    lang   : Language code (default "en")
    api_id : Your API key for authentication and usage tracking
    """
    try:
        logger.info(f"AshtakaVarga full request: dob={dob}, tob={tob}, lat={lat}, lon={lon}, tz={tz}")
        bav       = get_ashtakavarga(dob, tob, lat, lon, tz)
        remaining = _get_remaining_calls(api_id, "/ashtakavarga/", dob)
        logger.info("AshtakaVarga calculated successfully")
        return {
            "status"              : 200,
            "response"            : _format_bav_response(bav),
            "remaining_api_calls" : remaining,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        logger.error(f"AshtakaVarga error: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating AshtakaVarga: {str(e)}\n{traceback.format_exc()}"
        )


@router.get("/planet/{planet}")
@log_api_call("/ashtakavarga/planet/{planet}")   # ← logs with parameterised path
def get_planet_ashtakavarga(
    planet: str,
    dob   : str,
    tob   : str,
    lat   : float,
    lon   : float,
    tz    : float,
    lang  : str = "en",
    api_id: Optional[str] = Query(None),         # ← authentication / usage tracking
):
    """
    Get Bhinna AshtakaVarga for a single planet.

    Parameters
    ----------
    planet : Sun | Moon | Mars | Mercury | Jupiter | Venus | Saturn
    dob    : Date of birth  DD/MM/YYYY
    tob    : Time of birth  HH:MM
    lat    : Latitude
    lon    : Longitude
    tz     : Timezone offset in hours
    api_id : Your API key for authentication and usage tracking
    """
    valid = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    if planet not in valid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid planet '{planet}'. Valid values: {', '.join(valid)}"
        )
    try:
        logger.info(f"Planet BAV request: planet={planet}, dob={dob}")
        bav       = get_ashtakavarga(dob, tob, lat, lon, tz)
        remaining = _get_remaining_calls(api_id, "/ashtakavarga/planet/{planet}", dob)
        return {
            "status": 200,
            "response": {
                "planet"      : planet,
                "bav"         : _to_rashi_map(bav[planet]),
                "total_points": sum(bav[planet]),
            },
            "remaining_api_calls": remaining,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating planet AshtakaVarga: {str(e)}\n{traceback.format_exc()}"
        )


@router.get("/sarva")
@log_api_call("/ashtakavarga/sarva")      # ← logs every call
def get_sarva_ashtakavarga(
    dob   : str,
    tob   : str,
    lat   : float,
    lon   : float,
    tz    : float,
    lang  : str = "en",
    api_id: Optional[str] = Query(None),  # ← authentication / usage tracking
):
    """
    Get only the Sarva (Total) AshtakaVarga — sum of all 7 planet BAVs.

    Parameters
    ----------
    dob    : Date of birth  DD/MM/YYYY
    tob    : Time of birth  HH:MM
    lat    : Latitude
    lon    : Longitude
    tz     : Timezone offset in hours
    api_id : Your API key for authentication and usage tracking
    """
    try:
        logger.info(f"Sarva BAV request: dob={dob}, tob={tob}")
        bav       = get_ashtakavarga(dob, tob, lat, lon, tz)
        remaining = _get_remaining_calls(api_id, "/ashtakavarga/sarva", dob)
        return {
            "status": 200,
            "response": {
                "sarva_ashtakavarga": _to_rashi_map(bav["Total"]),
                "grand_total"       : sum(bav["Total"]),
            },
            "remaining_api_calls": remaining,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Sarva AshtakaVarga: {str(e)}\n{traceback.format_exc()}"
        )