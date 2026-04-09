import swisseph as swe
from datetime import datetime
from typing import Dict, List, Any, Tuple

def calculate_planet_positions(jd: float) -> Dict[str, float]:
    """Calculate positions of all planets needed for dosha calculations"""
    PLANETS = {
        'Sun': swe.SUN,
        'Moon': swe.MOON,
        'Mars': swe.MARS,
        'Mercury': swe.MERCURY,
        'Jupiter': swe.JUPITER,
        'Venus': swe.VENUS,
        'Saturn': swe.SATURN,
        'Rahu': swe.MEAN_NODE,
        'Ketu': swe.MEAN_NODE
    }
    
    planet_positions = {}
    for name, p in PLANETS.items():
        lon = swe.calc_ut(jd, p)[0][0]
        if name == 'Ketu':
            lon = (lon + 180) % 360  # Ketu opposite Rahu
        planet_positions[name] = lon
    
    return planet_positions

def get_house(lon: float, houses: List[float]) -> int:
    """Return house number (1-12) of a planet."""
    for i in range(12):
        start = houses[i]
        end = houses[(i+1) % 12]
        if end < start:
            end += 360
        pos = lon
        if pos < start:
            pos += 360
        if start <= pos < end:
            return i + 1
    return 1  # Default to 1st house if calculation fails

def is_conjunction(lon1: float, lon2: float, orb: float = 10) -> bool:
    """Check if two longitudes are within orb degrees."""
    diff = abs((lon1 - lon2 + 180) % 360 - 180)
    return diff <= orb

def calculate_mangal_dosh(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en") -> Dict[str, Any]:
    """Calculate Mangal Dosh (Manglik Dosha)"""
    try:
        # Parse date and time
        dob_parts = dob.split("/")
        if len(dob_parts) != 3:
            return {"error": "Invalid date format. Use DD/MM/YYYY"}
            
        day, month, year = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
        
        tob_parts = tob.split(":")
        if len(tob_parts) != 2:
            return {"error": "Invalid time format. Use HH:MM"}
            
        hour, minute = int(tob_parts[0]), int(tob_parts[1])
        
        # Calculate Julian Day
        decimal_time = hour + minute / 60.0
        ut_hour = decimal_time - tz
        jd = swe.julday(year, month, day, ut_hour)
        
        # Set ephemeris
        swe.set_ephe_path('.')  # current folder or path to ephemeris files
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)  # Use Lahiri Ayanamsa
        
        # Get planet positions
        planet_positions = calculate_planet_positions(jd)
        
        # Calculate houses
        houses, ascmc = swe.houses(jd, lat, lon, b'P')
        asc_deg = ascmc[0]
        
        # Check Mangal Dosh
        mangal_houses = [1, 2, 4, 7, 8, 12]
        mars_house = get_house(planet_positions['Mars'], houses)
        has_manglik = mars_house in mangal_houses
        
        # Calculate score and factors
        score = 0
        factors = []
        
        if mars_house in [1, 7]:
            score += 5
            factors.append(f"Mars in {mars_house}{'st' if mars_house == 1 else 'th'} house (very strong influence)")
        elif mars_house in [2, 4, 8, 12]:
            score += 3
            factors.append(f"Mars in {mars_house}{'nd' if mars_house == 2 else 'th'} house (moderate influence)")
        
        # Check aspects
        aspect_houses = [(mars_house + h - 1) % 12 + 1 for h in [4, 7, 8]]
        if 1 in aspect_houses:
            score += 2
            factors.append("Mars aspects the 1st house (Ascendant)")
        if 7 in aspect_houses:
            score += 2
            factors.append("Mars aspects the 7th house (Marriage)")
        
        # Check conjunctions with other planets
        for planet in ['Moon', 'Venus', 'Jupiter']:
            if is_conjunction(planet_positions['Mars'], planet_positions[planet]):
                score -= 1
                factors.append(f"Mars conjunct with {planet} (reducing effect)")
        
        # Generate response
        is_dosha_present = score >= 3
        
        if lang.lower() == "hi":
            bot_response = "मंगल दोष आपकी कुंडली में " + ("मौजूद है" if is_dosha_present else "मौजूद नहीं है") + "।"
            if is_dosha_present:
                bot_response += " यह विवाह और दांपत्य जीवन में चुनौतियां ला सकता है। उपाय के लिए विशेषज्ञ से परामर्श करें।"
        else:
            bot_response = "Mangal Dosh is " + ("present" if is_dosha_present else "not present") + " in your horoscope."
            if is_dosha_present:
                bot_response += " This may bring challenges in marriage and marital life. Consult an expert for remedies."
        
        return {
            "factors": factors,
            "is_dosha_present": is_dosha_present,
            "bot_response": bot_response,
            "score": score,
            "mars_house": mars_house
        }
        
    except Exception as e:
        return {"error": str(e)}

def calculate_pitra_dosh(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en") -> Dict[str, Any]:
    """Calculate Pitra Dosh (Ancestral Curse)"""
    try:
        # Parse date and time
        dob_parts = dob.split("/")
        if len(dob_parts) != 3:
            return {"error": "Invalid date format. Use DD/MM/YYYY"}
            
        day, month, year = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
        
        tob_parts = tob.split(":")
        if len(tob_parts) != 2:
            return {"error": "Invalid time format. Use HH:MM"}
            
        hour, minute = int(tob_parts[0]), int(tob_parts[1])
        
        # Calculate Julian Day
        decimal_time = hour + minute / 60.0
        ut_hour = decimal_time - tz
        jd = swe.julday(year, month, day, ut_hour)
        
        # Set ephemeris
        swe.set_ephe_path('.')
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        
        # Get planet positions
        planet_positions = calculate_planet_positions(jd)
        
        # Calculate houses
        houses, ascmc = swe.houses(jd, lat, lon, b'P')
        
        # Check Pitra Dosh
        sun_house = get_house(planet_positions['Sun'], houses)
        sun_lon = planet_positions['Sun']
        rahu_lon = planet_positions['Rahu']
        ketu_lon = planet_positions['Ketu']
        
        malefics = ['Saturn', 'Mars', 'Rahu', 'Ketu']
        afflicted = any(is_conjunction(sun_lon, planet_positions[m]) for m in malefics)
        
        # Main conditions for Pitra Dosh
        condition1 = sun_house == 9 and afflicted
        condition2 = is_conjunction(sun_lon, rahu_lon)
        condition3 = is_conjunction(sun_lon, ketu_lon)
        condition4 = sun_house == 9 and get_house(planet_positions['Saturn'], houses) == 9
        
        has_pitra = condition1 or condition2 or condition3 or condition4
        
        # Calculate score and factors
        score = 0
        factors = []
        
        if condition1:
            score += 5
            factors.append("Sun in 9th house afflicted by malefics")
        if condition2:
            score += 4
            factors.append("Sun conjunct with Rahu")
        if condition3:
            score += 4
            factors.append("Sun conjunct with Ketu")
        if condition4:
            score += 3
            factors.append("Sun and Saturn both in 9th house")
        
        # Check Moon's position
        moon_house = get_house(planet_positions['Moon'], houses)
        if moon_house == 9 and any(is_conjunction(planet_positions['Moon'], planet_positions[m]) for m in malefics):
            score += 2
            factors.append("Moon in 9th house afflicted by malefics")
        
        # Generate response
        is_dosha_present = score >= 3
        
        if lang.lower() == "hi":
            bot_response = "पितृ दोष आपकी कुंडली में " + ("मौजूद है" if is_dosha_present else "मौजूद नहीं है") + "।"
            if is_dosha_present:
                bot_response += " यह पूर्वजों के आशीर्वाद में बाधा डाल सकता है। श्राद्ध और तर्पण जैसे उपाय करने की सलाह दी जाती है।"
        else:
            bot_response = "Pitra Dosh is " + ("present" if is_dosha_present else "not present") + " in your horoscope."
            if is_dosha_present:
                bot_response += " This may cause obstacles in ancestral blessings. Remedies like Shraddha and Tarpan are advised."
        
        return {
            "factors": factors,
            "is_dosha_present": is_dosha_present,
            "bot_response": bot_response,
            "score": score,
            "sun_house": sun_house
        }
        
    except Exception as e:
        return {"error": str(e)}

def calculate_kaalsarp_dosh(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en") -> Dict[str, Any]:
    """Calculate Kaal Sarp Dosh"""
    try:
        # Parse date and time
        dob_parts = dob.split("/")
        if len(dob_parts) != 3:
            return {"error": "Invalid date format. Use DD/MM/YYYY"}
            
        day, month, year = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
        
        tob_parts = tob.split(":")
        if len(tob_parts) != 2:
            return {"error": "Invalid time format. Use HH:MM"}
            
        hour, minute = int(tob_parts[0]), int(tob_parts[1])
        
        # Calculate Julian Day
        decimal_time = hour + minute / 60.0
        ut_hour = decimal_time - tz
        jd = swe.julday(year, month, day, ut_hour)
        
        # Set ephemeris
        swe.set_ephe_path('.')
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        
        # Get planet positions
        planet_positions = calculate_planet_positions(jd)
        
        # Calculate houses
        houses, ascmc = swe.houses(jd, lat, lon, b'P')
        
        # Check Kaal Sarp Dosh
        rahu = planet_positions['Rahu']
        ketu = planet_positions['Ketu']
        
        def between_rahu_ketu(lon):
            if rahu < ketu:
                return rahu < lon < ketu
            else:
                return lon > rahu or lon < ketu
        
        inner_planets = ['Sun', 'Moon', 'Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']
        between_flags = [between_rahu_ketu(planet_positions[p]) for p in inner_planets]
        has_kaalsarp = all(between_flags)
        
        # Calculate partial Kaal Sarp
        partial_count = sum(between_flags)
        partial_kaalsarp = partial_count >= 5 and partial_count < 7
        
        # Calculate score and factors
        score = 0
        factors = []
        
        if has_kaalsarp:
            score += 5
            factors.append("All planets between Rahu and Ketu (Full Kaal Sarp Dosh)")
        elif partial_kaalsarp:
            score += 3
            factors.append(f"{partial_count} out of 7 planets between Rahu and Ketu (Partial Kaal Sarp)")
        
        # Check Rahu-Ketu axis
        rahu_house = get_house(rahu, houses)
        ketu_house = get_house(ketu, houses)
        
        axis_pairs = [(1, 7), (2, 8), (3, 9), (4, 10), (5, 11), (6, 12)]
        if (rahu_house, ketu_house) in axis_pairs or (ketu_house, rahu_house) in axis_pairs:
            score += 2
            factors.append(f"Rahu-Ketu axis across houses {rahu_house}-{ketu_house}")
        
        # Generate response
        is_dosha_present = score >= 3
        
        if lang.lower() == "hi":
            bot_response = "कालसर्प दोष आपकी कुंडली में " + ("मौजूद है" if is_dosha_present else "मौजूद नहीं है") + "।"
            if is_dosha_present:
                if has_kaalsarp:
                    bot_response += " यह पूर्ण कालसर्प दोष है जो जीवन के विभिन्न क्षेत्रों में बाधाएं उत्पन्न कर सकता है।"
                else:
                    bot_response += " यह आंशिक कालसर्प दोष है जो कुछ क्षेत्रों में चुनौतियां ला सकता है।"
        else:
            bot_response = "Kaal Sarp Dosh is " + ("present" if is_dosha_present else "not present") + " in your horoscope."
            if is_dosha_present:
                if has_kaalsarp:
                    bot_response += " This is a full Kaal Sarp Dosh which may create obstacles in various areas of life."
                else:
                    bot_response += " This is a partial Kaal Sarp Dosh which may bring challenges in some areas."
        
        return {
            "factors": factors,
            "is_dosha_present": is_dosha_present,
            "bot_response": bot_response,
            "score": score,
            "planets_between_rahu_ketu": partial_count,
            "full_kaalsarp": has_kaalsarp,
            "partial_kaalsarp": partial_kaalsarp
        }
        
    except Exception as e:
        return {"error": str(e)}

def calculate_papasamaya(dob: str, tob: str, lat: float, lon: float, tz: float, lang: str = "en") -> Dict[str, Any]:
    """Calculate Papasamaya (Inauspicious Time)"""
    try:
        # Parse date and time
        dob_parts = dob.split("/")
        if len(dob_parts) != 3:
            return {"error": "Invalid date format. Use DD/MM/YYYY"}
            
        day, month, year = int(dob_parts[0]), int(dob_parts[1]), int(dob_parts[2])
        
        tob_parts = tob.split(":")
        if len(tob_parts) != 2:
            return {"error": "Invalid time format. Use HH:MM"}
            
        hour, minute = int(tob_parts[0]), int(tob_parts[1])
        
        # Calculate Julian Day
        decimal_time = hour + minute / 60.0
        ut_hour = decimal_time - tz
        jd = swe.julday(year, month, day, ut_hour)
        
        # Set ephemeris
        swe.set_ephe_path('.')
        swe.set_sid_mode(swe.SIDM_LAHIRI, 0, 0)
        
        # Get planet positions
        planet_positions = calculate_planet_positions(jd)
        
        # Calculate houses
        houses, ascmc = swe.houses(jd, lat, lon, b'P')
        
        # Check Papasamaya
        kendra_houses = [1, 4, 7, 10]
        malefics = ['Saturn', 'Mars', 'Rahu', 'Ketu']
        
        malefic_house_flags = []
        malefic_in_kendra = []
        
        for m in malefics:
            h = get_house(planet_positions[m], houses)
            if h in kendra_houses:
                malefic_house_flags.append(True)
                malefic_in_kendra.append(f"{m} in {h}{'st' if h == 1 else 'th'} house")
        
        moon_afflicted = any(is_conjunction(planet_positions['Moon'], planet_positions[m]) for m in malefics)
        has_papasamaya = any(malefic_house_flags) or moon_afflicted
        
        # Calculate score and factors
        score = 0
        factors = []
        
        for flag, info in zip(malefic_house_flags, malefic_in_kendra):
            if flag:
                score += 2
                factors.append(info)
        
        if moon_afflicted:
            score += 3
            afflicting_planets = [m for m in malefics if is_conjunction(planet_positions['Moon'], planet_positions[m])]
            factors.append(f"Moon afflicted by {', '.join(afflicting_planets)}")
        
        # Check lagna lord
        lagna_sign = int(ascmc[0] / 30) + 1
        lagna_lords = {
            1: 'Mars', 2: 'Venus', 3: 'Mercury', 4: 'Moon', 5: 'Sun', 6: 'Mercury',
            7: 'Venus', 8: 'Mars', 9: 'Jupiter', 10: 'Saturn', 11: 'Saturn', 12: 'Jupiter'
        }
        lagna_lord = lagna_lords.get(lagna_sign)
        
        if lagna_lord and any(is_conjunction(planet_positions[lagna_lord], planet_positions[m]) for m in malefics):
            score += 2
            factors.append(f"Lagna lord ({lagna_lord}) afflicted by malefics")
        
        # Generate response
        is_dosha_present = score >= 3
        
        if lang.lower() == "hi":
            bot_response = "पापसमय दोष आपकी कुंडली में " + ("मौजूद है" if is_dosha_present else "मौजूद नहीं है") + "।"
            if is_dosha_present:
                bot_response += " यह जीवन में विभिन्न प्रकार की बाधाओं और चुनौतियों का कारण बन सकता है।"
        else:
            bot_response = "Papasamaya is " + ("present" if is_dosha_present else "not present") + " in your horoscope."
            if is_dosha_present:
                bot_response += " This may cause various obstacles and challenges in life."
        
        return {
            "factors": factors,
            "is_dosha_present": is_dosha_present,
            "bot_response": bot_response,
            "score": score,
            "malefics_in_kendra": len(malefic_in_kendra),
            "moon_afflicted": moon_afflicted
        }
        
    except Exception as e:
        return {"error": str(e)}