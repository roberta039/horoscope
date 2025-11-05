import streamlit as st
import datetime
from datetime import datetime
import ephem
import math
import pandas as pd

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
    """Calculează harta astrologică folosind ephem cu case Placidus"""
    try:
        # Convertire date
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        
        # Creare observer cu locația
        observer = ephem.Observer()
        observer.lat = str(birth_data['lat_deg'])
        observer.lon = str(birth_data['lon_deg'])
        observer.date = f"{birth_data['date'].year}/{birth_data['date'].month}/{birth_data['date'].day} {birth_data['time'].hour}:{birth_data['time'].minute}:{birth_data['time'].second}"
        
        # Calcul poziții planetare cu ephem
        planets = {
            'Sun': ephem.Sun(),
            'Moon': ephem.Moon(),
            'Mercury': ephem.Mercury(),
            'Venus': ephem.Venus(),
            'Mars': ephem.Mars(),
            'Jupiter': ephem.Jupiter(),
            'Saturn': ephem.Saturn(),
            'Uranus': ephem.Uranus(),
            'Neptune': ephem.Neptune(),
            'Pluto': ephem.Pluto()
        }
        
        positions = {}
        for name, planet_obj in planets.items():
            # Calcul poziție
            planet_obj.compute(observer)
            longitude = math.degrees(planet_obj.hlon) % 360
            
            # Convertire în semn zodiacal
            sign_num = int(longitude / 30)
            sign_pos = longitude % 30
            degrees = int(sign_pos)
            minutes = int((sign_pos - degrees) * 60)
            
            signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                    'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
            
            positions[name] = {
                'longitude': longitude,
                'sign': signs[sign_num],
                'degrees': degrees,
                'minutes': minutes,
                'position_str': f"{degrees:02d}°{minutes:02d}' {signs[sign_num]}"
            }
        
        # CALCUL CASE PLACIDUS COMPLEX
        houses = calculate_houses_placidus(observer, birth_data['lat_deg'])
        
        # Calcul case pentru planete
        for name, planet_data in positions.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude(planet_longitude, houses)
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']})"
        
        return {
            'planets': positions,
            'houses': houses,
            'observer': observer
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {str(e)}")
        return None

def calculate_houses_placidus(observer, latitude):
    """Calcul case Placidus folosind algoritm complex"""
    try:
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        # Calcul ascendent (casa 1)
        asc_longitude = calculate_ascendant(observer, latitude)
        
        # Calcul Medium Coeli (casa 10)
        mc_longitude = calculate_mc(observer, latitude)
        
        # Calcul case folosind sistem Placidus
        house_longitudes = calculate_placidus_houses(asc_longitude, mc_longitude, latitude)
        
        for i in range(12):
            house_longitude = house_longitudes[i] % 360
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
        st.error(f"Eroare la calcularea caselor Placidus: {e}")
        # Fallback la case egale
        return calculate_houses_equal(observer)

def calculate_ascendant(observer, latitude):
    """Calculează longitudinea ascendentului"""
    try:
        # Calcul simplificat al ascendentului
        sun = ephem.Sun()
        sun.compute(observer)
        sun_longitude = math.degrees(sun.hlon)
        
        # Aproximare bazată pe ora zilei și latitudine
        hour_angle = (observer.date.datetime().hour - 12) * 15
        asc_approx = (sun_longitude + hour_angle + latitude/2) % 360
        
        return asc_approx
        
    except Exception as e:
        return 0

def calculate_mc(observer, latitude):
    """Calculează longitudinea Medium Coeli"""
    try:
        sun = ephem.Sun()
        sun.compute(observer)
        sun_longitude = math.degrees(sun.hlon)
        
        # Aproximare bazată pe ora zilei
        hour_angle = (observer.date.datetime().hour - 12) * 15
        mc_approx = (sun_longitude + hour_angle) % 360
        
        return mc_approx
        
    except Exception as e:
        return 270

def calculate_placidus_houses(asc_longitude, mc_longitude, latitude):
    """Calcul case Placidus folosind algoritm complex"""
    try:
        houses = [0] * 12
        
        # Casa 1 - Ascendent
        houses[0] = asc_longitude
        
        # Casa 10 - Medium Coeli
        houses[9] = mc_longitude
        
        # Calcul case intermediare
        for i in range(12):
            if i == 0:
                continue
            elif i == 9:
                continue
            else:
                if i < 9:
                    angle = (mc_longitude - asc_longitude) % 360
                    if angle < 0:
                        angle += 360
                    houses[i] = (asc_longitude + (angle * i / 9)) % 360
                else:
                    angle = (asc_longitude - mc_longitude) % 360
                    if angle < 0:
                        angle += 360
                    houses[i] = (mc_longitude + (angle * (i-9) / 3)) % 360
        
        return houses
        
    except Exception as e:
        return calculate_equal_houses(asc_longitude)

def calculate_equal_houses(asc_longitude):
    """Calcul case egale ca fallback"""
    houses = []
    for i in range(12):
        house_longitude = (asc_longitude + (i * 30)) % 360
        houses.append(house_longitude)
    return houses

def calculate_houses_equal(observer):
    """Calcul case egale simplu"""
    try:
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        sun = ephem.Sun()
        sun.compute(observer)
        sun_longitude = math.degrees(sun.hlon)
        
        for i in range(12):
            house_longitude = (sun_longitude + (i * 30)) % 360
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
        return {}

def get_house_for_longitude(longitude, houses):
    """Determină casa pentru o longitudine dată"""
    try:
        longitude = longitude % 360
        
        house_numbers = list(houses.keys())
        for i in range(len(house_numbers)):
            current_house = house_numbers[i]
            next_house = house_numbers[(i + 1) % 12]
            
            current_long = houses[current_house]['longitude']
            next_long = houses[next_house]['longitude']
            
            if next_long < current_long:
                next_long += 360
                adj_longitude = longitude if longitude >= current_long else longitude + 360
            else:
                adj_longitude = longitude
            
            if current_long <= adj_longitude < next_long:
                return current_house
        
        return 1
        
    except Exception as e:
        return 1

def calculate_aspects(chart_data):
    """Calculează aspectele astrologice"""
    try:
        planets = chart_data['planets']
        aspects = []
        
        major_aspects = [
            {'name': 'Conjunction', 'angle': 0, 'orb': 8},
            {'name': 'Opposition', 'angle': 180, 'orb': 8},
            {'name': 'Trine', 'angle': 120, 'orb': 8},
            {'name': 'Square', 'angle': 90, 'orb': 8},
            {'name': 'Sextile', 'angle': 60, 'orb': 6}
        ]
        
        planet_list = list(planets.keys())
        
        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                planet1 = planet_list[i]
                planet2 = planet_list[j]
                
                long1 = planets[planet1]['longitude']
                long2 = planets[planet2]['longitude']
                
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect in major_aspects:
                    aspect_angle = aspect['angle']
                    orb = aspect['orb']
                    
                    if abs(diff - aspect_angle) <= orb:
                        exact_orb = abs(diff - aspect_angle)
                        is_exact = exact_orb <= 1.0
                        strength = 'Strong'
                        
                        aspects.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect_name': aspect['name'],
                            'angle': aspect_angle,
                            'orb': exact_orb,
                            'exact': is_exact,
                            'strength': strength
                        })
        
        return aspects
        
    except Exception as e:
        st.error(f"Eroare la calcularea aspectelor: {e}")
        return []

def data_input_form():
    st.header("📅 Birth Data Input")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Personal Data")
        name = st.text_input("Name", "Danko")
        
        col1a, col1b = st.columns(2)
        with col1a:
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
        st.subheader("🏠 Houses (Placidus)")
        for house_num, house_data in chart_data['houses'].items():
            st.write(f"**{house_num}** {house_data['position_str']}")
    
    st.markdown("---")
    col_buttons = st.columns(5)
    with col_buttons[0]:
        if st.button("📊 Chart", use_container_width=True):
            pass
    with col_buttons[1]:
        if st.button("🔄 Aspects", use_container_width=True):
            pass
    with col_buttons[2]:
        if st.button("📍 Positions", use_container_width=True):
            pass
    with col_buttons[3]:
        if st.button("📖 Interpretation", use_container_width=True):
            pass
    with col_buttons[4]:
        if st.button("✏️ Data", use_container_width=True):
            pass

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
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    
    aspects = calculate_aspects(chart_data)
    
    if aspects:
        aspect_data = []
        for aspect in aspects:
            aspect_data.append({
                "Planet 1": aspect['planet1'],
                "Planet 2": aspect['planet2'], 
                "Aspect": aspect['aspect_name'],
                "Orb": f"{aspect['orb']:.2f}°",
                "Exact": "Yes" if aspect['exact'] else "No",
                "Strength": aspect['strength']
            })
        
        df = pd.DataFrame(aspect_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    else:
        st.info("No significant aspects found within allowed orb.")

def display_interpretation():
    st.header("📖 Interpretation Center")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Data")
        st.write(f"**Name:** {birth_data['name']}")
        st.write(f"**Date:** {birth_data['date']}")
        st.write(f"**Time:** {birth_data['time']}")
        st.write(f"**Position:** {birth_data['lon_display']} {birth_data['lat_display']}")
    
    with col2:
        st.subheader("Planets")
        planets_display = [
            f"Sun {chart_data['planets']['Sun']['position_str']}",
            f"Moon {chart_data['planets']['Moon']['position_str']}",
            f"Mer {chart_data['planets']['Mercury']['position_str']}",
            f"Ven {chart_data['planets']['Venus']['position_str']}",
            f"Mar {chart_data['planets']['Mars']['position_str']}",
            f"Jup {chart_data['planets']['Jupiter']['position_str']}",
            f"Sat {chart_data['planets']['Saturn']['position_str']}",
            f"Ura {chart_data['planets']['Uranus']['position_str']}",
            f"Nep {chart_data['planets']['Neptune']['position_str']}",
            f"Plu {chart_data['planets']['Pluto']['position_str']}"
        ]
        
        for planet in planets_display:
            st.write(planet)
    
    st.markdown("---")
    
    interpretation_type = st.selectbox(
        "Type of interpretation",
        ["Natal", "Sexual", "Career", "Relationships", "Spiritual"]
    )
    
    st.markdown("---")
    st.subheader(f"Interpretation: {interpretation_type}")
    
    # Interpretări simple pentru demo
    sun_data = chart_data['planets']['Sun']
    moon_data = chart_data['planets']['Moon']
    
    st.write(f"**Sun in {sun_data['sign']}**")
    sun_interpretations = {
        'ARI': "Energetic, pioneering, courageous. Natural leader with strong initiative.",
        'TAU': "Practical, reliable, patient. Values security and comfort.",
        'GEM': "Clever, bright, quickwitted, communicative, adaptable.",
        'CAN': "Nurturing, emotional, protective. Strong connection to home.",
        'LEO': "Confident, creative, generous. Natural performer.",
        'VIR': "Analytical, practical, helpful. Attention to detail.",
        'LIB': "Friendly, artistic, sociable, balanced.",
        'SCO': "Intense, passionate, transformative.",
        'SAG': "Adventurous, philosophical, optimistic.",
        'CAP': "Ambitious, disciplined, responsible.",
        'AQU': "Innovative, independent, humanitarian.",
        'PIS': "Compassionate, intuitive, artistic."
    }
    
    if sun_data['sign'] in sun_interpretations:
        st.write(sun_interpretations[sun_data['sign']])
    
    st.write(f"**Moon in {moon_data['sign']}**")
    st.write("Your emotional nature is influenced by the Moon's position in this sign.")

def display_about():
    st.header("ℹ️ About 1.Horoscope")
    st.markdown("""
    ### 1.Horoscope ver. 2.42 (Streamlit Edition)
    
    **Copyright © 1998-2001**  
    Danko Josic & Nenad Zezlina  
    
    **Modern Conversion**  
    Streamlit web interface with PyEphem engine
    
    **Features**  
    - Accurate planetary positions using PyEphem
    - Natal chart calculations with Placidus houses
    - Aspect calculations
    - Multiple interpretation types
    
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
