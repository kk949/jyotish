def build_birthdata(payload: dict) -> dict:
    return {
        "name": payload["name"],
        "gender": payload["gender"],
        "DOB": {
            "year": int(payload["year"]),
            "month": int(payload["month"]),
            "day": int(payload["day"]),
        },
        "TOB": {
            "hour": int(payload["hour"]),
            "min": int(payload["minute"]),
            "sec": int(payload.get("second", 0)),
        },
        "POB": {
            "name": payload["place"],
            "lon": float(payload["longitude"]),
            "lat": float(payload["latitude"]),
            "timezone": float(payload["timezone"]),
        }
    }