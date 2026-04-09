import swisseph as swe
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
import os
try:
    from svglib.svglib import svg2rlg
except Exception:
    svg2rlg = None
import jyotichart as chart
import jyotishyamitra as jm
from support import panchanga
from support import dashas as dasha_support
from support import localization
import support.mod_astrodata as data
from datetime import datetime
from support.center_header import CenteredHeader
import io
from api_logger import get_user
import urllib.request
import reportlab.rl_config
reportlab.rl_config.warnOnMissingFontGlyphs = True
reportlab.rl_config.verbose = True

def _degree_to_sign(deg):
    signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
    return signs[int(deg // 30)]

def _sign_meta(name):
    m = {
        "Aries": ("Mars","Fire"),
        "Taurus": ("Venus","Earth"),
        "Gemini": ("Mercury","Air"),
        "Cancer": ("Moon","Water"),
        "Leo": ("Sun","Fire"),
        "Virgo": ("Mercury","Earth"),
        "Libra": ("Venus","Air"),
        "Scorpio": ("Mars","Water"),
        "Sagittarius": ("Jupiter","Fire"),
        "Capricorn": ("Saturn","Earth"),
        "Aquarius": ("Saturn","Air"),
        "Pisces": ("Jupiter","Water")
    }
    return m.get(name,("",""))

class KundaliPDF:
    def __init__(self, user_name, day, month, year, time_hhmm, tz, place, lat, lon, company_name="",company_mobile="",api_id=""):
        self.user_name = user_name
        self.day = day
        self.month = month
        self.year = year
        self.time_hhmm = time_hhmm
        self.tz = tz
        self.place = place
        self.lat = lat
        self.lon = lon
        self.app_id = api_id
        
        safe_name = re.sub(r'[^A-Za-z0-9]', '', self.user_name.title())
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        self.filename = f"{safe_name}_{timestamp}.pdf"

        self.company_name = company_name
        self.company_mobile = company_mobile 
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle('Title', parent=self.styles['Heading1'], fontName='Helvetica-Bold', fontSize=24, textColor=colors.HexColor('#000000'), alignment=TA_CENTER, spaceAfter=20)
        self.header_style = ParagraphStyle('Header', parent=self.styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, textColor=colors.HexColor('#000000'), backColor=colors.HexColor('#FFFFFF'), spaceAfter=10, spaceBefore=10,alignment=TA_CENTER)
        self.text_style = ParagraphStyle('Text', parent=self.styles['Normal'], fontName='Helvetica', fontSize=10)
        self.interp_style = ParagraphStyle('Interp', parent=self.styles['Normal'], fontName='Helvetica', fontSize=8, alignment=TA_JUSTIFY, leading=10)
        self.doc = SimpleDocTemplate(self.filename, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=40, bottomMargin=40)
        self.story = []

    def add_section_header(self, text):
        self.story.append(Spacer(1, 10))
        self.story.append(CenteredHeader(text))
        self.story.append(Spacer(1, 20))


    def _tithi_name(self, tno):
        names = [
            'Pratipada','Dvitiya','Tritiya','Chaturthi','Panchami','Shashthi','Saptami','Ashtami','Navami','Dashami',
            'Ekadashi','Dvadashi','Trayodashi','Chaturdashi','Purnima','Pratipada','Dvitiya','Tritiya','Chaturthi','Panchami',
            'Shashthi','Saptami','Ashtami','Navami','Dashami','Ekadashi','Dvadashi','Trayodashi','Chaturdashi','Amavasya'
        ]
        try:
            return names[int(tno)-1]
        except Exception:
            return str(tno)

    def _tithi_abbr(self, tno):
        prefix = 'S.' if int(tno) <= 15 else 'K.'
        return f"{prefix}{self._tithi_name(tno)}"

    def _yoga_name(self, yno):
        names = ['Vishkambha','Priti','Ayushman','Saubhagya','Shobhana','Atiganda','Sukarma','Dhriti','Shoola','Ganda','Vriddhi','Dhruva','Vyaghata','Harshana','Vajra','Siddhi','Vyatipata','Variyana','Parigha','Shiva','Siddha','Sadhya','Shubha','Shukla','Brahma','Indra','Vaidhriti']
        try:
            return names[int(yno)-1]
        except Exception:
            return str(yno)

    def _karana_name(self, kno):
        names = ['Bava','Balava','Kaulava','Taitila','Garaja','Vanija','Vishti','Shakuni','Chatushpada','Naga','Kimstughna']
        try:
            return names[(int(kno)-1) % len(names)]
        except Exception:
            return str(kno)

    def _nakshatra_name(self, nno):
        names = ['Ashvini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purva Phalguni','Uttara Phalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purva Ashadha','Uttara Ashadha','Shravana','Dhanishta','Shatabhisha','Purva Bhadrapada','Uttara Bhadrapada','Revati']
        try:
            return names[int(nno)-1]
        except Exception:
            return str(nno)

    def _nakshatra_lord(self, name):
        m = {
            'Ashvini':'Ketu','Bharani':'Venus','Krittika':'Sun','Rohini':'Moon','Mrigashira':'Mars','Ardra':'Rahu','Punarvasu':'Jupiter','Pushya':'Saturn','Ashlesha':'Mercury','Magha':'Ketu','Purva Phalguni':'Venus','Uttara Phalguni':'Sun','Hasta':'Moon','Chitra':'Mars','Swati':'Rahu','Vishakha':'Jupiter','Anuradha':'Saturn','Jyeshtha':'Mercury','Mula':'Ketu','Purva Ashadha':'Venus','Uttara Ashadha':'Sun','Shravana':'Moon','Dhanishta':'Mars','Shatabhisha':'Rahu','Purva Bhadrapada':'Jupiter','Uttara Bhadrapada':'Saturn','Revati':'Mercury'
        }
        return m.get(name,'')

    def _planet_varna(self, planet):
        mp = {
            'Sun':'Kshatriya','Moon':'Vaishya','Mars':'Kshatriya','Mercury':'Vaishya','Jupiter':'Brahmana','Venus':'Brahmana','Saturn':'Shudra','Rahu':'Shudra','Ketu':'Brahmana'
        }
        return mp.get(planet,'')

    def _nakshatra_letters(self, name):
        m = {
            'Ashvini':['Chu','Che','Cho','La'],
            'Bharani':['Li','Lu','Le','Lo'],
            'Krittika':['A','I','U','E'],
            'Rohini':['O','Va','Vi','Vu'],
            'Mrigashira':['Ve','Vo','Ka','Ki'],
            'Ardra':['Ku','Ga','Na','Cha'],
            'Punarvasu':['Ke','Ko','Ha','Hi'],
            'Pushya':['Hu','He','Ho','Da'],
            'Ashlesha':['De','Do','Me','Mo'],
            'Magha':['Ma','Mi','Mu','Me'],
            'Purva Phalguni':['Mo','Ta','Ti','Tu'],
            'Uttara Phalguni':['Te','To','Pa','Pe'],
            'Hasta':['Pu','Sha','Na','Tha'],
            'Chitra':['Pe','Po','Ra','Ri'],
            'Swati':['Ru','Re','Ro','Ta'],
            'Vishakha':['Ti','Tu','Te','To'],
            'Anuradha':['Na','Ne','Nu','Ne'],
            'Jyeshtha':['No','Ya','Yi','Yu'],
            'Mula':['Ye','Yo','Ba','Bi'],
            'Purva Ashadha':['Bu','Da','Pi','Pu'],
            'Uttara Ashadha':['Ke','Ko','Pa','Pe'],
            'Shravana':['Ka','Ki','Ku','Ga'],
            'Dhanishta':['Go','Sa','Si','Su'],
            'Shatabhisha':['Se','So','Ga','Gi'],
            'Purva Bhadrapada':['Gu','Ge','Go','Sa'],
            'Uttara Bhadrapada':['Se','So','Da','Di'],
            'Revati':['De','Do','Cha','Chi']
        }
        return m.get(name,[''])

    def _paya_from_weekday(self, weekday_name):
        m = {
            'Sunday':'Gold','Monday':'Silver','Tuesday':'Copper','Wednesday':'Iron','Thursday':'Gold','Friday':'Silver','Saturday':'Iron'
        }
        return m.get(weekday_name,'')

    def _fmt_hms(self, time_val):
        hours = int(time_val)
        minutes = int((time_val - hours) * 60)
        seconds = int(((time_val - hours) * 60 - minutes) * 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def _sun_event(self, jd, lat, lon, tz, event):
        geopos = (lon, lat, 0)
        rsmi = (swe.CALC_RISE if event == 'rise' else swe.CALC_SET) | swe.BIT_DISC_CENTER
        result = swe.rise_trans(jd - tz/24, swe.SUN, rsmi, geopos, 0, 0, swe.FLG_SWIEPH)
        if result and result[0] >= 0:
            local_jd = result[1][0] + tz/24.0
            frac_day = local_jd - int(local_jd)
            return self._fmt_hms(frac_day * 24)
        return ''

    def compute(self):
        hh, mm = [int(x) for x in self.time_hhmm.split(':')]
        hour_dec = hh + mm/60.0
        jd = swe.julday(self.year, self.month, self.day, hour_dec)
        place = panchanga.Place(self.lat, self.lon, self.tz)
        sr = self._sun_event(jd, self.lat, self.lon, self.tz, 'rise')
        ss = self._sun_event(jd, self.lat, self.lon, self.tz, 'set')
        ti = panchanga.tithi(jd, place)
        yo = panchanga.yoga(jd, place)
        na = panchanga.nakshatra(jd, place)
        ka = panchanga.karana(jd, place)
        asc = panchanga.ascendant(jd, place)
        planets = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE, "Ketu": swe.MEAN_NODE
        }
        pos = {}
        for name, pid in planets.items():
            lon = swe.calc_ut(jd, pid)[0][0]
            if name == "Ketu":
                lon = (lon + 180) % 360
            pos[name] = lon
        return jd, pos, sr, ss, ti, yo, na, ka, asc

    def add_cover(self, sr, ss):
        try:
            img_path = os.path.join(os.path.dirname(__file__), 'assets', 'loard_ganesh.png')
            img = Image(img_path)
            img.hAlign = 'CENTER'
            img.drawHeight = 2.5*inch
            img.drawWidth = 2.5*inch
            self.story.append(img)
            self.story.append(Spacer(1, 0.2*inch))
        except Exception:
            print("Error adding cover image")
            pass
        self.story.append(Paragraph('|| Shree Ganeshaya Namaha ||', self.title_style))
        # self.story.append(Paragraph('HOROSCOPE', self.title_style))
        self.story.append(Spacer(1, 0.2*inch))
        band_width = self.doc.pagesize[0] - self.doc.leftMargin - self.doc.rightMargin
        band_style = ParagraphStyle('Band', parent=self.styles['Heading2'], fontName='Helvetica-Bold', fontSize=14, alignment=TA_CENTER, textColor=colors.HexColor('#000000'))
        band_text = Paragraph(f"HOROSCOPE <br/>{self.user_name}<br/>{self.day:02d}/{self.month:02d}/{self.year} • {self.time_hhmm}<br/>{self.place}", band_style)
        generated_by_text=Paragraph(f"Generated By",band_style)
        band_tbl = Table([[band_text]], colWidths=[band_width], rowHeights=[2.0*inch])
        band_tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#FFD700')),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'CENTER')
        ]))
        self.story.append(band_tbl)
        self.story.append(Spacer(1, 0.2*inch))
        self.story.append(generated_by_text)
        logo_url = None
        try:
            user = get_user(self.app_id)
            if user and hasattr(user, 'pdf_logo'):
                logo_url = user.pdf_logo
                print("Fetched logo URL:", logo_url)
        except Exception as e:
            print("Error fetching logo URL:", e)

        if logo_url:
            try:
                print("Downloading image...")
                with urllib.request.urlopen(logo_url) as response:
                    img_data = response.read()

                img_io = io.BytesIO(img_data)
                pdf_logo = Image(img_io)
                pdf_logo.hAlign = 'CENTER'
                pdf_logo.drawHeight = 0.5 * inch
                pdf_logo.drawWidth = 0.5 * inch
                print("Image added successfully.")

                self.story.append(pdf_logo)
                self.story.append(Spacer(1, 0.2 * inch))

            except Exception as e:
                print("Error adding logo:", e)
        self.story.append(PageBreak())

    def apply_alternate_row_color(self, style, table_data, header_rows=1, color='#FFF2CC'):
        """
        Adds alternate row background coloring to an existing TableStyle.
        
        :param style: existing TableStyle instance
        :param table_data: list (2D array) of table rows
        :param header_rows: number of header rows to skip
        :param color: hex background color for alternating rows
        :return: updated TableStyle instance
        """
        total_rows = len(table_data)

        for row in range(header_rows, total_rows):
            if row % 2 == 1:  # Apply to odd rows only
                style.add('BACKGROUND', (0, row), (-1, row), colors.HexColor(color))

        return style


    def add_basic_details_grid(self, sr, ss, ti, yo, na, ka, asc):
        # self.story.append(Paragraph('Basic Astrological Details', self.header_style))
        self.add_section_header("Basic Astrological Details")

        asc_sign_name = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][asc[0]]
        asc_lord, element = _sign_meta(asc_sign_name)
        weekday = datetime(self.year,self.month,self.day).strftime('%A')
        nk_name = self._nakshatra_name(na[0])
        nk_lord = self._nakshatra_lord(nk_name)
        varna = self._planet_varna(nk_lord)
        paya = self._paya_from_weekday(weekday)
        name_alpha = self._nakshatra_letters(nk_name)[0]

        base_style = TableStyle([
            ('TOPPADDING', (0, 0), (-1, -1), 10), # 10 points of top padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10), # 10 points of bottom padding
            ('BOX',(0,0),(-1,-1),1.5,colors.HexColor('#D5B86A')),
            # ('GRID',(0,0),(-1,-1),0.2,colors.HexColor('#E5CF8A')),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),10),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [
                colors.HexColor('#FFFFFF'),
                colors.HexColor('#FFF2CC')
            ]),
        ])
        
        
        left_basic_rows = [
            ['Date of Birth', f"{self.day:02d}/{self.month:02d}/{self.year}"],
            ['Time of Birth', self.time_hhmm],
            ['Place of birth', self.place],
            ['Latitude', str(self.lat)],
            ['Longitude', str(self.lon)],
            ['Time Zone', str(self.tz)],
            ['Ayanamsha', f"{swe.get_ayanamsa(swe.julday(self.year, self.month, self.day, 12.0)):.6f}"],
            ['Sunrise', sr],
            ['Sunset', ss]
        ]
        
        # base_style = self.apply_alternate_row_color(base_style, left_basic_rows, header_rows=0)

        left_basic_tbl = Table(left_basic_rows, colWidths=[1.7*inch, 1.7*inch],cornerRadii=[8,8,8,8])
        left_basic_tbl.setStyle(base_style)

        ghatka_rows = [
            ['Month', weekday],
            ['Tithi', self._tithi_name(ti[0])],
            ['Rasi', asc_sign_name],
            ['Tatva', element],
            ['lord', asc_lord],
            ['Nakshatra', nk_name],
            ['Same-sex lagna', asc_sign_name],
            ['Opposite-sex lagna', ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][((asc[0]+6)%12)]]
        ]
        ghatka_tbl = Table(ghatka_rows, colWidths=[1.7*inch, 1.7*inch],cornerRadii=[8,8,8,8])   
        ghatka_tbl.setStyle(base_style)

        right_panchang_rows = [
            ['Tithi', self._tithi_name(ti[0])],
            ['Yog', self._yoga_name(yo[0])],
            ['Nakshatra', nk_name],
            ['Karana', self._karana_name(ka[0])]
        ]
        right_panchang_tbl = Table(right_panchang_rows, colWidths=[1.7*inch, 1.7*inch],cornerRadii=[8,8,8,8])   
        right_panchang_tbl.setStyle(base_style)

        right_astro_rows = [
            ['Tithi', self._tithi_abbr(ti[0])],
            ['Varna', varna],
            ['Yoni', ''],
            ['Vasya', ''],
            ['Nadi', ''],
            ['Rasi', asc_sign_name],
            ['Rasi lord', asc_lord],
            ['Karana', self._karana_name(ka[0])],
            ['Tatva', element],
            ['Nakshatra', nk_name],
            ['Nakshatra lord', nk_lord],
            ['Ascendant', asc_sign_name],
            ['Paya', paya],
            ['Name Alphabet', name_alpha]
        ]
        right_astro_tbl = Table(right_astro_rows, colWidths=[1.7*inch, 1.7*inch],cornerRadii=[8,8,8,8])     
        right_astro_tbl.setStyle(base_style)

        left_col = [
            Spacer(1,0.15*inch),
            Paragraph('Basic Details', self.header_style),
            left_basic_tbl,
            Spacer(1,0.15*inch),
            Paragraph('Ghatka Chakra', self.header_style),
            ghatka_tbl
        ]

        right_col = [  
            Spacer(1,0.15*inch),
            Paragraph('Panchang Details', self.header_style),
            right_panchang_tbl,
            Spacer(1,0.15*inch),
            Paragraph('Astrological Details', self.header_style),
            right_astro_tbl
        ]

        parent = Table([[left_col,  right_col]], colWidths=[3.5*inch, 3.5*inch])
        parent.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP')
        ]))
        self.story.append(parent)
        self.story.append(PageBreak())

    def add_planet_table(self, pos, asc_deg):
        self.add_section_header('Planetary Positions')
        header = ['Planet','R','Sign','Degrees','Sign Lord','Nakshatra','Nakshatra Lord','House']
        rows = [header]
        for name, lon in pos.items():
            sign = _degree_to_sign(lon)
            slord, _ = _sign_meta(sign)
            deg_in_sign = lon % 30
            nak_index = int(lon / 13.333333)
            nak_name = ['Ashvini','Bharani','Krittika','Rohini','Mrigashira','Ardra','Punarvasu','Pushya','Ashlesha','Magha','Purvaphalguni','Uttaraphalguni','Hasta','Chitra','Swati','Vishakha','Anuradha','Jyeshtha','Mula','Purvashadha','Uttarashadha','Shravana','Dhanista','Shatabhisha','Purvabhadra','Uttarabhadra','Revati'][nak_index]
            rows.append([name,'',sign,f"{deg_in_sign:.2f}",slord,nak_name,self._nakshatra_lord(nak_name),str(int(((lon - asc_deg) % 360) // 30) + 1)])
        tbl = Table(rows, colWidths=[1*inch,0.4*inch,1*inch,0.8*inch,1*inch,1.2*inch,1.2*inch,0.6*inch],cornerRadii=[8,8,8,8])
        planet_style = TableStyle([
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8), # 8 points of top padding
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8), # 8 points of bottom padding
              # Optional: add different padding to the header row
            ('TOPPADDING', (0, 0), (-1, 0), 15),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 15),
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F2F2F2')),
            ('BOX',(0,0),(-1,-1), 1.0, colors.HexColor('#D5B86A')),
            # ('GRID',(0,0),(-1,-1),0.2,colors.HexColor('#CCCCCC')),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [
                colors.HexColor('#FFFFFF'),
                colors.HexColor('#FFF2CC')
            ]),
        ])
        tbl.setStyle(planet_style)
        self.story.append(tbl)
        self.story.append(Spacer(1,0.2*inch))
        self.add_section_header('Planet Nature')
        self.story.append(Spacer(1,0.2*inch))

        def nature_label(p, sign_name, house_num):
            own = {
                'Sun': {'Leo'},
                'Moon': {'Cancer'},
                'Mars': {'Aries','Scorpio'},
                'Mercury': {'Gemini','Virgo'},
                'Jupiter': {'Sagittarius','Pisces'},
                'Venus': {'Taurus','Libra'},
                'Saturn': {'Capricorn','Aquarius'},
                'Rahu': set(),
                'Ketu': set()
            }
            exalt = {
                'Sun': {'Aries'},
                'Moon': {'Taurus'},
                'Mars': {'Capricorn'},
                'Mercury': {'Virgo'},
                'Jupiter': {'Cancer'},
                'Venus': {'Pisces'},
                'Saturn': {'Libra'},
                'Rahu': {'Taurus'},
                'Ketu': {'Scorpio'}
            }
            debil = {
                'Sun': {'Libra'},
                'Moon': {'Scorpio'},
                'Mars': {'Cancer'},
                'Mercury': {'Pisces'},
                'Jupiter': {'Capricorn'},
                'Venus': {'Virgo'},
                'Saturn': {'Aries'},
                'Rahu': {'Scorpio'},
                'Ketu': {'Taurus'}
            }
            friends = {
                'Sun': {'Moon','Mars','Jupiter'},
                'Moon': {'Sun','Mercury'},
                'Mars': {'Sun','Moon','Jupiter'},
                'Mercury': {'Sun','Venus'},
                'Jupiter': {'Sun','Moon','Mars'},
                'Venus': {'Mercury','Saturn'},
                'Saturn': {'Mercury','Venus'},
                'Rahu': set(),
                'Ketu': set()
            }
            enemies = {
                'Sun': {'Saturn','Venus'},
                'Moon': {'Rahu','Ketu'},
                'Mars': {'Mercury','Saturn'},
                'Mercury': {'Moon'},
                'Jupiter': {'Venus','Mercury'},
                'Venus': {'Sun','Moon'},
                'Saturn': {'Sun','Moon','Mars'},
                'Rahu': set(),
                'Ketu': set()
            }
            score = 0
            if sign_name in exalt.get(p,set()):
                score += 2
            elif sign_name in debil.get(p,set()):
                score -= 2
            elif sign_name in own.get(p,set()):
                score += 2
            slord, _ = _sign_meta(sign_name)
            if slord in friends.get(p,set()):
                score += 1
            if slord in enemies.get(p,set()):
                score -= 1
            if int(house_num) in [6,8,12]:
                score -= 1
            if p in ['Rahu','Ketu']:
                return ('Natural Malefic','red')
            if score >= 2:
                return ('Benefic','green')
            if score <= -2:
                return ('Highly Malefic','red')
            if score <= -1:
                return ('Malefic','red')
            return ('Neutral','black')

        cards = []
        for r in rows[1:]:
            planet = r[0]
            sign = r[2]
            nak = r[5]
            house_num = r[7]
            # derive pada from longitude
            lon_val = pos[planet]
            nak_span = 13.3333333333
            rem = lon_val % nak_span
            pada = int(rem / (nak_span/4)) + 1
            label, color_val = nature_label(planet, sign, house_num)
            title = Paragraph(f"<b>{planet}</b>", ParagraphStyle('t', parent=self.styles['Heading3'], alignment=TA_CENTER))
            lines = [
                Paragraph(f"{sign}", self.text_style),
                Paragraph(f"{nak}({pada})", self.text_style),
                Paragraph(f"<font color='{color_val}'>{label}</font>", self.text_style)
            ]
            box = Table([[title],[lines[0]],[lines[1]],[lines[2]]], colWidths=[2.1*inch], rowHeights=None, cornerRadii=[8,8,8,8])
            box.setStyle(TableStyle([
                ('ALIGN',(0,0),(-1,-1),'CENTER'),
                ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
                ('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#FFFFFF')),
                ('BOX',(0,0),(-1,-1), 1.0, colors.HexColor('#D5B86A')),
                ('TOPPADDING',(0,0),(-1,-1),6),
                ('BOTTOMPADDING',(0,0),(-1,-1),6)
            ]))
            cards.append(box)

        rows_of_cards = []
        for i in range(0, len(cards), 3):
            rows_of_cards.append(cards[i:i+3])
        grid = Table(rows_of_cards, colWidths=[2.2*inch,2.2*inch,2.2*inch])
        grid.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ALIGN',(0,0),(-1,-1),'CENTER'),
            ('LEFTPADDING',(0,0),(-1,-1),6),
            ('RIGHTPADDING',(0,0),(-1,-1),6)
        ]))
        self.story.append(grid)
        self.story.append(PageBreak())

    def add_charts(self):
        self.add_section_header('Horoscope Charts')
        def get_sign_number(sign_name):
            signs = {
                "Aries": 1, "Taurus": 2, "Gemini": 3, "Cancer": 4,
                "Leo": 5, "Virgo": 6, "Libra": 7, "Scorpio": 8,
                "Sagittarius": 9, "Capricorn": 10, "Aquarius": 11, "Pisces": 12
            }
            return signs.get(sign_name, 1)

        def get_house_number(planet_sign, lagna_sign):
            if isinstance(planet_sign, str):
                planet_sign = get_sign_number(planet_sign)
            if isinstance(lagna_sign, str):
                lagna_sign = get_sign_number(lagna_sign)
            house = (int(planet_sign) - int(lagna_sign)) % 12
            return 12 if house == 0 else house

        def get_sign_name(sign_num):
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

        def svg_to_flowable(svg_path, target_width, target_height):
            if not (svg_path and os.path.exists(svg_path)):
                return Paragraph('Chart generation failed', self.text_style)
            if svg2rlg:
                try:
                    drawing = svg2rlg(svg_path)
                    if hasattr(drawing, 'width') and drawing.width:
                        sx = target_width / float(drawing.width)
                        sy = target_height / float(drawing.height) if getattr(drawing, 'height', None) else sx
                        scale = min(sx, sy)
                        drawing.width *= scale
                        if getattr(drawing, 'height', None):
                            drawing.height *= scale
                        drawing.scale(scale, scale)
                    return drawing
                except Exception:
                    pass
            png_path = os.path.splitext(svg_path)[0] + '.png'
            if os.path.exists(png_path):
                try:
                    im = Image(png_path)
                    iw, ih = getattr(im, 'imageWidth', None), getattr(im, 'imageHeight', None)
                    if iw and ih:
                        sx = target_width / float(iw)
                        sy = target_height / float(ih)
                        scale = min(sx, sy)
                        im.drawWidth = iw * scale
                        im.drawHeight = ih * scale
                    im.hAlign = 'CENTER'
                    return im
                except Exception:
                    pass
            return Paragraph('Chart render error', self.text_style)

        def build_chart_flowable(div_chart_key, asc_mode, title, target_width, target_height):
            import tempfile, shutil
            temp_dir = tempfile.mkdtemp(prefix="charts_")
            jm.input_birthdata(
                name=self.user_name,
                gender='Male',
                place=self.place,
                longitude=str(self.lon),
                lattitude=str(self.lat),
                timezone=str(self.tz),
                year=str(self.year),
                month=str(self.month),
                day=str(self.day),
                hour=self.time_hhmm.split(':')[0],
                min=self.time_hhmm.split(':')[1],
                sec='0'
            )
            if jm.validate_birthdata() != 'SUCCESS':
                return None
            bd = jm.get_birthdata()
            chart_data = jm.generate_astrologicalData(bd, 'ASTRODATA_DICTIONARY')

            chart_obj = chart.NorthChart(title, self.user_name, IsFullChart=True)
            chart_obj.updatechartcfg(
                aspect=True,
                clr_background='white',
                clr_outbox='#D5B86A',
                clr_line='#D5B86A',
                clr_sign='#D5B86A', 
                clr_houses=["#FFFFFF"]*12
            )

            if asc_mode == 'lagna':
                asc_sign_num = chart_data[div_chart_key]["ascendant"]["sign"]
            elif asc_mode == 'moon':
                asc_sign_num = chart_data[div_chart_key]["planets"]["Moon"]["sign"]
            else:
                asc_sign_num = chart_data[div_chart_key]["ascendant"]["sign"]

            chart_obj.set_ascendantsign(get_sign_name(asc_sign_num))

            for planet_name, pdata in chart_data[div_chart_key]["planets"].items():
                if planet_name in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
                    base_sign = asc_sign_num
                    house_num = get_house_number(pdata["sign"], base_sign)
                    retro = pdata.get("retrograde", False)
                    chart_obj.add_planet(planet=planet_name, symbol=planet_name[:2], housenum=house_num, retrograde=retro)

            chart_obj.draw(temp_dir, "chart")
            svg_path = os.path.join(temp_dir, "chart.svg")
            flow = svg_to_flowable(svg_path, target_width, target_height)
            try:
                shutil.rmtree(temp_dir)
            except Exception:
                pass
            return flow

        avail_w = self.doc.pagesize[0] - self.doc.leftMargin - self.doc.rightMargin
        avail_h = self.doc.pagesize[1] - self.doc.topMargin - self.doc.bottomMargin
        
        # Adjust dimensions to fit everything on one page
        # Top chart (Lagna) gets ~35% height
        # Bottom charts (Moon/Navamsa) get ~35% height
        # Remaining ~30% for titles, text and spacing
        
        top_w = avail_w * 0.45
        top_h = avail_h * 0.35
        half_w = avail_w * 0.45 
        half_h = avail_h * 0.35
        
        lagna_flow = build_chart_flowable('D1', 'lagna', '', top_w, top_h)
        moon_flow = build_chart_flowable('D1', 'moon', '', half_w, half_h)
        nav_flow = build_chart_flowable('D9', 'lagna', '', half_w, half_h)

        lagna_title = Paragraph("Lagna Chart (Birth Chart)", self.header_style)
        moon_title = Paragraph("Moon Chart", self.header_style)
        nav_title = Paragraph("Navamsa Chart (D9)", self.header_style)

        top_interp = Paragraph(localization.get_text("birth_chart_interpretation"), self.interp_style)
        
        # Top Table: Left column [Title, Chart], Right column [Interpretation]
        # Spacer column in between
        top_left_col = [lagna_title, lagna_flow]
        top_tbl = Table([[ top_left_col, Spacer(1, 0), top_interp]], colWidths=[avail_w * 0.45, avail_w * 0.05, avail_w * 0.50])
        top_tbl.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('ALIGN',(0,0),(-1,-1),'LEFT')
        ]))

        bottom_left = [moon_title, moon_flow, Paragraph(localization.get_text("moon_chart_interpretation"), self.interp_style)]
        bottom_right = [nav_title, nav_flow, Paragraph(localization.get_text("navamsa_chart_interpretation"), self.interp_style)]
        bl_tbl = Table([[bottom_left]], colWidths=[avail_w * 0.45])
        br_tbl = Table([[bottom_right]], colWidths=[avail_w * 0.45])

        # Add spacer columns to balance layout to 100% width (45% + 10% + 45%)
        spacer = Spacer(1, 0)
        bottom_row = Table([[bl_tbl, spacer, br_tbl]], colWidths=[avail_w * 0.45, avail_w * 0.10, avail_w * 0.45])
        
        layout = Table([[top_tbl],[Spacer(1, 10)],[bottom_row]], colWidths=[avail_w])
        layout.setStyle(TableStyle([
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('ALIGN',(0,0),(-1,-1),'CENTER')
        ]))
        self.story.append(layout)
        self.story.append(PageBreak())

    def add_friendship_tables(self):
        self.story.append(Paragraph('Composite Friendship Tables', self.header_style))
        planets = ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn']
        header = [''] + planets
        matrix = [header]
        for r in planets:
            row = [r] + ['Neutral']*len(planets)
            matrix.append(row)
        tbl = Table(matrix, colWidths=[0.9*inch]*8)
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F2F2F2')),
            ('BACKGROUND',(0,0),(0,-1),colors.HexColor('#F2F2F2')),
            ('GRID',(0,0),(-1,-1),0.2,colors.HexColor('#CCCCCC')),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),8)
        ]))
        self.story.append(Paragraph('Permanent Friendship', self.text_style))
        self.story.append(tbl)
        self.story.append(Paragraph('Temporal Friendship', self.text_style))
        self.story.append(tbl)
        self.story.append(Paragraph('Five-Fold Friendship', self.text_style))
        self.story.append(tbl)
        self.story.append(PageBreak())

    def add_vimshottari(self):
        self.story.append(CenteredHeader("Vimshottari Dasha"))
        self.story.append(Spacer(1, 10))

        if "Vimshottari" not in data.charts["Dashas"] or "mahadashas" not in data.charts["Dashas"]["Vimshottari"]:
            return

        mahadashas = data.charts["Dashas"]["Vimshottari"]["mahadashas"]
        md_list = list(mahadashas.values())

        # Helper to format date
        def fmt_date(dt_str):
            try:
                dt = datetime.strptime(str(dt_str), "%Y-%m-%d %H:%M:%S")
                return dt.strftime("%a %b %d %Y")
            except:
                try:
                    return str(dt_str).split(' ')[0]
                except:
                    return ""

        cells = []
        col_width = (A4[0] - 60) / 3.0
        
        small_style = ParagraphStyle('Small', parent=self.styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
        small_right = ParagraphStyle('SmallRight', parent=self.styles['Normal'], fontName='Helvetica', fontSize=8, leading=10, alignment=TA_RIGHT)
        header_para_style = ParagraphStyle('MDHeader', parent=self.styles['Normal'], fontName='Helvetica-Bold', fontSize=9, alignment=TA_CENTER, leading=11)

        for md in md_list:
            md_start = fmt_date(md.get("startDate", ""))
            md_end = fmt_date(md.get("endDate", ""))
            
            # Header for the cell
            header_para = Paragraph(f"{md.get('lord','')}<br/>{md_start}<br/>{md_end}", header_para_style)
            
            # Antardashas
            ad_rows = []
            if "antardasha" in md:
                for ad in md["antardasha"]:
                    ad_end = fmt_date(ad.get("endDate", ""))
                    ad_rows.append([Paragraph(f"{ad.get('lord','')}", small_style), Paragraph(f"{ad_end}", small_right)])
            
            if ad_rows:
                ad_table = Table(ad_rows, colWidths=[col_width*0.45, col_width*0.55])
                ad_table.setStyle(TableStyle([
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('LEFTPADDING', (0,0), (-1,-1), 2),
                    ('RIGHTPADDING', (0,0), (-1,-1), 2),
                    ('TOPPADDING', (0,0), (-1,-1), 2),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                    ('ROWBACKGROUNDS', (0,0), (-1,-1), [colors.white, colors.HexColor('#FFF8E1')]),
                ]))
            else:
                ad_table = Paragraph("", small_style)

            cell_content = [[header_para], [ad_table]]
            cell_table = Table(cell_content, colWidths=[col_width-4]) # subtract padding/margin estimate
            cell_table.setStyle(TableStyle([
                ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#DAA520')),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LINEBELOW', (0,0), (-1,0), 0.5, colors.HexColor('#DAA520')),
                ('LEFTPADDING', (0,0), (-1,-1), 0),
                ('RIGHTPADDING', (0,0), (-1,-1), 0),
                ('TOPPADDING', (0,0), (-1,-1), 2),
                ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            cells.append(cell_table)

        grid_data = []
        for i in range(0, len(cells), 3):
            row = cells[i:i+3]
            while len(row) < 3:
                row.append("")
            grid_data.append(row)

        if grid_data:
            final_table = Table(grid_data, colWidths=[col_width, col_width, col_width])
            final_table.setStyle(TableStyle([
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
                ('LEFTPADDING', (0,0), (-1,-1), 2),
                ('RIGHTPADDING', (0,0), (-1,-1), 2),
                ('TOPPADDING', (0,0), (-1,-1), 5),
                ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ]))
            self.story.append(final_table)
        
        self.story.append(PageBreak())

    def add_current_dasha(self):
        self.story.append(Paragraph('Current Ongoing Dasha', self.header_style))
        hdr = ['Dasha Name','Planets','Start Date','End Date']
        rows = [hdr]
        cur = data.charts["Dashas"]["Vimshottari"]["current"]
        if cur.get("dasha"):
            d = data.charts["Dashas"]["Vimshottari"]["mahadashas"][cur["dasha"]]
            rows.append([cur["dasha"],'',str(d["startDate"]),str(d["endDate"])])
        tbl = Table(rows, colWidths=[1.6*inch,1.2*inch,1.6*inch,1.6*inch])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor('#F2F2F2')),
            ('GRID',(0,0),(-1,-1),0.2,colors.HexColor('#CCCCCC')),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),8)
        ]))
        self.story.append(tbl)
        self.story.append(Paragraph('NOTE: All dates indicate dashas end date.', self.text_style))
        self.story.append(PageBreak())

    def add_ascendant_report(self, asc):
        self.story.append(Paragraph('Ascendant Report', self.header_style))
        asc_sign_name = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"][asc[0]]
        lord, _ = _sign_meta(asc_sign_name)
        rows = [
            ['Ascendant Name', asc_sign_name],
            ['Lord', lord],
            ['Symbol', ''],
            ['Characteristics', ''],
            ['Lucky Gems', ''],
            ['Day of Fast', ''],
            ['Mantra', '']
        ]
        tbl = Table(rows, colWidths=[2.5*inch, 3.5*inch])
        tbl.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(1,0),colors.HexColor('#F2F2F2')),
            ('BOX',(0,0),(-1,-1),0.8,colors.HexColor('#CCCCCC')),
            ('GRID',(0,0),(-1,-1),0.2,colors.HexColor('#CCCCCC')),
            ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
            ('FONTSIZE',(0,0),(-1,-1),10)
        ]))
        self.story.append(tbl)
        self.story.append(Spacer(1,0.2*inch))
        text = 'Personality, Career, Marriage, Behavior, Strengths'
        for _ in range(5):
            self.story.append(Paragraph(text, self.text_style))
        self.story.append(Paragraph('Spiritual Advice', self.header_style))
        self.story.append(Paragraph('Focus on mindfulness and devotion.', self.text_style))
        self.story.append(Paragraph('Positive Traits', self.header_style))
        self.story.append(Paragraph('• Courage • Compassion • Discipline', self.text_style))
        self.story.append(Paragraph('Negative Traits', self.header_style))
        self.story.append(Paragraph('• Impatience • Overthinking', self.text_style))
        self.story.append(PageBreak())

    def add_footer(self):
        self.story.append(Paragraph('Thank you', self.title_style))
        self.story.append(Paragraph('Company Name', self.text_style))
        self.story.append(Paragraph('Address', self.text_style))
        self.story.append(Paragraph('Website • Email • Phone', self.text_style))

    def build(self):
        jd, pos, sr, ss, ti, yo, na, ka, asc = self.compute()
        self.add_cover(sr, ss)
        self.add_basic_details_grid(sr, ss, ti, yo, na, ka, asc)
        asc_deg = asc[0]*30 + asc[1][0] + asc[1][1]/60 + asc[1][2]/3600
        self.add_planet_table(pos, asc_deg)
        self.add_charts()
        jm.input_birthdata(
            name=self.user_name,
            gender='Male',
            place=self.place,
            longitude=str(self.lon),
            lattitude=str(self.lat),
            timezone=str(self.tz),
            year=str(self.year),
            month=str(self.month),
            day=str(self.day),
            hour=self.time_hhmm.split(':')[0],
            min=self.time_hhmm.split(':')[1],
            sec='0'
        )
        if jm.validate_birthdata() == 'SUCCESS':
            bd = jm.get_birthdata()
            astro = jm.generate_astrologicalData(bd, 'ASTRODATA_DICTIONARY')
            dasha_support.clearDashaDetails()
            dasha_support.Vimshottari(astro['D1'], bd)
            self.add_vimshottari()
            self.add_current_dasha()
        self.add_ascendant_report(asc)
        self.add_footer()
        self.doc.build(self.story)

def generate_kundali_pdf(user_name, day, month, year, time_hhmm, tz, place, lat, lon, company_name="",company_mobile="",api_id=""):
    k = KundaliPDF(user_name, day, month, year, time_hhmm, tz, place, lat, lon, company_name,company_mobile,api_id)
    k.build()
