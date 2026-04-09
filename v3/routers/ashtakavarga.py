"""
routers/ashtakavarga.py
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from core.api_logger import log_api_call, get_remaining_calls
from services.ashtakavarga_service import get_ashtakavarga, format_bav
from core.exceptions import InvalidBirthDataError, ChartComputationError

router = APIRouter(prefix="/ashtakavarga", tags=["Ashtakavarga"])

_VALID_PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]


@router.get("/")
@log_api_call("/ashtakavarga/")
def full_ashtakavarga(dob: str, tob: str, lat: float, lon: float, tz: float,
                      lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        bav = get_ashtakavarga(dob, tob, lat, lon, tz)
        return {"status": 200, "response": format_bav(bav),
                "remaining_api_calls": get_remaining_calls(api_id, "/ashtakavarga/")}
    except (InvalidBirthDataError, ValueError) as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/planet/{planet}")
@log_api_call("/ashtakavarga/planet/{planet}")
def planet_bav(planet: str, dob: str, tob: str, lat: float, lon: float, tz: float,
               lang: str = "en", api_id: Optional[str] = Query(None)):
    if planet not in _VALID_PLANETS:
        raise HTTPException(400, f"Invalid planet '{planet}'. Valid: {', '.join(_VALID_PLANETS)}")
    try:
        bav      = get_ashtakavarga(dob, tob, lat, lon, tz)
        rashis   = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        bav_list = [{"rashi": rashis[i], "rashi_num": i+1, "points": bav[planet][i]}
                    for i in range(12)]
        return {"status": 200,
                "response": {"planet": planet, "bav": bav_list,
                             "total_points": sum(bav[planet])},
                "remaining_api_calls": get_remaining_calls(api_id,
                                       "/ashtakavarga/planet/{planet}")}
    except (InvalidBirthDataError, ValueError) as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")


@router.get("/sarva")
@log_api_call("/ashtakavarga/sarva")
def sarva_bav(dob: str, tob: str, lat: float, lon: float, tz: float,
              lang: str = "en", api_id: Optional[str] = Query(None)):
    try:
        bav    = get_ashtakavarga(dob, tob, lat, lon, tz)
        rashis = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo",
                  "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
        sarva  = [{"rashi": rashis[i], "rashi_num": i+1, "points": bav["Total"][i]}
                  for i in range(12)]
        return {"status": 200,
                "response": {"sarva_ashtakavarga": sarva,
                             "grand_total": sum(bav["Total"])},
                "remaining_api_calls": get_remaining_calls(api_id, "/ashtakavarga/sarva")}
    except (InvalidBirthDataError, ValueError) as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback; raise HTTPException(500, f"{e}\n{traceback.format_exc()}")
