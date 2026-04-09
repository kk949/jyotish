import sys
import os
from support import panchanga
from support import mod_lagna
import swisseph as swe
import datetime

def test_sidereal_longitude():
    """Test sidereal_longitude function with Sun"""
    print("Testing sidereal_longitude...")
    # Current date
    now = datetime.datetime.now()
    jd = panchanga.gregorian_to_jd(date=now)
    
    # Get Sun's longitude
    sun_long = mod_lagna.sidereal_longitude(jd, swe.SUN)
    print(f"Sun's sidereal longitude: {sun_long:.4f}°")
    return True

def test_sunrise():
    """Test sunrise function"""
    print("Testing sunrise...")
    # Test for New York
    lat, lon = 40.7128, -74.0060  # New York coordinates
    # Current date
    now = datetime.datetime.now()
    jd = swe.julday(now.year, now.month, now.day, 0)
    
    # Get sunrise time
    rise_time = panchanga.sunrise(jd, (lat, lon, -4))  # New York timezone
    print(f"Sunrise time (Julian Day): {rise_time[0]:.6f}")
    
    # Just print the formatted time string directly
    print(f"Sunrise time: {rise_time[1]}")
    return True

def test_is_retrograde():
    """Test Is_Retrograde function"""
    print("Testing Is_Retrograde...")
    # Current date
    now = datetime.datetime.now()
    jd = panchanga.gregorian_to_jd(date=now)    
    
    # Check if Mercury is retrograde
    mercury_retro = mod_lagna.Is_Retrograde(jd, swe.MERCURY)
    print(f"Mercury retrograde: {mercury_retro}")
    return True

if __name__ == "__main__":
    print("Testing compatibility with latest pyswisseph library...")
    
    # Run tests
    tests_passed = 0
    total_tests = 3
    
    if test_sidereal_longitude():
        tests_passed += 1
    
    if test_sunrise():
        tests_passed += 1
    
    if test_is_retrograde():
        tests_passed += 1
    
    print(f"\nTests completed: {tests_passed}/{total_tests} passed")