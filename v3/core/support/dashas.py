#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# dashas.py -- module for Dasha computation. All Dahsa data computed for given birth details handled here.
#   Dashas [Vimshottari etc]
# 
# Copyright (C) 2022 Shyam Bhat  <vicharavandana@gmail.com>
# Downloaded from "https://github.com/VicharaVandana/jyotishyam.git"
#
# This file is part of the "jyotishyam" Python library
# for computing Hindu jataka with sidereal lahiri ayanamsha technique 
# using swiss ephemeries
#

#import necessary modules
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import support.mod_astrodata as data
from support.mod_general import *

#necessary definitions and constructs for Dasha
dashaVimshottariSkeleton = {"Venus":{   "Nakshatras": ["Bharani", "Purva Phalguni", "Purva Ashadha"],
                                        "duration"  : 20, #20 years out of 120 years
                                        "percentage": (20.0/120),
                                        "prev-dasha": "Ketu",
                                        "next-dasha": "Sun"
                                    },
                            "Sun":  {   "Nakshatras": ["Kritika", "Uttara Phalguni", "Uttara Ashadha"],
                                        "duration"  : 6, #6 years out of 120 years
                                        "percentage": (6.0/120),
                                        "prev-dasha": "Venus",
                                        "next-dasha": "Moon"
                                    },
                            "Moon": {   "Nakshatras": ["Rohini", "Hasta", "Shravana"],
                                        "duration"  : 10, #10 years out of 120 years
                                        "percentage": (10.0/120),
                                        "prev-dasha": "Sun",
                                        "next-dasha": "Mars"
                                    },
                            "Mars": {   "Nakshatras": ["Mrigashira", "Chitra", "Dhanishta"],
                                        "duration"  : 7, #7 years out of 120 years
                                        "percentage": (7.0/120),
                                        "prev-dasha": "Moon",
                                        "next-dasha": "Rahu"
                                    },
                            "Rahu": {   "Nakshatras": ["Ardra", "Swati", "Shatabhishak"],
                                        "duration"  : 18, #18 years out of 120 years
                                        "percentage": (18.0/120),
                                        "prev-dasha": "Mars",
                                        "next-dasha": "Jupiter"
                                    },
                            "Jupiter": {"Nakshatras": ["Punarvasu", "Vishaka", "Purva Ashadha"],
                                        "duration"  : 16, #16 years out of 120 years
                                        "percentage": (16.0/120),
                                        "prev-dasha": "Rahu",
                                        "next-dasha": "Saturn"
                                    },
                            "Saturn": { "Nakshatras": ["Pushya", "Anurada", "Uttara Bhadrapada"],
                                        "duration"  : 19, #19 years out of 120 years
                                        "percentage": (19.0/120),
                                        "prev-dasha": "Jupiter",
                                        "next-dasha": "Mercury"
                                      },
                            "Mercury": {"Nakshatras": ["Ashlesha", "Jyeshta", "Revati"],
                                        "duration"  : 17, #17 years out of 120 years
                                        "percentage": (17.0/120),
                                        "prev-dasha": "Saturn",
                                        "next-dasha": "Ketu"
                                    },
                            "Ketu": {   "Nakshatras": ["Ashwini", "Magha", "Mula"],
                                        "duration"  : 7, #7 years out of 120 years
                                        "percentage": (7.0/120),
                                        "prev-dasha": "Mercury",
                                        "next-dasha": "Venus"
                                    }
                            }

#Takes Moon longitude in seconds, Dasha lord and Birth date and gives the start date of Dasha lords dasha
def computeStartDate_FirstDashaLord(lngsecondsMoon, dashaLord, birthDate):
    #lenth of a nakshatra in seconds is 13deg x 3600 + 20min x 60
    l_nakLenseconds = ((13*3600)+(20*60))
    #dasha lord dasha duration in days
    l_dashaDurationDays = 365.25 * dashaVimshottariSkeleton[dashaLord]["duration"]
    #How much moon has progressed into the nakshatra in seconds 
    l_deltalngseconds = lngsecondsMoon % l_nakLenseconds

    #calculate how many days have passed on birthday since dasha lord started his dasha
    l_elapsedDashaDurationDays = ((l_deltalngseconds * l_dashaDurationDays) / l_nakLenseconds)
    ##print(f'elapsed duration in days is {l_elapsedDashaDurationDays}')
    #Calculate the start date of dasha from subtracting elapsed date from birthday
    l_dashaStartDate = birthDate - timedelta(days=l_elapsedDashaDurationDays)

    return(l_dashaStartDate)

vimshottariDasha = []
mahadashaPlanetEntry = {
                        "name": "",
                        "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "entryString": "",
                        "level": "mahadasha",
                        "sublevel": "antardasha",
                        "antardasha" : []   #contains array of Antardasha planet entries
                        }
antardashaPlanetEntry = {
                        "name": "",
                        "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "entryString": "",
                        "level": "antardasha",
                        "sublevel": "paryantardasha",
                        "paryantardasha" : []   #contains array of paryantardasha planet entries
                        }
paryantardashaPlanetEntry = {
                        "name": "",
                        "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                        "entryString": "",
                        "level": "paryantardasha",
                        "sublevel": "sookshma-antardasha",
                        #"paryantardasha" : []   #contains array of paryantardasha planet entries
                        }
#dashaStrings = []
#dashaCodeLines = []

def clearDashaDetails():
    #global dashaStrings
    #global dashaCodeLines
    global vimshottariDasha
    global mahadashaPlanetEntry
    global antardashaPlanetEntry
    global paryantardashaPlanetEntry
    #dashaStrings = []
    #dashaCodeLines = []
    vimshottariDasha = []
    mahadashaPlanetEntry = {
                            "name": "",
                            "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "entryString": "",
                            "level": "mahadasha",
                            "sublevel": "antardasha",
                            "antardasha" : []   #contains array of Antardasha planet entries
                            }.copy()
    antardashaPlanetEntry = {
                            "name": "",
                            "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "entryString": "",
                            "level": "antardasha",
                            "sublevel": "paryantardasha",
                            "paryantardasha" : []   #contains array of paryantardasha planet entries
                            }.copy()
    paryantardashaPlanetEntry = {
                            "name": "",
                            "startDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "endDate": datetime(year=1, month=1, day=1, hour=0, minute=0, second=0),
                            "entryString": "",
                            "level": "paryantardasha",
                            "sublevel": "sookshma-antardasha",
                            #"paryantardasha" : []   #contains array of paryantardasha planet entries
                            }.copy()
    return(True)
def computeVimshottariDasha(lngsecondsMoon, nakshatraLord, birthDate):
    #global dashaStrings
    #global dashaCodeLines
    global vimshottariDasha
    global mahadashaPlanetEntry
    global antardashaPlanetEntry
    global paryantardashaPlanetEntry
    idcnt = 0
    l_DashaStartDate = computeStartDate_FirstDashaLord(lngsecondsMoon, nakshatraLord, birthDate)
    currentDate = datetime.now()
    data.charts["Dashas"]["Vimshottari"]["current"]["date"] = str(currentDate)
    data.charts["Dashas"]["Vimshottari"]["current"]["dasha"] = ""
    data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"] = ""
    data.charts["Dashas"]["Vimshottari"]["current"]["paryantardasha"] = ""
    #print(f'start date is :{l_DashaStartDate}')
    l_firstPlanet = nakshatraLord
    l_wholeDuration = relativedelta(years=120)  #whole vimshottari dasha is for 120 years
    #compute Vimshottari table
    res_mahadasha = computeSubPeriods(l_DashaStartDate, l_firstPlanet, l_wholeDuration, "Mahadasha", birthDate)
    mahadasha_cnt = 0
    for item in res_mahadasha:
        mahadashaPlanetEntry["name"] = item["name"]
        mahadashaPlanetEntry["startDate"] = item["startDate"]
        mahadashaPlanetEntry["endDate"] = item["endDate"]
        mahadashaPlanetEntry["entryString"] = item["entryString"]
        #dashaStrings.append(f'Dasha: {item["entryString"]} iid={idcnt}, open=False')
        #dashaCodeLines.append(f'tree.insert("", END, text = "{item["entryString"]}", iid={idcnt}, open=False)')
        dashaIdx = idcnt
        antar_pos = 0
        idcnt = idcnt + 1
        #Adding Mahadasha details
        mahadasha_cnt = mahadasha_cnt + 1
        mahadashaPlanetName = mahadashaPlanetEntry["name"]
        l_mahadasha = {}
        l_mahadasha["lord"] = mahadashaPlanetName
        l_mahadasha["dashaNum"] = mahadasha_cnt
        l_mahadasha["startDate"] = str(item["startDate"])
        l_mahadasha["endDate"] = str(item["endDate"])
        startage = (item["startage"])
        endAge = (item["endage"])
        l_dur = (endAge-startage)      
        l_mahadasha["duration"] = f" {l_dur.years}yr {l_dur.months}m {l_dur.days}d"
        l_mahadasha["startage"] = f" {startage.years}yr {startage.months}m {startage.days}d"
        l_mahadasha["endage"] = f" {endAge.years}yr {endAge.months}m {endAge.days}d"
        l_mahadasha["antardasha"] = []
        if(currentDate >= item["startDate"]) and (currentDate < item["endDate"]):
            data.charts["Dashas"]["Vimshottari"]["current"]["dasha"] = l_mahadasha.copy()["lord"]
        
        data.charts["Dashas"]["Vimshottari"]["mahadashas"][mahadashaPlanetName] = l_mahadasha.copy()

        #for Antardasha
        l_DashaStartDate = item["startDate"]
        l_firstPlanet = item["name"]
        l_wholeDuration = item["endDate"] - item["startDate"]
        res_antardasha = computeSubPeriods(l_DashaStartDate, l_firstPlanet, l_wholeDuration, "Antardasha", birthDate)
        antardasha_cnt = 0
        for item2 in res_antardasha:
            antardashaPlanetEntry["name"] = item2["name"]
            antardashaPlanetEntry["startDate"] = item2["startDate"]
            antardashaPlanetEntry["endDate"] = item2["endDate"]
            antardashaPlanetEntry["entryString"] = item2["entryString"]
            #dashaStrings.append(f'  AntarDasha: {item2["entryString"]} iid={idcnt}, open=False')
            #dashaCodeLines.append(f'tree.insert("", END, text = "{item2["entryString"]}", iid={idcnt}, open=False)')
            antardashaIdx = idcnt
            #dashaCodeLines.append(f'tree.move({antardashaIdx}, {dashaIdx}, {antar_pos}) ')
            paryantar_pos = 0
            idcnt = idcnt + 1
            antar_pos = antar_pos + 1
            #Adding Antardasha details
            antardasha_cnt = antardasha_cnt + 1
            antardashaPlanetName = antardashaPlanetEntry["name"]
            l_antardasha = {}
            l_antardasha["lord"] = antardashaPlanetName
            l_antardasha["dashaLord"] = mahadashaPlanetName
            l_antardasha["bhuktiNum"] = antardasha_cnt
            l_antardasha["startDate"] = str(item2["startDate"])
            l_antardasha["endDate"] = str(item2["endDate"])
            startage = (item2["startage"])
            endAge = (item2["endage"])
            l_dur = relativedelta((birthDate+endAge), (birthDate+startage))         
            l_antardasha["duration"] = f" {l_dur.years}yr {l_dur.months}m {l_dur.days}d"
            l_antardasha["startage"] = f" {startage.years}yr {startage.months}m {startage.days}d"
            l_antardasha["endage"] = f" {endAge.years}yr {endAge.months}m {endAge.days}d"  
            if(currentDate >= item2["startDate"]) and (currentDate < item2["endDate"]):
                data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"] = l_antardasha.copy()["lord"]     
            data.charts["Dashas"]["Vimshottari"]["antardashas"][f'{mahadashaPlanetName}-{antardashaPlanetName}'] = l_antardasha.copy()
            l_mahadasha["antardasha"].append(l_antardasha.copy())

            #for Paryantardasha
            l_DashaStartDate = item2["startDate"]
            l_firstPlanet = item2["name"]
            l_wholeDuration = item2["endDate"] - item2["startDate"]
            res_paryantardasha = computeSubPeriods(l_DashaStartDate, l_firstPlanet, l_wholeDuration, "Antardasha", birthDate)
            paryantardasha_cnt = 0
            for item3 in res_paryantardasha:
                paryantardashaPlanetEntry["name"] = item3["name"]
                paryantardashaPlanetEntry["startDate"] = item3["startDate"]
                paryantardashaPlanetEntry["endDate"] = item3["endDate"]
                paryantardashaPlanetEntry["entryString"] = item3["entryString"]
                #dashaStrings.append(f'\tParyantarDasha: {item3["entryString"]} iid={idcnt}, open=False')
                #dashaCodeLines.append(f'tree.insert("", END, text = "{item3["entryString"]}", iid={idcnt}, open=False)')
                paryantardashaIdx = idcnt
                #dashaCodeLines.append(f'tree.move({paryantardashaIdx}, {antardashaIdx}, {paryantar_pos}) ')
                paryantar_pos = paryantar_pos + 1
                idcnt = idcnt + 1

                #Adding Paryantardasha details
                paryantardasha_cnt = paryantardasha_cnt + 1
                paryantardashaPlanetName = paryantardashaPlanetEntry["name"]
                l_paryantardasha = {}
                l_paryantardasha["lord"] = paryantardashaPlanetName
                l_paryantardasha["bhuktiLord"] = antardashaPlanetName
                l_paryantardasha["dashaLord"] = mahadashaPlanetName
                l_paryantardasha["pariNum"] = paryantardasha_cnt
                l_paryantardasha["startDate"] = str(item3["startDate"])
                l_paryantardasha["endDate"] = str(item3["endDate"])
                startage = (item3["startage"])
                endAge = (item3["endage"])
                l_dur = relativedelta((birthDate+endAge), (birthDate+startage))         
                l_paryantardasha["duration"] = f" {l_dur.years}yr {l_dur.months}m {l_dur.days}d"
                l_paryantardasha["startage"] = f" {startage.years}yr {startage.months}m {startage.days}d"
                l_paryantardasha["endage"] = f" {endAge.years}yr {endAge.months}m {endAge.days}d"       
                if(currentDate >= item3["startDate"]) and (currentDate < item3["endDate"]):
                    #print(f'''paryantar dasha {mahadashaPlanetName}-{antardashaPlanetName}-{paryantardashaPlanetName} ({currentDate} >= {item3["startDate"]}) and ({currentDate} > {item3["endDate"]})''')
                    data.charts["Dashas"]["Vimshottari"]["current"]["paryantardasha"] = l_paryantardasha.copy()["lord"]  
                data.charts["Dashas"]["Vimshottari"]["paryantardashas"][f'{mahadashaPlanetName}-{antardashaPlanetName}-{paryantardashaPlanetName}'] = l_paryantardasha.copy()

                antardashaPlanetEntry["paryantardasha"].append(item3.copy())

            mahadashaPlanetEntry["antardasha"].append(item2.copy())

        data.charts["Dashas"]["Vimshottari"]["mahadashas"][mahadashaPlanetName] = l_mahadasha.copy()
        vimshottariDasha.append(mahadashaPlanetEntry.copy())
        #print(item["entryString"])
    return


#Takes the start date and time and starting planets and whole duration and computes a set
#the set of sub periods of planets in that duration like planet name, its start date, end date, duration and age
def computeSubPeriods(startdate,firstPlanet,wholeDuration, level, birthday):
    l_dashaStartDate = startdate
    l_dashaEndDate = l_dashaStartDate + wholeDuration
    l_120thpart = ((l_dashaEndDate - l_dashaStartDate)/120)
    l_focusplanet = firstPlanet
    l_planetStartDate = l_dashaStartDate
    l_SubPeriods = []
    l_planetEntry = {
                        "name": "",
                        "startDate": l_dashaStartDate,
                        "endDate": l_dashaEndDate,
                        "entryString": ""
                    }
    #print(f'{level}s under planet {firstPlanet}')
    for lplanetnum in range(9):   #for all nine planets
        l_planetDuration = (dashaVimshottariSkeleton[l_focusplanet]["duration"] * l_120thpart)
        l_planetEndDate = (l_planetStartDate + l_planetDuration)
        l_durDays = int(str(l_planetDuration).split("days")[0].strip())
        startAge = relativedelta(l_planetStartDate, birthday)
        endAge = relativedelta(l_planetEndDate, birthday)
        if((startAge.years <= 0) and (startAge.months <= 0) and (startAge.days <= 0)):
            startAge.years = 0
            startAge.months = 0
            startAge.days = 0
        if((endAge.years >= 0) and (endAge.months >= 0) and (endAge.days >= 0)):
            l_planetEntry["name"] = l_focusplanet
            l_planetEntry["startDate"] = l_planetStartDate
            l_planetEntry["endDate"] = l_planetEndDate
            l_planetEntry["duration"] = l_planetDuration
            l_planetEntry["startage"] = startAge
            l_planetEntry["endage"] = endAge
            l_planetEntry["entryString"] = f'{l_focusplanet} - ({str(l_planetStartDate)[:-4]}) to ({str(l_planetEndDate)[:-4]}) ({l_durDays} days) Age[({endAge.years}year {endAge.months}month {endAge.days}days)]'
            l_SubPeriods.append(l_planetEntry.copy())
            #print(f'{l_focusplanet} - ({l_planetStartDate}) to ({l_planetEndDate}) ({l_durDays} days) Age[({endAge.years}year {endAge.months}month{endAge.days}days)]')
        #setup needed for moving to next planet in chain
        l_planetStartDate = l_planetEndDate
        l_focusplanet = dashaVimshottariSkeleton[l_focusplanet]["next-dasha"]
    return(l_SubPeriods)

def Vimshottari(division, birthdata):
    moonlngsec = (((signnum(division["planets"]["Moon"]["sign"])-1) * 30 * 3600) + 
                  ((division["planets"]["Moon"]["pos"]["deg"]) * 3600) + 
                  ((division["planets"]["Moon"]["pos"]["min"]) * 60) + 
                  (division["planets"]["Moon"]["pos"]["sec"]))

    nakshatraLord = division["planets"]["Moon"]["nak-ruler"]

    bdaytime = datetime(year=birthdata["DOB"]["year"], 
                        month=birthdata["DOB"]["month"], 
                        day=birthdata["DOB"]["day"], 
                        hour=birthdata["TOB"]["hour"], 
                        minute=birthdata["TOB"]["min"], 
                        second=birthdata["TOB"]["sec"])

    computeVimshottariDasha(moonlngsec, nakshatraLord, bdaytime)
    #print(vimshottariDasha)
    return

# Yogini Dasha definitions
yoginiDashaSkeleton = {
    "Mangala": {"duration": 1, "deity": "Dakini", "element": "Fire"},
    "Sasi": {"duration": 2, "deity": "Rangini", "element": "Earth"},
    "Ravi": {"duration": 3, "deity": "Kakini", "element": "Fire"},
    "Budha": {"duration": 4, "deity": "Shakini", "element": "Air"},
    "Shukra": {"duration": 5, "deity": "Yamuna", "element": "Water"},
    "Kuja": {"duration": 6, "deity": "Sankata", "element": "Fire"},
    "Guru": {"duration": 7, "deity": "Pingala", "element": "Ether"},
    "Shani": {"duration": 8, "deity": "Dhanya", "element": "Air"}
}

# Chara Dasha definitions
charaDashaSequence = [
"Aries","Taurus","Gemini","Cancer","Leo","Virgo",
"Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]
# Mahadasha Predictions - Returns predictions for a specific Mahadasha
def getMahadashaPredictions(planet_name):
    predictions = {
        "Sun": {
            "general": "Period of authority, leadership, and recognition. Focus on career advancement and government relations.",
            "favorable": "Government service, administrative roles, leadership positions.",
            "challenges": "Health issues related to heart, eyes, or vitality. Ego conflicts possible.",
            "remedies": "Worship of Lord Shiva, donate wheat, jaggery, copper, and wear ruby."
        },
        "Moon": {
            "general": "Period of emotional growth, intuition, and public recognition. Good for creative pursuits.",
            "favorable": "Travel, public relations, creative arts, dealing with liquids or public.",
            "challenges": "Emotional instability, water-related problems, issues with mother or women.",
            "remedies": "Worship of Goddess Parvati, donate rice, silver, milk, and wear pearl."
        },
        "Mars": {
            "general": "Period of courage, energy, and technical skills. Good for property and land matters.",
            "favorable": "Technical fields, military, sports, surgery, real estate, engineering.",
            "challenges": "Accidents, injuries, conflicts, blood-related ailments, impulsiveness.",
            "remedies": "Worship of Lord Hanuman, donate red lentils, copper items, and wear coral."
        },
        "Rahu": {
            "general": "Period of unconventional growth, foreign connections, and sudden changes.",
            "favorable": "Foreign travel, occult sciences, research, unconventional careers.",
            "challenges": "Deception, confusion, phobias, respiratory issues, poisoning.",
            "remedies": "Worship of Lord Ganesha, donate goat, blue items, and wear hessonite."
        },
        "Jupiter": {
            "general": "Period of wisdom, education, spirituality, and expansion. Good for finances.",
            "favorable": "Teaching, counseling, banking, law, publishing, religious activities.",
            "challenges": "Overindulgence, liver problems, weight gain, excessive optimism.",
            "remedies": "Worship of Lord Vishnu, donate yellow items, gol d, turmeric, and wear yellow sapphire."
        },
        "Saturn": {
            "general": "Period of discipline, hard work, and delayed rewards. Focus on long-term goals.",
            "favorable": "Government service, mining, oil, agriculture, labor-intensive work.",
            "challenges": "Delays, obstacles, chronic ailments, joint pains, depression.",
            "remedies": "Worship of Lord Hanuman and Shani, donate black items, iron, and wear blue sapphire."
        },
        "Mercury": {
            "general": "Period of communication, intellect, and business acumen. Good for education.",
            "favorable": "Writing, teaching, accounting, trading, communication, technology.",
            "challenges": "Nervousness, speech problems, skin issues, overthinking.",
            "remedies": "Worship of Lord Vishnu, donate green items, emerald, and wear emerald."
        },
        "Ketu": {
            "general": "Period of spiritual growth, detachment, and sudden changes. Focus on liberation.",
            "favorable": "Spiritual pursuits, healing, research, technical fields, occult sciences.",
            "challenges": "Isolation, confusion, mysterious ailments, accidents.",
            "remedies": "Worship of Lord Ganesha, donate goat, multicolored items, and wear cat's eye."
        },
        "Venus": {
            "general": "Period of luxury, relationships, arts, and sensual pleasures. Good for marriage.",
            "favorable": "Arts, entertainment, luxury items, beauty industry, relationships.",
            "challenges": "Overindulgence, reproductive issues, kidney problems, laziness.",
            "remedies": "Worship of Goddess Lakshmi, donate white items, silver, and wear diamond."
        }
    }
    
    if planet_name in predictions:
        return predictions[planet_name]
    else:
        return {
            "general": "No specific predictions available for this planet.",
            "favorable": "Consult an astrologer for personalized guidance.",
            "challenges": "Consult an astrologer for personalized guidance.",
            "remedies": "Consult an astrologer for personalized guidance."
        }

# Current Mahadasha - Returns the current Mahadasha lord
def getCurrentMahadasha():
    currentDate = datetime.now()
    current_dasha = data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
    if current_dasha:
        return {
            "lord": current_dasha,
            "predictions": getMahadashaPredictions(current_dasha)
        }
    return {"lord": "Unknown", "predictions": {}}

# Current Mahadasha Full - Returns complete details of current Mahadasha
def getCurrentMahaDashaFull():
    currentDate = datetime.now()
    current_dasha = data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
    
    if current_dasha and current_dasha in data.charts["Dashas"]["Vimshottari"]["mahadashas"]:
        mahadasha_details = data.charts["Dashas"]["Vimshottari"]["mahadashas"][current_dasha]
        mahadasha_details["predictions"] = getMahadashaPredictions(current_dasha)
        return mahadasha_details
    
    return {"lord": "Unknown", "predictions": {}}

# Get Specific Dasha - Returns details for a specific Dasha period
def getSpecificDasha(dasha_lord, date=None):
    if not date:
        date = datetime.now()
    
    if dasha_lord in data.charts["Dashas"]["Vimshottari"]["mahadashas"]:
        dasha_details = data.charts["Dashas"]["Vimshottari"]["mahadashas"][dasha_lord]
        dasha_details["predictions"] = getMahadashaPredictions(dasha_lord)
        return dasha_details
    
    return {"error": f"No dasha information available for {dasha_lord}"}

# -------------------------------------------------------
# CHARA DASHA (Jaimini System)
# -------------------------------------------------------



SIGN_LORDS = {
"Aries":"Mars",
"Taurus":"Venus",
"Gemini":"Mercury",
"Cancer":"Moon",
"Leo":"Sun",
"Virgo":"Mercury",
"Libra":"Venus",
"Scorpio":"Mars",
"Sagittarius":"Jupiter",
"Capricorn":"Saturn",
"Aquarius":"Saturn",
"Pisces":"Jupiter"
}

ODD_SIGNS = ["Aries","Gemini","Leo","Libra","Sagittarius","Aquarius"]


def getPlanetSign(division, planet):
    try:
        return division["planets"][planet]["sign"]
    except:
        return None


def signDistance(start, end):

    s = charaDashaSequence.index(start)
    e = charaDashaSequence.index(end)

    if e >= s:
        return e - s + 1
    else:
        return (12 - s) + e + 1


def getDashaDirection(lagna):

    if lagna in ODD_SIGNS:
        return "forward"
    else:
        return "reverse"


def getCharaYears(sign, division):

    lord = SIGN_LORDS[sign]

    lord_sign = getPlanetSign(division, lord)

    if lord_sign is None:
        return 1

    years = signDistance(sign, lord_sign)

    return years


def generateCharaSequence(lagna):

    direction = getDashaDirection(lagna)

    lagna_index = charaDashaSequence.index(lagna)

    sequence = []

    for i in range(12):

        if direction == "forward":
            sign = charaDashaSequence[(lagna_index + i) % 12]
        else:
            sign = charaDashaSequence[(lagna_index - i) % 12]

        sequence.append(sign)

    return sequence


def generateCharaTimeline(division):

    lagna = division["ascendant"]["sign"]

    sequence = generateCharaSequence(lagna)

    dashas = []

    start_year = 0

    for sign in sequence:

        years = getCharaYears(sign, division)

        dashas.append({
            "sign": sign,
            "years": years,
            "start": start_year,
            "end": start_year + years
        })

        start_year += years

    return dashas


# -------------------------------------------------------
# CURRENT CHARA DASHA
# -------------------------------------------------------

def getCharDashaCurrent(division, birthdata):

    timeline = generateCharaTimeline(division)

    birth_date = datetime(
        year=int(birthdata["DOB"]["year"]),
        month=int(birthdata["DOB"]["month"]),
        day=int(birthdata["DOB"]["day"])
    )

    current_date = datetime.now()

    years_passed = (current_date - birth_date).days / 365.25

    for d in timeline:

        if d["start"] <= years_passed < d["end"]:

            remaining = d["end"] - years_passed

            return {
                "current_sign": d["sign"],
                "remaining_years": round(remaining,2),
                "total_years": d["years"]
            }

    return {
        "current_sign": None,
        "remaining_years": None
    }


# -------------------------------------------------------
# CHARA DASHA MAIN PERIODS
# -------------------------------------------------------

def getCharDashaMain(division, birthdata):

    timeline = generateCharaTimeline(division)

    birth_date = datetime(
        year=birthdata["DOB"]["year"],
        month=birthdata["DOB"]["month"],
        day=birthdata["DOB"]["day"]
    )

    periods = []

    for item in timeline:

        start_date = birth_date + timedelta(days=int(item["start"] * 365.25))
        end_date = birth_date + timedelta(days=int(item["end"] * 365.25))

        periods.append({
            "sign": item["sign"],
            "start_date": start_date,
            "end_date": end_date,
            "duration_years": item["years"]
        })

    return periods


# -------------------------------------------------------
# CHARA DASHA SUB PERIODS
# -------------------------------------------------------

def getCharDashaSub(division, birthdata, main_sign):

    main_periods = getCharDashaMain(division, birthdata)

    main_period = next((p for p in main_periods if p["sign"] == main_sign), None)

    if not main_period:
        return {"error": f"Invalid sign {main_sign}"}

    start_date = main_period["start_date"]
    total_days = (main_period["end_date"] - start_date).days

    sub_periods = []

    current_date = start_date

    for i in range(12):

        sub_sign = charaDashaSequence[i]

        portion = 1 / 12

        sub_days = int(total_days * portion)

        end_date = current_date + timedelta(days=sub_days)

        sub_periods.append({
            "sign": sub_sign,
            "start_date": current_date,
            "end_date": end_date,
            "duration_days": sub_days
        })

        current_date = end_date

    return sub_periods
NAKSHATRA_LIST = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
"Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni",
"Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha",
"Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta",
"Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"
]
# Yogini Dasha Main - Returns main periods of Yogini Dasha
def getYoginiDashaMain(division, birthdata):
    # Yogini Dasha is based on Moon's nakshatra
    moon_nakshatra = division["planets"]["Moon"]["nakshatra_name"]

    if moon_nakshatra not in NAKSHATRA_LIST:
        raise Exception(f"Unknown nakshatra: {moon_nakshatra}")

    nakshatra_number = NAKSHATRA_LIST.index(moon_nakshatra) + 1
    
    # Determine starting Yogini based on nakshatra remainder when divided by 8
    yogini_index = (nakshatra_number - 1) % 8
    yogini_lords = list(yoginiDashaSkeleton.keys())
    
    birth_date = datetime(year=birthdata["DOB"]["year"], 
                         month=birthdata["DOB"]["month"], 
                         day=birthdata["DOB"]["day"])
    
    yogini_periods = []
    current_date = birth_date
    
    # Calculate position within nakshatra (simplified)
    moon_longitude = (((signnum(division["planets"]["Moon"]["sign"])-1) * 30) + 
                     division["planets"]["Moon"]["pos"]["deg"] + 
                     (division["planets"]["Moon"]["pos"]["min"] / 60) + 
                     (division["planets"]["Moon"]["pos"]["sec"] / 3600))
    
    nakshatra_size = 13 + (20/60)  # 13°20'
    position_in_nakshatra = moon_longitude % nakshatra_size
    fraction_completed = position_in_nakshatra / nakshatra_size
    
    # Calculate remaining duration in first dasha
    first_lord = yogini_lords[yogini_index]
    first_duration = yoginiDashaSkeleton[first_lord]["duration"]
    remaining_years = first_duration * (1 - fraction_completed)
    
    # Adjust first period
    first_end_date = birth_date + timedelta(days=int(remaining_years * 365.25))
    yogini_periods.append({
        "lord": first_lord,
        "deity": yoginiDashaSkeleton[first_lord]["deity"],
        "element": yoginiDashaSkeleton[first_lord]["element"],
        "start_date": birth_date,
        "end_date": first_end_date,
        "duration_years": remaining_years
    })
    
    current_date = first_end_date
    
    # Calculate subsequent periods
    for i in range(1, 8):
        next_index = (yogini_index + i) % 8
        lord = yogini_lords[next_index]
        years = yoginiDashaSkeleton[lord]["duration"]
        
        end_date = current_date + timedelta(days=int(years * 365.25))
        
        yogini_periods.append({
            "lord": lord,
            "deity": yoginiDashaSkeleton[lord]["deity"],
            "element": yoginiDashaSkeleton[lord]["element"],
            "start_date": current_date,
            "end_date": end_date,
            "duration_years": years
        })
        
        current_date = end_date
    
    return yogini_periods

# Yogini Dasha Sub - Returns sub-periods of Yogini Dasha
def getYoginiDashaSub(division, birthdata, main_lord):
    if main_lord not in yoginiDashaSkeleton:
        return {"error": f"Invalid Yogini lord: {main_lord}"}
    
    # Find the main period details
    main_periods = getYoginiDashaMain(division, birthdata)
    main_period = next((p for p in main_periods if p["lord"] == main_lord), None)
    
    if not main_period:
        return {"error": f"Could not find main period for {main_lord}"}
    
    start_date = main_period["start_date"]
    total_days = (main_period["end_date"] - start_date).days
    
    yogini_lords = list(yoginiDashaSkeleton.keys())
    main_lord_index = yogini_lords.index(main_lord)
    
    sub_periods = []
    current_date = start_date
    
    # Sub-periods follow the same sequence starting from the main lord
    for i in range(8):
        sub_lord_index = (main_lord_index + i) % 8
        sub_lord = yogini_lords[sub_lord_index]
        sub_years = yoginiDashaSkeleton[sub_lord]["duration"]
        
        # Proportion of sub-period within main period
        total_years = sum(yoginiDashaSkeleton[lord]["duration"] for lord in yoginiDashaSkeleton)
        sub_days = int(total_days * (sub_years / total_years))
        end_date = current_date + timedelta(days=sub_days)
        
        sub_periods.append({
            "lord": sub_lord,
            "deity": yoginiDashaSkeleton[sub_lord]["deity"],
            "element": yoginiDashaSkeleton[sub_lord]["element"],
            "start_date": current_date,
            "end_date": end_date,
            "duration_days": sub_days
        })
        
        current_date = end_date
    
    return sub_periods

# Get Paryantar Dasha - Returns Pratyantar Dasha details
def getParyantarDasha(mahadasha_lord=None, antardasha_lord=None):
    currentDate = datetime.now()
    
    # If no lords specified, get current dasha lords
    if not mahadasha_lord:
        mahadasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["dasha"]
    
    if not antardasha_lord:
        antardasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"]
    
    # Get all paryantardashas for the specified mahadasha-antardasha combination
    paryantardashas = {}
    prefix = f"{mahadasha_lord}-{antardasha_lord}-"
    
    for key, value in data.charts["Dashas"]["Vimshottari"]["paryantardashas"].items():
        if key.startswith(prefix):
            paryantardashas[key] = value
    
    # Find current paryantardasha if no specific lords are provided
    current_paryantardasha = None
    if mahadasha_lord == data.charts["Dashas"]["Vimshottari"]["current"]["dasha"] and \
       antardasha_lord == data.charts["Dashas"]["Vimshottari"]["current"]["bhukti"]:
        current_paryantardasha_lord = data.charts["Dashas"]["Vimshottari"]["current"]["paryantardasha"]
        if current_paryantardasha_lord:
            key = f"{mahadasha_lord}-{antardasha_lord}-{current_paryantardasha_lord}"
            if key in data.charts["Dashas"]["Vimshottari"]["paryantardashas"]:
                current_paryantardasha = data.charts["Dashas"]["Vimshottari"]["paryantardashas"][key]
    
    return {
        "mahadasha_lord": mahadasha_lord,
        "antardasha_lord": antardasha_lord,
        "current_paryantardasha": current_paryantardasha,
        "all_paryantardashas": paryantardashas
    }

# -------------------------------------------------------
# ATMAKARAKA (Jaimini)
# -------------------------------------------------------

def getAtmakaraka(division):

    max_deg = -1
    ak_planet = None

    for planet, pdata in division["planets"].items():

        try:
            deg = float(pdata["degree"])

            if deg > max_deg:
                max_deg = deg
                ak_planet = planet

        except:
            continue

    return {
        "planet": ak_planet,
        "degree": max_deg
    }

# -------------------------------------------------------
# KARAKAMSHA LAGNA
# -------------------------------------------------------

def getKarakamsha(chartD1, chartD9):

    ak = getAtmakaraka(chartD1)["planet"]

    if ak is None:
        return None

    try:
        return chartD9["planets"][ak]["sign"]
    except:
        return None

# -------------------------------------------------------
# ARUDHA LAGNA
# -------------------------------------------------------

def getArudhaLagna(division):

    lagna_sign = division["ascendant"]["sign"]

    lord = SIGN_LORDS.get(lagna_sign)

    if lord is None:
        return None

    lord_sign = division["planets"][lord]["sign"]

    s = charaDashaSequence.index(lagna_sign)
    l = charaDashaSequence.index(lord_sign)

    distance = (l - s) % 12

    arudha_index = (l + distance) % 12

    return charaDashaSequence[arudha_index]

# -------------------------------------------------------
# UPAPADA LAGNA
# -------------------------------------------------------

def getUpapadaLagna(division):

    twelfth_sign = charaDashaSequence[
        (charaDashaSequence.index(division["ascendant"]["sign"]) - 1) % 12
    ]

    lord = SIGN_LORDS[twelfth_sign]

    lord_sign = division["planets"][lord]["sign"]

    s = charaDashaSequence.index(twelfth_sign)
    l = charaDashaSequence.index(lord_sign)

    distance = (l - s) % 12

    ul_index = (l + distance) % 12

    return charaDashaSequence[ul_index]

# -------------------------------------------------------
# JAIMINI RASHI ASPECTS
# -------------------------------------------------------

def getJaiminiAspects(sign):

    movable = ["Aries","Cancer","Libra","Capricorn"]
    fixed = ["Taurus","Leo","Scorpio","Aquarius"]
    dual = ["Gemini","Virgo","Sagittarius","Pisces"]

    if sign in movable:
        return fixed

    if sign in fixed:
        return movable

    if sign in dual:
        return dual

SIGN_LIST = [
"Aries","Taurus","Gemini","Cancer","Leo","Virgo",
"Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

def signnum(sign):
    return SIGN_LIST.index(sign) + 1

if __name__ == "__main__":
    moonlngsec = (((signnum(data.lagna_moon["sign"])-1) * 30 * 3600) + 
                  ((data.lagna_moon["pos"]["deg"]) * 3600) + 
                  ((data.lagna_moon["pos"]["min"]) * 60) + 
                  (data.lagna_moon["pos"]["sec"]))

    nakshatraLord = data.lagna_moon["nak-ruler"]

    bdaytime = datetime(year=birthdata["DOB"]["year"], 
                        month=birthdata["DOB"]["month"], 
                        day=birthdata["DOB"]["day"], 
                        hour=birthdata["TOB"]["hour"], 
                        minute=birthdata["TOB"]["min"], 
                        second=birthdata["TOB"]["sec"])

    starttime = datetime(year=1989, month=11, day=11, hour=13, minute=8, second=48)
    #duration = relativedelta(years=dashaVimshottariSkeleton["Mars"]["duration"])
    #print(f'Duration of 7 years is {duration}')
    computeVimshottariDasha(moonlngsec, nakshatraLord, bdaytime)
    print(vimshottariDasha)
    #res = computeSubPeriods(starttime, "Mars", duration, "Antardasha", bdaytime)
    #for item in res:
        #print(item["entryString"])
    #print(debilitationSign_of_planet)

