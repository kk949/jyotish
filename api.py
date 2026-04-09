from fastapi import FastAPI, HTTPException, Response, Query
import swisseph as swe
from pydantic import BaseModel
from typing import Optional, Literal, Dict, Any, List
import json
import os
import tempfile
from datetime import datetime
from database import get_db_connection
from api_logger import log_api_call
from support.kundali_generation import generate_kundali_pdf
import re
import traceback
import jyotishyamitra as jm

# Import jyotichart for chart generation
import jyotichart as chart

# Import dosha calculation modules
from support.dosha_calculator import (calculate_mangal_dosh, calculate_pitra_dosh, calculate_kaalsarp_dosh, calculate_papasamaya)

# Import panchang and horoscope modules
from support.panchang import calculate_panchang
from support.horoscope import (
    generate_daily_horoscope,
    generate_weekly_horoscope,
    generate_monthly_horoscope
)

# Import ALL dasha functions
from support.dashas import (
    getCurrentMahadasha, 
    getCurrentMahaDashaFull, 
    getSpecificDasha,
    getParyantarDasha,
    getMahadashaPredictions,
    getCharDashaCurrent,
    getCharDashaMain,
    getCharDashaSub,
    getYoginiDashaMain,
    getYoginiDashaSub,
    Vimshottari,
    clearDashaDetails
)

import support.mod_astrodata as data
import logging
from logging.handlers import RotatingFileHandler
# with the other imports at the top
from support.ashtakavarga_service import router as ashtaka_router

# Get the directory where api.py is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_dir = os.path.join(BASE_DIR, "logs")

# Create logs folder if it doesn't exist
os.makedirs(log_dir, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, 'api.log'),
            maxBytes=10485760,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Jyotish API",
    description="API for Vedic Astrology calculations including Dashas, Panchang, and Horoscopes",
    version="1.0.0"
)
app.include_router(ashtaka_router)

class BirthData(BaseModel):
    name: str
    gender: str
    place: str
    longitude: str
    latitude: str
    timezone: str
    year: str
    month: str
    day: str
    hour: str
    minute: str
    second: Optional[str] = "0"
    
class ChartRequest(BaseModel):
    chart_type: Literal["north", "south"] = "north"
    chart_name: Optional[str] = "Birth Chart"
    person_name: Optional[str] = ""
    birth_data: Optional[BirthData] = None
    chart_data: Optional[dict] = None
    divisional_chart: Optional[str] = "D1"
    aspect: Optional[bool] = False
    clr_background: Optional[str] = "white"
    clr_outbox: Optional[str] = "yellow"
    clr_line: Optional[str] = "yellow"
    clr_sign: Optional[str] = "white"
    clr_Asc: Optional[str] = "white"
    clr_houses: Optional[list] = None
    planet_colors: Optional[dict] = None
    clr_planets: Optional[dict] = None

class DashaParams(BaseModel):
    """Parameters for Dasha calculations"""
    dob: str  # DD/MM/YYYY
    tob: str  # HH:MM
    lat: float
    lon: float
    tz: float
    lang: Optional[str] = "en"

def prepare_birth_data_for_dasha(dob: str, tob: str, lat: float, lon: float, tz: float):
    """
    Prepare birth data and calculate chart for Dasha calculations
    Returns the division (chart data) and birthdata
    """
    try:
        # Parse date and time
        day, month, year = dob.split('/')
        hour, minute = tob.split(':')
        
        # Input birth data into jyotishyamitra
        jm.input_birthdata(
            name="User",
            gender="Male",
            place="Birth Place",
            longitude=str(lon),
            lattitude=str(lat),
            timezone=str(tz),
            year=year,
            month=month,
            day=day,
            hour=hour,
            min=minute,
            sec="0"
        )
        
        # Validate birth data
        validation_result = jm.validate_birthdata()
        if validation_result != "SUCCESS":
            raise HTTPException(status_code=400, detail=validation_result)
        
        # Get birth data
        birth_data = jm.get_birthdata()
        
        # Generate astrological data
        chart_data = jm.generate_astrologicalData(birth_data, "ASTRODATA_DICTIONARY")
        
        # Clear previous dasha calculations
        clearDashaDetails()
        
        # Calculate Vimshottari Dasha
        Vimshottari(chart_data["D1"], birth_data)
        
        return chart_data["D1"], birth_data
        
    except Exception as e:
        logger.error(f"Error preparing birth data: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error preparing birth data: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Jyotish API with Complete Dasha System, Panchang, and Horoscopes",
        "version": "1.0.0",
        "endpoints": {
            "dasha": {
                "vimshottari": [
                    "/dasha/vimshottari/current",
                    "/dasha/vimshottari/full",
                    "/dasha/vimshottari/all",
                    "/dasha/vimshottari/antardasha",
                    "/dasha/vimshottari/paryantardasha",
                    "/dasha/vimshottari/predictions/{planet}"
                ],
                "chara": [
                    "/dasha/chara/current",
                    "/dasha/chara/main",
                    "/dasha/chara/sub/{sign}"
                ],
                "yogini": [
                    "/dasha/yogini/main",
                    "/dasha/yogini/sub/{lord}"
                ]
            },
            "panchang": [
                "/panchang/daily",
                "/panchang/muhurta"
            ],
            "horoscope": [
                "/horoscope/daily",
                "/horoscope/weekly",
                "/horoscope/monthly"
            ],
            "predictions": [
                "/prediction/daily-nakshatra",
                "/prediction/daily-sun"
            ],
            "dosha": [
                "/mangal-dosh",
                "/pitra-dosh",
                "/kaalsarp-dosha",
                "/papasamaya"
            ]
        }
    }

# =====================================================
# PANCHANG ENDPOINTS
# =====================================================

@app.get("/panchang/daily")
@log_api_call("/panchang/daily")
def get_daily_panchang(
    date: str,
    lat: float,
    lon: float,
    tz: float,
    lang: str = "en",
    api_id: Optional[str] = Query(None)
):
    """
    Get complete daily Panchang
    
    Parameters:
    - date: Date in DD/MM/YYYY format
    - lat: Latitude of location
    - lon: Longitude of location
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Complete Panchang with Tithi, Nakshatra, Yoga, Karana, Vara, and auspicious times
    """
    try:
        logger.info(f"Panchang request: date={date}, lat={lat}, lon={lon}")
        panchang = calculate_panchang(date, lat, lon, tz, lang)
        
        response = {
            "status": 200,
            "response": panchang
        }
        logger.info("Panchang calculated successfully")
        return response
        
    except Exception as e:
        logger.error(f"Panchang error: {str(e)}", exc_info=True)
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Panchang: {str(e)}\n{traceback.format_exc()}"
        )

   
@app.get("/panchang/muhurta")
@log_api_call("/panchang/muhurta")
def get_muhurta_times(
    date: str,
    lat: float,
    lon: float,
    tz: float,
    lang: str = "en",
    api_id: Optional[str] = Query(None)
):
    """
        Get auspicious and inauspicious muhurta times
        
        Parameters:
        - date: Date in DD/MM/YYYY format
        - lat: Latitude of location
        - lon: Longitude of location
        - tz: Timezone offset in hours
        - lang: Language code (default: "en")
        
        Returns:
        - Abhijit Muhurta, Rahu Kaal, and Yamghant Kaal timings
    """
    try:
        logger.info(f"Muhurta request: date={date}, lat={lat}, lon={lon}")
        # First get basic panchang to get sunrise/sunset and vara
        panchang = calculate_panchang(date, lat, lon, tz)
      
        sunrise = panchang["advanced_details"]["sun_rise"]
        sunset = panchang["advanced_details"]["sun_set"]
        vara_num = panchang["day"]["vara_number"]
        
        # Calculate special muhurtas
        abhijit = panchang["advanced_details"]["abhijit_muhurta"]
        rahu_kaal = panchang["rahukaal"]
        yamghant = panchang["yamakanta"]
        gulika = panchang["gulika"]
        response = {
            "status": 200,
            "response": {
                "date": date,
                "sunrise": sunrise,
                "sunset": sunset,
                "auspicious_times": {
                    "abhijit_muhurta": abhijit
                },
                "inauspicious_times": {
                    "rahu_kaal": rahu_kaal,
                    "yamghant_kaal": yamghant,
                    "gulika_kaal": gulika
                }
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Muhurta times: {str(e)}\n{traceback.format_exc()}"
        )

# =====================================================
# HOROSCOPE ENDPOINTS
# =====================================================

@app.get("/horoscope/daily")
@log_api_call("/horoscope/daily")
def get_daily_horoscope_zodiac(
    zodiac: int,
    date: str,
    lang: str = "en",
    api_id: Optional[str] = Query(None)
):
    """
    Get daily horoscope for a zodiac sign
    
    Parameters:
    - zodiac: Zodiac sign number (1-12: Aries to Pisces)
    - date: Date in DD/MM/YYYY format
    - lang: Language code (default: "en")
    
    Returns:
    - Complete daily horoscope with predictions for all life aspects
    """
    try:
        logger.info(f"Horoscope request: zodiac={zodiac}, date={date}")
        horoscope = generate_daily_horoscope(zodiac, date)
        
        # Calculate remaining API calls if api_id provided
        remaining = None
        try:
            if api_id:
                dt = datetime.strptime(date, "%d/%m/%Y")
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
                user = cur.fetchone()
                if user:
                    uid = user[0]
                    today = dt.strftime("%Y-%m-%d")
                    cur.execute(
                        "SELECT COUNT(*) FROM api_logs WHERE user_id = %s AND api_endpoint = %s AND DATE(created_at) = %s",
                        (uid, "/horoscope/daily", today)
                    )
                    used = cur.fetchone()[0]
                    remaining = max(0, 500000 - int(used))
                cur.close()
                conn.close()
        except Exception:
            remaining = 500000
        
        response = {
            "status": 200,
            "response": horoscope,
            "remaining_api_calls": remaining if remaining is not None else 500000
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error generating daily horoscope: {str(e)}\n{traceback.format_exc()}"
        )


@app.get("/horoscope/weekly")
@log_api_call("/horoscope/weekly")
def get_weekly_horoscope_zodiac(
    zodiac: int,
    start_date: str,
    lang: str = "en",
    api_id: Optional[str] = Query(None)
):
    """
    Get weekly horoscope for a zodiac sign
    
    Parameters:
    - zodiac: Zodiac sign number (1-12: Aries to Pisces)
    - start_date: Week start date in DD/MM/YYYY format
    - lang: Language code (default: "en")
    
    Returns:
    - Weekly horoscope with overview and key themes
    """
    try:
        logger.info(f"Weekly horoscope request: zodiac={zodiac}, start_date={start_date}")
        horoscope = generate_weekly_horoscope(zodiac, start_date)
        
        response = {
            "status": 200,
            "response": horoscope
        }
        
        logger.info("Weekly horoscope calculated successfully")
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Weekly horoscope error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating weekly horoscope: {str(e)}\n{traceback.format_exc()}"
        )


@app.get("/horoscope/monthly")
@log_api_call("/horoscope/monthly")
def get_monthly_horoscope_zodiac(
    zodiac: int,
    month: int,
    year: int,
    lang: str = "en",
    api_id: Optional[str] = Query(None)
):
    """
    Get monthly horoscope for a zodiac sign
    
    Parameters:
    - zodiac: Zodiac sign number (1-12: Aries to Pisces)
    - month: Month number (1-12)
    - year: Year
    - lang: Language code (default: "en")
    
    Returns:
    - Monthly horoscope with themes and week-by-week breakdown
    """
    try:
        logger.info(f"Monthly horoscope request: zodiac={zodiac}, month={month}, year={year}")
        horoscope = generate_monthly_horoscope(zodiac, month, year)
        
        response = {
            "status": 200,
            "response": horoscope
        }
        
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Monthly horoscope error: {str(e)}", exc_info=True)   
        raise HTTPException(
            status_code=500,
            detail=f"Error generating monthly horoscope: {str(e)}\n{traceback.format_exc()}"
        )

# =====================================================
# VIMSHOTTARI DASHA ENDPOINTS
# =====================================================

@app.get("/dasha/vimshottari/current")
@log_api_call("/dasha/vimshottari/current")
def get_current_vimshottari_dasha(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get current running Vimshottari Mahadasha
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Current Mahadasha lord and predictions
    """
    try:
        logger.info(f"Vimshottari Dasha request: dob={dob}, tob={tob}, lat={lat}, lon={lon}, tz={tz}")
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        current_dasha = getCurrentMahadasha()
        
        response = {
            "status": 200,
            "response": {
                "current_mahadasha": current_dasha,
                "calculation_date": str(datetime.now())
            }
        }
        
        logger.info("Vimshottari Dasha calculated successfully")    
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500, 
            detail=f"Error calculating current Vimshottari Dasha: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/full")
@log_api_call("/dasha/vimshottari/full")
def get_full_current_mahadasha(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get complete details of current Vimshottari Mahadasha including dates, duration, and age
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Complete current Mahadasha details with predictions
    """
    try:
        logger.info(f"Full Vimshottari Dasha request: dob={dob}, tob={tob}, lat={lat}, lon={lon}, tz={tz}")
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        current_dasha_full = getCurrentMahaDashaFull()
        
        response = {
            "status": 200,
            "response": {
                "current_mahadasha": current_dasha_full,
                "calculation_date": str(datetime.now())
            }
        }
        
        logger.info("Full Vimshottari Dasha calculated successfully")    
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating full current Mahadasha: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/all")
@log_api_call("/dasha/vimshottari/all")
def get_all_mahadashas(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get all Vimshottari Mahadashas from birth
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - All Mahadashas with complete details
    """
    try:
        logger.info(f"Vimshottari Dasha request: dob={dob}, tob={tob}, lat={lat}, lon={lon}, tz={tz}")
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        all_mahadashas = data.charts["Dashas"]["Vimshottari"]["mahadashas"]
        current_dasha = data.charts["Dashas"]["Vimshottari"]["current"]
        
        response = {
            "status": 200,
            "response": {
                "all_mahadashas": all_mahadashas,
                "current": current_dasha,
                "total_cycle_years": 120,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating all Mahadashas: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/antardasha")
@log_api_call("/dasha/vimshottari/antardasha")
def get_antardashas(dob: str, tob: str, lat: float, lon: float, tz: float, 
                    mahadasha_lord: Optional[str] = None, lang: str = "en", api_id: str = None):
    """
    Get Antardashas (sub-periods) for a specific Mahadasha or current Mahadasha
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - mahadasha_lord: Specific Mahadasha lord (optional, defaults to current)
    - lang: Language code (default: "en")
    
    Returns:
    - Antardashas for the specified Mahadasha
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        if not mahadasha_lord:
            mahadasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
        
        # Get all antardashas for this mahadasha lord
        antardashas = {}
        all_antardashas = data.charts["Dashas"]["Vimshottari"]["antardashas"]
        
        for key, value in all_antardashas.items():
            if key.startswith(f"{mahadasha_lord}-"):
                antardashas[key] = value
        
        response = {
            "status": 200,
            "response": {
                "mahadasha_lord": mahadasha_lord,
                "antardashas": antardashas,
                "current_antardasha": data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"],
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Antardashas: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/paryantardasha")
@log_api_call("/dasha/vimshottari/paryantardasha")
def get_paryantardashas(dob: str, tob: str, lat: float, lon: float, tz: float,
                        mahadasha_lord: Optional[str] = None,
                        antardasha_lord: Optional[str] = None,
                        lang: str = "en", api_id: str = None):
    """
    Get Paryantardashas (sub-sub-periods) for a specific Mahadasha-Antardasha combination
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - mahadasha_lord: Specific Mahadasha lord (optional, defaults to current)
    - antardasha_lord: Specific Antardasha lord (optional, defaults to current)
    - lang: Language code (default: "en")
    
    Returns:
    - Paryantardashas for the specified period
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        if not mahadasha_lord:
            mahadasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
        if not antardasha_lord:
            antardasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"]
            
        paryantardashas = getParyantarDasha(mahadasha_lord, antardasha_lord)
        
        response = {
            "status": 200,
            "response": {
                "mahadasha_lord": mahadasha_lord,
                "antardasha_lord": antardasha_lord,
                "paryantardashas": paryantardashas,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Paryantardashas: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/predictions/{planet}")
@log_api_call("/dasha/vimshottari/predictions/{planet}")
def get_planet_predictions(planet: str, api_id: str = None):
    """
    Get predictions, remedies, and guidance for a specific planet's Mahadasha
    
    Parameters:
    - planet: Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
    
    Returns:
    - Predictions, favorable activities, challenges, and remedies
    """
    try:
        valid_planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        
        if planet not in valid_planets:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid planet. Valid planets are: {', '.join(valid_planets)}"
            )
        
        predictions = getMahadashaPredictions(planet)
        
        response = {
            "status": 200,
            "response": {
                "planet": planet,
                "predictions": predictions
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error getting predictions: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/vimshottari/specific/{planet}")
@log_api_call("/dasha/vimshottari/specific/{planet}")
def get_specific_planet_dasha(planet: str, dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get details for a specific planet's Mahadasha
    
    Parameters:
    - planet: Planet name (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu)
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Complete details for the specified planet's Mahadasha
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        specific_dasha = getSpecificDasha(planet)
        
        response = {
            "status": 200,
            "response": {
                "planet": planet,
                "dasha_details": specific_dasha,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error getting specific Dasha: {str(e)}\n{traceback.format_exc()}"
        )

# =====================================================
# CHARA DASHA ENDPOINTS (Jaimini System)
# =====================================================
@app.get("/dasha/chara/current")
@log_api_call("/dasha/chara/current")
def get_current_chara_dasha(dob: str, tob: str, lat: float, lon: float, tz: float, api_id: str = None, lang: str = "en"):
    """
    Get current Chara Dasha (Jaimini System)
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Current Chara Dasha sign and remaining years
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        current_chara = getCharDashaCurrent(division, birth_data)
        
        response = {
            "status": 200,
            "response": {
                "current_chara_dasha": division,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating current Chara Dasha: {str(e)}\n{traceback.format_exc()}"
        )


@app.get("/dasha/chara/main")
@log_api_call("/dasha/chara/main")
def get_chara_dasha_main(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get all main Chara Dasha periods (12 signs)
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - All Chara Dasha main periods with dates and durations
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        main_chara = getCharDashaMain(division, birth_data)
        
        # Convert datetime objects to strings
        for period in main_chara:
            period['start_date'] = str(period['start_date'])
            period['end_date'] = str(period['end_date'])
        
        response = {
            "status": 200,
            "response": {
                "chara_dasha_main_periods": main_chara,
                "total_periods": len(main_chara),
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Chara Dasha main periods: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/chara/sub/{sign}")
@log_api_call("/dasha/chara/sub/{sign}")
def get_chara_dasha_sub(sign: str, dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get sub-periods for a specific Chara Dasha sign
    
    Parameters:
    - sign: Zodiac sign (Aries, Taurus, Gemini, etc.)
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Sub-periods for the specified Chara Dasha sign
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        sub_chara = getCharDashaSub(division, birth_data, sign)
        
        # Convert datetime objects to strings if present
        if isinstance(sub_chara, list):
            for period in sub_chara:
                if 'start_date' in period:
                    period['start_date'] = str(period['start_date'])
                if 'end_date' in period:
                    period['end_date'] = str(period['end_date'])
        
        response = {
            "status": 200,
            "response": {
                "main_sign": sign,
                "sub_periods": sub_chara,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Chara Dasha sub-periods: {str(e)}\n{traceback.format_exc()}"
        )

# =====================================================
# YOGINI DASHA ENDPOINTS
# =====================================================

@app.get("/dasha/yogini/main")
@log_api_call("/dasha/yogini/main")
def get_yogini_dasha_main(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get all main Yogini Dasha periods (8 Yoginis)
    
    Parameters:
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - All Yogini Dasha main periods with deities and elements
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        main_yogini = getYoginiDashaMain(division, birth_data)
        
        # Convert datetime objects to strings
        for period in main_yogini:
            period['start_date'] = str(period['start_date'])
            period['end_date'] = str(period['end_date'])
        
        response = {
            "status": 200,
            "response": {
                "yogini_dasha_main_periods": main_yogini,
                "total_periods": len(main_yogini),
                "total_cycle_years": 36,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Yogini Dasha main periods: {str(e)}\n{traceback.format_exc()}"
        )

@app.get("/dasha/yogini/sub/{lord}")
@log_api_call("/dasha/yogini/sub/{lord}")
def get_yogini_dasha_sub(lord: str, dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """
    Get sub-periods for a specific Yogini Dasha lord
    
    Parameters:
    - lord: Yogini lord (Mangala, Sasi, Ravi, Budha, Shukra, Kuja, Guru, Shani)
    - dob: Date of birth in DD/MM/YYYY format
    - tob: Time of birth in HH:MM format
    - lat: Latitude of birth place
    - lon: Longitude of birth place
    - tz: Timezone offset in hours
    - lang: Language code (default: "en")
    
    Returns:
    - Sub-periods for the specified Yogini lord
    """
    try:
        division, birth_data = prepare_birth_data_for_dasha(dob, tob, lat, lon, tz)
        
        sub_yogini = getYoginiDashaSub(division, birth_data, lord)
        
        # Convert datetime objects to strings if present
        if isinstance(sub_yogini, list):
            for period in sub_yogini:
                if 'start_date' in period:
                    period['start_date'] = str(period['start_date'])
                if 'end_date' in period:
                    period['end_date'] = str(period['end_date'])
        
        response = {
            "status": 200,
            "response": {
                "main_lord": lord,
                "sub_periods": sub_yogini,
                "calculation_date": str(datetime.now())
            }
        }
        
        return response
        
    except Exception as e:
        import traceback
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating Yogini Dasha sub-periods: {str(e)}\n{traceback.format_exc()}"
        )

# =====================================================
# DOSHA ENDPOINTS
# =====================================================

@app.get("/pitra-dosh")
@log_api_call("/pitra-dosh")
def get_pitra_dosha(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """Get Pitra Dosha analysis based on birth details"""
    try:
        pitra_dosha_result = calculate_pitra_dosh(dob, tob, lat, lon, tz, lang)
        
        response = {
            "status": 200,
            "response": pitra_dosha_result
        }
        
        return response
    except Exception as e:
        import traceback
        error_detail = f"Error calculating Pitra Dosha: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/kaalsarp-dosha")
@log_api_call("/kaalsarp-dosha")
def get_kaalsarp_dosha(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """Get Kaalsarp Dosha analysis based on birth details"""
    try:
        kaalsarp_dosha_result = calculate_kaalsarp_dosh(dob, tob, lat, lon, tz, lang)
        
        response = {
            "status": 200,
            "response": kaalsarp_dosha_result
        }
        
        return response
    except Exception as e:
        import traceback
        error_detail = f"Error calculating Kaalsarp Dosha: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/papasamaya")
@log_api_call("/papasamaya")
def get_papasamaya(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """Get Papasamaya (Inauspicious Time) analysis based on birth details"""
    try:
        papasamaya_result = calculate_papasamaya(dob, tob, lat, lon, tz, lang)
        
        response = {
            "status": 200,
            "response": papasamaya_result
        }
        
        return response
    except Exception as e:
        import traceback
        error_detail = f"Error calculating Papasamaya: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/mangal-dosh")
@log_api_call("/mangal-dosh")
def get_mangal_dosh(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en", api_id: str = None):
    """Get Mangal Dosha analysis based on birth details"""
    try:
        mangal_dosh_result = calculate_mangal_dosh(dob, tob, lat, lon, tz, lang)
        
        logger.info(f"Mangal Dosha calculation successful for dob={dob}, tob={tob}, lat={lat}, lon={lon}, tz={tz}, lang={lang}")
        
        response = {
            "status": 200,
            "response": mangal_dosh_result
        }
        
        return response
    except Exception as e:
        logger.error(f"Error calculating Mangal Dosha: {str(e)}\n{traceback.format_exc()}")
        import traceback
        error_detail = f"Error calculating Mangal Dosha: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

# =====================================================
# PREDICTION ENDPOINTS
# =====================================================

@app.get("/prediction/daily-nakshatra")
@log_api_call("/prediction/daily-nakshatra")
def get_daily_nakshatra_prediction(
    nakshatra: int,
    dob: str,
    api_id: Optional[str] = Query(None, alias="api_key"),
    lang: str = "en"
):
    try:
        dt = datetime.strptime(dob, "%d/%m/%Y")
        if nakshatra < 1 or nakshatra > 27:
            raise HTTPException(status_code=400, detail="Invalid nakshatra")

        names = [
            "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
            "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purvaphalguni", "Uttaraphalguni",
            "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Mula",
            "Purvashadha", "Uttarashadha", "Sravana", "Dhanista", "Shatabhisha",
            "Purvabhadra", "Uttarabhadra", "Revati"
        ]
        nname = names[nakshatra - 1]

        color_map = [
            ("pale-red", "#FFB8BE"), ("saffron", "#F4C430"), ("white", "#FFFFFF"), ("silver", "#C0C0C0"),
            ("green", "#008000"), ("blue", "#0000FF"), ("gold", "#FFD700"), ("yellow", "#FFFF00"),
            ("purple", "#800080"), ("maroon", "#800000"), ("pink", "#FFC0CB"), ("orange", "#FFA500"),
            ("teal", "#008080"), ("navy", "#000080"), ("brown", "#A52A2A"), ("olive", "#808000"),
            ("indigo", "#4B0082"), ("cyan", "#00FFFF"), ("magenta", "#FF00FF"), ("violet", "#EE82EE"),
            ("beige", "#F5F5DC"), ("coral", "#FF7F50"), ("khaki", "#F0E68C"), ("lavender", "#E6E6FA"),
            ("salmon", "#FA8072"), ("turquoise", "#40E0D0"), ("black", "#000000")
        ]
        lucky_color, lucky_color_code = color_map[nakshatra - 1]

        import random
        random.seed(f"{nakshatra}-{dob}-{lang}")
        lucky_number = [random.randint(1, 40), random.randint(1, 40)]

        msgs: Dict[str, str] = {
            "physique": "A sublime aura will envelop you, making your presence enchanting and unforgettable wherever you go.",
            "status": "Kindness and consideration will mark your words in all interactions, shaping you into an influential figure admired for your character.",
            "finances": "Exercise utmost caution in money transactions to avoid falling victim to fraudulent schemes that could compromise your finances.",
            "relationship": "You'll fulfill promises made and make an enduring mark on your partner's heart. Your genuine commitment will leave a lasting impression, solidifying your special place in their life.",
            "career": "Given your business's consistent growth and increased stocks, consider adding new shareholders to bolster your stake and capitalize on expanding opportunities.",
            "travel": "You might have been feeling the need of moving from your old house to a new house. This day brings you the perfect opportunity for booking your a new apartment.",
            "family": "Travel and journeys will bring prosperity. Consider embarking on a family trip to strengthen bonds with your spouse and children, fostering cherished memories.",
            "friends": "Distinguishing between true friends and those who merely seek personal gain will enable you to prune your social circle.",
            "health": "Exercise vigilance concerning your father's health, particularly in the realm of respiratory health. Early consultation with a doctor will help avert potential issues.",
            "total_score": "Anticipate a day of discovery and enrichment. Engage in self-reflection and exploration, discovering new interests and hobbies that enrich your life with joy and satisfaction."
        }

        scores = {
            "physique": random.randint(60, 85),
            "status": random.randint(80, 99),
            "finances": random.randint(60, 80),
            "relationship": random.randint(70, 90),
            "career": random.randint(60, 80),
            "travel": random.randint(70, 90),
            "family": random.randint(70, 90),
            "friends": random.randint(70, 90),
            "health": random.randint(50, 70),
            "total_score": random.randint(80, 95)
        }

        bot_response = {k: {"score": scores[k], "split_response": msgs[k]} for k in msgs}

        remaining = None
        try:
            if api_id:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
                user = cur.fetchone()
                if user:
                    uid = user[0]
                    today = dt.strftime("%Y-%m-%d")
                    cur.execute(
                        "SELECT COUNT(*) FROM api_logs WHERE user_id = %s AND api_endpoint = %s AND DATE(created_at) = %s",
                        (uid, "/prediction/daily-nakshatra", today)
                    )
                    used = cur.fetchone()[0]
                    remaining = max(0, 500000 - int(used))
                cur.close()
                conn.close()
        except Exception:
            remaining = 500000

        response = {
            "status": 200,
            "response": {
                "lucky_color": lucky_color,
                "lucky_color_code": lucky_color_code,
                "lucky_number": lucky_number,
                "bot_response": bot_response,
                "nakshatra": nname.lower()
            },
            "remaining_api_calls": remaining if remaining is not None else 500000
        }

        return response
    except Exception as e:
        import traceback
        error_detail = f"Error generating daily nakshatra prediction: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.get("/prediction/daily-sun")
@log_api_call("/prediction/daily-sun")
def get_daily_sun_prediction(
    zodiac: int,
    date: str,
    api_id: Optional[str] = Query(None, alias="api_key"),
    lang: str = "en",
    split: bool = False,
    prediction_type: Literal["big", "small"] = Query("big", alias="type")
):
    try:
        dt = datetime.strptime(date, "%d/%m/%Y")
        if zodiac < 1 or zodiac > 12:
            raise HTTPException(status_code=400, detail="Invalid zodiac")

        zodiac_names = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        zname = zodiac_names[zodiac - 1]

        lucky_colors = {
            "Aries": [("Red", "#FF0000"), ("Orange", "#FFA500"), ("White", "#FFFFFF")],
            "Taurus": [("Green", "#008000"), ("Pink", "#FFC0CB"), ("White", "#FFFFFF")],
            "Gemini": [("Yellow", "#FFFF00"), ("Green", "#008000"), ("Orange", "#FFA500")],
            "Cancer": [("White", "#FFFFFF"), ("Silver", "#C0C0C0"), ("Cream", "#FFFDD0")],
            "Leo": [("Gold", "#FFD700"), ("Orange", "#FFA500"), ("Red", "#FF0000")],
            "Virgo": [("Green", "#008000"), ("Brown", "#A52A2A"), ("White", "#FFFFFF")],
            "Libra": [("Blue", "#0000FF"), ("Pink", "#FFC0CB"), ("White", "#FFFFFF")],
            "Scorpio": [("Red", "#FF0000"), ("Black", "#000000"), ("Maroon", "#800000")],
            "Sagittarius": [("Purple", "#800080"), ("Blue", "#0000FF"), ("Yellow", "#FFFF00")],
            "Capricorn": [("Black", "#000000"), ("Brown", "#A52A2A"), ("Grey", "#808080")],
            "Aquarius": [("Blue", "#0000FF"), ("Silver", "#C0C0C0"), ("Grey", "#808080")],
            "Pisces": [("Sea Green", "#2E8B57"), ("Purple", "#800080"), ("White", "#FFFFFF")]
        }

        horoscope_templates = {
            "physique": [
                "Expect accolades for your choice of attire, as your outfits will reflect your sophisticated taste and enhance your natural allure.",
                "Your energy levels are high today, making it a perfect time to focus on your fitness goals and self-care routines.",
                "People will notice your radiant appearance today. Your natural charm will be at its peak, attracting positive attention.",
                "Consider trying a new look or style today. Your confidence will shine through any changes you make to your appearance.",
                "Your physical presence will command attention today. Take pride in your appearance and let your inner confidence show."
            ],
            "status": [
                "Expect increased dealings; exercise care while negotiating rents and agreements to ensure favorable outcomes.",
                "Your reputation will grow stronger today. People in positions of authority will take notice of your achievements.",
                "Social standing improves as you make valuable connections. Network strategically to maximize opportunities.",
                "Recognition for your hard work is coming. Be prepared to accept praise graciously and leverage it for future success.",
                "Your influence expands today. Use your growing status wisely to help others and advance your own goals."
            ],
            "finances": [
                "Prepare for unexpected prosperity as someone might bequeath a substantial inheritance, propelling you into wealth and abundance.",
                "Financial opportunities knock at your door. Stay alert for investment prospects that align with your long-term goals.",
                "Money matters stabilize today. It's a good time to review your budget and make strategic financial decisions.",
                "Unexpected income may arrive from past investments or forgotten sources. Keep your financial records organized.",
                "Consider consulting a financial advisor today. Important decisions regarding money will have lasting impacts."
            ],
            "relationship": [
                "Estranged relations, including ex-partners and adversaries, may seek reconciliation. Even former foes will approach you voluntarily, opening avenues for healing conversations.",
                "Deep connections strengthen today. Spend quality time with loved ones to nurture your most important relationships.",
                "Communication flows easily in romantic matters. Express your feelings openly and listen with an open heart.",
                "Past misunderstandings may be resolved today. Approach reconciliation with patience and genuine understanding.",
                "Your emotional intelligence is heightened. Use this to navigate complex relationship dynamics with grace."
            ],
            "career": [
                "Innovative ideas will flow effortlessly, driven by your sharp intellect. Your introduction of novel concepts in your profession will garner widespread appreciation.",
                "Leadership opportunities emerge today. Step up and showcase your abilities to guide others toward success.",
                "Collaboration brings exceptional results. Work closely with colleagues to achieve breakthrough outcomes.",
                "Your expertise will be recognized by superiors. Prepare for new responsibilities that advance your career trajectory.",
                "Strategic thinking pays off today. Long-term planning and careful execution will yield impressive professional gains."
            ],
            "travel": [
                "You will have friends come over to your place with a car, with which you might want to take a short travel. If done, you will cherish as memories after a long time.",
                "Wanderlust strikes today. Even a short journey will refresh your spirit and provide new perspectives.",
                "Travel plans made today will be fortunate. Whether for business or pleasure, movement brings positive changes.",
                "Local explorations yield unexpected discoveries. Take time to appreciate the beauty in your immediate surroundings.",
                "If considering a trip, today favors planning and booking. Your choices will lead to memorable experiences."
            ],
            "family": [
                "If you've been considering purchasing a budget-friendly vehicle, today might be the ideal day to make that investment in your own mode of transportation.",
                "Family harmony prevails today. Gatherings will be joyful and strengthen bonds between generations.",
                "A family member may seek your advice. Your wisdom and experience will provide valuable guidance.",
                "Domestic matters require attention today. Addressing home improvements or family concerns will bring satisfaction.",
                "Celebrate family achievements today. Acknowledging each other's successes strengthens your collective bond."
            ],
            "friends": [
                "A time for forgiveness and reconciliation is upon you. Even adversaries might put past differences behind and extend the hand of friendship.",
                "Social circles expand today. New friendships formed now have the potential to become lifelong connections.",
                "Friends provide unexpected support today. Don't hesitate to reach out when you need assistance or companionship.",
                "Your social calendar fills with exciting invitations. Choose activities that truly align with your interests.",
                "Be the friend you wish to have. Your generosity and kindness will be returned manifold by your social circle."
            ],
            "health": [
                "Women may experience significant stomach pains today; avoid lifting heavy objects or engaging in physically demanding tasks.",
                "Energy levels fluctuate today. Listen to your body's signals and rest when needed to maintain optimal health.",
                "Mental health takes priority today. Practice mindfulness, meditation, or other stress-reducing activities.",
                "Dietary choices impact your wellbeing significantly today. Choose nourishing foods that support your body's needs.",
                "Physical activity brings unexpected benefits today. Even moderate exercise will boost your mood and vitality."
            ],
            "total_score": [
                "A special day unfolds, marked by forging beneficial connections. Triumph over challenges and make lasting impressions on those who cross your path, enhancing your future endeavors.",
                "The stars align favorably for you today. Embrace opportunities with confidence and trust in your abilities to succeed.",
                "Balance and harmony characterize your day. Navigate challenges with grace and celebrate victories with gratitude.",
                "Your positive energy attracts favorable outcomes today. Maintain an optimistic outlook and watch opportunities multiply.",
                "Today marks a significant point in your journey. The decisions you make now will have lasting positive impacts."
            ]
        }

        swe.set_ephe_path('.')
        jd = swe.julday(dt.year, dt.month, dt.day, 12.0)
        sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
        moon_pos = swe.calc_ut(jd, swe.MOON)[0][0]

        import random
        seed_base = f"{dt.strftime('%Y-%m-%d')}-{zname}"
        random.seed(seed_base)

        aspect = abs((sun_pos - moon_pos + 180) % 360 - 180)
        aspect_strength = 100 - (aspect / 180 * 100)

        scores = {
            "physique": int(40 + aspect_strength * 0.3 + random.randint(0, 30)),
            "status": int(50 + aspect_strength * 0.4 + random.randint(0, 30)),
            "finances": int(50 + aspect_strength * 0.35 + random.randint(0, 30)),
            "relationship": int(45 + aspect_strength * 0.4 + random.randint(0, 30)),
            "career": int(55 + aspect_strength * 0.35 + random.randint(0, 30)),
            "travel": int(50 + aspect_strength * 0.3 + random.randint(0, 30)),
            "family": int(50 + aspect_strength * 0.35 + random.randint(0, 30)),
            "friends": int(50 + aspect_strength * 0.35 + random.randint(0, 30)),
            "health": int(40 + aspect_strength * 0.25 + random.randint(0, 35))
        }
        scores["total_score"] = sum(scores.values()) // len(scores)

        colors = lucky_colors.get(zname, [("White", "#FFFFFF")])
        color_idx = hash(seed_base) % len(colors)
        lc_name, lc_code = colors[color_idx]

        random.seed(hash(seed_base) % 10000)
        lucky_number = sorted(random.sample(range(1, 100), 2))

        random.seed(hash(seed_base) % 1000)
        bot_response = {}
        for cat, templates in horoscope_templates.items():
            txt = random.choice(templates)
            if prediction_type == "small":
                txt = txt.split(".")[0] + "."
            bot_response[cat] = {"score": scores[cat], "split_response": txt}

        remaining = None
        try:
            if api_id:
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute("SELECT id FROM users WHERE app_id = %s", (api_id,))
                user = cur.fetchone()
                if user:
                    uid = user[0]
                    today = dt.strftime("%Y-%m-%d")
                    cur.execute(
                        "SELECT COUNT(*) FROM api_logs WHERE user_id = %s AND api_endpoint = %s AND DATE(created_at) = %s",
                        (uid, "/prediction/daily-sun", today)
                    ) 
                    used = cur.fetchone()[0]
                    remaining = max(0, 500000 - int(used))
                cur.close()
                conn.close()
        except Exception:
            remaining = 500000

        response = {
            "status": 200,
            "response": {
                "lucky_color": lc_name.lower(),
                "lucky_color_code": lc_code,
                "lucky_number": lucky_number,
                "bot_response": bot_response,
                "zodiac": zname
            },
            "remaining_api_calls": remaining if remaining is not None else 500000
        }

        return response
    except Exception as e:
        import traceback
        error_detail = f"Error generating daily sun prediction: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

# =====================================================
# PDF GENERATION ENDPOINT
# =====================================================

def _slugify_name(name: str) -> str:
    import re
    s = re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
    return s.lower()

@app.post("/pdf/kundali")
@log_api_call("/pdf/kundali")
def create_kundali_pdf(
    name: str,
    dob: str,  # DD/MM/YYYY
    tob: str,  # HH:MM
    tz: float,
    place: str,
    lat: float,
    lon: float
):
    try:
        try:
            day, month, year = [int(x) for x in dob.split('/')]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid dob format, expected DD/MM/YYYY")

        ts = datetime.now().strftime('%Y%m%d%H%M%S')
        name_slug = _slugify_name(name)
        fname = f"{name_slug}_{ts}.pdf"
        output_path = os.path.join(os.getcwd(), fname)

        generate_kundali_pdf(name, day, month, year, tob, tz, place, lat, lon, output_path)

        full_path = os.path.abspath(output_path)
        return {
            "status": 200,
            "url": full_path
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        raise HTTPException(status_code=500, detail=f"Error generating Kundali PDF: {str(e)}\n{traceback.format_exc()}")

# =====================================================
# CHART ENDPOINTS
# =====================================================

@app.post("/chart/{chart_type}")
def get_divisional_chart(
    chart_type: str,
    data: BirthData = None,
    chart_data: dict = None,
    chart_style: Literal["north", "south"] = "north",
    chart_name: str = "Birth Chart",
    person_name: str = "",
    aspect: bool = True,
    clr_background: str = "black",
    clr_outbox: str = "red",
    clr_line: str = "yellow",
    clr_sign: str = "pink",
    clr_Asc: str = "pink",
    clr_houses: list = None
):
    """Generate a specific divisional chart (D1, D2, D3, etc.) in SVG format."""
    request = ChartRequest(
        chart_type=chart_style,
        chart_name=chart_name,
        person_name=person_name,
        birth_data=data,
        chart_data=chart_data,
        divisional_chart=chart_type.upper(),
        aspect=aspect,
        clr_background=clr_background,
        clr_outbox=clr_outbox,
        clr_line=clr_line,
        clr_sign=clr_sign,
        clr_Asc=clr_Asc,
        clr_houses=clr_houses
    )
    
    return generate_chart(request)

@app.get('/chart')
def get_chart(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en"):
    """Get Jyotichart based on birth details"""
    try:
        chart_result = calculate_chart(dob, tob, lat, lon, tz, lang)
        
        response = {
            "status": 200,
            "response": chart_result    
        }
        
        return response
    except Exception as e:
        import traceback
        error_detail = f"Error calculating Jyotichart: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/calculate")
def calculate_chart(data: BirthData):
    """Calculate astrological chart from birth data"""
    validation_result = jm.input_birthdata(
        name=data.name,
        gender=data.gender,
        place=data.place,
        longitude=data.longitude,
        lattitude=data.latitude,
        timezone=data.timezone,
        year=data.year,
        month=data.month,
        day=data.day,
        hour=data.hour,
        min=data.minute,
        sec=data.second
    )
    
    validation_result = jm.validate_birthdata()
    if validation_result != "SUCCESS":
        raise HTTPException(status_code=400, detail=validation_result)
    
    temp_output_file = "temp_output.json"
    current_dir = os.getcwd()
    jm.set_output(current_dir, "temp_output")
    
    result = jm.generate_astrologicalData(jm.get_birthdata())
    
    try:
        output_file_path = os.path.join(current_dir, temp_output_file)
        with open(output_file_path, "r") as f:
            chart_data = json.load(f)
        
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
            
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chart: {str(e)}")


@app.post("/generate-chart")
def generate_chart(request: ChartRequest):
    """Generate an astrological chart in SVG format."""

    # -----------------------------
    # ✅ Helper: Fix color format
    # -----------------------------
    def fix_color(color):
        if not color:
            return color

        color = str(color).strip()

        # Allow named colors
        named_colors = [
            "black", "white", "red", "blue", "green", "yellow",
            "gray", "grey", "orange", "pink", "purple", "brown"
        ]

        if color.lower() in named_colors:
            return color

        # Add # if missing
        if not color.startswith("#"):
            return f"#{color}"

        return color

    # -----------------------------
    # Validate Input
    # -----------------------------
    if not request.birth_data and not request.chart_data:
        raise HTTPException(status_code=400, detail="Either birth_data or chart_data must be provided")

    if request.birth_data:
        validation_result = jm.input_birthdata(
            name=request.birth_data.name,
            gender=request.birth_data.gender,
            place=request.birth_data.place,
            longitude=request.birth_data.longitude,
            lattitude=request.birth_data.latitude,
            timezone=request.birth_data.timezone,
            year=request.birth_data.year,
            month=request.birth_data.month,
            day=request.birth_data.day,
            hour=request.birth_data.hour,
            min=request.birth_data.minute,
            sec=request.birth_data.second
        )

        validation_result = jm.validate_birthdata()
        if validation_result != "SUCCESS":
            raise HTTPException(status_code=400, detail=validation_result)

        birth_data = jm.get_birthdata()
        chart_data = jm.generate_astrologicalData(birth_data, "ASTRODATA_DICTIONARY")
    else:
        chart_data = request.chart_data

    divisional_chart = request.divisional_chart.upper() if request.divisional_chart else "D1"
    if divisional_chart not in chart_data:
        raise HTTPException(status_code=400, detail=f"Divisional chart {divisional_chart} not found")

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # -----------------------------
            # Create Chart Object
            # -----------------------------
            if request.chart_type == "north":
                chart_obj = chart.NorthChart(request.chart_name, request.person_name, IsFullChart=True)
            else:
                chart_obj = chart.SouthChart(request.chart_name, request.person_name, IsFullChart=True)

            # -----------------------------
            # ✅ Fix Colors BEFORE passing
            # -----------------------------
            house_colors = request.clr_houses if request.clr_houses else ["white"] * 12
            house_colors = [fix_color(c) for c in house_colors]

            clr_background = fix_color(request.clr_background)
            clr_outbox = fix_color(request.clr_outbox)
            clr_line = fix_color(request.clr_line)
            clr_sign = fix_color(request.clr_sign)
            clr_Asc = fix_color(request.clr_Asc)

            # -----------------------------
            # Apply Config
            # -----------------------------
            if request.chart_type == "north":
                chart_obj.updatechartcfg(
                    aspect=request.aspect,
                    clr_background=clr_background,
                    clr_outbox=clr_outbox,
                    clr_line=clr_line,
                    clr_sign=clr_sign,
                    clr_houses=house_colors
                )
            else:
                chart_obj.updatechartcfg(
                    aspect=request.aspect,
                    clr_background=clr_background,
                    clr_outbox=clr_outbox,
                    clr_line=clr_line,
                    clr_Asc=clr_Asc,
                    clr_houses=house_colors
                )

            # -----------------------------
            # Set Ascendant
            # -----------------------------
            lagna_sign = get_sign_name(chart_data[divisional_chart]["ascendant"]["sign"])
            chart_obj.set_ascendantsign(lagna_sign)

            # -----------------------------
            # Add Planets
            # -----------------------------
            for planet_name, planet_data in chart_data[divisional_chart]["planets"].items():
                if planet_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                    house_num = get_house_number(
                        planet_data["sign"],
                        chart_data[divisional_chart]["ascendant"]["sign"]
                    )
                    is_retrograde = planet_data.get("retrograde", False)

                    request_planet_colors = getattr(request, "planet_colors", None) or getattr(request, "clr_planets", None)
                    planet_color = (
                        request_planet_colors.get(planet_name)
                        if isinstance(request_planet_colors, dict)
                        else planet_data.get("color")
                    ) or "black"

                    chart_obj.add_planet(
                        planet=planet_name,
                        symbol=planet_name[:2],
                        housenum=house_num,
                        retrograde=is_retrograde,
                        colour=planet_color
                    )

            # -----------------------------
            # Draw SVG
            # -----------------------------
            chart_obj.draw(temp_dir, "chart")
            svg_path = os.path.join(temp_dir, "chart.svg")

            # -----------------------------
            # Read SVG
            # -----------------------------
            svg_content = None
            encodings = ['utf-8', 'utf-16', 'utf-16-le', 'utf-16-be', 'latin-1']

            for encoding in encodings:
                try:
                    with open(svg_path, "r", encoding=encoding) as f:
                        svg_content = f.read()
                    if svg_content and ('<svg' in svg_content.lower()):
                        break
                except:
                    continue

            if not svg_content:
                with open(svg_path, "rb") as f:
                    return Response(
                        content=f.read(),
                        media_type="image/svg+xml"
                    )

            svg_content = svg_content.strip()

            # -----------------------------
            # ✅ FINAL FIX (IMPORTANT)
            # Fix missing # in SVG itself
            # -----------------------------
            svg_content = re.sub(r'(?<=fill:)([0-9a-fA-F]{6})', r'#\1', svg_content)
            svg_content = re.sub(r'(?<=stroke:)([0-9a-fA-F]{6})', r'#\1', svg_content)

            # Ensure XML header
            if not svg_content.startswith("<?xml"):
                svg_content = '<?xml version="1.0" encoding="UTF-8"?>\n' + svg_content

            # -----------------------------
            # Return Response
            # -----------------------------
            return Response(
                content=svg_content,
                media_type="image/svg+xml",
                headers={
                    "Content-Disposition": "inline; filename=chart.svg",
                    "Cache-Control": "no-cache"
                }
            )

        except Exception as e:
            import traceback
            raise HTTPException(
                status_code=500,
                detail=f"{str(e)}\n{traceback.format_exc()}"
            )

def get_sign_name(sign_num):
    """Convert sign number to sign name for jyotichart"""
    signs = {
        1: "Aries",
        2: "Taurus",
        3: "Gemini",
        4: "Cancer",
        5: "Leo",
        6: "Virgo",
        7: "Libra",
        8: "Scorpio",
        9: "Sagittarius",
        10: "Capricorn",
        11: "Aquarius",
        12: "Pisces"
    }
    return signs.get(sign_num, "Aries")

def get_house_number(planet_sign, lagna_sign):
    """Calculate house number based on planet sign and lagna sign"""
    if isinstance(planet_sign, str):
        planet_sign = get_sign_number(planet_sign)
    if isinstance(lagna_sign, str):
        lagna_sign = get_sign_number(lagna_sign)
    
    house = (int(planet_sign) - int(lagna_sign)) % 12
    if house == 0:
        house = 12
    return house

def get_sign_number(sign_name):
    """Convert sign name to sign number for calculations"""
    signs = {
        "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
        "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
        "Sagittarius": 9,  "Capricorn": 10,
        "Aquarius": 11, "Pisces": 12
    }
    return signs.get(sign_name, 1)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)