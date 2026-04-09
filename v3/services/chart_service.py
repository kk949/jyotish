"""
services/chart_service.py
--------------------------
SINGLE entry point for all chart computation in the application.

Why this exists
---------------
jyotishyamitra (jm) uses module-level mutable state.  If two HTTP requests
call jm.generate_astrologicalData() at the same time they corrupt each
other's data.  This service owns the ONE threading.Lock that serialises
all chart computation.  Every other service (dasha, ashtakavarga, dosha …)
calls compute_chart() here instead of calling jm directly.

Usage
-----
    from services.chart_service import compute_chart

    chart_data = compute_chart(dob="15/06/1990", tob="10:30",
                               lat=19.07, lon=72.87, tz=5.5)
    d1 = chart_data["D1"]
"""

import logging
from concurrent.futures import ProcessPoolExecutor, TimeoutError

import jyotishyamitra as jm
from core.exceptions import InvalidBirthDataError, ChartComputationError

logger = logging.getLogger(__name__)

# 🚀 Process pool (parallel + safe)
_executor = ProcessPoolExecutor(max_workers=4)


def _compute_chart_internal(payload: dict) -> dict:
    try:
        jm.clear_birthdata()

        jm.input_birthdata(**payload)

        result = jm.validate_birthdata()
        if result != "SUCCESS":
            raise InvalidBirthDataError(result)

        birth_data = jm.get_birthdata()

        return jm.generate_astrologicalData(
            birth_data,
            returnval="ASTRODATA_DICTIONARY"
        )

    except Exception as e:
        raise e


def compute_chart(
    dob: str,
    tob: str,
    lat: float,
    lon: float,
    tz: float,
    name: str = "User",
    gender: str = "Male",
    place: str = "Birth Place",
    sec: str = "0",
) -> dict:

    try:
        hour, minute = tob.strip().split(":")
        day, month, year = dob.strip().split("/")
    except ValueError:
        raise InvalidBirthDataError("Invalid DOB/TOB format")

    payload = {
        "name": name,
        "gender": gender,
        "place": place,
        "longitude": str(lon),
        "lattitude": str(lat),
        "timezone": str(tz),
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "min": minute,
        "sec": sec,
    }

    future = _executor.submit(_compute_chart_internal, payload)

    try:
        result = future.result(timeout=20)
    except TimeoutError:
        raise ChartComputationError("Chart computation timeout")
    except InvalidBirthDataError:
        raise
    except Exception as e:
        logger.error(f"Chart computation failed: {e}")
        raise ChartComputationError(str(e))

    return result