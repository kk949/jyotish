"""
Comprehensive test script for all Dasha API endpoints
Run this script to test all Dasha calculations
"""

import requests
import json
from datetime import datetime

# API Configuration
BASE_URL = "http://localhost:8000"

# Sample Birth Data
BIRTH_DATA = {
    "dob": "01/10/1977",
    "tob": "11:40",
    "lat": 11.0,
    "lon": 77.0,
    "tz": 5.5,
    "lang": "en"
}

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80 + "\n")

def print_response(response, title="Response"):
    """Pretty print API response"""
    if response.status_code == 200:
        print(f"✅ {title} - SUCCESS")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ {title} - FAILED")
        print(f"Status Code: {response.status_code}")
        print(f"Error: {response.text}")
    print("-" * 80)

def test_vimshottari_dashas():
    """Test all Vimshottari Dasha endpoints"""
    print_section("VIMSHOTTARI DASHA TESTS")
    
    # 1. Test Current Mahadasha
    print("1. Testing Current Mahadasha...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/current",
        params=BIRTH_DATA
    )
    print_response(response, "Current Mahadasha")
    
    # 2. Test Full Current Mahadasha
    print("\n2. Testing Full Current Mahadasha...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/full",
        params=BIRTH_DATA
    )
    print_response(response, "Full Current Mahadasha")
    
    # 3. Test All Mahadashas
    print("\n3. Testing All Mahadashas...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/all",
        params=BIRTH_DATA
    )
    print_response(response, "All Mahadashas")
    
    # 4. Test Antardashas (current)
    print("\n4. Testing Antardashas (Current)...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/antardasha",
        params=BIRTH_DATA
    )
    print_response(response, "Current Antardashas")
    
    # 5. Test Antardashas (specific - Jupiter)
    print("\n5. Testing Antardashas (Jupiter)...")
    params = BIRTH_DATA.copy()
    params["mahadasha_lord"] = "Jupiter"
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/antardasha",
        params=params
    )
    print_response(response, "Jupiter Antardashas")
    
    # 6. Test Paryantardashas
    print("\n6. Testing Paryantardashas...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/paryantardasha",
        params=BIRTH_DATA
    )
    print_response(response, "Paryantardashas")
    
    # 7. Test Predictions for each planet
    print("\n7. Testing Predictions for All Planets...")
    planets = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    for planet in planets:
        print(f"\n   Testing {planet} Predictions...")
        response = requests.get(f"{BASE_URL}/dasha/vimshottari/predictions/{planet}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ {planet}: {data['response']['predictions']['general'][:80]}...")
        else:
            print(f"   ❌ {planet}: Failed")
    
    # 8. Test Specific Planet Dasha
    print("\n8. Testing Specific Planet Dasha (Venus)...")
    response = requests.get(
        f"{BASE_URL}/dasha/vimshottari/specific/Venus",
        params=BIRTH_DATA
    )
    print_response(response, "Venus Specific Dasha")

def test_chara_dashas():
    """Test all Chara Dasha endpoints"""
    print_section("CHARA DASHA TESTS (Jaimini System)")
    
    # 1. Test Current Chara Dasha
    print("1. Testing Current Chara Dasha...")
    response = requests.get(
        f"{BASE_URL}/dasha/chara/current",
        params=BIRTH_DATA
    )
    print_response(response, "Current Chara Dasha")
    
    # 2. Test Chara Dasha Main Periods
    print("\n2. Testing Chara Dasha Main Periods...")
    response = requests.get(
        f"{BASE_URL}/dasha/chara/main",
        params=BIRTH_DATA
    )
    print_response(response, "Chara Dasha Main Periods")
    
    # 3. Test Chara Dasha Sub-periods
    print("\n3. Testing Chara Dasha Sub-periods...")
    signs = ["Aries", "Leo", "Sagittarius"]  # Test a few signs
    
    for sign in signs:
        print(f"\n   Testing {sign} Sub-periods...")
        response = requests.get(
            f"{BASE_URL}/dasha/chara/sub/{sign}",
            params=BIRTH_DATA
        )
        if response.status_code == 200:
            data = response.json()
            sub_periods = data['response']['sub_periods']
            if isinstance(sub_periods, list):
                print(f"   ✅ {sign}: {len(sub_periods)} sub-periods found")
            else:
                print(f"   ✅ {sign}: Data received")
        else:
            print(f"   ❌ {sign}: Failed - {response.text}")

def test_yogini_dashas():
    """Test all Yogini Dasha endpoints"""
    print_section("YOGINI DASHA TESTS")
    
    # 1. Test Yogini Dasha Main Periods
    print("1. Testing Yogini Dasha Main Periods...")
    response = requests.get(
        f"{BASE_URL}/dasha/yogini/main",
        params=BIRTH_DATA
    )
    print_response(response, "Yogini Dasha Main Periods")
    
    # 2. Test Yogini Dasha Sub-periods
    print("\n2. Testing Yogini Dasha Sub-periods...")
    yogini_lords = ["Mangala", "Guru", "Shani"]  # Test a few lords
    
    for lord in yogini_lords:
        print(f"\n   Testing {lord} Sub-periods...")
        response = requests.get(
            f"{BASE_URL}/dasha/yogini/sub/{lord}",
            params=BIRTH_DATA
        )
        if response.status_code == 200:
            data = response.json()
            sub_periods = data['response']['sub_periods']
            if isinstance(sub_periods, list):
                print(f"   ✅ {lord}: {len(sub_periods)} sub-periods found")
            else:
                print(f"   ✅ {lord}: Data received")
        else:
            print(f"   ❌ {lord}: Failed - {response.text}")

def test_api_root():
    """Test API root endpoint to see all available endpoints"""
    print_section("API ROOT - Available Endpoints")
    
    response = requests.get(f"{BASE_URL}/")
    print_response(response, "API Root")

def create_summary_report(birth_data):
    """Create a comprehensive summary report"""
    print_section("COMPREHENSIVE DASHA SUMMARY REPORT")
    
    print(f"Birth Details:")
    print(f"  Date of Birth: {birth_data['dob']}")
    print(f"  Time of Birth: {birth_data['tob']}")
    print(f"  Location: Lat {birth_data['lat']}, Lon {birth_data['lon']}")
    print(f"  Timezone: UTC+{birth_data['tz']}")
    print(f"  Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "-"*80 + "\n")
    
    # Get current Vimshottari Dasha
    try:
        response = requests.get(f"{BASE_URL}/dasha/vimshottari/full", params=birth_data)
        if response.status_code == 200:
            data = response.json()
            current = data['response']['current_mahadasha']
            
            print("📊 CURRENT VIMSHOTTARI DASHA STATUS")
            print("-" * 80)
            print(f"  Mahadasha Lord: {current['lord']}")
            print(f"  Period: {current['dashaNum']} of 9")
            print(f"  Start Date: {current['startDate']}")
            print(f"  End Date: {current['endDate']}")
            print(f"  Duration: {current['duration']}")
            print(f"  Current Age: {current['startage']} to {current['endage']}")
            print("\n  Predictions:")
            pred = current['predictions']
            print(f"  • General: {pred['general']}")
            print(f"  • Favorable: {pred['favorable']}")
            print(f"  • Challenges: {pred['challenges']}")
            print(f"  • Remedies: {pred['remedies']}")
    except Exception as e:
        print(f"❌ Error getting Vimshottari Dasha: {str(e)}")
    
    print("\n" + "-"*80 + "\n")
    
    # Get current Chara Dasha
    try:
        response = requests.get(f"{BASE_URL}/dasha/chara/current", params=birth_data)
        if response.status_code == 200:
            data = response.json()
            chara = data['response']['current_chara_dasha']
            
            print("📊 CURRENT CHARA DASHA STATUS (Jaimini)")
            print("-" * 80)
            print(f"  Current Sign: {chara['current_sign']}")
            print(f"  Remaining Years: {chara['remaining_years']:.2f}")
    except Exception as e:
        print(f"❌ Error getting Chara Dasha: {str(e)}")
    
    print("\n" + "-"*80 + "\n")
    
    # Get Yogini Dasha
    try:
        response = requests.get(f"{BASE_URL}/dasha/yogini/main", params=birth_data)
        if response.status_code == 200:
            data = response.json()
            yogini_periods = data['response']['yogini_dasha_main_periods']
            
            print("📊 YOGINI DASHA PERIODS")
            print("-" * 80)
            print(f"  Total Cycle: {data['response']['total_cycle_years']} years")
            print(f"  Number of Periods: {data['response']['total_periods']}")
            print("\n  Main Periods:")
            for i, period in enumerate(yogini_periods[:3], 1):  # Show first 3
                print(f"  {i}. {period['lord']} ({period['deity']}) - {period['duration_years']} years")
            if len(yogini_periods) > 3:
                print(f"  ... and {len(yogini_periods) - 3} more periods")
    except Exception as e:
        print(f"❌ Error getting Yogini Dasha: {str(e)}")
    
    print("\n" + "="*80 + "\n")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "🌟"*40)
    print("        JYOTISH API - COMPLETE DASHA SYSTEM TEST SUITE")
    print("🌟"*40 + "\n")
    
    try:
        # Test API availability
        test_api_root()
        
        # Test Vimshottari Dashas
        test_vimshottari_dashas()
        
        # Test Chara Dashas
        test_chara_dashas()
        
        # Test Yogini Dashas
        test_yogini_dashas()
        
        # Create Summary Report
        create_summary_report(BIRTH_DATA)
        
        print("\n" + "✅"*40)
        print("        ALL TESTS COMPLETED!")
        print("✅"*40 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Please make sure the API server is running on http://localhost:8000")
        print("Start the server with: python api.py")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

def test_specific_endpoint(endpoint_type="vimshottari", endpoint_name="current"):
    """Test a specific endpoint"""
    print_section(f"TESTING SPECIFIC ENDPOINT: {endpoint_type}/{endpoint_name}")
    
    if endpoint_type == "vimshottari":
        url = f"{BASE_URL}/dasha/vimshottari/{endpoint_name}"
    elif endpoint_type == "chara":
        url = f"{BASE_URL}/dasha/chara/{endpoint_name}"
    elif endpoint_type == "yogini":
        url = f"{BASE_URL}/dasha/yogini/{endpoint_name}"
    else:
        print(f"❌ Invalid endpoint type: {endpoint_type}")
        return
    
    response = requests.get(url, params=BIRTH_DATA)
    print_response(response, f"{endpoint_type.title()} - {endpoint_name.title()}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test specific endpoint
        if sys.argv[1] == "specific" and len(sys.argv) >= 4:
            test_specific_endpoint(sys.argv[2], sys.argv[3])
        elif sys.argv[1] == "summary":
            create_summary_report(BIRTH_DATA)
        elif sys.argv[1] == "vimshottari":
            test_vimshottari_dashas()
        elif sys.argv[1] == "chara":
            test_chara_dashas()
        elif sys.argv[1] == "yogini":
            test_yogini_dashas()
        else:
            print("Usage:")
            print("  python test_dasha_endpoints.py              # Run all tests")
            print("  python test_dasha_endpoints.py summary      # Generate summary report only")
            print("  python test_dasha_endpoints.py vimshottari  # Test Vimshottari only")
            print("  python test_dasha_endpoints.py chara        # Test Chara only")
            print("  python test_dasha_endpoints.py yogini       # Test Yogini only")
            print("  python test_dasha_endpoints.py specific vimshottari current")
    else:
        # Run all tests
        run_all_tests()