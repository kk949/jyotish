"""
services/dosha_service.py
--------------------------
Thin wrapper around support.dosha_calculator — keeps routers clean.
"""
from support.dosha_calculator import (
    calculate_mangal_dosh,
    calculate_pitra_dosh,
    calculate_kaalsarp_dosh,
    calculate_papasamaya,
)


def get_mangal_dosh(dob, tob, lat, lon, tz, lang="en"):
    return calculate_mangal_dosh(dob, tob, lat, lon, tz, lang)

def get_pitra_dosh(dob, tob, lat, lon, tz, lang="en"):
    return calculate_pitra_dosh(dob, tob, lat, lon, tz, lang)

def get_kaalsarp_dosh(dob, tob, lat, lon, tz, lang="en"):
    return calculate_kaalsarp_dosh(dob, tob, lat, lon, tz, lang)

def get_papasamaya(dob, tob, lat, lon, tz, lang="en"):
    return calculate_papasamaya(dob, tob, lat, lon, tz, lang)
