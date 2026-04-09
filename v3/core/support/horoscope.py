"""
Horoscope Module
Generates daily, weekly, and monthly horoscopes based on zodiac signs
Uses pyswisseph for planetary positions and transits
"""

import swisseph as swe
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple
import random

# Initialize Swiss Ephemeris
swe.set_ephe_path('.')

# Zodiac sign details
ZODIAC_SIGNS = {
    1: {"name": "Aries", "ruler": "Mars", "element": "Fire", "quality": "Cardinal"},
    2: {"name": "Taurus", "ruler": "Venus", "element": "Earth", "quality": "Fixed"},
    3: {"name": "Gemini", "ruler": "Mercury", "element": "Air", "quality": "Mutable"},
    4: {"name": "Cancer", "ruler": "Moon", "element": "Water", "quality": "Cardinal"},
    5: {"name": "Leo", "ruler": "Sun", "element": "Fire", "quality": "Fixed"},
    6: {"name": "Virgo", "ruler": "Mercury", "element": "Earth", "quality": "Mutable"},
    7: {"name": "Libra", "ruler": "Venus", "element": "Air", "quality": "Cardinal"},
    8: {"name": "Scorpio", "ruler": "Mars", "element": "Water", "quality": "Fixed"},
    9: {"name": "Sagittarius", "ruler": "Jupiter", "element": "Fire", "quality": "Mutable"},
    10: {"name": "Capricorn", "ruler": "Saturn", "element": "Earth", "quality": "Cardinal"},
    11: {"name": "Aquarius", "ruler": "Saturn", "element": "Air", "quality": "Fixed"},
    12: {"name": "Pisces", "ruler": "Jupiter", "element": "Water", "quality": "Mutable"}
}

# Planet indices for pyswisseph
PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN
}

# Lucky colors for each zodiac
LUCKY_COLORS = {
    "Aries": [("Red", "#FF0000"), ("Scarlet", "#FF2400"), ("Orange", "#FFA500")],
    "Taurus": [("Green", "#008000"), ("Pink", "#FFC0CB"), ("Emerald", "#50C878")],
    "Gemini": [("Yellow", "#FFFF00"), ("Light Green", "#90EE90"), ("Orange", "#FFA500")],
    "Cancer": [("White", "#FFFFFF"), ("Silver", "#C0C0C0"), ("Pearl", "#EAE0C8")],
    "Leo": [("Gold", "#FFD700"), ("Orange", "#FFA500"), ("Red", "#FF0000")],
    "Virgo": [("Green", "#008000"), ("Brown", "#A52A2A"), ("Navy", "#000080")],
    "Libra": [("Blue", "#0000FF"), ("Pink", "#FFC0CB"), ("Lavender", "#E6E6FA")],
    "Scorpio": [("Maroon", "#800000"), ("Red", "#FF0000"), ("Black", "#000000")],
    "Sagittarius": [("Purple", "#800080"), ("Blue", "#0000FF"), ("Yellow", "#FFFF00")],
    "Capricorn": [("Black", "#000000"), ("Brown", "#A52A2A"), ("Grey", "#808080")],
    "Aquarius": [("Blue", "#0000FF"), ("Turquoise", "#40E0D0"), ("Silver", "#C0C0C0")],
    "Pisces": [("Sea Green", "#2E8B57"), ("Purple", "#800080"), ("Lavender", "#E6E6FA")]
}

# Life aspects for predictions
LIFE_ASPECTS = [
    "health", "career", "finance", "relationship", "family",
    "education", "travel", "spirituality", "social", "overall"
]


def get_planetary_positions(date: str) -> Dict[str, float]:
    """
    Get positions of all major planets for a given date
    
    Args:
        date: Date in DD/MM/YYYY format
        
    Returns:
        Dictionary of planet positions in degrees
    """
    try:
        day, month, year = map(int, date.split('/'))
        jd = swe.julday(year, month, day, 12.0)  # Noon UTC
        
        positions = {}
        for planet_name, planet_id in PLANETS.items():
            planet_data = swe.calc_ut(jd, planet_id)
            positions[planet_name] = planet_data[0][0]  # Longitude in degrees
        
        # Add Rahu (North Node) and Ketu (South Node)
        rahu_data = swe.calc_ut(jd, swe.MEAN_NODE)
        positions["Rahu"] = rahu_data[0][0]
        positions["Ketu"] = (rahu_data[0][0] + 180) % 360
        
        return positions
        
    except Exception as e:
        raise Exception(f"Error getting planetary positions: {str(e)}")


def get_sign_from_longitude(longitude: float) -> int:
    """
    Get zodiac sign number from longitude
    
    Args:
        longitude: Ecliptic longitude in degrees (0-360)
        
    Returns:
        Sign number (1-12)
    """
    return int(longitude / 30) + 1


def calculate_aspects(positions: Dict[str, float], zodiac_num: int) -> Dict[str, List[str]]:
    """
    Calculate planetary aspects affecting a zodiac sign
    
    Args:
        positions: Dictionary of planetary positions
        zodiac_num: Zodiac sign number (1-12)
        
    Returns:
        Dictionary of favorable and challenging aspects
    """
    favorable = []
    challenging = []
    
    # Sign's starting longitude
    sign_start = (zodiac_num - 1) * 30
    sign_end = sign_start + 30
    
    for planet, longitude in positions.items():
        # Calculate angular distance
        distance = abs(sign_start + 15 - longitude)  # From sign's midpoint
        if distance > 180:
            distance = 360 - distance
        
        # Conjunction (0-10 degrees)
        if distance <= 10:
            favorable.append(f"{planet} in conjunction")
        
        # Trine (120 degrees, ±10)
        elif 110 <= distance <= 130:
            favorable.append(f"{planet} in trine")
        
        # Sextile (60 degrees, ±8)
        elif 52 <= distance <= 68:
            favorable.append(f"{planet} in sextile")
        
        # Square (90 degrees, ±8)
        elif 82 <= distance <= 98:
            challenging.append(f"{planet} in square")
        
        # Opposition (180 degrees, ±10)
        elif 170 <= distance <= 190:
            challenging.append(f"{planet} in opposition")
    
    return {
        "favorable": favorable,
        "challenging": challenging
    }


def generate_prediction_score(aspects: Dict[str, List[str]], planet_positions: Dict[str, float], 
                              zodiac_num: int, seed: str) -> Dict[str, int]:
    """
    Generate prediction scores for different life aspects
    
    Args:
        aspects: Favorable and challenging aspects
        planet_positions: Current planetary positions
        zodiac_num: Zodiac sign number
        seed: Seed for random number generation
        
    Returns:
        Dictionary of scores for each life aspect
    """
    random.seed(seed)
    
    # Base score calculation
    favorable_count = len(aspects["favorable"])
    challenging_count = len(aspects["challenging"])
    
    base_score = 50 + (favorable_count * 5) - (challenging_count * 3)
    base_score = max(30, min(90, base_score))  # Clamp between 30-90
    
    scores = {}
    for aspect in LIFE_ASPECTS:
        # Add some variation for each aspect
        variation = random.randint(-15, 15)
        score = base_score + variation
        scores[aspect] = max(0, min(100, score))
    
    return scores


def get_horoscope_messages(zodiac_name: str, scores: Dict[str, int], 
                           aspects: Dict[str, List[str]], seed: str) -> Dict[str, str]:
    """
    Generate horoscope messages based on scores and aspects
    
    Args:
        zodiac_name: Name of zodiac sign
        scores: Prediction scores
        aspects: Planetary aspects
        seed: Seed for random selection
        
    Returns:
        Dictionary of messages for each life aspect
    """
    random.seed(seed)
    
    # Template messages for different score ranges
    messages = {
        "health": {
            "high": [
                "Your vitality is at its peak. This is an excellent time to start new fitness routines or health regimens.",
                "Energy levels are surging. Channel this vitality into productive activities and self-care practices.",
                "Physical and mental well-being are well-aligned. Maintain this balance through mindful practices."
            ],
            "medium": [
                "Moderate your energy expenditure. Balance activity with adequate rest to maintain optimal health.",
                "Pay attention to minor health signals. Preventive care will keep you in good shape.",
                "Maintain your current health routines. Consistency is key to sustained well-being."
            ],
            "low": [
                "Exercise caution with physical activities. Rest and recovery should be your priority.",
                "Consider consulting health professionals for any persistent concerns. Prevention is better than cure.",
                "Avoid overexertion. Listen to your body's signals and take time for recuperation."
            ]
        },
        "career": {
            "high": [
                "Professional opportunities are abundant. Your skills and expertise will be recognized and rewarded.",
                "This is an excellent time for career advancement. Take initiative in important projects and presentations.",
                "Your professional network expands favorably. Collaborations and partnerships bring success."
            ],
            "medium": [
                "Steady progress in your career path. Focus on consolidating your current position and skills.",
                "Opportunities arise through persistence. Continue your dedicated efforts for gradual advancement.",
                "Maintain professional relationships. Networking and teamwork support your career goals."
            ],
            "low": [
                "Navigate workplace challenges with patience and diplomacy. Avoid hasty decisions or conflicts.",
                "Focus on skill development rather than immediate advancement. Long-term growth requires preparation.",
                "Exercise caution in professional dealings. Verify information and consult mentors before major decisions."
            ]
        },
        "finance": {
            "high": [
                "Financial prospects are bright. Strategic investments and careful planning bring profitable returns.",
                "Money flows favorably. This is a good time for important financial decisions and investments.",
                "Your financial acumen is sharp. Trust your judgment in monetary matters while staying informed."
            ],
            "medium": [
                "Maintain fiscal discipline. Balance spending with saving to ensure financial stability.",
                "Moderate financial gains are indicated. Continue with your current financial strategies.",
                "Review your budget and expenses. Small adjustments can lead to improved financial health."
            ],
            "low": [
                "Exercise extreme caution in financial matters. Avoid risky investments and unnecessary expenses.",
                "Conserve resources and avoid lending money. Focus on financial security and debt reduction.",
                "Seek professional financial advice before major decisions. This is a time for prudence, not speculation."
            ]
        },
        "relationship": {
            "high": [
                "Relationships flourish under favorable cosmic influences. Express your feelings and strengthen bonds.",
                "Harmony prevails in personal connections. This is an excellent time for important relationship commitments.",
                "Love and friendship bring joy. Invest time in nurturing meaningful relationships."
            ],
            "medium": [
                "Relationships require balanced effort. Maintain open communication and mutual understanding.",
                "Steady relationship dynamics. Continue showing appreciation and support to loved ones.",
                "Small gestures of love and care strengthen bonds. Be present for those who matter."
            ],
            "low": [
                "Relationship challenges may arise. Practice patience, empathy, and effective communication.",
                "Avoid conflicts and misunderstandings. Choose your words carefully and listen actively.",
                "Give space when needed. Sometimes distance helps clarify feelings and perspectives."
            ]
        },
        "family": {
            "high": [
                "Family harmony is strong. Enjoy quality time with loved ones and create lasting memories.",
                "Domestic matters resolve favorably. Your home is a source of comfort and support.",
                "Family celebrations and gatherings bring joy. Strengthen bonds through shared experiences."
            ],
            "medium": [
                "Family life remains stable. Maintain regular communication and show appreciation to relatives.",
                "Balance family obligations with personal time. Healthy boundaries support overall well-being.",
                "Small family matters need attention. Address concerns promptly to maintain harmony."
            ],
            "low": [
                "Family situations require patience and understanding. Avoid heated arguments or confrontations.",
                "Domestic challenges test your resilience. Seek compromise and maintain family unity.",
                "Tread carefully in family matters. Listen more, speak less, and prioritize reconciliation."
            ]
        },
        "education": {
            "high": [
                "Learning and intellectual pursuits are highly favored. Your mind is sharp and receptive.",
                "Academic or educational endeavors bring excellent results. This is ideal for exams and learning new skills.",
                "Knowledge acquisition comes easily. Explore new subjects or deepen expertise in your field."
            ],
            "medium": [
                "Steady progress in educational pursuits. Consistent effort yields satisfactory results.",
                "Learning requires focused attention. Create structured study plans for better outcomes.",
                "Knowledge builds gradually. Stay patient and persistent in your educational journey."
            ],
            "low": [
                "Educational challenges require extra effort. Seek help from teachers or mentors when needed.",
                "Avoid starting new courses now. Focus on completing existing commitments first.",
                "Concentration may be difficult. Create optimal study conditions and minimize distractions."
            ]
        },
        "travel": {
            "high": [
                "Travel brings exciting opportunities and experiences. Journey plans proceed smoothly and successfully.",
                "This is an excellent time for both business and leisure trips. New horizons await exploration.",
                "Travel broadens perspectives and creates valuable connections. Safe and enjoyable journeys ahead."
            ],
            "medium": [
                "Travel plans proceed with normal preparation. Ensure all arrangements are confirmed.",
                "Short trips are favorable. Plan carefully for longer journeys to ensure smooth experiences.",
                "Travel opportunities exist but require practical planning. Balance adventure with preparation."
            ],
            "low": [
                "Postpone non-essential travel if possible. Focus on local activities and commitments.",
                "Travel delays or complications are possible. Have backup plans and stay flexible.",
                "Exercise caution while traveling. Double-check arrangements and stay alert to surroundings."
            ]
        },
        "spirituality": {
            "high": [
                "Spiritual awareness deepens significantly. Inner peace and clarity guide your path.",
                "This is an ideal time for meditation, prayer, and spiritual practices. Divine connection strengthens.",
                "Wisdom and intuition are heightened. Trust your inner guidance in all matters."
            ],
            "medium": [
                "Maintain regular spiritual practices. Consistency brings gradual inner growth and peace.",
                "Spiritual journey continues steadily. Seek balance between material and spiritual pursuits.",
                "Inner reflection provides valuable insights. Allocate quiet time for contemplation."
            ],
            "low": [
                "Spiritual confusion or doubt may arise. Seek guidance from trusted spiritual mentors.",
                "Material concerns may overshadow spiritual needs. Strive to maintain balance.",
                "Return to basic spiritual practices. Simplicity often provides the deepest connection."
            ]
        },
        "social": {
            "high": [
                "Social life thrives with meaningful interactions. New friendships and networking opportunities abound.",
                "Your charisma attracts positive people. Enjoy social gatherings and strengthen community bonds.",
                "Social influence expands. Use this to create positive change and help others."
            ],
            "medium": [
                "Social interactions remain pleasant. Maintain existing friendships while being open to new connections.",
                "Balance social activities with personal time. Quality matters more than quantity in relationships.",
                "Social obligations are manageable. Choose engagements that align with your values and interests."
            ],
            "low": [
                "Social energy is low. It's okay to decline invitations and focus on self-care.",
                "Avoid social conflicts or misunderstandings. Choose your social circles carefully.",
                "Retreat and recharge. Solitude can be healing and provide necessary perspective."
            ]
        },
        "overall": {
            "high": [
                "The cosmic energies align in your favor. This is a powerful time for growth and achievement across all life areas.",
                "Fortune smiles upon you. Embrace opportunities with confidence and positive expectations.",
                "Your stars shine bright. Trust in your abilities and the universe's support for your journey."
            ],
            "medium": [
                "Life proceeds with balanced energies. Consistent effort brings steady progress and satisfaction.",
                "Opportunities and challenges balance each other. Navigate with wisdom and patience.",
                "Maintain your current course. Small adjustments rather than major changes serve you well."
            ],
            "low": [
                "Navigate this period with extra care and patience. Challenges are temporary learning opportunities.",
                "This is a time for introspection and consolidation. Avoid major initiatives or risky ventures.",
                "Difficult phases pass. Stay grounded, seek support when needed, and maintain faith in better days ahead."
            ]
        }
    }
    
    result = {}
    for aspect in LIFE_ASPECTS:
        score = scores[aspect]
        if score >= 70:
            level = "high"
        elif score >= 45:
            level = "medium"
        else:
            level = "low"
        
        result[aspect] = random.choice(messages[aspect][level])
    
    return result


def calculate_lucky_elements(zodiac_num: int, date: str, planet_positions: Dict[str, float]) -> Dict[str, Any]:
    """
    Calculate lucky elements for the day
    
    Args:
        zodiac_num: Zodiac sign number
        date: Date in DD/MM/YYYY format
        planet_positions: Current planetary positions
        
    Returns:
        Dictionary with lucky color, number, time, and day
    """
    zodiac_name = ZODIAC_SIGNS[zodiac_num]["name"]
    
    # Lucky color
    colors = LUCKY_COLORS.get(zodiac_name, [("White", "#FFFFFF")])
    seed = f"{date}-{zodiac_name}-color"
    random.seed(hash(seed) % 10000)
    lucky_color, lucky_color_code = random.choice(colors)
    
    # Lucky numbers (2 numbers)
    seed = f"{date}-{zodiac_name}-numbers"
    random.seed(hash(seed) % 10000)
    lucky_numbers = sorted(random.sample(range(1, 100), 2))
    
    # Lucky time (based on ruling planet's position)
    ruler = ZODIAC_SIGNS[zodiac_num]["ruler"]
    ruler_position = planet_positions.get(ruler, 0)
    # Convert position to hours (0-360 -> 0-24)
    lucky_hour = int((ruler_position / 360) * 24)
    lucky_time = f"{lucky_hour:02d}:00 - {(lucky_hour+1)%24:02d}:00"
    
    # Lucky day (based on ruling planet)
    lucky_days = {
        "Sun": "Sunday",
        "Moon": "Monday",
        "Mars": "Tuesday",
        "Mercury": "Wednesday",
        "Jupiter": "Thursday",
        "Venus": "Friday",
        "Saturn": "Saturday"
    }
    lucky_day = lucky_days.get(ruler, "Sunday")
    
    return {
        "lucky_color": lucky_color.lower(),
        "lucky_color_code": lucky_color_code,
        "lucky_numbers": lucky_numbers,
        "lucky_time": lucky_time,
        "lucky_day": lucky_day
    }


def generate_daily_horoscope(zodiac: int, date: str) -> Dict[str, Any]:
    """
    Generate complete daily horoscope for a zodiac sign
    
    Args:
        zodiac: Zodiac sign number (1-12)
        date: Date in DD/MM/YYYY format
        
    Returns:
        Complete horoscope dictionary
    """
    try:
        if zodiac < 1 or zodiac > 12:
            raise ValueError("Zodiac number must be between 1 and 12")
        
        zodiac_info = ZODIAC_SIGNS[zodiac]
        zodiac_name = zodiac_info["name"]
        
        # Get planetary positions
        planet_positions = get_planetary_positions(date)
        
        # Calculate aspects
        aspects = calculate_aspects(planet_positions, zodiac)
        
        # Generate seed for consistent daily predictions
        seed = f"{date}-{zodiac_name}"
        
        # Generate scores
        scores = generate_prediction_score(aspects, planet_positions, zodiac, seed)
        
        # Generate messages
        messages = get_horoscope_messages(zodiac_name, scores, aspects, seed)
        
        # Calculate lucky elements
        lucky_elements = calculate_lucky_elements(zodiac, date, planet_positions)
        
        # Format response
        bot_response = {}
        for aspect in LIFE_ASPECTS:
            bot_response[aspect] = {
                "score": scores[aspect],
                "split_response": messages[aspect]
            }
        
        horoscope = {
            "zodiac_sign": zodiac_name.lower(),
            "zodiac_number": zodiac,
            "date": date,
            "element": zodiac_info["element"].lower(),
            "quality": zodiac_info["quality"].lower(),
            "ruling_planet": zodiac_info["ruler"].lower(),
            "lucky_color": lucky_elements["lucky_color"],
            "lucky_color_code": lucky_elements["lucky_color_code"],
            "lucky_number": lucky_elements["lucky_numbers"],
            "lucky_time": lucky_elements["lucky_time"],
            "lucky_day": lucky_elements["lucky_day"],
            "planetary_aspects": {
                "favorable": aspects["favorable"],
                "challenging": aspects["challenging"]
            },
            "bot_response": bot_response
        }
        
        return horoscope
        
    except Exception as e:
        raise Exception(f"Error generating daily horoscope: {str(e)}")


def generate_weekly_horoscope(zodiac: int, start_date: str) -> Dict[str, Any]:
    """
    Generate weekly horoscope for a zodiac sign
    
    Args:
        zodiac: Zodiac sign number (1-12)
        start_date: Week start date in DD/MM/YYYY format
        
    Returns:
        Weekly horoscope dictionary
    """
    try:
        zodiac_info = ZODIAC_SIGNS[zodiac]
        zodiac_name = zodiac_info["name"]
        
        # Parse start date
        day, month, year = map(int, start_date.split('/'))
        start_dt = datetime(year, month, day)
        end_dt = start_dt + timedelta(days=6)
        
        # Get planetary positions for middle of week
        mid_date = (start_dt + timedelta(days=3)).strftime("%d/%m/%Y")
        planet_positions = get_planetary_positions(mid_date)
        
        # Calculate aspects
        aspects = calculate_aspects(planet_positions, zodiac)
        
        # Generate seed
        seed = f"{start_date}-week-{zodiac_name}"
        
        # Generate weekly scores (slightly more stable than daily)
        random.seed(seed)
        favorable_count = len(aspects["favorable"])
        challenging_count = len(aspects["challenging"])
        base_score = 50 + (favorable_count * 5) - (challenging_count * 3)
        
        weekly_summary = {
            "overview": "",
            "key_focus": [],
            "opportunities": [],
            "challenges": [],
            "advice": ""
        }
        
        # Generate overview based on score
        if base_score >= 70:
            weekly_summary["overview"] = f"An excellent week ahead for {zodiac_name}! The planetary alignments support growth and success across multiple life areas."
        elif base_score >= 45:
            weekly_summary["overview"] = f"A balanced week for {zodiac_name}. Mix of opportunities and minor challenges requiring steady navigation."
        else:
            weekly_summary["overview"] = f"A challenging week for {zodiac_name}. Focus on patience and careful planning to navigate obstacles successfully."
        
        # Key focus areas
        focus_areas = ["career development", "relationship harmony", "financial planning", 
                      "health maintenance", "spiritual growth"]
        weekly_summary["key_focus"] = random.sample(focus_areas, 3)
        
        # Opportunities and challenges based on aspects
        if aspects["favorable"]:
            weekly_summary["opportunities"] = [
                f"Leverage {aspects['favorable'][0]} for personal growth",
                "Networking and collaborations bring positive outcomes",
                "Creative projects receive favorable cosmic support"
            ]
        
        if aspects["challenging"]:
            weekly_summary["challenges"] = [
                f"Navigate {aspects['challenging'][0]} with patience",
                "Minor delays possible in planned activities",
                "Communication requires extra clarity"
            ]
        
        # Advice
        advice_templates = [
            "Stay flexible and adapt to changing circumstances throughout the week.",
            "Trust your intuition when making important decisions.",
            "Balance work commitments with personal well-being.",
            "Strengthen relationships through open and honest communication.",
            "Focus on long-term goals rather than short-term setbacks."
        ]
        weekly_summary["advice"] = random.choice(advice_templates)
        
        return {
            "zodiac_sign": zodiac_name.lower(),
            "week_start": start_date,
            "week_end": end_dt.strftime("%d/%m/%Y"),
            "weekly_summary": weekly_summary,
            "planetary_aspects": aspects
        }
        
    except Exception as e:
        raise Exception(f"Error generating weekly horoscope: {str(e)}")


def generate_monthly_horoscope(zodiac: int, month: int, year: int) -> Dict[str, Any]:
    """
    Generate monthly horoscope for a zodiac sign
    
    Args:
        zodiac: Zodiac sign number (1-12)
        month: Month number (1-12)
        year: Year
        
    Returns:
        Monthly horoscope dictionary
    """
    try:
        zodiac_info = ZODIAC_SIGNS[zodiac]
        zodiac_name = zodiac_info["name"]
        
        # Get planetary positions for middle of month
        mid_date = f"15/{month:02d}/{year}"
        planet_positions = get_planetary_positions(mid_date)
        
        # Calculate aspects
        aspects = calculate_aspects(planet_positions, zodiac)
        
        # Generate seed
        seed = f"{month}-{year}-month-{zodiac_name}"
        random.seed(seed)
        
        # Monthly themes
        themes = {
            "primary": "",
            "secondary": [],
            "lucky_dates": [],
            "challenging_dates": []
        }
        
        primary_themes = [
            "Career advancement and professional recognition",
            "Relationship deepening and emotional connections",
            "Financial growth and material security",
            "Personal transformation and self-discovery",
            "Health improvement and vitality enhancement",
            "Creative expression and artistic pursuits",
            "Spiritual awakening and inner wisdom",
            "Social expansion and community building"
        ]
        
        themes["primary"] = random.choice(primary_themes)
        themes["secondary"] = random.sample([t for t in primary_themes if t != themes["primary"]], 2)
        
        # Generate lucky and challenging dates
        all_dates = list(range(1, 29))  # Simplified to avoid month-end variations
        themes["lucky_dates"] = sorted(random.sample(all_dates, 5))
        themes["challenging_dates"] = sorted(random.sample([d for d in all_dates if d not in themes["lucky_dates"]], 3))
        
        # Month overview by weeks
        week_overview = {}
        for week in range(1, 5):
            favorable_count = len(aspects["favorable"])
            score = random.randint(45, 85) + (favorable_count * 2)
            
            if score >= 70:
                week_overview[f"week_{week}"] = "Highly favorable - pursue important goals"
            elif score >= 50:
                week_overview[f"week_{week}"] = "Moderately positive - steady progress expected"
            else:
                week_overview[f"week_{week}"] = "Exercise patience - focus on consolidation"
        
        month_names = ["January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]
        
        return {
            "zodiac_sign": zodiac_name.lower(),
            "month": month_names[month - 1],
            "year": year,
            "themes": themes,
            "week_by_week": week_overview,
            "planetary_influences": {
                "favorable": aspects["favorable"],
                "challenging": aspects["challenging"]
            },
            "overall_rating": random.randint(60, 90)
        }
        
    except Exception as e:
        raise Exception(f"Error generating monthly horoscope: {str(e)}")