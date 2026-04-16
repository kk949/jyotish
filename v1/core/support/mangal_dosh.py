#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# mangal_dosh.py -- module for Mangal Dosh (Mars Affliction) calculations
#
# Copyright (C) 2023 Shyam Bhat  <vicharavandana@gmail.com>
# Downloaded from "https://github.com/VicharaVandana/jyotishyam.git"
#
# This file is part of the "jyotishyam" Python library
# for computing Hindu jataka with sidereal lahiri ayanamsha technique 
# using swiss ephemeries

import swisseph as swe
import math
from datetime import datetime
import support.mod_constants as c
import support.mod_general as gen

# Houses considered for Mangal Dosh
MANGAL_HOUSES = [1, 2, 4, 7, 8, 12]

def calculate_mangal_dosh(dob, tob, latitude, longitude, timezone):
    """
    Calculate Mangal Dosh (Mars Affliction) based on birth details
    
    Parameters:
    dob (str): Date of birth in DD/MM/YYYY format
    tob (str): Time of birth in HH:MM format
    latitude (float): Latitude of birth place
    longitude (float): Longitude of birth place
    timezone (float): Timezone offset in hours
    
    Returns:
    dict: Mangal Dosh analysis results
    """
    # Parse date and time
    day, month, year = map(int, dob.split('/'))
    hour, minute = map(int, tob.split(':'))
    decimal_time = hour + minute / 60.0
    
    # Convert local time to UT
    ut_hour = decimal_time - float(timezone)
    jd = swe.julday(year, month, day, ut_hour)
    
    # Set ephemeris path to default
    swe.set_ephe_path(None)
    
    # Calculate positions
    mars_pos = swe.calc_ut(jd, swe.MARS)[0]  # returns (longitude, latitude, distance, speed_long, speed_lat, speed_dist)
    mars_long = mars_pos[0]
    
    moon_pos = swe.calc_ut(jd, swe.MOON)[0]
    moon_long = moon_pos[0]
    
    saturn_pos = swe.calc_ut(jd, swe.SATURN)[0]
    saturn_long = saturn_pos[0]
    
    rahu_pos = swe.calc_ut(jd, swe.MEAN_NODE)[0]  # Rahu = MEAN_NODE
    rahu_long = rahu_pos[0]
    
    # Calculate Ascendant (Lagna)
    house_cusps, ascmc = swe.houses(jd, latitude, longitude, b'P')  # Placidus
    asc_deg = ascmc[0]
    
    # Determine houses for planets
    mars_house = get_house(mars_long, house_cusps)
    moon_house = get_house(moon_long, house_cusps)
    saturn_house = get_house(saturn_long, house_cusps)
    rahu_house = get_house(rahu_long, house_cusps)
    
    # Calculate Moon Lagna (house positions from Moon)
    moon_lagna_houses = {}
    for i in range(1, 13):
        moon_lagna_houses[i] = (moon_house + i - 1) % 12 + 1
    
    # Mars house from Moon Lagna
    mars_moon_house = moon_lagna_houses.get(mars_house, mars_house)
    
    # Check aspects
    mars_aspects = get_mars_aspects(mars_house)
    
    # Calculate Mangal Dosh factors
    factors = {}
    is_dosha_present = False
    score = 0
    
    # Check from Lagna (Ascendant)
    if mars_house in MANGAL_HOUSES:
        factors["lagna"] = f"Mangal dosh from lagna, mars in house {mars_house}"
        is_dosha_present = True
        score += 25
    
    # Check from Moon Lagna
    if mars_moon_house in MANGAL_HOUSES:
        factors["moon"] = f"Mangal dosh from moon lagna, mars in house {mars_moon_house}, aspecting the houses {', '.join(map(str, mars_aspects))}"
        is_dosha_present = True
        score += 20
    
    # Check Mars-Saturn association
    if abs(mars_long - saturn_long) < 10 or abs(mars_long - saturn_long) > 350:
        factors["saturn"] = f"Mangal dosh along with mars-saturn association/aspect, mars in house {mars_house} and saturn in house {saturn_house}"
        is_dosha_present = True
        score += 15
    elif mars_house == saturn_house:
        factors["saturn"] = f"Mangal dosh along with mars-saturn conjunction, both in house {mars_house}"
        is_dosha_present = True
        score += 15
    
    # Check Mars-Rahu association
    if abs(mars_long - rahu_long) < 10 or abs(mars_long - rahu_long) > 350:
        # Check if Rahu is in Scorpio (Mars' sign)
        rahu_sign = int(rahu_long / 30) + 1
        if rahu_sign == 8:  # Scorpio
            factors["rahu"] = f"Rahu transforming into mars in house {rahu_house} in the sign of Scorpio"
            is_dosha_present = True
            score += 7
    
    # Generate bot response
    bot_response = ""
    if score == 0:
        bot_response = "No Mangal Dosh detected in your chart."
    elif score < 30:
        bot_response = f"You are {score}% manglik, which is considered mild. No remedies needed."
    elif score < 50:
        bot_response = f"You are {score}% manglik, which is moderate. Some simple remedies may help."
    else:
        bot_response = f"You are {score}% manglik. It is good to consult an astrologer."
    
    return {
        "factors": factors,
        "is_dosha_present": is_dosha_present,
        "bot_response": bot_response,
        "score": score
    }

def get_house(planet_long, house_cusps):
    """
    Determine which house a planet is in based on its longitude
    
    Parameters:
    planet_long (float): Planet's longitude
    house_cusps (list): List of house cusps longitudes
    
    Returns:
    int: House number (1-12)
    """
    # 12 houses; house_cusps[0] = 1st house cusp
    for i in range(12):
        start = house_cusps[i]
        end = house_cusps[(i+1) % 12]
        # Wrap around 360°
        if end < start:
            end += 360
        pos = planet_long
        if pos < start:
            pos += 360
        if start <= pos < end:
            return i + 1
    return 1  # Default to 1st house if not found

def get_mars_aspects(mars_house):
    """
    Get houses aspected by Mars based on its house position
    
    Parameters:
    mars_house (int): House position of Mars (1-12)
    
    Returns:
    list: List of houses aspected by Mars
    """
    # Mars aspects 4th, 7th and 8th houses from its position
    aspects = []
    aspects.append((mars_house + 3) % 12 or 12)  # 4th aspect
    aspects.append((mars_house + 6) % 12 or 12)  # 7th aspect
    aspects.append((mars_house + 7) % 12 or 12)  # 8th aspect
    return aspects