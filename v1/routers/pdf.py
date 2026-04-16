"""
routers/pdf.py  — PDF generation endpoints
"""
import os
import re
from datetime import datetime
from fastapi import APIRouter, HTTPException
from models.requests import KundaliPdfRequest
from core.exceptions import InvalidBirthDataError
from core.support.kundali_generation import generate_kundali_pdf
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/pdf", tags=["PDF"])


def _slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()


@router.post("/kundali")
def create_kundali_pdf(req: KundaliPdfRequest):
    """
    Generate a Kundali PDF and return its file path.

    Parameters
    ----------
    name  : Person's name
    dob   : Date of birth  DD/MM/YYYY
    tob   : Time of birth  HH:MM
    tz    : Timezone offset in hours
    place : Place of birth
    lat   : Latitude
    lon   : Longitude
    """
    try:
        day, month, year = [int(x) for x in req.dob.split("/")]
    except ValueError:
        raise HTTPException(400, "Invalid dob format — expected DD/MM/YYYY")

    try:
        ts          = datetime.now().strftime("%Y%m%d%H%M%S")
        fname       = f"{_slugify(req.name)}_{ts}.pdf"
        output_path = os.path.join(os.getcwd(), fname)

        generate_kundali_pdf(
            req.name, day, month, year,
            req.tob, req.tz, req.place,
            req.lat, req.lon, output_path,
        )

        return {"status": 200, "url": os.path.abspath(output_path)}

    except InvalidBirthDataError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        import traceback
        raise HTTPException(500, f"Error generating Kundali PDF: {e}\n{traceback.format_exc()}")
