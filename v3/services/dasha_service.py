"""
services/dasha_service.py
--------------------------
All Dasha computation — business logic only, no HTTP concerns.
"""

import logging
from typing import Optional

import support.mod_astrodata as data
from services.chart_service import compute_chart
from support.dashas import (
    getCurrentMahadasha, getCurrentMahaDashaFull, getSpecificDasha,
    getParyantarDasha, getMahadashaPredictions,
    getCharDashaCurrent, getCharDashaMain, getCharDashaSub,
    getYoginiDashaMain, getYoginiDashaSub,
    Vimshottari, clearDashaDetails,
)
from core.exceptions import InvalidBirthDataError

logger = logging.getLogger(__name__)

VALID_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter",
                 "Venus", "Saturn", "Rahu", "Ketu"]


def _prepare(dob: str, tob: str, lat: float, lon: float, tz: float):
    """Compute chart + Vimshottari dasha. Returns (d1_division, birth_data)."""
    chart_data = compute_chart(dob=dob, tob=tob, lat=lat, lon=lon, tz=tz)
    clearDashaDetails()
    from input.birthdata import birthdata as bd
    Vimshottari(chart_data["D1"], bd)
    return chart_data["D1"], bd


# ── Vimshottari ───────────────────────────────────────────────────────────────

def get_current_mahadasha(dob, tob, lat, lon, tz):
    _prepare(dob, tob, lat, lon, tz)
    return getCurrentMahadasha()

def get_full_mahadasha(dob, tob, lat, lon, tz):
    _prepare(dob, tob, lat, lon, tz)
    return getCurrentMahaDashaFull()

def get_all_mahadashas(dob, tob, lat, lon, tz):
    _prepare(dob, tob, lat, lon, tz)
    return {
        "all_mahadashas": data.charts["Dashas"]["Vimshottari"]["mahadashas"],
        "current"       : data.charts["Dashas"]["Vimshottari"]["current"],
        "total_cycle_years": 120,
    }

def get_antardashas(dob, tob, lat, lon, tz, mahadasha_lord: Optional[str] = None):
    _prepare(dob, tob, lat, lon, tz)
    lord = mahadasha_lord or data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
    all_ant = data.charts["Dashas"]["Vimshottari"]["antardashas"]
    antardashas = {k: v for k, v in all_ant.items() if k.startswith(f"{lord}-")}
    return {
        "mahadasha_lord"   : lord,
        "antardashas"      : antardashas,
        "current_antardasha": data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"],
    }

def get_paryantardashas(dob, tob, lat, lon, tz,
                        mahadasha_lord=None, antardasha_lord=None):
    _prepare(dob, tob, lat, lon, tz)
    md = mahadasha_lord or data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
    ad = antardasha_lord or data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"]
    return {
        "mahadasha_lord" : md,
        "antardasha_lord": ad,
        "paryantardashas": getParyantarDasha(md, ad),
    }

def get_mahadasha_predictions(planet: str):
    if planet not in VALID_PLANETS:
        raise InvalidBirthDataError(
            f"Invalid planet '{planet}'. Valid: {', '.join(VALID_PLANETS)}"
        )
    return getMahadashaPredictions(planet)

def get_specific_dasha(dob, tob, lat, lon, tz, planet: str):
    _prepare(dob, tob, lat, lon, tz)
    return getSpecificDasha(planet)


# ── Chara ─────────────────────────────────────────────────────────────────────

def get_chara_current(dob, tob, lat, lon, tz):
    d1, bd = _prepare(dob, tob, lat, lon, tz)
    return getCharDashaCurrent(d1, bd)

def get_chara_main(dob, tob, lat, lon, tz):
    d1, bd = _prepare(dob, tob, lat, lon, tz)
    periods = getCharDashaMain(d1, bd)
    for p in periods:
        p["start_date"] = str(p["start_date"])
        p["end_date"]   = str(p["end_date"])
    return periods

def get_chara_sub(dob, tob, lat, lon, tz, sign: str):
    d1, bd = _prepare(dob, tob, lat, lon, tz)
    sub = getCharDashaSub(d1, bd, sign)
    if isinstance(sub, list):
        for p in sub:
            if "start_date" in p: p["start_date"] = str(p["start_date"])
            if "end_date"   in p: p["end_date"]   = str(p["end_date"])
    return sub


# ── Yogini ────────────────────────────────────────────────────────────────────

def get_yogini_main(dob, tob, lat, lon, tz):
    d1, bd = _prepare(dob, tob, lat, lon, tz)
    periods = getYoginiDashaMain(d1, bd)
    for p in periods:
        p["start_date"] = str(p["start_date"])
        p["end_date"]   = str(p["end_date"])
    return periods

def get_yogini_sub(dob, tob, lat, lon, tz, lord: str):
    d1, bd = _prepare(dob, tob, lat, lon, tz)
    sub = getYoginiDashaSub(d1, bd, lord)
    if isinstance(sub, list):
        for p in sub:
            if "start_date" in p: p["start_date"] = str(p["start_date"])
            if "end_date"   in p: p["end_date"]   = str(p["end_date"])
    return sub
