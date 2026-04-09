"""
models/requests.py
------------------
All Pydantic request models used across routers.
Keep these here — never redefine them inside a router file.
"""

from pydantic import BaseModel, field_validator
from typing import Optional, Literal


class BirthData(BaseModel):
    name     : str
    gender   : str
    place    : str
    longitude: str
    latitude : str
    timezone : str
    year     : str
    month    : str
    day      : str
    hour     : str
    minute   : str
    second   : Optional[str] = "0"


class ChartRequest(BaseModel):
    chart_type       : Literal["north", "south"] = "north"
    chart_name       : Optional[str] = "Birth Chart"
    person_name      : Optional[str] = ""
    birth_data       : Optional[BirthData] = None
    chart_data       : Optional[dict] = None
    divisional_chart : Optional[str] = "D1"
    aspect           : Optional[bool] = False
    clr_background   : Optional[str] = "white"
    clr_outbox       : Optional[str] = "yellow"
    clr_line         : Optional[str] = "yellow"
    clr_sign         : Optional[str] = "white"
    clr_Asc          : Optional[str] = "white"
    clr_houses       : Optional[list] = None


class DashaParams(BaseModel):
    dob : str   # DD/MM/YYYY
    tob : str   # HH:MM
    lat : float
    lon : float
    tz  : float
    lang: Optional[str] = "en"


class PanchangParams(BaseModel):
    date: str   # DD/MM/YYYY
    lat : float
    lon : float
    tz  : float
    lang: Optional[str] = "en"


class KundaliPdfRequest(BaseModel):
    name : str
    dob  : str   # DD/MM/YYYY
    tob  : str   # HH:MM
    tz   : float
    place: str
    lat  : float
    lon  : float
