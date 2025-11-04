import streamlit as st
import datetime
from datetime import datetime
import flatlib
from flatlib import const
from flatlib.chart import Chart
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
import pandas as pd

def main():
    st.set_page_config(page_title="1.Horoscope", layout="wide", page_icon="♈")
    
    # Inițializare session state
    if 'chart' not in st.session_state:
        st.session_state.chart = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    
    # Sidebar cu meniul principal
    with st.sidebar:
        st.title("♈ 1.Horoscope")
        st.markdown("---")
        
        menu_option = st.radio(
            "Main Menu",
            ["Data Input", "Chart", "Aspects", "Positions", "Interpretation", "About"]
        )
    
    if menu_option == "Data Input":
        data_input_form()
    elif menu_option == "Chart":
        display_chart()
    elif menu_option == "Aspects":
        display_aspects()
    elif menu_option == "Positions":
        display_positions()
    elif menu_option == "Interpretation":
        display_interpretation()
    elif menu_option == "About":
        display_about()

def calculate_chart(birth_data):
    """Calculează harta astrologică folosind flatlib"""
    try:
        # Convertire date pentru flatlib
        date_str = birth_data['date'].strftime('%Y/%m/%d')
        time_str = birth_data['time'].strftime('%H:%M:%S')
        datetime_str = f"{date_str} {time_str}"
        
        # Creare obiecte flatlib
        dt = Datetime(datetime_str, birth_data['time_zone'].replace('GMT', ''))
        pos = GeoPos(birth_data['lat_deg'], birth_data['lon_deg'])
        
        # Calculare chart cu sistemul de case Placidus
        chart = Chart(dt, pos, hsys=const.HOUSES_PLACIDUS)
        
        return chart
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {e}")
        return None

def data_input_form():
    st.header("📅 Birth Data Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Data")
        name = st.text_input("Name", "Danko")
        
        # Data și ora nașterii
        col1a, col1b = st.columns(2)
        with col1a:
            birth_date = st.date_input("Birth Date", datetime(1956, 4, 25).date())
        with col1b:
            birth_time = st.time_input("Birth Time", datetime(1956, 4, 25, 21, 0).time())
        
        # Fus orar
        time_zones = [f"GMT{i:+d}" for i in range(-12, 13)]
        time_zone = st.selectbox("Time Zone", time_zones, index=12)  # GMT-1
        
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
        
        # Convertire coordonate pentru calcul
        lon = longitude_deg if longitude_dir == "East" else -longitude_deg
        lat = latitude_deg + (latitude_min / 60.0)
        lat = lat if latitude_dir == "North" else -lat
        
        st.write(f"**Coordinates:** {lat:.2f}° {lon:.2f}°")
    
    st.markdown("---")
    
    # Buton de calcul
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
            
            # Calculare chart
            chart = calculate_chart(birth_data)
            
            if chart:
                st.session_state.chart = chart
                st.session_state.birth_data = birth_data
                st.success("Chart calculated successfully!")
                
                # Auto-navigare la chart
                st.session_state.current_page = "Chart"
    
    # Butoanele de navigare
    st.markdown("---")
    col_buttons = st.columns(5)
    with col_buttons[0]:
        if st.button("📊 Chart", use_container_width=True):
            st.session_state.current_page = "Chart"
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

def display_chart():
    st.header("♈ Astrological Chart")
    
    if st.session_state.chart is None:
        st.warning("Please enter birth data and calculate chart first!")
        return
    
    chart = st.session_state.chart
    birth_data = st.session_state.birth_data
    
    # Afișare date de bază
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
        
        # Lista planetelor principale
        planets = [
            const.SUN, const.MOON, const.MERCURY, const.VENUS, const.MARS,
            const.JUPITER, const.SATURN, const.URANUS, const.NEPTUNE, const.PLUTO
        ]
        
        planet_names = {
            const.SUN: "Sun", const.MOON: "Moon", const.MERCURY: "Mercury",
            const.VENUS: "Venus", const.MARS: "Mars", const.JUPITER: "Jupiter",
            const.SATURN: "Saturn", const.URANUS: "Uranus", 
            const.NEPTUNE: "Neptune", const.PLUTO: "Pluto"
        }
        
        planet_data = []
        for planet_id in planets:
            planet = chart.get(planet_id)
            sign = planet.sign()
            house = planet.house()
            retrograde = "R" if planet.retrograde() else ""
            
            # Formatare poziție
            deg = int(planet.signPos)
            min = int((planet.signPos - deg) * 60)
            position_str = f"{deg:02d}°{min:02d}' {sign}({house}){retrograde}"
            
            planet_data.append({
                "Planet": planet_names[planet_id],
                "Position": position_str
            })
        
        # Afișare planet
        for planet in planet_data:
            st.write(f"**{planet['Planet']}** {planet['Position']}")
    
    with col2:
        st.subheader("🏠 Houses (Placidus)")
        
        houses_data = []
        for i in range(1, 13):
            house = chart.houses.get(i)
            sign = house.sign()
            
            # Formatare poziție
            deg = int(house.signPos)
            min = int((house.signPos - deg) * 60)
            position_str = f"{deg:02d}°{min:02d}' {sign}"
            
            houses_data.append({
                "House": i,
                "Position": position_str
            })
        
        # Afișare case
        for house in houses_data:
            st.write(f"**{house['House']}** {house['Position']}")
    
    st.markdown("---")
    st.info("🎯 Tap on any planet or house number to see detailed information")

def display_positions():
    st.header("📍 Detailed Planetary Positions")
    
    if st.session_state.chart is None:
        st.warning("Please calculate chart first!")
        return
    
    chart = st.session_state.chart
    
    # Tabel detaliat cu toate pozițiile
    positions_data = []
    
    # Obiecte astrologice
    objects = [
        (const.SUN, "Sun"), (const.MOON, "Moon"), (const.MERCURY, "Mercury"),
        (const.VENUS, "Venus"), (const.MARS, "Mars"), (const.JUPITER, "Jupiter"),
        (const.SATURN, "Saturn"), (const.URANUS, "Uranus"), (const.NEPTUNE, "Neptune"),
        (const.PLUTO, "Pluto"), (const.NORTH_NODE, "North Node"), (const.CHIRON, "Chiron")
    ]
    
    for obj_id, obj_name in objects:
        try:
            obj = chart.get(obj_id)
            sign = obj.sign()
            house = obj.house()
            retrograde = "R" if obj.retrograde() else ""
            
            # Calcul grade, minute
            deg = int(obj.signPos)
            min = int((obj.signPos - deg) * 60)
            
            positions_data.append({
                "Object": obj_name,
                "Sign": sign,
                "Degrees": deg,
                "Minutes": min,
                "House": house,
                "Retrograde": retrograde,
                "Full Position": f"{deg}°{min:02d}' {sign}({house}){retrograde}"
            })
        except:
            continue
    
    # Afișare tabel
    df = pd.DataFrame(positions_data)
    st.dataframe(
        df[["Object", "Full Position"]],
        use_container_width=True,
        hide_index=True
    )

def display_aspects():
    st.header("🔄 Astrological Aspects")
    
    if st.session_state.chart is None:
        st.warning("Please calculate chart first!")
        return
    
    chart = st.session_state.chart
    
    # Obține aspectele
    aspects = chart.aspects()
    
    aspect_data = []
    for aspect in aspects:
        if aspect.active:
            aspect_data.append({
                "Planet 1": aspect.id1,
                "Planet 2": aspect.id2,
                "Aspect": aspect.type,
                "Orb": f"{aspect.orb:.2f}°",
                "Exact": "Yes" if aspect.exact else "No"
            })
    
    if aspect_data:
        df = pd.DataFrame(aspect_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No major aspects found")

def display_interpretation():
    st.header("📖 Interpretation Center")
    
    if st.session_state.chart is None:
        st.warning("Please calculate chart first!")
        return
    
    chart = st.session_state.chart
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
        sun = chart.get(const.SUN)
        moon = chart.get(const.MOON)
        asc = chart.get(const.ASC)
        
        st.write(f"**Sun:** {sun.sign()} in house {sun.house()}")
        st.write(f"**Moon:** {moon.sign()} in house {moon.house()}")
        st.write(f"**Ascendant:** {asc.sign()}")
    
    st.markdown("---")
    
    # Interpretare bazată pe poziții
    interpretation_type = st.selectbox(
        "Interpretation Focus",
        ["Natal Profile", "Personality", "Relationships", "Career", "Spiritual"]
    )
    
    st.subheader(f"Interpretation: {interpretation_type}")
    
    # Interpretări simple bazate pe poziția Soarelui
    sun = chart.get(const.SUN)
    sun_sign = sun.sign()
    
    interpretations = {
        "ARIES": "Energetic, pioneering, courageous. Natural leader with strong initiative.",
        "TAURUS": "Practical, reliable, patient. Values security and comfort.",
        "GEMINI": "Communicative, versatile, intellectual. Curious and adaptable.",
        "CANCER": "Nurturing, emotional, protective. Strong connection to home and family.",
        "LEO": "Confident, creative, generous. Natural performer and leader.",
        "VIRGO": "Analytical, practical, helpful. Attention to detail and service-oriented.",
        "LIBRA": "Diplomatic, social, harmonious. Seeks balance and partnership.",
        "SCORPIO": "Intense, passionate, transformative. Deep emotional understanding.",
        "SAGITTARIUS": "Adventurous, philosophical, optimistic. Seeks truth and expansion.",
        "CAPRICORN": "Ambitious, disciplined, responsible. Builds lasting structures.",
        "AQUARIUS": "Innovative, independent, humanitarian. Forward-thinking and original.",
        "PISCES": "Compassionate, intuitive, artistic. Connected to spiritual realms."
    }
    
    if sun_sign in interpretations:
        st.write(f"**Sun in {sun_sign}**")
        st.write(interpretations[sun_sign])

def display_about():
    st.header("ℹ️ About 1.Horoscope")
    
    st.markdown("""
    ### 1.Horoscope ver. 2.42 (Streamlit Edition)
    
    **Copyright © 1998-2001**  
    Danko Josic & Nenad Zezlina  
    All rights reserved
    
    ---
    
    **Streamlit Conversion**  
    Modern web interface with original Palm OS functionality
    
    **Astrological Engine**  
    Powered by Flatlib with Swiss Ephemeris
    
    **Original Concept**  
    Palm OS application for astrological calculations
    """)
    
    st.info("""
    This is unlicensed version.  
    1.Chart is shareware. Please help us support it.
    
    For information on how to register check:
    www.j-sistem.hr/online
    or
    www.1horoscope.com
    """)

if __name__ == "__main__":
    main()
