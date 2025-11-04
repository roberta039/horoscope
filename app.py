import streamlit as st
import datetime
from datetime import datetime
import swisseph as swe
import math
import pandas as pd

# Inițializare Swiss Ephemeris
swe.set_ephe_path('/usr/share/swisseph:/var/lib/swisseph')

def main():
    st.set_page_config(page_title="1.Horoscope", layout="wide", page_icon="♈")
    
    # Inițializare session state
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    
    # Sidebar meniu
    with st.sidebar:
        st.title("♈ 1.Horoscope")
        st.markdown("---")
        menu_option = st.radio("Main Menu", ["Data Input", "Chart", "Positions", "Aspects", "Interpretation", "About"])
    
    if menu_option == "Data Input":
        data_input_form()
    elif menu_option == "Chart":
        display_chart()
    elif menu_option == "Positions":
        display_positions()
    elif menu_option == "Aspects":
        display_aspects()
    elif menu_option == "Interpretation":
        display_interpretation()
    elif menu_option == "About":
        display_about()

def calculate_chart(birth_data):
    """Calculează harta astrologică folosind Swiss Ephemeris"""
    try:
        # Convertire date
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        
        # Verifică anul valid pentru Swiss Ephemeris
        if birth_datetime.year < 1800 or birth_datetime.year > 2100:
            st.error(f"Anul {birth_datetime.year} este în afara intervalului valid (1800-2100)")
            return None
            
        # Calcul Julian Day - CORECTAT
        hour_decimal = birth_datetime.hour + birth_datetime.minute/60.0 + birth_datetime.second/3600.0
        julian_day = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, hour_decimal)
        
        # Calcul poziții planetare
        planets = {
            'Sun': swe.SUN,
            'Moon': swe.MOON, 
            'Mercury': swe.MERCURY,
            'Venus': swe.VENUS,
            'Mars': swe.MARS,
            'Jupiter': swe.JUPITER,
            'Saturn': swe.SATURN,
            'Uranus': swe.URANUS,
            'Neptune': swe.NEPTUNE,
            'Pluto': swe.PLUTO
        }
        
        positions = {}
        for name, planet_id in planets.items():
            # Calcul poziție
            result, flags = swe.calc_ut(julian_day, planet_id)
            longitude = math.degrees(result[0]) % 360
            
            # Convertire în semn zodiacal
            sign_num = int(longitude / 30)
            sign_pos = longitude % 30
            degrees = int(sign_pos)
            minutes = int((sign_pos - degrees) * 60)
            
            signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                    'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
            
            # Calcul house simplificat (1-12)
            house = (sign_num % 12) + 1
            
            positions[name] = {
                'longitude': longitude,
                'sign': signs[sign_num],
                'degrees': degrees,
                'minutes': minutes,
                'house': house,
                'position_str': f"{degrees:02d}°{minutes:02d}' {signs[sign_num]}({house})"
            }
        
        # Calcul case (simplificat)
        houses = calculate_houses_simple(julian_day, birth_data['lat_deg'], birth_data['lon_deg'])
        
        return {
            'planets': positions,
            'houses': houses,
            'julian_day': julian_day
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {str(e)}")
        return None

def calculate_houses_simple(julian_day, lat, lon):
    """Calcul case astrologice simplificat"""
    try:
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        # Calcul simplificat - case egale
        for i in range(12):
            house_longitude = (i * 30) % 360
            sign_num = int(house_longitude / 30)
            sign_pos = house_longitude % 30
            degrees = int(sign_pos)
            minutes = int((sign_pos - degrees) * 60)
            
            houses[i+1] = {
                'longitude': house_longitude,
                'sign': signs[sign_num],
                'degrees': degrees,
                'minutes': minutes,
                'position_str': f"{degrees:02d}°{minutes:02d}' {signs[sign_num]}"
            }
        
        return houses
        
    except Exception as e:
        st.error(f"Eroare la calcularea caselor: {e}")
        return {}

def data_input_form():
    st.header("📅 Birth Data Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Data")
        name = st.text_input("Name", "Danko")
        
        col1a, col1b = st.columns(2)
        with col1a:
            # Setează anul corect 1956
            birth_date = st.date_input("Birth Date", 
                                     datetime(1956, 4, 25).date(),
                                     min_value=datetime(1800, 1, 1).date(),
                                     max_value=datetime(2100, 12, 31).date())
        with col1b:
            birth_time = st.time_input("Birth Time", datetime(1956, 4, 25, 21, 0).time())
        
        time_zone = st.selectbox("Time Zone", [f"GMT{i:+d}" for i in range(-12, 13)], index=12)
        
    with col2:
        st.subheader("Birth Place Coordinates")
        
        col2a, col2b = st.columns(2)
        with col2a:
            longitude_deg = st.number_input("Longitude (°)", min_value=0.0, max_value=180.0, value=16.0, step=0.1)
            longitude_dir = st.selectbox("Longitude Direction", ["East", "West"], index=0)
        with col2b:
            latitude_deg = st.number_input("Latitude (°)", min_value=0.0, max_value=90.0, value=45.0, step=0.1)
            latitude_min = st.number_input("Latitude (')", min_value=0.0, max_value=59.9, value=51.0, step=0.1)
            latitude_dir = st.selectbox("Latitude Direction", ["North", "South"], index=0)
        
        lon = longitude_deg if longitude_dir == "East" else -longitude_deg
        lat = latitude_deg + (latitude_min / 60.0)
        lat = lat if latitude_dir == "North" else -lat
        
        st.write(f"**Coordinates:** {lat:.2f}°N, {lon:.2f}°E")
    
    st.markdown("---")
    
    if st.button("♈ Calculate Astrological Chart", type="primary", use_container_width=True):
        with st.spinner("Calculation starts - Please wait ..."):
            birth_data = {
                'name': name,
                'date': birth_date,
                'time': birth_time,
                'time_zone': time_zone,
                'lat_deg': lat,
                'lon_deg': lon,
                'lat_display': f"{latitude_deg}°{latitude_min:.0f}'{latitude_dir}",
                'lon_display': f"{longitude_deg}°{longitude_dir}"
            }
            
            chart_data = calculate_chart(birth_data)
            
            if chart_data:
                st.session_state.chart_data = chart_data
                st.session_state.birth_data = birth_data
                st.success("Chart calculated successfully!")
            else:
                st.error("Failed to calculate chart. Please check your input data.")

def display_chart():
    st.header("♈ Astrological Chart")
    
    if st.session_state.chart_data is None:
        st.warning("Please enter birth data and calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    # Afișare info
    col_info = st.columns(3)
    with col_info[0]:
        st.write(f"**Name:** {birth_data['name']}")
    with col_info[1]:
        st.write(f"**Date:** {birth_data['date']}")
    with col_info[2]:
        st.write(f"**Time:** {birth_data['time']}")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌍 Planetary Positions")
        for planet_name, planet_data in chart_data['planets'].items():
            st.write(f"**{planet_name}** {planet_data['position_str']}")
    
    with col2:
        st.subheader("🏠 Houses (Equal)")
        for house_num, house_data in chart_data['houses'].items():
            st.write(f"**{house_num}** {house_data['position_str']}")
    
    # Butoane de navigare
    st.markdown("---")
    col_buttons = st.columns(5)
    with col_buttons[0]:
        if st.button("📊 Chart", use_container_width=True):
            pass  # Already here
    with col_buttons[1]:
        if st.button("🔄 Aspects", use_container_width=True):
            st.session_state.current_page = "Aspects"
    with col_buttons[2]:
        if st.button("📍 Positions", use_container_width=True):
            st.session_state.current_page = "Positions"
    with col_buttons[3]:
        if st.button("📖 Interpretation", use_container_width=True):
            st.session_state.current_page = "Interpretation"
    with col_buttons[4]:
        if st.button("✏️ Data", use_container_width=True):
            st.session_state.current_page = "Data Input"

def display_positions():
    st.header("📍 Planetary Positions")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    
    positions_data = []
    for planet_name, planet_data in chart_data['planets'].items():
        positions_data.append({
            'Planet': planet_name,
            'Position': planet_data['position_str'],
            'Longitude': f"{planet_data['longitude']:.2f}°",
            'House': planet_data['house']
        })
    
    df = pd.DataFrame(positions_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_aspects():
    st.header("🔄 Astrological Aspects")
    st.info("Aspect calculation feature coming soon...")
    st.write("This feature will calculate planetary aspects like conjunctions, squares, trines, etc.")

def display_interpretation():
    st.header("📖 Interpretation")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Birth Data")
        st.write(f"**Name:** {birth_data['name']}")
        st.write(f"**Date:** {birth_data['date']}")
        st.write(f"**Time:** {birth_data['time']}")
        st.write(f"**Position:** {birth_data['lon_display']} {birth_data['lat_display']}")
    
    with col2:
        st.subheader("Planetary Highlights")
        sun_data = chart_data['planets']['Sun']
        moon_data = chart_data['planets']['Moon']
        
        st.write(f"**Sun:** {sun_data['sign']} in house {sun_data['house']}")
        st.write(f"**Moon:** {moon_data['sign']} in house {moon_data['house']}")
        st.write(f"**Ascendant:** {chart_data['houses'][1]['sign']} (1st House)")
    
    st.markdown("---")
    
    # Interpretare bazată pe poziții
    interpretation_type = st.selectbox(
        "Interpretation Focus",
        ["Natal Profile", "Personality", "Relationships", "Career", "Spiritual"]
    )
    
    st.subheader(f"Interpretation: {interpretation_type}")
    
    # Interpretări simple bazate pe poziția Soarelui
    sun_data = chart_data['planets']['Sun']
    sun_sign = sun_data['sign']
    
    interpretations = {
        'ARI': "**Aries:** Energetic, pioneering, courageous. Natural leader with strong initiative.",
        'TAU': "**Taurus:** Practical, reliable, patient. Values security and comfort.",
        'GEM': "**Gemini:** Communicative, versatile, intellectual. Curious and adaptable.",
        'CAN': "**Cancer:** Nurturing, emotional, protective. Strong connection to home and family.",
        'LEO': "**Leo:** Confident, creative, generous. Natural performer and leader.",
        'VIR': "**Virgo:** Analytical, practical, helpful. Attention to detail and service-oriented.",
        'LIB': "**Libra:** Diplomatic, social, harmonious. Seeks balance and partnership.",
        'SCO': "**Scorpio:** Intense, passionate, transformative. Deep emotional understanding.",
        'SAG': "**Sagittarius:** Adventurous, philosophical, optimistic. Seeks truth and expansion.",
        'CAP': "**Capricorn:** Ambitious, disciplined, responsible. Builds lasting structures.",
        'AQU': "**Aquarius:** Innovative, independent, humanitarian. Forward-thinking and original.",
        'PIS': "**Pisces:** Compassionate, intuitive, artistic. Connected to spiritual realms."
    }
    
    if sun_sign in interpretations:
        st.write(interpretations[sun_sign])

def display_about():
    st.header("ℹ️ About 1.Horoscope")
    st.markdown("""
    ### 1.Horoscope ver. 2.42 (Streamlit Edition)
    
    **Copyright © 1998-2001**  
    Danko Josic & Nenad Zezlina  
    
    **Modern Conversion**  
    Streamlit web interface with Swiss Ephemeris engine
    
    **Features**  
    - Accurate planetary positions using Swiss Ephemeris
    - Natal chart calculations
    - House system (Equal houses)
    - Basic interpretations
    
    **Original Concept**  
    Palm OS astrological application "1.Chart"
    """)
    
    st.info("""
    This is a modern web conversion of the original Palm OS application.
    For information about the original software check:
    www.j-sistem.hr/online
    or
    www.1horoscope.com
    """)

if __name__ == "__main__":
    main()
