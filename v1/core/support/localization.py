"""
Localization support for Jyotish API.
Stores text translations for supported languages.
"""

from typing import Dict

# Supported languages
# en: English
# hi: Hindi
# bn: Bengali
# ml: Malayalam
# mr: Marathi
# gu: Gujarati
# te: Telugu
# ta: Tamil

DEFAULT_LANGUAGE = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "welcome": "Welcome to Jyotish API",
        "error_generic": "An error occurred",
        "success": "Success",
        
        # Planets
        "sun": "Sun",
        "moon": "Moon",
        "mars": "Mars",
        "mercury": "Mercury",
        "jupiter": "Jupiter",
        "venus": "Venus",
        "saturn": "Saturn",
        "rahu": "Rahu",
        "ketu": "Ketu",
        
        # Zodiac signs
        "aries": "Aries",
        "taurus": "Taurus",
        "gemini": "Gemini",
        "cancer": "Cancer",
        "leo": "Leo",
        "virgo": "Virgo",
        "libra": "Libra",
        "scorpio": "Scorpio",
        "sagittarius": "Sagittarius",
        "capricorn": "Capricorn",
        "aquarius": "Aquarius",
        "pisces": "Pisces",
        
        # Days of week (Vara)
        "sunday": "Sunday",
        "monday": "Monday",
        "tuesday": "Tuesday",
        "wednesday": "Wednesday",
        "thursday": "Thursday",
        "friday": "Friday",
        "saturday": "Saturday",
        
        # Tithi names
        "pratipada": "Pratipada",
        "dwitiya": "Dwitiya",
        "tritiya": "Tritiya",
        "chaturthi": "Chaturthi",
        "panchami": "Panchami",
        "shashthi": "Shashthi",
        "saptami": "Saptami",
        "ashtami": "Ashtami",
        "navami": "Navami",
        "dashami": "Dashami",
        "ekadashi": "Ekadashi",
        "dwadashi": "Dwadashi",
        "trayodashi": "Trayodashi",
        "chaturdashi": "Chaturdashi",
        "purnima": "Purnima",
        "amavasya": "Amavasya",
        
        # Paksha
        "shukla_paksha": "Shukla Paksha",
        "krishna_paksha": "Krishna Paksha",
        
        # Nakshatra names
        "ashwini": "Ashwini",
        "bharani": "Bharani",
        "krittika": "Krittika",
        "rohini": "Rohini",
        "mrigashira": "Mrigashira",
        "ardra": "Ardra",
        "punarvasu": "Punarvasu",
        "pushya": "Pushya",
        "ashlesha": "Ashlesha",
        "magha": "Magha",
        "purva_phalguni": "Purva Phalguni",
        "uttara_phalguni": "Uttara Phalguni",
        "hasta": "Hasta",
        "chitra": "Chitra",
        "swati": "Swati",
        "vishakha": "Vishakha",
        "anuradha": "Anuradha",
        "jyeshtha": "Jyeshtha",
        "mula": "Mula",
        "purva_ashadha": "Purva Ashadha",
        "uttara_ashadha": "Uttara Ashadha",
        "shravana": "Shravana",
        "dhanishta": "Dhanishta",
        "shatabhisha": "Shatabhisha",
        "purva_bhadrapada": "Purva Bhadrapada",
        "uttara_bhadrapada": "Uttara Bhadrapada",
        "revati": "Revati",
        
        # Yoga names
        "vishkambha": "Vishkambha",
        "priti": "Priti",
        "ayushman": "Ayushman",
        "saubhagya": "Saubhagya",
        "shobhana": "Shobhana",
        "atiganda": "Atiganda",
        "sukarman": "Sukarman",
        "dhriti": "Dhriti",
        "shula": "Shula",
        "ganda": "Ganda",
        "vriddhi": "Vriddhi",
        "dhruva": "Dhruva",
        "vyaghata": "Vyaghata",
        "harshana": "Harshana",
        "vajra": "Vajra",
        "siddhi": "Siddhi",
        "vyatipata": "Vyatipata",
        "variyan": "Variyan",
        "parigha": "Parigha",
        "shiva": "Shiva",
        "siddha": "Siddha",
        "sadhya": "Sadhya",
        "shubha": "Shubha",
        "shukla": "Shukla",
        "brahma": "Brahma",
        "indra": "Indra",
        "vaidhriti": "Vaidhriti",
        
        # Karana names
        "bava": "Bava",
        "balava": "Balava",
        "kaulava": "Kaulava",
        "taitila": "Taitila",
        "garaja": "Garaja",
        "vanija": "Vanija",
        "vishti": "Vishti",
        "shakuni": "Shakuni",
        "chatushpada": "Chatushpada",
        "naga": "Naga",
        "kimstughna": "Kimstughna",
        
        # Month names
        "chaitra": "Chaitra",
        "vaishakha": "Vaishakha",
        "jyeshtha": "Jyeshtha",
        "ashadha": "Ashadha",
        "shravana": "Shravana",
        "bhadrapada": "Bhadrapada",
        "ashwin": "Ashwin",
        "kartika": "Kartika",
        "margashirsha": "Margashirsha",
        "pausha": "Pausha",
        "magha": "Magha",
        "phalguna": "Phalguna",
        
        # Ritu (Seasons)
        "vasanta": "Vasanta",
        "grishma": "Grishma",
        "varsha": "Varsha",
        "sharada": "Sharada",
        "hemanta": "Hemanta",
        "shishira": "Shishira",
        
        # Ayana
        "uttarayana": "Uttarayana",
        "dakshinayana": "Dakshinayana",
        
        # Common terms
        "sunrise": "Sunrise",
        "sunset": "Sunset",
        "moonrise": "Moonrise",
        "moonset": "Moonset",
        "rahukaal": "Rahu Kaal",
        "gulika": "Gulika Kaal",
        "yamaganda": "Yamaganda Kaal",
        "abhijit_muhurta": "Abhijit Muhurta",
        "vara": "Vara",
        "tithi": "Tithi",
        "nakshatra": "Nakshatra",
        "yoga": "Yoga",
        "karana": "Karana",
        "masa": "Masa",
        "ritu": "Ritu",
        "paksha": "Paksha",
        "auspicious": "Auspicious",
        "inauspicious": "Inauspicious",
        "next_tithi": "Next Tithi",
        "next_nakshatra": "Next Nakshatra",
        "next_yoga": "Next Yoga",
        "next_karana": "Next Karana",
        
        # Deity names
        "shiva": "Shiva",
        "vishnu": "Vishnu",
        "brahma": "Brahma",
        "varuna": "Varuna",
        "indra": "Indra",
        "agni": "Agni",
        "yama": "Yama",
        "kaali": "Kaali",
        "kalyuga": "Kalyuga",
        
        # Tithi meanings
        "tithi_meaning_pratipada": "First day after new moon or full moon.",
        "tithi_special_pratipada": "Good for starting new ventures.",
        "tithi_meaning_dwitiya": "Second day after new moon or full moon.",
        "tithi_special_dwitiya": "Good for peaceful activities.",
        "tithi_meaning_tritiya": "Third day after new moon or full moon.",
        "tithi_special_tritiya": "Excellent for beginnings and creative work.",
        "tithi_meaning_chaturthi": "Fourth day after new moon or full moon.",
        "tithi_special_chaturthi": "Auspicious for removing obstacles.",
        "tithi_meaning_panchami": "Fifth day after new moon or full moon.",
        "tithi_special_panchami": "Good for learning and intellectual pursuits.",
        "tithi_meaning_shashthi": "Sixth day after new moon or full moon.",
        "tithi_special_shashthi": "Favorable for overcoming enemies.",
        "tithi_meaning_saptami": "Seventh day after new moon or full moon.",
        "tithi_special_saptami": "Good for spiritual practices.",
        "tithi_meaning_ashtami": "Eighth day after new moon or full moon.",
        "tithi_special_ashtami": "Powerful day for worship and meditation.",
        "tithi_meaning_navami": "Ninth day after new moon or full moon.",
        "tithi_special_navami": "Auspicious for religious ceremonies.",
        "tithi_meaning_dashami": "Tenth day after new moon or full moon.",
        "tithi_special_dashami": "Good for all auspicious activities.",
        "tithi_meaning_ekadashi": "Eleventh day after new moon or full moon.",
        "tithi_special_ekadashi": "Sacred day for fasting and spiritual practices.",
        "tithi_meaning_dwadashi": "Twelfth day after new moon or full moon.",
        "tithi_special_dwadashi": "Favorable for all good works.",
        "tithi_meaning_trayodashi": "Thirteenth day after new moon or full moon.",
        "tithi_special_trayodashi": "Good for material pursuits.",
        "tithi_meaning_chaturdashi": "Fourteenth day after Purnima or Amavasya.",
        "tithi_special_chaturdashi": "Good for work related to spiritual practices and seeking blessings.",
        "tithi_meaning_purnima": "Full moon day.",
        "tithi_special_purnima": "Highly auspicious for prayers and spiritual activities.",
        "tithi_meaning_amavasya": "New moon day.",
        "tithi_special_amavasya": "Important for ancestor worship.",
        
        "birth_chart_interpretation": "The Birth Chart, or Lagna Chart (D1), is the most fundamental map of the heavens at the exact moment of your birth.",
        "moon_chart_interpretation": "The Moon Chart, or Chandra Kundali, places the Moon in the first house and is analyzed to understand your emotional nature.",
        "navamsa_chart_interpretation": "The Navamsa Chart (D9) is the most important divisional chart, used to assess the strength and dignity of planets.",
    },
    "hi": {
        "welcome": "ज्योतिष एपीआई में आपका स्वागत है",
        "sun": "सूर्य",
        "moon": "चंद्रमा",
        "mars": "मंगल",
        "mercury": "बुध",
        "jupiter": "बृहस्पति",
        "venus": "शुक्र",
        "saturn": "शनि",
        "rahu": "राहु",
        "ketu": "केतु",
        "sunday": "रविवार",
        "monday": "सोमवार",
        "tuesday": "मंगलवार",
        "wednesday": "बुधवार",
        "thursday": "गुरुवार",
        "friday": "शुक्रवार",
        "saturday": "शनिवार",
    },
}

def get_text(key: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Retrieve text for a specific key and language.
    Falls back to default language if translation is missing.
    """
    if not lang:
        lang = DEFAULT_LANGUAGE
        
    lang = lang.lower()
    if lang not in TRANSLATIONS:
        lang = DEFAULT_LANGUAGE
    
    lang_dict = TRANSLATIONS.get(lang, {})
    default_dict = TRANSLATIONS.get(DEFAULT_LANGUAGE, {})
    
    if key in lang_dict:
        return lang_dict[key]
    
    if key in default_dict:
        return default_dict[key]
        
    return key


def get_localized_name(name: str, lang: str = DEFAULT_LANGUAGE) -> str:
    """
    Get localized name by converting to lowercase and replacing spaces
    """
    key = name.lower().replace(" ", "_")
    return get_text(key, lang)