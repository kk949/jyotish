"""
services/panchang_service.py
----------------------------
Thin wrapper around support.panchang — keeps routers clean.
"""
from support.panchang import calculate_panchang   # existing module, unchanged


def get_panchang(date: str, lat: float, lon: float, tz: float, lang: str = "en"):
    return calculate_panchang(date, lat, lon, tz, lang)


def get_muhurta(date: str, lat: float, lon: float, tz: float):
    panchang = calculate_panchang(date, lat, lon, tz)
    return {
        "date"   : date,
        "sunrise": panchang["advanced_details"]["sun_rise"],
        "sunset" : panchang["advanced_details"]["sun_set"],
        "auspicious_times": {
            "abhijit_muhurta": panchang["advanced_details"]["abhijit_muhurta"]
        },
        "inauspicious_times": {
            "rahu_kaal"   : panchang["rahukaal"],
            "yamghant_kaal": panchang["yamakanta"],
            "gulika_kaal" : panchang["gulika"],
        },
    }
