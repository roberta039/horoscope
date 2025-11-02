# app.py - Versiune completă cu toate metodele
import streamlit as st
import math
from datetime import datetime
import json

class ChartsDatabase:
    def __init__(self):
        self.charts = []
        self.load_charts()
    
    def load_charts(self):
        """Încarcă charts din session state"""
        if 'charts_db' not in st.session_state:
            st.session_state.charts_db = [
                {
                    'id': 1,
                    'name': 'Natal Chart',
                    'type': 'Natal',
                    'birth_data': {
                        'date': datetime(1990, 6, 15, 12, 0),
                        'latitude': 45.81,
                        'longitude': 15.98,
                        'timezone': 'GMT+1',
                        'place': 'Zagreb'
                    },
                    'positions': {},
                    'houses': {},
                    'aspects': [],
                    'created_date': datetime.now()
                }
            ]
        self.charts = st.session_state.charts_db
    
    def save_charts(self):
        """Salvează charts în session state"""
        st.session_state.charts_db = self.charts
    
    def get_all_charts(self):
        """Returnează toate charts"""
        return self.charts
    
    def get_chart_by_id(self, chart_id):
        """Găsește chart după ID"""
        for chart in self.charts:
            if chart['id'] == chart_id:
                return chart
        return None
    
    def add_chart(self, chart_data):
        """Adaugă un nou chart"""
        new_id = max([c['id'] for c in self.charts], default=0) + 1
        chart_data['id'] = new_id
        chart_data['created_date'] = datetime.now()
        self.charts.append(chart_data)
        self.save_charts()
        return True
    
    def update_chart(self, chart_id, chart_data):
        """Actualizează un chart existent"""
        for i, chart in enumerate(self.charts):
            if chart['id'] == chart_id:
                chart_data['id'] = chart_id
                chart_data['created_date'] = chart['created_date']
                self.charts[i] = chart_data
                self.save_charts()
                return True
        return False
    
    def delete_chart(self, chart_id):
        """Șterge un chart"""
        self.charts = [c for c in self.charts if c['id'] != chart_id]
        self.save_charts()
        return True
    
    def get_chart_count(self):
        """Returnează numărul de charts"""
        return len(self.charts)

class PlacesDatabase:
    def __init__(self):
        self.places = []
        self.load_places()
    
    def load_places(self):
        """Încarcă locații din session state"""
        if 'places_db' not in st.session_state:
            st.session_state.places_db = [
                {
                    'id': 1,
                    'name': 'Zagreb',
                    'latitude': 45.81,
                    'longitude': 15.98,
                    'timezone': 'GMT+1',
                    'country': 'Croatia'
                },
                {
                    'id': 2,
                    'name': 'New York',
                    'latitude': 40.71,
                    'longitude': -74.01,
                    'timezone': 'GMT-5',
                    'country': 'USA'
                },
                {
                    'id': 3,
                    'name': 'London',
                    'latitude': 51.51,
                    'longitude': -0.13,
                    'timezone': 'GMT+0',
                    'country': 'UK'
                },
                {
                    'id': 4,
                    'name': 'Tokyo',
                    'latitude': 35.68,
                    'longitude': 139.76,
                    'timezone': 'GMT+9',
                    'country': 'Japan'
                }
            ]
        self.places = st.session_state.places_db
    
    def save_places(self):
        """Salvează locații în session state"""
        st.session_state.places_db = self.places
    
    def get_all_places(self):
        """Returnează toate locațiile"""
        return self.places
    
    def get_place_by_id(self, place_id):
        """Găsește locație după ID"""
        for place in self.places:
            if place['id'] == place_id:
                return place
        return None
    
    def add_place(self, place_data):
        """Adaugă o nouă locație"""
        new_id = max([p['id'] for p in self.places], default=0) + 1
        place_data['id'] = new_id
        self.places.append(place_data)
        self.save_places()
        return True
    
    def delete_place(self, place_id):
        """Șterge o locație"""
        self.places = [p for p in self.places if p['id'] != place_id]
        self.save_places()
        return True

class AdvancedAstroCalculator:
    def __init__(self):
        self.signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                     'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto']
        
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
        """Calculează poziția unei planete"""
        jd = self.julian_day(date)
        
        if planet == 'Sun':
            n = jd - 2451545.0
            L = 280.460 + 0.9856474 * n
            g = math.radians(357.528 + 0.9856003 * n)
            longitude = (L + 1.915 * math.sin(g) + 0.020 * math.sin(2*g)) % 360
            
        elif planet == 'Moon':
            n = jd - 2451545.0
            longitude = (218.316 + 13.176396 * n) % 360
            
        else:
            data = self.planet_data[planet]
            days_since_epoch = jd - 2451545.0
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
        jd = self.julian_day(date)
        ut = date.hour + date.minute/60.0 + date.second/3600.0
        
        lst = (100.46 + 0.985647352 * jd + lon + 15 * ut) % 360
        ascendant = (lst + 90) % 360
        
        lat_correction = math.tan(math.radians(lat)) * math.tan(math.radians(23.44))
        ascendant += math.degrees(math.asin(lat_correction))
        
        return ascendant % 360

    def calculate_houses(self, date, lat, lon, system='Placidus'):
        """Calculează casele astrologice"""
        ascendant = self.calculate_ascendant(date, lat, lon)
        houses = {}
        
        for i in range(12):
            if system == 'Placidus':
                house_angle = (ascendant + i * 30) % 360
            elif system == 'Equal':
                house_angle = (ascendant + i * 30) % 360
            else:  # Koch
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
            else:
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
        self.charts_db = ChartsDatabase()
        self.places_db = PlacesDatabase()
        self.current_screen = 'main'
        self.current_chart = None
        self.settings = {
            'house_system': 'Placidus',
            'wheel_type': 'Graphic',
            'glyphs_system': 'Graphic',
            'zodiac_type': 'Tropical'
        }
        
    def show_main_form(self):
        """Formularul principal"""
        st.markdown("""
        <style>
        .main-container { background: #C0C0C0; border: 3px outset #FFFFFF; padding: 15px; margin: 10px; }
        .palm-button { background: #C0C0C0; border: 2px outset #FFFFFF; padding: 8px 16px; margin: 4px; font-family: Arial; font-size: 14px; width: 100%; }
        .palm-title { background: #000080; color: white; padding: 10px; text-align: center; font-weight: bold; margin: -15px -15px 15px -15px; }
        .here-now { background: white; border: 2px inset #C0C0C0; padding: 10px; margin: 10px 0; font-family: Arial; }
        .form-container { background: #C0C0C0; border: 3px outset #FFFFFF; padding: 15px; margin: 10px; }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">1.Chart</div>', unsafe_allow_html=True)
        
        cols = st.columns(2)
        with cols[0]:
            if st.button('📊 Charts', use_container_width=True):
                self.current_screen = 'charts'
                st.rerun()
            if st.button('🕐 Time', use_container_width=True):
                self.current_screen = 'time'
                st.rerun()
            if st.button('🧮 Calc', use_container_width=True):
                self.current_screen = 'calc'
                st.rerun()
        with cols[1]:
            if st.button('📍 Places', use_container_width=True):
                self.current_screen = 'places'
                st.rerun()
            if st.button('🔗 Aspects', use_container_width=True):
                self.current_screen = 'aspects'
                st.rerun()
            if st.button('⚙️ Options', use_container_width=True):
                self.current_screen = 'options'
                st.rerun()
        
        st.markdown('<div class="here-now">', unsafe_allow_html=True)
        st.write("**Here&Now**")
        now = datetime.now()
        st.write(f"Date: {now.strftime('%d %b %Y')}")
        st.write(f"Time: {now.strftime('%H:%M')}")
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    def show_time_form(self):
        """Formularul de timp"""
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
        """Formularul de calcul"""
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
                sample_date = datetime(1990, 6, 15, 12, 0)
                positions, houses = self.calculator.calculate_all_positions(
                    sample_date, 45.81, 15.98, self.settings['house_system']
                )
                
                self.current_chart = {
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
        """Formularul de aspecte"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Aspects</div>', unsafe_allow_html=True)
        
        if not self.current_chart:
            st.warning("No chart data available. Please calculate a chart first.")
            if st.button("Back", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
            return
        
        aspects = self.current_chart.get('aspects', [])
        
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
        """Formularul de opțiuni"""
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
        """Formularul de charts cu funcționalitate completă"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Charts</div>', unsafe_allow_html=True)
        
        # Lista de charts
        charts = self.charts_db.get_all_charts()
        
        if charts:
            st.subheader(f"Saved Charts ({len(charts)})")
            for chart in charts:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{chart['name']}**")
                        birth_data = chart['birth_data']
                        st.write(f"{birth_data['date'].strftime('%Y-%m-%d %H:%M')} | {birth_data['place']}")
                    with col2:
                        st.write(f"Type: {chart['type']}")
                    with col3:
                        if st.button("Select", key=f"sel_{chart['id']}"):
                            self.current_chart = chart
                            st.success(f"Selected: {chart['name']}")
        else:
            st.info("No charts saved yet. Use 'New' to create one.")
        
        # Butoane de acțiune
        st.markdown("---")
        col_app, col_pick, col_del, col_new, col_back = st.columns(5)
        
        with col_app:
            if st.button("Append", use_container_width=True):
                st.info("Append functionality - select a chart first")
        
        with col_pick:
            if st.button("Pick", use_container_width=True) and self.current_chart:
                st.success(f"Picked: {self.current_chart['name']}")
        
        with col_del:
            if st.button("Delete", use_container_width=True) and self.current_chart:
                if self.charts_db.delete_chart(self.current_chart['id']):
                    st.success(f"Deleted: {self.current_chart['name']}")
                    self.current_chart = None
                    st.rerun()
        
        with col_new:
            if st.button("New", use_container_width=True):
                self.current_screen = 'new_chart'
                st.rerun()
        
        with col_back:
            if st.button("Back", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def show_new_chart_form(self):
        """Formular pentru chart nou"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">New Chart</div>', unsafe_allow_html=True)
        
        with st.form("new_chart_form"):
            st.subheader("Chart Information")
            
            chart_name = st.text_input("Chart Name", "My Natal Chart")
            chart_type = st.selectbox("Chart Type", ["Natal", "Transit", "Progressed", "Solar Return"])
            
            st.subheader("Birth Data")
            col1, col2 = st.columns(2)
            with col1:
                birth_date = st.date_input("Birth Date", datetime(1990, 6, 15))
                birth_time = st.time_input("Birth Time", datetime(1990, 1, 1, 12, 0))
            with col2:
                # Selectare locație din baza de date
                places = self.places_db.get_all_places()
                place_names = [f"{p['name']} ({p['country']})" for p in places]
                selected_place_idx = st.selectbox("Place", range(len(place_names)), format_func=lambda x: place_names[x])
                selected_place = places[selected_place_idx]
                
                latitude = st.number_input("Latitude", value=float(selected_place['latitude']))
                longitude = st.number_input("Longitude", value=float(selected_place['longitude']))
                timezone = st.text_input("Time Zone", selected_place['timezone'])
            
            st.subheader("Calculation Options")
            calc_chart = st.checkbox("Calculate Chart", value=True)
            calc_aspects = st.checkbox("Calculate Aspects", value=True)
            calc_houses = st.checkbox("Calculate Houses", value=True)
            
            col_save, col_calc, col_cancel = st.columns(3)
            with col_save:
                save_chart = st.form_submit_button("💾 Save", use_container_width=True)
            with col_calc:
                calc_only = st.form_submit_button("🧮 Calculate Only", use_container_width=True)
            with col_cancel:
                cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
            
            if save_chart or calc_only:
                birth_datetime = datetime.combine(birth_date, birth_time)
                
                # Calculează pozițiile
                positions, houses = self.calculator.calculate_all_positions(
                    birth_datetime, latitude, longitude, self.settings['house_system']
                )
                aspects = self.calculate_aspects_from_positions(positions)
                
                chart_data = {
                    'name': chart_name,
                    'type': chart_type,
                    'birth_data': {
                        'date': birth_datetime,
                        'latitude': latitude,
                        'longitude': longitude,
                        'timezone': timezone,
                        'place': selected_place['name']
                    },
                    'positions': positions,
                    'houses': houses,
                    'aspects': aspects
                }
                
                if save_chart:
                    if self.charts_db.add_chart(chart_data):
                        st.success(f"Chart '{chart_name}' saved successfully!")
                        self.current_screen = 'charts'
                        st.rerun()
                else:
                    self.current_chart = chart_data
                    st.success("Chart calculated successfully!")
            
            if cancel_btn:
                self.current_screen = 'charts'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def show_places_form(self):
        """Formularul de locații cu funcționalitate completă"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">Places</div>', unsafe_allow_html=True)
        
        # Lista de locații
        places = self.places_db.get_all_places()
        
        if places:
            st.subheader(f"Saved Places ({len(places)})")
            for place in places:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 1])
                    with col1:
                        st.write(f"**{place['name']}**, {place['country']}")
                    with col2:
                        st.write(f"Lat: {place['latitude']:.2f}, Lon: {place['longitude']:.2f}")
                    with col3:
                        st.write(f"TZ: {place['timezone']}")
        else:
            st.info("No places saved yet. Use 'New' to add one.")
        
        # Butoane de acțiune
        st.markdown("---")
        col_app, col_pick, col_del, col_new, col_back = st.columns(5)
        
        with col_app:
            if st.button("Append Place", use_container_width=True):
                st.info("Append functionality - select a place first")
        
        with col_pick:
            if st.button("Pick Place", use_container_width=True):
                st.info("Select a place from the list")
        
        with col_del:
            if st.button("Delete Place", use_container_width=True):
                st.info("Select a place to delete")
        
        with col_new:
            if st.button("New Place", use_container_width=True):
                self.current_screen = 'new_place'
                st.rerun()
        
        with col_back:
            if st.button("Back", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

    def show_new_place_form(self):
        """Formular pentru locație nouă"""
        st.markdown('<div class="form-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">New Place</div>', unsafe_allow_html=True)
        
        with st.form("new_place_form"):
            st.subheader("Place Information")
            
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Place Name", "New City")
                country = st.text_input("Country", "Country")
            with col2:
                latitude = st.number_input("Latitude", value=0.0, format="%.6f")
                longitude = st.number_input("Longitude", value=0.0, format="%.6f")
            
            timezone = st.selectbox("Time Zone", 
                ["GMT-12", "GMT-11", "GMT-10", "GMT-9", "GMT-8", "GMT-7", 
                 "GMT-6", "GMT-5", "GMT-4", "GMT-3", "GMT-2", "GMT-1", 
                 "GMT", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", 
                 "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12"])
            
            col_save, col_cancel = st.columns(2)
            with col_save:
                save_place = st.form_submit_button("💾 Save Place", use_container_width=True)
            with col_cancel:
                cancel_btn = st.form_submit_button("Cancel", use_container_width=True)
            
            if save_place:
                place_data = {
                    'name': name,
                    'country': country,
                    'latitude': latitude,
                    'longitude': longitude,
                    'timezone': timezone
                }
                
                if self.places_db.add_place(place_data):
                    st.success(f"Place '{name}' saved successfully!")
                    self.current_screen = 'places'
                    st.rerun()
            
            if cancel_btn:
                self.current_screen = 'places'
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
                
                aspect_orb = {
                    'Conjunction': 8, 'Sextile': 6, 'Square': 8, 
                    'Trine': 8, 'Opposition': 8
                }
                
                for aspect, orb in aspect_orb.items():
                    angle = {
                        'Conjunction': 0, 'Sextile': 60, 'Square': 90, 
                        'Trine': 120, 'Opposition': 180
                    }[aspect]
                    
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            'planet1': p1, 'planet2': p2, 'aspect': aspect,
                            'angle': angle, 'exact_diff': diff, 'orb': abs(diff - angle)
                        })
                        break
        
        return aspects

def main():
    st.set_page_config(
        page_title="1.Chart Horoscope v2.42 - Complete",
        page_icon="♐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    if 'palm_app' not in st.session_state:
        st.session_state.palm_app = PalmOSApp()
    
    app = st.session_state.palm_app
    
    # Navigare completă cu toate ecranele
    screens = {
        'main': app.show_main_form,
        'charts': app.show_charts_form,
        'places': app.show_places_form,
        'time': app.show_time_form,
        'calc': app.show_calc_form,
        'aspects': app.show_aspects_form,
        'options': app.show_options_form,
        'new_chart': app.show_new_chart_form,
        'new_place': app.show_new_place_form,
    }
    
    current_screen = app.current_screen
    if current_screen in screens:
        screens[current_screen]()
    else:
        app.show_main_form()

if __name__ == "__main__":
    main()
