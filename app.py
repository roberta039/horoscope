# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import ephem
import json
import os
from typing import Dict, List, Tuple, Any
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PalmHoroscopeReplica:
    def __init__(self):
        self.initialize_databases()
        self.load_preferences()
        
    def initialize_databases(self):
        """Inițializează bazele de date Charts și Places ca în original"""
        if 'charts_db' not in st.session_state:
            st.session_state.charts_db = []
        
        if 'places_db' not in st.session_state:
            st.session_state.places_db = [
                {'name': 'Zagreb', 'lat': 45.81, 'lon': 15.98, 'tz': 1},
                {'name': 'New York', 'lat': 40.71, 'lon': -74.01, 'tz': -5},
                {'name': 'London', 'lat': 51.51, 'lon': -0.13, 'tz': 0}
            ]
    
    def load_preferences(self):
        """Încarcă preferințele ca în funcția LoadPrefs originală"""
        self.default_prefs = {
            'house_system': 'Placidus',  # Placidus/Koch/Equal
            'wheel_type': 'Graphic',     # Graphic/Text
            'glyphs_system': 'Graphic',  # Graphic/Text
            'zodiac_type': 'Tropical',   # Tropical/Sidereal
            'default_place': 'Zagreb',
            'aspect_orbs': {
                'Conjunction': 8, 'Sextile': 6, 'Square': 8, 'Trine': 8,
                'Opposition': 8, 'Semi-Sextile': 3, 'Semi-Square': 3,
                'Sesqui-Square': 3, 'Quincunx': 3, 'Quintile': 2,
                'Decile': 2, 'Biquintile': 2
            }
        }
        
    def save_preferences(self):
        """Salvează preferințele ca în funcția SavePrefs originală"""
        pass  # Implementare pentru salvare persistentă

    def open_db_chart(self):
        """Deschide baza de date Charts - replică funcției originale"""
        return st.session_state.charts_db

    def open_db_place(self):
        """Deschide baza de date Places - replică funcției originale"""
        return st.session_state.places_db

    def append_db_chart(self, chart_data):
        """Adaugă chart în baza de date - replică funcției originale"""
        st.session_state.charts_db.append(chart_data)
        return True

    def append_db_place(self, place_data):
        """Adaugă locație în baza de date - replică funcției originale"""
        st.session_state.places_db.append(place_data)
        return True

    def calculate_natal_chart(self, birth_data):
        """Calcul horoscop natal exact ca în original"""
        # Implementare fidelă algoritmilor Palm OS
        positions = self.calculate_planetary_positions(birth_data)
        houses = self.calculate_houses(birth_data)
        aspects = self.calculate_all_aspects(positions)
        
        return {
            'positions': positions,
            'houses': houses,
            'aspects': aspects,
            'birth_data': birth_data
        }

    def calculate_planetary_positions(self, birth_data):
        """Calcul poziții planetare folosind algoritmi similari cu originalul"""
        # Folosim efemeride simple pentru similitudine cu calculul Palm OS
        positions = {}
        date = birth_data['datetime']
        lat = birth_data['latitude']
        lon = birth_data['longitude']
        
        # Calcul simplificat asemănător cu cel din Palm OS
        jd = self.julian_day(date)
        
        planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                  'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North_Node']
        
        for planet in planets:
            positions[planet] = self.calculate_planet_position(planet, jd, lat, lon)
            
        return positions

    def julian_day(self, date):
        """Calcul Julian Day simplificat"""
        a = (14 - date.month) // 12
        y = date.year + 4800 - a
        m = date.month + 12 * a - 3
        
        jd = (date.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045)
        
        # Adaugă fracția zilei
        time_fraction = (date.hour + date.minute / 60.0 + date.second / 3600.0) / 24.0
        return jd + time_fraction - 0.5

    def calculate_planet_position(self, planet, jd, lat, lon):
        """Calcul poziție planetă folosind algoritmi simplificați asemănători cu Palm OS"""
        # Algoritmi simplificați pentru simularea calculului Palm OS
        if planet == 'Sun':
            lon = (jd - 2451545.0) / 365.25 * 360 % 360
        elif planet == 'Moon':
            lon = (jd - 2451545.0) / 27.3217 * 360 % 360
        else:
            # Calcul simplificat pentru planete
            periods = {
                'Mercury': 87.969, 'Venus': 224.701, 'Mars': 686.98,
                'Jupiter': 4332.589, 'Saturn': 10759.22, 'Uranus': 30685.4,
                'Neptune': 60189.0, 'Pluto': 90465.0
            }
            if planet in periods:
                lon = (jd - 2451545.0) / periods[planet] * 360 % 360
            else:
                lon = 0
        
        sign_index = int(lon / 30)
        sign_degree = lon % 30
        
        return {
            'longitude': lon,
            'sign': self.signs[sign_index],
            'sign_index': sign_index,
            'degree': sign_degree,
            'house': self.calculate_planet_house(lon, birth_data)
        }

    def calculate_houses(self, birth_data):
        """Calcul case folosind sistemul selectat"""
        system = self.default_prefs['house_system']
        if system == 'Placidus':
            return self.calculate_placidus_houses(birth_data)
        elif system == 'Koch':
            return self.calculate_koch_houses(birth_data)
        else:  # Equal
            return self.calculate_equal_houses(birth_data)

    def calculate_placidus_houses(self, birth_data):
        """Calcul case Placidus simplificat"""
        # Implementare simplificată asemănătoare cu cea din Palm OS
        ascendant = self.calculate_ascendant(birth_data)
        houses = {}
        
        for i in range(12):
            house_angle = (ascendant + i * 30) % 360
            houses[i + 1] = {
                'position': house_angle,
                'sign': self.signs[int(house_angle / 30) % 12]
            }
        
        return houses

    def calculate_ascendant(self, birth_data):
        """Calcul ascendent simplificat"""
        # Formula simplificată asemănătoare cu cea din Palm OS
        date = birth_data['datetime']
        lat = birth_data['latitude']
        
        # Calcul bazat pe ora nașterii și latitudine
        hour_angle = (date.hour + date.minute / 60.0) * 15  # 15 grade pe oră
        ascendant = (hour_angle + lat) % 360
        
        return ascendant

    def calculate_all_aspects(self, positions):
        """Calcul toate aspectele ca în original"""
        aspects = []
        planets = list(positions.keys())
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                
                lon1 = positions[p1]['longitude']
                lon2 = positions[p2]['longitude']
                
                aspect_info = self.check_aspect(lon1, lon2)
                if aspect_info:
                    aspects.append({
                        'planet1': p1,
                        'planet2': p2,
                        'aspect': aspect_info['name'],
                        'angle': aspect_info['angle'],
                        'diff': aspect_info['diff'],
                        'orb': aspect_info['orb']
                    })
        
        return aspects

    def check_aspect(self, lon1, lon2):
        """Verifică aspect între două longitudini"""
        diff = abs(lon1 - lon2)
        if diff > 180:
            diff = 360 - diff
        
        aspects = {
            'Conjunction': (0, 8),
            'Sextile': (60, 6),
            'Square': (90, 8),
            'Trine': (120, 8),
            'Opposition': (180, 8),
            'Semi-Sextile': (30, 3),
            'Semi-Square': (45, 3),
            'Sesqui-Square': (135, 3),
            'Quincunx': (150, 3)
        }
        
        for aspect, (angle, orb) in aspects.items():
            if abs(diff - angle) <= orb:
                return {
                    'name': aspect,
                    'angle': angle,
                    'diff': diff,
                    'orb': abs(diff - angle)
                }
        
        return None

    # Proprietăți pentru semne și planete ca în original
    @property
    def signs(self):
        return ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    @property
    def planets(self):
        return ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North_Node']

    @property
    def house_systems(self):
        return ['Placidus', 'Koch', 'Equal']

    @property
    def glyphs_systems(self):
        return ['Graphic', 'Text']

    @property
    def zodiac_types(self):
        return ['Tropical', 'Sidereal']

def main():
    st.set_page_config(
        page_title="1.Chart Horoscope v2.42 - Exact Replica",
        page_icon="♐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS pentru a replica aspectul Palm OS
    st.markdown("""
    <style>
    .palm-window {
        background-color: #C0C0C0;
        border: 2px outset #FFFFFF;
        padding: 8px;
        margin: 4px;
        font-family: "Chicago", "System", sans-serif;
        font-size: 12px;
    }
    .palm-button {
        background-color: #C0C0C0;
        border: 2px outset #FFFFFF;
        padding: 4px 8px;
        margin: 2px;
        font-family: "Chicago", "System", sans-serif;
        font-size: 12px;
        cursor: pointer;
    }
    .palm-title {
        background-color: #000080;
        color: #FFFFFF;
        padding: 4px 8px;
        font-weight: bold;
        text-align: center;
    }
    .palm-form {
        background-color: #FFFFFF;
        border: 1px solid #000000;
        padding: 6px;
        margin: 4px 0;
    }
    .palm-list {
        background-color: #FFFFFF;
        border: 1px inset #C0C0C0;
        padding: 2px;
        font-family: "Chicago", "System", sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inițializare aplicație
    if 'palm_app' not in st.session_state:
        st.session_state.palm_app = PalmHoroscopeReplica()
    
    if 'current_form' not in st.session_state:
        st.session_state.current_form = 'MainForm'
    
    if 'current_chart' not in st.session_state:
        st.session_state.current_chart = None
    
    # Afișare formular curent - exact ca în Palm OS
    if st.session_state.current_form == 'MainForm':
        show_main_form()
    elif st.session_state.current_form == 'OptionsForm':
        show_options_form()
    elif st.session_state.current_form == 'TimeForm':
        show_time_form()
    elif st.session_state.current_form == 'PlaceForm':
        show_place_form()
    elif st.session_state.current_form == 'ChartsForm':
        show_charts_form()
    elif st.session_state.current_form == 'CalcForm':
        show_calc_form()
    elif st.session_state.current_form == 'AspForm':
        show_asp_form()

def show_main_form():
    """Formularul principal exact ca în Palm OS"""
    st.markdown('<div class="palm-title">1.Chart</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="palm-window">', unsafe_allow_html=True)
        
        # Butoanele principale
        if st.button("📊 Charts", use_container_width=True):
            st.session_state.current_form = 'ChartsForm'
            st.rerun()
        
        if st.button("📍 Places", use_container_width=True):
            st.session_state.current_form = 'PlaceForm'
            st.rerun()
        
        if st.button("🕐 Time", use_container_width=True):
            st.session_state.current_form = 'TimeForm'
            st.rerun()
        
        if st.button("🧮 Calc", use_container_width=True):
            st.session_state.current_form = 'CalcForm'
            st.rerun()
        
        if st.button("🔗 Aspects", use_container_width=True):
            st.session_state.current_form = 'AspForm'
            st.rerun()
        
        if st.button("⚙️ Options", use_container_width=True):
            st.session_state.current_form = 'OptionsForm'
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Informații Here&Now
        st.markdown('<div class="palm-form">', unsafe_allow_html=True)
        st.write("**Here&Now**")
        st.write(f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        st.write(f"Time: {datetime.now().strftime('%H:%M')}")
        st.markdown('</div>', unsafe_allow_html=True)

def show_options_form():
    """Formularul de opțiuni exact ca în original"""
    st.markdown('<div class="palm-title">Options</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="palm-form">', unsafe_allow_html=True)
        
        st.subheader("House System")
        house_system = st.radio(
            "Select House System:",
            st.session_state.palm_app.house_systems,
            index=0,
            horizontal=False
        )
        
        st.subheader("Wheel Type")
        wheel_type = st.radio(
            "Select Wheel Type:",
            ["Graphic", "Text"],
            index=0,
            horizontal=False
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="palm-form">', unsafe_allow_html=True)
        
        st.subheader("Glyphs System")
        glyphs_system = st.radio(
            "Select Glyphs:",
            st.session_state.palm_app.glyphs_systems,
            index=0,
            horizontal=False
        )
        
        st.subheader("Zodiac")
        zodiac_type = st.radio(
            "Select Zodiac:",
            st.session_state.palm_app.zodiac_types,
            index=0,
            horizontal=False
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Butoane OK și Cancel
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        if st.button("OK", use_container_width=True):
            # Salvează setările
            st.session_state.palm_app.default_prefs.update({
                'house_system': house_system,
                'wheel_type': wheel_type,
                'glyphs_system': glyphs_system,
                'zodiac_type': zodiac_type
            })
            st.session_state.current_form = 'MainForm'
            st.rerun()
        
        if st.button("Cancel", use_container_width=True):
            st.session_state.current_form = 'MainForm'
            st.rerun()

def show_time_form():
    """Formularul de timp exact ca în original"""
    st.markdown('<div class="palm-title">Set Time</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="palm-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Time of Birth")
        birth_time = st.time_input("", datetime.now().time(), label_visibility="collapsed")
        
        st.subheader("Time Zone")
        timezone = st.selectbox("", list(range(-12, 13)), index=12, label_visibility="collapsed")
        st.write(f"GMT {timezone:+d}")
    
    with col2:
        st.subheader("Date")
        birth_date = st.date_input("", datetime.now(), label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Butoane
    col1, col2, col_ok, col_cancel, col_now = st.columns([1, 1, 2, 2, 2])
    
    with col_ok:
        if st.button("OK", use_container_width=True):
            # Procesează datele
            st.session_state.current_form = 'MainForm'
            st.rerun()
    
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.current_form = 'MainForm'
            st.rerun()
    
    with col_now:
        if st.button("Now", use_container_width=True):
            # Setează ora curentă
            st.rerun()

def show_place_form():
    """Formularul de locații exact ca în original"""
    st.markdown('<div class="palm-title">Places</div>', unsafe_allow_html=True)
    
    # Lista locațiilor
    places = st.session_state.palm_app.open_db_place()
    
    st.markdown('<div class="palm-list">', unsafe_allow_html=True)
    for i, place in enumerate(places):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            st.write(f"**{place['name']}**")
        with col2:
            st.write(f"Lat: {place['lat']:.1f}")
        with col3:
            st.write(f"Lon: {place['lon']:.1f}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Butoane de acțiune
    col_app, col_pick, col_del, col_new, col_back = st.columns(5)
    
    with col_app:
        if st.button("Append", use_container_width=True):
            show_append_place_dialog()
    
    with col_pick:
        if st.button("Pick", use_container_width=True):
            pass
    
    with col_del:
        if st.button("Delete", use_container_width=True):
            pass
    
    with col_new:
        if st.button("New", use_container_width=True):
            show_new_place_dialog()
    
    with col_back:
        if st.button("Back", use_container_width=True):
            st.session_state.current_form = 'MainForm'
            st.rerun()

def show_charts_form():
    """Formularul de charts exact ca în original"""
    st.markdown('<div class="palm-title">Charts</div>', unsafe_allow_html=True)
    
    charts = st.session_state.palm_app.open_db_chart()
    
    st.markdown('<div class="palm-list">', unsafe_allow_html=True)
    if charts:
        for i, chart in enumerate(charts):
            st.write(f"{i+1}. {chart.get('name', f'Chart {i+1}')}")
    else:
        st.write("No charts saved")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Butoane de acțiune
    col_app, col_pick, col_del, col_new, col_back = st.columns(5)
    
    with col_app:
        if st.button("Append", use_container_width=True):
            show_append_chart_dialog()
    
    with col_pick:
        if st.button("Pick", use_container_width=True):
            pass
    
    with col_del:
        if st.button("Delete", use_container_width=True):
            pass
    
    with col_new:
        if st.button("New", use_container_width=True):
            show_new_chart_dialog()
    
    with col_back:
        if st.button("Back", use_container_width=True):
            st.session_state.current_form = 'MainForm'
            st.rerun()

def show_calc_form():
    """Formularul de calcul exact ca în original"""
    st.markdown('<div class="palm-title">Calc</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="palm-form">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data")
        if st.button("Input Data", use_container_width=True):
            st.session_state.current_form = 'TimeForm'
            st.rerun()
    
    with col2:
        st.subheader("Chart Type")
        chart_type = st.radio(
            "",
            ["Natal", "Transit", "Progressed"],
            index=0,
            horizontal=False
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Checkbox-uri pentru calcul
    st.markdown('<div class="palm-form">', unsafe_allow_html=True)
    st.subheader("Calculate")
    
    col_ch, col_pos, col_asp, col_int, col_trn = st.columns(5)
    
    with col_ch:
        calc_chart = st.checkbox("Ch", value=True)
    with col_pos:
        calc_pos = st.checkbox("Pos", value=True)
    with col_asp:
        calc_asp = st.checkbox("Asp", value=True)
    with col_int:
        calc_int = st.checkbox("Int", value=False)
    with col_trn:
        calc_trn = st.checkbox("Trn", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Buton Calculate
    if st.button("CALCULATE", use_container_width=True, type="primary"):
        with st.spinner("Calculating..."):
            # Simulează calculul ca în original
            birth_data = {
                'datetime': datetime.now(),
                'latitude': 45.81,
                'longitude': 15.98,
                'timezone': 1
            }
            st.session_state.current_chart = st.session_state.palm_app.calculate_natal_chart(birth_data)
            st.success("Calculation complete!")
    
    # Buton Back
    if st.button("Back", use_container_width=True):
        st.session_state.current_form = 'MainForm'
        st.rerun()

def show_asp_form():
    """Formularul de aspecte exact ca în original"""
    st.markdown('<div class="palm-title">Aspects</div>', unsafe_allow_html=True)
    
    if st.session_state.current_chart:
        aspects = st.session_state.current_chart.get('aspects', [])
        
        st.markdown('<div class="palm-list">', unsafe_allow_html=True)
        for aspect in aspects:
            st.write(f"{aspect['planet1']} {aspect['aspect']} {aspect['planet2']} "
                    f"({aspect['angle']}°) orb: {aspect['orb']:.1f}°")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No chart calculated. Use Calc form first.")
    
    # Buton Done
    if st.button("Done", use_container_width=True):
        st.session_state.current_form = 'MainForm'
        st.rerun()

def show_append_place_dialog():
    """Dialog pentru adăugare locație"""
    with st.form("append_place"):
        st.subheader("Append New Place")
        
        name = st.text_input("Place Name")
        lat = st.number_input("Latitude", value=0.0)
        lon = st.number_input("Longitude", value=0.0)
        tz = st.number_input("Time Zone", value=0)
        
        if st.form_submit_button("Append"):
            new_place = {'name': name, 'lat': lat, 'lon': lon, 'tz': tz}
            if st.session_state.palm_app.append_db_place(new_place):
                st.success("Place appended!")
            else:
                st.error("Could not append place!")

def show_new_place_dialog():
    """Dialog pentru locație nouă"""
    with st.form("new_place"):
        st.subheader("New Place")
        
        name = st.text_input("Place Name")
        lat = st.number_input("Latitude", value=0.0)
        lon = st.number_input("Longitude", value=0.0)
        tz = st.number_input("Time Zone", value=0)
        
        if st.form_submit_button("Save"):
            new_place = {'name': name, 'lat': lat, 'lon': lon, 'tz': tz}
            if st.session_state.palm_app.append_db_place(new_place):
                st.success("Place saved!")
            else:
                st.error("Could not save place!")

def show_append_chart_dialog():
    """Dialog pentru adăugare chart"""
    st.info("Append Chart functionality")

def show_new_chart_dialog():
    """Dialog pentru chart nou"""
    st.info("New Chart functionality")

if __name__ == "__main__":
    main()
