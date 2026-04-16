import json
import sys
from typing import Any, Dict, List, Tuple


def _print_result(method: str, path: str, status: int, ok: bool, detail: str = ""):
    flag = "OK" if ok else "FAIL"
    line = f"{flag:4} {method:6} {status:3} {path}"
    if detail:
        line += f"  - {detail}"
    print(line)


def main() -> int:
    # Import v3 app (no server needed)
    sys.path.insert(0, r"d:/jyotish/v3")
    from fastapi.testclient import TestClient  # type: ignore
    import api as v3_api  # v3/api.py

    client = TestClient(v3_api.app)

    api_id = "smoke-test"
    dob = "27/03/1992"
    tob = "11:55"
    lat = 22.3039
    lon = 70.8022
    tz = 5.5

    birth_data = {
        "name": "Dhaval",
        "gender": "male",
        "place": "Latipur, Jamangar",
        "longitude": str(lon),
        "latitude": str(lat),
        "timezone": str(tz),
        "year": "1992",
        "month": "03",
        "day": "27",
        "hour": "11",
        "minute": "55",
        "second": "0",
    }

    # Each test: (method, path, query_params, json_body, expected_statuses)
    tests: List[Tuple[str, str, Dict[str, Any], Any, List[int]]] = [
        ("GET", "/", {}, None, [200]),

        # Panchang
        ("GET", "/panchang/daily", {"date": dob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/panchang/muhurta", {"date": dob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Horoscope
        ("GET", "/horoscope/daily", {"zodiac": 1, "date": dob, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/horoscope/weekly", {"zodiac": 1, "start_date": dob, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/horoscope/monthly", {"zodiac": 1, "month": 3, "year": 1992, "lang": "en", "api_id": api_id}, None, [200]),

        # Predictions
        # Note: these endpoints use api_key alias, not api_id
        ("GET", "/prediction/daily-nakshatra", {"nakshatra": 1, "dob": dob, "lang": "en", "api_key": api_id}, None, [200]),
        ("GET", "/prediction/daily-sun", {"zodiac": 1, "date": dob, "lang": "en", "api_key": api_id}, None, [200]),

        # Dosha
        ("GET", "/mangal-dosh", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/pitra-dosh", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/kaalsarp-dosha", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/papasamaya", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Ashtakavarga
        ("GET", "/ashtakavarga/", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/ashtakavarga/planet/Sun", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/ashtakavarga/sarva", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Dasha (Vimshottari)
        ("GET", "/dasha/vimshottari/current", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/full", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/all", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/antardasha", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "mahadasha_lord": "Sun", "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/paryantardasha", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "mahadasha_lord": "Sun", "antardasha_lord": "Moon", "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/predictions/Sun", {"api_id": api_id}, None, [200]),
        ("GET", "/dasha/vimshottari/specific/Sun", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Dasha (Chara)
        ("GET", "/dasha/chara/current", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/chara/main", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/chara/sub/Aries", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Dasha (Yogini)
        ("GET", "/dasha/yogini/main", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),
        ("GET", "/dasha/yogini/sub/Moon", {"dob": dob, "tob": tob, "lat": lat, "lon": lon, "tz": tz, "lang": "en", "api_id": api_id}, None, [200]),

        # Chart
        ("POST", "/calculate", {}, birth_data, [200]),
        ("POST", "/generate-chart", {}, {"chart_type": "north", "chart_name": "Birth Chart", "person_name": "Dhaval", "birth_data": birth_data, "divisional_chart": "D1", "aspect": False,
                                         "clr_background": "black", "clr_outbox": "black", "clr_line": "yellow", "clr_sign": "black", "clr_Asc": "black",
                                         "clr_houses": ["#ffffff"] * 12,
                                         "planet_colors": {"Sun": "#FF8C00", "Moon": "#5B9BD5"}}, [200]),
        # This endpoint has two possible body params (data + chart_data),
        # so send BirthData under the "data" key.
        ("POST", "/chart/D1", {}, {"data": birth_data}, [200]),

        # PDF
        ("POST", "/pdf/kundali", {}, {"name": "Dhaval", "dob": dob, "tob": tob, "tz": tz, "place": "Latipur", "lat": lat, "lon": lon}, [200]),
    ]

    failures = 0
    for method, path, params, body, expected in tests:
        try:
            if method == "GET":
                r = client.get(path, params=params)
            elif method == "POST":
                r = client.post(path, params=params, json=body)
            else:
                raise RuntimeError(f"Unsupported method {method}")

            ok = r.status_code in expected
            detail = ""
            if not ok:
                failures += 1
                try:
                    detail = json.dumps(r.json())[:300]
                except Exception:
                    detail = (r.text or "")[:300]

            _print_result(method, path, r.status_code, ok, detail)
        except Exception as e:
            failures += 1
            _print_result(method, path, 0, False, repr(e)[:300])

    print()
    print(f"Failures: {failures} / {len(tests)}")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

