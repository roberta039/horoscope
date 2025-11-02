# app.py - Versiune completă integrată
import streamlit as st
import math
from datetime import datetime

class AdvancedAstroCalculator:
    def __init__(self):
        self.signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
        # Elemente orbitale aproximative (simplificate)
        self.planet_data = {
            'Sun': {'period': 365.25, 'offset': 280.0},
            'Moon': {'period': 27.3217, 'offset': 0.0},
            'Mercury': {'period': 87.969, 'offset': 0.0},
            'Venus': {'period': 224.701, 'offset': 0.0},
            'Mars': {'period': 686.98, 'offset': 0.0},
            'Jupiter': {'period': 4332.589, 'offset': 0.0},
            'Saturn': {'period': 10759.22, 'offset': 0.0},
            'Uranus': {'period': 30685.4, 'offset': 0.0},
            'Neptune': {'period': 60189.0, 'offset': 0.0},
            'Pluto': {'period': 90465.0, 'offset': 0.0}
        }

    def julian_day(self, date):
        """Calculează ziua juliană"""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        
        jd = date.day + ((153 * m + 2) // 5) + 365 * y + (y // 4) - (y // 100) + (y // 400) - 32045
        time_fraction = (date.hour - 12) / 24.0 + date.minute / 1440.0 + date.second / 86400.0
        return jd + time_fraction

    def calculate_planet_position(self, planet, date):
        """Calculează poziția unei planete folosind algoritmi simplificați"""
        jd = self.julian_day(date)
        
        if planet == 'Sun':
            # Poziția Soarelui - calcul simplificat
            n = jd - 2451545.0  # Număr de zile de la epoch J2000
            L = 280.460 + 0.9856474 * n  # Longitudine medie
            g = math.radians(357.528 + 0.9856003 * n)  # Anomalie medie
            longitude = (L + 1.915 * math.sin(g) + 0.020 * math.sin(2*g)) % 360
            
        elif planet == 'Moon':
            # Poziția Lunii - calcul simplificat
            n = jd - 2451545.0
            longitude = (218.316 + 13.176396 * n) % 360
            
        else:
            # Pentru alte planete - calcul bazat pe perioade orbitale
            data = self.planet_data[planet]
            days_since_epoch = jd - 2451545.0  # J2000
            longitude = (data['offset'] + (days_since_epoch / data['period']) * 360) % 360
        
        sign_index = int(longitude / 30)
        degree = longitude % 30
        
        return {
            'longitude': longitude,
            'sign': self.signs[sign_index],
            'sign_index': sign_index,
            'degree': degree,
            'minute': (degree - int(degree)) * 60
        }

    def calculate_ascendant(self, date, lat, lon):
        """Calculează ascendentul"""
        # Calcul simplificat al ascendentului
        jd = self.julian_day(date)
        ut = date.hour + date.minute/60.0 + date.second/3600.0
        
        # Longitudine ecliptică a punctului estic
        lst = (100.46 + 0.985647352 * jd + lon + 15 * ut) % 360
        ascendant = (lst + 90) % 360
        
        # Corecție pentru latitudine (simplificată)
        lat_correction = math.tan(math.radians(lat)) * math.tan(math.radians(23.44))
        ascendant += math.degrees(math.asin(lat_correction))
        
        return ascendant % 360

    def calculate_houses(self, date, lat, lon, system='Placidus'):
        """Calculează casele astrologice"""
        ascendant = self.calculate_ascendant(date, lat, lon)
        houses = {}
        
        if system == 'Placidus':
            # Sistem Placidus simplificat
            for i in range(12):
                house_angle = (ascendant + i * 30) % 360
                houses[i + 1] = {
                    'position': house_angle,
                    'sign': self.signs[int(house_angle / 30) % 12],
                    'longitude': house_angle
                }
                
        elif system == 'Equal':
            # Case egale
            for i in range(12):
                house_angle = (ascendant + i * 30) % 360
                houses[i + 1] = {
                    'position': house_angle,
                    'sign': self.signs[int(house_angle / 30) % 12],
                    'longitude': house_angle
                }
                
        else:  # Koch
            # Sistem Koch simplificat
            for i in range(12):
                house_angle = (ascendant + (i * 30) + (i * i * 0.5)) % 360
                houses[i + 1] = {
                    'position': house_angle,
                    'sign': self.signs[int(house_angle / 30) % 12],
                    'longitude': house_angle
                }
        
        return houses

    def get_planet_house(self, planet_longitude, houses):
        """Determină casa unei planete"""
        for house_num, house_data in houses.items():
            house_start = house_data['longitude']
            house_end = (house_start + 30) % 360
            
            if house_start <= house_end:
                if house_start <= planet_longitude < house_end:
                    return house_num
            else:  # Cazul când casa trece peste 360°
                if planet_longitude >= house_start or planet_longitude < house_end:
                    return house_num
        return 1

    def calculate_all_positions(self, date, lat, lon, house_system='Placidus'):
        """Calculează toate pozițiile planetare și casele"""
        houses = self.calculate_houses(date, lat, lon, house_system)
        positions = {}
        
        for planet in self.planets:
            pos = self.calculate_planet_position(planet, date)
            house = self.get_planet_house(pos['longitude'], houses)
            
            positions[planet] = {
                'longitude': pos['longitude'],
                'sign': pos['sign'],
                'sign_index': pos['sign_index'],
                'degree': int(pos['degree']),
                'minute': int(pos['minute']),
                'house': house,
                'house_position': f"House {house}"
            }
        
        # Adaugă ascendentul
        ascendant_pos = self.calculate_ascendant(date, lat, lon)
        ascendant_sign_index = int(ascendant_pos / 30)
        
        positions['Ascendant'] = {
            'longitude': ascendant_pos,
            'sign': self.signs[ascendant_sign_index],
            'sign_index': ascendant_sign_index,
            'degree': int(ascendant_pos % 30),
            'minute': int((ascendant_pos % 30 - int(ascendant_pos % 30)) * 60),
            'house': 1,
            'house_position': 'Ascendant'
        }
        
        return positions, houses

class PalmOSApp:
    def __init__(self):
        self.calculator = AdvancedAstroCalculator()
        self.current_screen = 'main'
        self.chart_data = None
        self.settings = {
            'house_system': 'Placidus',
            'wheel_type': 'Graphic',
            'glyphs_system': 'Graphic',
            'zodiac_type': 'Tropical'
        }
        
    def show_main_form(self):
        """Formularul principal exact ca în Palm OS"""
        st.markdown("""
        <style>
        .main-container {
            background: #C0C0C0;
            border: 3px outset #FFFFFF;
            padding: 15px;
            margin: 10px;
        }
        .palm-button {
            background: #C0C0C0;
            border: 2px outset #FFFFFF;
            padding: 8px 16px;
            margin: 4px;
            font-family: Arial;
            font-size: 14px;
            width: 100%;
        }
        .palm-title {
            background: #000080;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            margin: -15px -15px 15px -15px;
        }
        .here-now {
            background: white;
            border: 2px inset #C0C0C0;
            padding: 10px;
            margin: 10px 0;
            font-family: Arial;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">1.Chart</div>', unsafe_allow_html=True)
        
        # Butoanele principale
        cols = st.columns(2)
        
        with cols[0]:
            if st.button('📊 Charts', key='btn_charts', use_container_width=True):
                self.current_screen = 'charts'
                st.rerun()
                
            if st.button('🕐 Time', key='btn_time', use_container_width=True):
                self.current_screen = 'time'
                st.rerun()
                
            if st.button('🧮 Calc', key='btn_calc', use_container_width=True):
                self.current_screen = 'calc'
                st.rerun()
        
        with cols[1]:
            if st.button('📍 Places', key='btn_places', use_container_width=True):
                self.current_screen = 'places'
                st.rerun()
                
            if st.button('🔗 Aspects', key='btn_aspects', use_container_width=True):
                self.current_screen = 'aspects'
                st.rerun()
                
            if st.button('⚙️ Options', key='btn_options', use_container_width=True):
                self.current_screen = 'options'
                st.rerun()
        
        # Here & Now
        st.markdown('<div class="here-now">', unsafe_allow_html=True)
        st.write("**Here&Now**")
        now = datetime.now()
        st.write(f"Date: {now.strftime('%d %b %Y')}")
        st.write(f"Time: {now.strftime('%H:%M')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_time_form(self):
        """Formularul de timp ca în original"""
        st.markdown("""
        <style>
        .form-container {
            background: #C0C0C0;
            border: 3px outset #FFFFFF;
            padding: 15px;
            margin: 10px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Set Time</div>', unsafe_allow_html=True)
        
        with st.form("time_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Time of Birth")
                birth_time = st.time_input("", datetime.now().time(), label_visibility="collapsed")
                
                st.subheader("Time Zone")
                timezone = st.selectbox("", 
                    ["GMT-12", "GMT-11", "GMT-10", "GMT-9", "GMT-8", "GMT-7", 
                     "GMT-6", "GMT-5", "GMT-4", "GMT-3", "GMT-2", "GMT-1", 
                     "GMT", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", 
                     "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12"],
                    index=12, label_visibility="collapsed")
            
            with col2:
                st.subheader("Date")
                birth_date = st.date_input("", datetime.now(), label_visibility="collapsed")
            
            # Butoane
            col_ok, col_cancel, col_now = st.columns([2, 2, 1])
            
            with col_ok:
                submit_ok = st.form_submit_button("OK", use_container_width=True)
            
            with col_cancel:
                submit_cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            with col_now:
                submit_now = st.form_submit_button("Now", use_container_width=True)
            
            if submit_ok:
                self.current_screen = 'main'
                st.rerun()
            elif submit_cancel:
                self.current_screen = 'main'
                st.rerun()
            elif submit_now:
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_calc_form(self):
        """Formularul de calcul complet"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Calc</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data")
            if st.button("Input Data", use_container_width=True):
                self.current_screen = 'time'
                st.rerun()
        
        with col2:
            st.subheader("Chart Type")
            chart_type = st.radio("", ["Natal", "Transit", "Progressed"], index=0, label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Checkbox-uri pentru calcul
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        st.subheader("Calculate")
        
        cols = st.columns(5)
        with cols[0]:
            calc_chart = st.checkbox("Ch", value=True, key="calc_ch")
        with cols[1]:
            calc_pos = st.checkbox("Pos", value=True, key="calc_pos")
        with cols[2]:
            calc_asp = st.checkbox("Asp", value=True, key="calc_asp")
        with cols[3]:
            calc_int = st.checkbox("Int", value=False, key="calc_int")
        with cols[4]:
            calc_trn = st.checkbox("Trn", value=False, key="calc_trn")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Buton Calculate
        if st.button("CALCULATE", use_container_width=True, type="primary"):
            with st.spinner("Calculating planetary positions..."):
                # Exemplu de calcul
                sample_date = datetime(1990, 6, 15, 12, 0)
                positions, houses = self.calculator.calculate_all_positions(
                    sample_date, 45.81, 15.98, self.settings['house_system']
                )
                
                self.chart_data = {
                    'positions': positions,
                    'houses': houses,
                    'birth_data': {
                        'date': sample_date,
                        'latitude': 45.81,
                        'longitude': 15.98
                    },
                    'aspects': self.calculate_aspects_from_positions(positions)
                }
            st.success("Calculation complete!")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_aspects_form(self):
        """Formularul de aspecte detaliat"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Aspects</div>', unsafe_allow_html=True)
        
        if not self.chart_data:
            st.warning("No chart data available. Please calculate a chart first.")
            if st.button("Back", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
            return
        
        aspects = self.chart_data.get('aspects', [])
        
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        
        if aspects:
            for aspect in aspects:
                st.write(f"**{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}**")
                st.write(f"Angle: {aspect['angle']}° | Exact: {aspect['exact_diff']:.2f}° | Orb: {aspect['orb']:.2f}°")
                st.divider()
        else:
            st.info("No aspects found within orb limits")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Done", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_options_form(self):
        """Formularul de opțiuni complet"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Options</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="background: white; padding: 10px; margin: 5px; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
            
            st.subheader("House System")
            self.settings['house_system'] = st.radio(
                "",
                ["Placidus", "Koch", "Equal"],
                index=0,
                key="house_system",
                label_visibility="collapsed"
            )
            
            st.subheader("Wheel Type")
            self.settings['wheel_type'] = st.radio(
                "",
                ["Graphic", "Text"],
                index=0,
                key="wheel_type",
                label_visibility="collapsed"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background: white; padding: 10px; margin: 5px; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
            
            st.subheader("Glyphs System")
            self.settings['glyphs_system'] = st.radio(
                "",
                ["Graphic", "Text"],
                index=0,
                key="glyphs_system",
                label_visibility="collapsed"
            )
            
            st.subheader("Zodiac")
            self.settings['zodiac_type'] = st.radio(
                "",
                ["Tropical", "Sidereal"],
                index=0,
                key="zodiac_type",
                label_visibility="collapsed"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Butoane OK și Cancel
        col_ok, col_cancel = st.columns(2)
        
        with col_ok:
            if st.button("OK", use_container_width=True):
                st.success("Options saved!")
                self.current_screen = 'main'
                st.rerun()
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_charts_form(self):
        """Formularul de charts"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Charts</div>', unsafe_allow_html=True)
        
        st.info("Charts database functionality - To be implemented")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_places_form(self):
        """Formularul de places"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Places</div>', unsafe_allow_html=True)
        
        st.info("Places database functionality - To be implemented")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def calculate_aspects_from_positions(self, positions):
        """Calculează aspectele din pozițiile planetare"""
        aspects = []
        planets = [p for p in positions.keys() if p != 'Ascendant']
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                lon1 = positions[p1]['longitude']
                lon2 = positions[p2]['longitude']
                
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verifică aspecte majore
                aspect_orb = {
                    'Conjunction': 8,
                    'Sextile': 6,
                    'Square': 8,
                    'Trine': 8,
                    'Opposition': 8
                }
                
                for aspect, orb in aspect_orb.items():
                    angle = {
                        'Conjunction': 0,
                        'Sextile': 60,
                        'Square': 90,
                        'Trine': 120,
                        'Opposition': 180
                    }[aspect]
                    
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            'planet1': p1,
                            'planet2': p2,
                            'aspect': aspect,
                            'angle': angle,
                            'exact_diff': diff,
                            'orb': abs(diff - angle)
                        })
                        break
        
        return aspects

def main():
    st.set_page_config(
        page_title="1.Chart Horoscope v2.42 - Exact Replica",
        page_icon="♐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inițializare aplicație
    if 'palm_app' not in st.session_state:
        st.session_state.palm_app = PalmOSApp()
    
    app = st.session_state.palm_app
    
    # Navigare între ecrane
    if app.current_screen == 'main':
        app.show_main_form()
    elif app.current_screen == 'time':
        app.show_time_form()
    elif app.current_screen == 'calc':
        app.show_calc_form()
    elif app.current_screen == 'aspects':
        app.show_aspects_form()
    elif app.current_screen == 'options':
        app.show_options_form()
    elif app.current_screen == 'charts':
        app.show_charts_form()
    elif app.current_screen == 'places':
        app.show_places_form()

if __name__ == "__main__":
    main()
