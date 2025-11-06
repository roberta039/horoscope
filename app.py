import streamlit as st
import datetime
from datetime import datetime
import math
import pandas as pd
import swisseph as swe
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Circle, Wedge
import matplotlib.patches as patches
import time

def main():
    st.set_page_config(
        page_title="Professional Horoscope", 
        layout="wide", 
        page_icon="♈",
        initial_sidebar_state="expanded"
    )
    
    # Inițializare session state cu valori default
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    if 'calculation_time' not in st.session_state:
        st.session_state.calculation_time = 0
    
    # Custom CSS pentru îmbunătățirea interfeței
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #FFD700;
        text-align: center;
        margin-bottom: 1rem;
    }
    .planet-card {
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FFD700;
        background-color: #262730;
        margin: 0.2rem 0;
    }
    .house-card {
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E90FF;
        background-color: #262730;
        margin: 0.2rem 0;
    }
    .aspect-card {
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #FF69B4;
        background-color: #262730;
        margin: 0.2rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar meniu
    with st.sidebar:
        st.markdown('<div class="main-header">♈ Professional Horoscope</div>', unsafe_allow_html=True)
        st.markdown("---")
        
        menu_option = st.radio(
            "**Main Menu**", 
            ["📅 Data Input", "🎯 Chart", "📍 Positions", "🔄 Aspects", "📖 Interpretation", "ℹ️ About"],
            index=0
        )
        
        # Afișează info calcul dacă există
        if st.session_state.chart_data:
            st.markdown("---")
            st.success("✅ Chart Calculated")
            if st.session_state.birth_data:
                st.write(f"**Name:** {st.session_state.birth_data.get('name', 'N/A')}")
                st.write(f"**Date:** {st.session_state.birth_data.get('date', 'N/A')}")
                st.write(f"**Time:** {st.session_state.birth_data.get('time', 'N/A')}")
            st.write(f"**Calculation time:** {st.session_state.calculation_time:.2f}s")
    
    # Navigare pagini
    if menu_option == "📅 Data Input":
        data_input_form()
    elif menu_option == "🎯 Chart":
        display_chart()
    elif menu_option == "📍 Positions":
        display_positions()
    elif menu_option == "🔄 Aspects":
        display_aspects()
    elif menu_option == "📖 Interpretation":
        display_interpretation()
    elif menu_option == "ℹ️ About":
        display_about()

@st.cache_data
def setup_ephemeris():
    """Configurează calea către fișierele de efemeride cu caching"""
    try:
        # Căi prioritate pentru diferite medii
        possible_paths = [
            '/mount/src/horoscope/ephe',  # Streamlit Cloud
            './ephe',                           # Cale relativă locală
            './swisseph-data/ephe',             # Submodul
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe'),  # Cale absolută
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swisseph-data', 'ephe')
        ]
        
        for ephe_path in possible_paths:
            if os.path.exists(ephe_path):
                swe.set_ephe_path(ephe_path)
                return True, f"Ephemeris path: {ephe_path}"
        
        # Fallback: folosește fișierele incluse cu pyswisseph
        swe.set_ephe_path(None)
        return True, "Using built-in Swiss Ephemeris files"
        
    except Exception as e:
        return False, f"Error setting up ephemeris: {e}"

@st.cache_data(ttl=3600)  # Cache pentru 1 oră
def calculate_chart_cached(_birth_data):
    """Versiune cached a calculului chart-ului"""
    return calculate_chart(_birth_data)

def calculate_chart(birth_data):
    """Calculează harta astrologică folosind Swiss Ephemeris"""
    start_time = time.time()
    
    try:
        # Configurează efemeridele
        success, message = setup_ephemeris()
        if not success:
            st.error(f"Eroare efemeride: {message}")
            return None
        
        # Validare date
        if not validate_birth_data(birth_data):
            return None
        
        # Convertire date în format Julian
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        jd = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, 
                       birth_datetime.hour + birth_datetime.minute/60.0)
        
        # Calcul poziții planetare
        planets_data = calculate_planetary_positions_swiss(jd)
        if planets_data is None:
            return None
        
        # Calcul case Placidus
        houses_data = calculate_houses_placidus_swiss(jd, birth_data['lat_deg'], birth_data['lon_deg'])
        if houses_data is None:
            return None
        
        # Asociem planetele cu casele
        for planet_name, planet_data in planets_data.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_swiss(planet_longitude, houses_data)
            
            # Formatare string pozitie detaliată
            retro_symbol = " 🔄" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']} (House {planet_data['house']}){retro_symbol}"
            planet_data['position_short'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}{retro_symbol}"
        
        calculation_time = time.time() - start_time
        
        return {
            'planets': planets_data,
            'houses': houses_data,
            'jd': jd,
            'calculation_time': calculation_time
        }
        
    except Exception as e:
        st.error(f"❌ Eroare la calcularea chart-ului: {str(e)}")
        return None

def validate_birth_data(birth_data):
    """Validează datele de intrare"""
    try:
        if not birth_data.get('name', '').strip():
            st.warning("⚠️ Please enter a name")
            return False
            
        if birth_data['lat_deg'] < -90 or birth_data['lat_deg'] > 90:
            st.error("❌ Latitude must be between -90 and 90 degrees")
            return False
            
        if birth_data['lon_deg'] < -180 or birth_data['lon_deg'] > 180:
            st.error("
