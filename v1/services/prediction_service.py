"""
services/prediction_service.py
--------------------------------
Horoscope and prediction logic extracted from api.py.
Routers call these functions and only handle HTTP shaping.
"""

import random
import logging
import swisseph as swe
from datetime import datetime
from typing import Dict

from support.horoscope import (
    generate_daily_horoscope,
    generate_weekly_horoscope,
    generate_monthly_horoscope,
)

logger = logging.getLogger(__name__)

# ── Daily / Weekly / Monthly horoscope ───────────────────────────────────────

def get_daily_horoscope(zodiac: int, date: str):
    return generate_daily_horoscope(zodiac, date)

def get_weekly_horoscope(zodiac: int, start_date: str):
    return generate_weekly_horoscope(zodiac, start_date)

def get_monthly_horoscope(zodiac: int, month: int, year: int):
    return generate_monthly_horoscope(zodiac, month, year)


# ── Daily nakshatra prediction ────────────────────────────────────────────────

_NAKSHATRA_NAMES = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purvaphalguni","Uttaraphalguni",
    "Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
    "Purvashadha","Uttarashadha","Sravana","Dhanista","Shatabhisha",
    "Purvabhadra","Uttarabhadra","Revati",
]

_NAKSHATRA_COLORS = [
    ("pale-red","#FFB8BE"),("saffron","#F4C430"),("white","#FFFFFF"),
    ("silver","#C0C0C0"),("green","#008000"),("blue","#0000FF"),
    ("gold","#FFD700"),("yellow","#FFFF00"),("purple","#800080"),
    ("maroon","#800000"),("pink","#FFC0CB"),("orange","#FFA500"),
    ("teal","#008080"),("navy","#000080"),("brown","#A52A2A"),
    ("olive","#808000"),("indigo","#4B0082"),("cyan","#00FFFF"),
    ("magenta","#FF00FF"),("violet","#EE82EE"),("beige","#F5F5DC"),
    ("coral","#FF7F50"),("khaki","#F0E68C"),("lavender","#E6E6FA"),
    ("salmon","#FA8072"),("turquoise","#40E0D0"),("black","#000000"),
]

_NAKSHATRA_MSGS = {
    "physique"    : "A sublime aura will envelop you, making your presence enchanting wherever you go.",
    "status"      : "Kindness and consideration will mark your words, shaping you into an influential figure.",
    "finances"    : "Exercise caution in money transactions to avoid fraudulent schemes.",
    "relationship": "You'll make an enduring mark on your partner's heart with your genuine commitment.",
    "career"      : "Consider adding new shareholders to capitalise on expanding business opportunities.",
    "travel"      : "A short travel opportunity may arise — cherish it as a memory.",
    "family"      : "Travel and journeys will bring prosperity. Consider a family trip.",
    "friends"     : "Distinguishing true friends from those who seek personal gain will help prune your circle.",
    "health"      : "Vigilance concerning respiratory health is advisable. Early consultation will help.",
    "total_score" : "Anticipate a day of discovery. Engage in self-reflection to uncover new interests.",
}

def get_nakshatra_prediction(nakshatra: int, dob: str, lang: str = "en") -> dict:
    if nakshatra < 1 or nakshatra > 27:
        raise ValueError("nakshatra must be between 1 and 27")

    color_name, color_code = _NAKSHATRA_COLORS[nakshatra - 1]
    random.seed(f"{nakshatra}-{dob}-{lang}")

    scores = {k: random.randint(50, 99) for k in _NAKSHATRA_MSGS}
    bot_response = {k: {"score": scores[k], "split_response": v}
                    for k, v in _NAKSHATRA_MSGS.items()}

    return {
        "lucky_color"     : color_name,
        "lucky_color_code": color_code,
        "lucky_number"    : [random.randint(1, 40), random.randint(1, 40)],
        "bot_response"    : bot_response,
        "nakshatra"       : _NAKSHATRA_NAMES[nakshatra - 1].lower(),
    }


# ── Daily sun prediction ──────────────────────────────────────────────────────

_ZODIAC_NAMES = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

_LUCKY_COLORS: Dict[str, list] = {
    "Aries"      : [("Red","#FF0000"),("Orange","#FFA500"),("White","#FFFFFF")],
    "Taurus"     : [("Green","#008000"),("Pink","#FFC0CB"),("White","#FFFFFF")],
    "Gemini"     : [("Yellow","#FFFF00"),("Green","#008000"),("Orange","#FFA500")],
    "Cancer"     : [("White","#FFFFFF"),("Silver","#C0C0C0"),("Cream","#FFFDD0")],
    "Leo"        : [("Gold","#FFD700"),("Orange","#FFA500"),("Red","#FF0000")],
    "Virgo"      : [("Green","#008000"),("Brown","#A52A2A"),("White","#FFFFFF")],
    "Libra"      : [("Blue","#0000FF"),("Pink","#FFC0CB"),("White","#FFFFFF")],
    "Scorpio"    : [("Red","#FF0000"),("Black","#000000"),("Maroon","#800000")],
    "Sagittarius": [("Purple","#800080"),("Blue","#0000FF"),("Yellow","#FFFF00")],
    "Capricorn"  : [("Black","#000000"),("Brown","#A52A2A"),("Grey","#808080")],
    "Aquarius"   : [("Blue","#0000FF"),("Silver","#C0C0C0"),("Grey","#808080")],
    "Pisces"     : [("Sea Green","#2E8B57"),("Purple","#800080"),("White","#FFFFFF")],
}

_SUN_TEMPLATES = {
    "physique"    : ["Your energy levels are high — perfect for fitness goals.",
                     "Your natural charm will be at its peak, attracting positive attention."],
    "status"      : ["Your reputation will grow stronger today.",
                     "Recognition for your hard work is coming."],
    "finances"    : ["Financial opportunities knock — stay alert for investment prospects.",
                     "Money matters stabilise. Review your budget strategically."],
    "relationship": ["Deep connections strengthen today.",
                     "Communication flows easily in romantic matters."],
    "career"      : ["Leadership opportunities emerge today.",
                     "Strategic thinking pays off — planning yields impressive gains."],
    "travel"      : ["Even a short journey will refresh your spirit.",
                     "Travel plans made today will be fortunate."],
    "family"      : ["Family harmony prevails today.",
                     "A family member may seek your advice."],
    "friends"     : ["Social circles expand today.",
                     "Your generosity will be returned manifold."],
    "health"      : ["Listen to your body's signals and rest when needed.",
                     "Physical activity brings unexpected benefits today."],
    "total_score" : ["The stars align favourably — embrace opportunities with confidence.",
                     "Balance and harmony characterise your day."],
}

def get_sun_prediction(zodiac: int, date: str,
                       prediction_type: str = "big", lang: str = "en") -> dict:
    if zodiac < 1 or zodiac > 12:
        raise ValueError("zodiac must be between 1 and 12")

    dt      = datetime.strptime(date, "%d/%m/%Y")
    zname   = _ZODIAC_NAMES[zodiac - 1]
    seed    = f"{dt.strftime('%Y-%m-%d')}-{zname}"

    swe.set_ephe_path('.')
    jd      = swe.julday(dt.year, dt.month, dt.day, 12.0)
    sun_pos = swe.calc_ut(jd, swe.SUN)[0][0]
    moon_pos= swe.calc_ut(jd, swe.MOON)[0][0]

    random.seed(seed)
    aspect          = abs((sun_pos - moon_pos + 180) % 360 - 180)
    aspect_strength = 100 - (aspect / 180 * 100)

    scores = {k: min(99, int(50 + aspect_strength * 0.35 + random.randint(0, 30)))
              for k in _SUN_TEMPLATES}
    scores["total_score"] = sum(scores.values()) // len(scores)

    colors    = _LUCKY_COLORS.get(zname, [("White","#FFFFFF")])
    lc_name, lc_code = colors[hash(seed) % len(colors)]

    random.seed(hash(seed) % 1000)
    bot_response = {}
    for cat, templates in _SUN_TEMPLATES.items():
        txt = random.choice(templates)
        if prediction_type == "small":
            txt = txt.split(".")[0] + "."
        bot_response[cat] = {"score": scores[cat], "split_response": txt}

    random.seed(hash(seed) % 10000)
    lucky_number = sorted(random.sample(range(1, 100), 2))

    return {
        "lucky_color"     : lc_name.lower(),
        "lucky_color_code": lc_code,
        "lucky_number"    : lucky_number,
        "bot_response"    : bot_response,
        "zodiac"          : zname,
    }
