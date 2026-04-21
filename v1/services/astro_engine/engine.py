from .builder import build_birthdata
from .validator import validate_birthdata
from .lagna import compute_lagna
from .divisional import compute_divisional
from .dasha import compute_dasha
from .ashtakavarga import compute_ashtakavarga


def generate_chart(payload: dict) -> dict:
    # Step 1: Build
    birthdata = build_birthdata(payload)

    # Step 2: Validate
    validate_birthdata(birthdata)

    # Step 3: Initialize charts
    charts = {}

    # Step 4: Compute
    compute_lagna(charts, birthdata)
    compute_divisional(charts)
    compute_ashtakavarga(charts)
    compute_dasha(charts, birthdata)

    return charts