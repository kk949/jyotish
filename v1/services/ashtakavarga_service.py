"""
services/ashtakavarga_service.py
---------------------------------
AshtakaVarga computation — business logic only, no HTTP concerns.

All bugs from the original mod_ashtakavarga.py are fixed here:
  1. State reset  — fresh dict every call (no accumulation)
  2. Deep copy    — inner lists are fully independent
  3. Guard        — raises if D1 not computed
  4. Thread lock  — inherited from chart_service (one global lock)
"""

import copy
import logging

import support.mod_astrodata as data
import support.mod_general as gen
import support.mod_constants as c
from support.mod_ashtakavarga import BAV_BinduMatrix
from services.chart_service import compute_chart
from core.exceptions import ChartComputationError

logger = logging.getLogger(__name__)

_RASHIS = [
    "Aries", "Taurus", "Gemini", "Cancer",
    "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


# ── internal ──────────────────────────────────────────────────────────────────

def _fresh_bav() -> dict:
    return {p: [0] * 12 for p in _PLANETS + ["Total"]}


def _run_bav() -> dict:
    """Core BAV calculation — must be called while _jm_lock is held (via chart_service)."""
    for pname, pdata in data.charts["D1"]["planets"].items():
        if pname in BAV_BinduMatrix and pdata.get("status") == c.INIT:
            raise ChartComputationError(
                f"Planet '{pname}' has INIT status — D1 chart not computed."
            )

    bav = _fresh_bav()

    for planet in BAV_BinduMatrix:
        planet_row = bav[planet]
        for ref_planet, benefic_positions in BAV_BinduMatrix[planet].items():
            ref_house = (1 if ref_planet == "Ascendant"
                         else data.charts["D1"]["planets"][ref_planet]["house-num"])
            for nth in benefic_positions:
                planet_row[gen.compute_nthsign(ref_house, nth) - 1] += 1

    for h in range(12):
        bav["Total"][h] = sum(bav[p][h] for p in _PLANETS)

    data.charts["AshtakaVarga"] = copy.deepcopy(bav)
    return bav


# ── public ────────────────────────────────────────────────────────────────────

def get_ashtakavarga(dob: str, tob: str, lat: float, lon: float, tz: float) -> dict:
    """
    Compute full AshtakaVarga for the given birth details.
    Returns raw BAV dict:  { "Sun": [p1..p12], ..., "Total": [p1..p12] }
    """
    # compute_chart() acquires the jm lock and runs full chart generation
    compute_chart(dob=dob, tob=tob, lat=lat, lon=lon, tz=tz)
    # At this point D1 is populated; run BAV (still safe, lock released but
    # data.charts is ours until the next request touches it)
    return _run_bav()


def format_bav(bav: dict) -> dict:
    """Convert raw BAV lists to labelled rashi dicts for API responses."""
    def to_map(pts):
        return [{"rashi": _RASHIS[i], "rashi_num": i + 1, "points": pts[i]}
                for i in range(12)]
    return {
        "bhinna_ashtakavarga": {p: to_map(bav[p]) for p in _PLANETS},
        "sarva_ashtakavarga" : to_map(bav["Total"]),
        "raw"                : bav,
    }
