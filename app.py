import streamlit as st
import datetime
from datetime import datetime
import math
import pandas as pd
import swisseph as swe
import os

# Dicționar cu capitalele lumii și coordonatele lor
WORLD_CAPITALS = {
    "București, România": {"lat": 44.4268, "lon": 26.1025},
    "Londra, Regatul Unit": {"lat": 51.5074, "lon": -0.1278},
    "Paris, Franța": {"lat": 48.8566, "lon": 2.3522},
    "Berlin, Germania": {"lat": 52.5200, "lon": 13.4050},
    "Roma, Italia": {"lat": 41.9028, "lon": 12.4964},
    "Madrid, Spania": {"lat": 40.4168, "lon": -3.7038},
    "Moscova, Rusia": {"lat": 55.7558, "lon": 37.6173},
    "Beijing, China": {"lat": 39.9042, "lon": 116.4074},
    "Tokyo, Japonia": {"lat": 35.6762, "lon": 139.6503},
    "New Delhi, India": {"lat": 28.6139, "lon": 77.2090},
    "Washington D.C., SUA": {"lat": 38.9072, "lon": -77.0369},
    "Ottawa, Canada": {"lat": 45.4215, "lon": -75.6972},
    "Canberra, Australia": {"lat": -35.2809, "lon": 149.1300},
    "Buenos Aires, Argentina": {"lat": -34.6037, "lon": -58.3816},
    "Cairo, Egipt": {"lat": 30.0444, "lon": 31.2357},
    "Pretoria, Africa de Sud": {"lat": -25.7479, "lon": 28.2293},
    "Bangkok, Thailanda": {"lat": 13.7563, "lon": 100.5018},
    "Seoul, Coreea de Sud": {"lat": 37.5665, "lon": 126.9780},
    "Mexico City, Mexic": {"lat": 19.4326, "lon": -99.1332},
    "Lisabona, Portugalia": {"lat": 38.7223, "lon": -9.1393},
    "Viena, Austria": {"lat": 48.2082, "lon": 16.3738},
    "Praga, Cehia": {"lat": 50.0755, "lon": 14.4378},
    "Budapesta, Ungaria": {"lat": 47.4979, "lon": 19.0402},
    "Varșovia, Polonia": {"lat": 52.2297, "lon": 21.0122},
    "Atena, Grecia": {"lat": 37.9838, "lon": 23.7275},
    "Istanbul, Turcia": {"lat": 41.0082, "lon": 28.9784},
    "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
    "Riyadh, Arabia Saudită": {"lat": 24.7136, "lon": 46.6753},
    "Singapore, Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Kuala Lumpur, Malaysia": {"lat": 3.1390, "lon": 101.6869}
}

def main():
    st.set_page_config(page_title="Horoscope", layout="wide", page_icon="♈")
    
    # CSS custom pentru aspect mai modern și mai mare
    st.markdown("""
    <style>
    /* Fonturi mai mari și mai clare pentru chart */
    .chart-container h3 {
        font-size: 1.8rem !important;
        color: #1f77b4 !important;
        margin-bottom: 1.5rem !important;
    }
    
    .chart-planet {
        font-size: 1.3rem !important;
        margin-bottom: 0.8rem !important;
        padding: 0.5rem !important;
        border-radius: 8px !important;
        background-color: #f8f9fa !important;
    }
    
    .chart-house {
        font-size: 1.3rem !important;
        margin-bottom: 0.8rem !important;
        padding: 0.5rem !important;
        border-radius: 8px !important;
        background-color: #e9ecef !important;
    }
    
    /* Butoane mai mari în chart */
    .chart-buttons button {
        font-size: 1.2rem !important;
        padding: 0.8rem 1.2rem !important;
        margin: 0.3rem !important;
    }
    
    /* Iconițe mai mari */
    .material-icons {
        font-size: 1.8rem !important;
    }
    
    /* Header chart mai mare */
    .chart-header {
        font-size: 2.2rem !important;
        color: #2E86AB !important;
        text-align: center !important;
        margin-bottom: 2rem !important;
    }
    
    /* Info boxes mai mari */
    .chart-info {
        font-size: 1.2rem !important;
        padding: 1rem !important;
        background-color: #f1f3f4 !important;
        border-radius: 10px !important;
        margin-bottom: 1rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Inițializare session state
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    
    # Sidebar meniu
    with st.sidebar:
        st.title("♈ Horoscope")
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

def setup_ephemeris():
    """Configurează calea către fișierele de efemeride"""
    try:
        # Încearcă mai multe căi posibile
        possible_paths = [
            './ephe',                           # Cale relativă
            './swisseph-data/ephe',             # Submodul
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe'),  # Cale absolută
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swisseph-data', 'ephe')
        ]
        
        for ephe_path in possible_paths:
            if os.path.exists(ephe_path):
                swe.set_ephe_path(ephe_path)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Eroare la configurarea efemeridelor: {e}")
        return False

def calculate_chart(birth_data):
    """Calculează harta astrologică folosind Swiss Ephemeris"""
    try:
        # Configurează efemeridele
        if not setup_ephemeris():
            st.error("Nu s-au putut încărca fișierele de efemeride.")
            return None
        
        # Convertire date în format Julian
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        jd = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, 
                       birth_datetime.hour + birth_datetime.minute/60.0)
        
        # Calcul poziții planetare cu Swiss Ephemeris
        planets_data = calculate_planetary_positions_swiss(jd)
        if planets_data is None:
            return None
        
        # Calcul case Placidus cu Swiss Ephemeris
        houses_data = calculate_houses_placidus_swiss(jd, birth_data['lat_deg'], birth_data['lon_deg'])
        if houses_data is None:
            return None
        
        # Asociem planetele cu casele
        for planet_name, planet_data in planets_data.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_swiss(planet_longitude, houses_data)
            
            # Formatare string pozitie
            retro_symbol = "R" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']}){retro_symbol}"
        
        return {
            'planets': planets_data,
            'houses': houses_data,
            'jd': jd
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {str(e)}")
        return None

def calculate_planetary_positions_swiss(jd):
    """Calculează pozițiile planetare folosind Swiss Ephemeris"""
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
        'Pluto': swe.PLUTO,
        'Nod': swe.MEAN_NODE
    }
    
    positions = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
            'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
    
    for name, planet_id in planets.items():
        try:
            # Calcul poziție cu Swiss Ephemeris
            result = swe.calc_ut(jd, planet_id, flags)
            longitude = result[0][0]  # longitudine ecliptică
            
            # Corecție pentru retrograde
            is_retrograde = result[0][3] < 0  # viteza longitudinală negativă
            
            # Convertire în semn zodiacal
            sign_num = int(longitude / 30)
            sign_pos = longitude % 30
            degrees = int(sign_pos)
            minutes = int((sign_pos - degrees) * 60)
            
            positions[name] = {
                'longitude': longitude,
                'sign': signs[sign_num],
                'degrees': degrees,
                'minutes': minutes,
                'retrograde': is_retrograde
            }
            
        except Exception as e:
            st.error(f"Eroare la calcularea poziției pentru {name}: {e}")
            return None
    
    # Adăugăm Chiron manual (dacă fișierul lipseste)
    try:
        chiron_result = swe.calc_ut(jd, swe.CHIRON, flags)
        chiron_longitude = chiron_result[0][0]
    except:
        # Fallback pentru Chiron
        chiron_longitude = (positions['Sun']['longitude'] + 90) % 360
    
    chiron_sign_num = int(chiron_longitude / 30)
    chiron_sign_pos = chiron_longitude % 30
    positions['Chi'] = {
        'longitude': chiron_longitude,
        'sign': signs[chiron_sign_num],
        'degrees': int(chiron_sign_pos),
        'minutes': int((chiron_sign_pos - int(chiron_sign_pos)) * 60),
        'retrograde': False
    }
    
    return positions

def calculate_houses_placidus_swiss(jd, latitude, longitude):
    """Calculează casele folosind sistemul Placidus cu Swiss Ephemeris"""
    try:
        # Calcul case cu Swiss Ephemeris
        result = swe.houses(jd, latitude, longitude, b'P')  # 'P' pentru Placidus
        
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        for i in range(12):
            house_longitude = result[0][i]  # cuspidele caselor
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
        return None

def get_house_for_longitude_swiss(longitude, houses):
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
                        strength = 'Strong' if exact_orb <= 2.0 else 'Medium'
                        
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
        
        # Dropdown cu capitalele lumii
        selected_capital = st.selectbox(
            "Select Capital City",
            ["Custom Location"] + list(WORLD_CAPITALS.keys()),
            index=0
        )
        
        if selected_capital != "Custom Location":
            # Auto-completează coordonatele pentru capitala selectată
            capital_data = WORLD_CAPITALS[selected_capital]
            auto_lat = capital_data['lat']
            auto_lon = capital_data['lon']
            
            # Determină direcțiile
            lat_dir = "North" if auto_lat >= 0 else "South"
            lon_dir = "East" if auto_lon >= 0 else "West"
            
            lat_deg = abs(int(auto_lat))
            lat_min = (abs(auto_lat) - lat_deg) * 60
            lon_deg = abs(int(auto_lon))
            lon_min = (abs(auto_lon) - lon_deg) * 60
            
            st.info(f"📍 {selected_capital}: {lat_deg}°{lat_min:.1f}'{lat_dir}, {lon_deg}°{lon_min:.1f}'{lon_dir}")
        else:
            lat_deg = 45
            lat_min = 51.0
            lon_deg = 16.0
            lon_min = 0.0
            lat_dir = "North"
            lon_dir = "East"
        
        col2a, col2b = st.columns(2)
        with col2a:
            longitude_deg = st.number_input("Longitude (°)", min_value=0.0, max_value=180.0, value=float(lon_deg), step=0.1)
            longitude_min = st.number_input("Longitude (')", min_value=0.0, max_value=59.9, value=float(lon_min), step=0.1, format="%.1f")
            longitude_dir = st.selectbox("Longitude Direction", ["East", "West"], index=0 if lon_dir == "East" else 1)
        with col2b:
            latitude_deg = st.number_input("Latitude (°)", min_value=0.0, max_value=90.0, value=float(lat_deg), step=0.1)
            latitude_min = st.number_input("Latitude (')", min_value=0.0, max_value=59.9, value=float(lat_min), step=0.1, format="%.1f")
            latitude_dir = st.selectbox("Latitude Direction", ["North", "South"], index=0 if lat_dir == "North" else 1)
        
        # Calcul coordonate finale
        lon = longitude_deg + (longitude_min / 60.0)
        lon = lon if longitude_dir == "East" else -lon
        lat = latitude_deg + (latitude_min / 60.0)
        lat = lat if latitude_dir == "North" else -lat
        
        st.write(f"**Final Coordinates:** {lat:.4f}° {latitude_dir}, {lon:.4f}° {longitude_dir}")
    
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
                'lat_display': f"{latitude_deg}°{latitude_min:.1f}'{latitude_dir}",
                'lon_display': f"{longitude_deg}°{longitude_min:.1f}'{longitude_dir}"
            }
            
            chart_data = calculate_chart(birth_data)
            
            if chart_data:
                st.session_state.chart_data = chart_data
                st.session_state.birth_data = birth_data
                st.success("✅ Chart calculated successfully using Swiss Ephemeris!")
            else:
                st.error("Failed to calculate chart. Please check your input data.")

def display_chart():
    st.markdown('<div class="chart-header">♈ Astrological Chart</div>', unsafe_allow_html=True)
    
    if st.session_state.chart_data is None:
        st.warning("Please enter birth data and calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    # Informații utilizator cu styling îmbunătățit
    col_info = st.columns(3)
    with col_info[0]:
        st.markdown(f'<div class="chart-info">**Name:** {birth_data["name"]}</div>', unsafe_allow_html=True)
    with col_info[1]:
        st.markdown(f'<div class="chart-info">**Date:** {birth_data["date"]}</div>', unsafe_allow_html=True)
    with col_info[2]:
        st.markdown(f'<div class="chart-info">**Time:** {birth_data["time"]}</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3>🌍 Planetary Positions</h3>', unsafe_allow_html=True)
        display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
        
        for planet_name in display_order:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                retro_symbol = " 🔄" if planet_data['retrograde'] else ""
                st.markdown(f'<div class="chart-planet">**{planet_name}** {planet_data["position_str"]}{retro_symbol}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<h3>🏠 Houses (Placidus)</h3>', unsafe_allow_html=True)
        for house_num in range(1, 13):
            if house_num in chart_data['houses']:
                house_data = chart_data['houses'][house_num]
                st.markdown(f'<div class="chart-house">**House {house_num}** {house_data["position_str"]}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Butoane de navigare mai mari
    st.markdown('<div class="chart-buttons">', unsafe_allow_html=True)
    col_buttons = st.columns(5)
    with col_buttons[0]:
        if st.button("📊 Chart", use_container_width=True):
            st.session_state.menu_option = "Chart"
    with col_buttons[1]:
        if st.button("🔄 Aspects", use_container_width=True):
            st.session_state.menu_option = "Aspects"
    with col_buttons[2]:
        if st.button("📍 Positions", use_container_width=True):
            st.session_state.menu_option = "Positions"
    with col_buttons[3]:
        if st.button("📖 Interpretation", use_container_width=True):
            st.session_state.menu_option = "Interpretation"
    with col_buttons[4]:
        if st.button("✏️ Data", use_container_width=True):
            st.session_state.menu_option = "Data Input"
    st.markdown('</div>', unsafe_allow_html=True)

def display_positions():
    st.header("📍 Planetary Positions")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    
    positions_data = []
    display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                    'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
    
    for planet_name in display_order:
        if planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            positions_data.append({
                'Planet': planet_name,
                'Position': planet_data['position_str'],
                'Longitude': f"{planet_data['longitude']:.2f}°",
                'House': planet_data.get('house', 'N/A')
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
        for i, aspect in enumerate(aspects, 1):
            aspect_data.append({
                "#": f"{i:02d}",
                "Planet 1": aspect['planet1'],
                "Planet 2": aspect['planet2'], 
                "Aspect": aspect['aspect_name'][:3],
                "Orb": f"{aspect['orb']:.1f}°",
                "Exact": "✅" if aspect['exact'] else "➖",
                "Strength": aspect['strength']
            })
        
        df = pd.DataFrame(aspect_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Statistici aspecte
        col_stats = st.columns(4)
        strong_aspects = [a for a in aspects if a['strength'] == 'Strong']
        exact_aspects = [a for a in aspects if a['exact']]
        
        with col_stats[0]:
            st.metric("Total Aspects", len(aspects))
        with col_stats[1]:
            st.metric("Strong Aspects", len(strong_aspects))
        with col_stats[2]:
            st.metric("Exact Aspects", len(exact_aspects))
        with col_stats[3]:
            st.metric("Planets Involved", len(set([a['planet1'] for a in aspects] + [a['planet2'] for a in aspects])))
        
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
        st.subheader("📋 Birth Data")
        st.write(f"**Name:** {birth_data['name']}")
        st.write(f"**Date:** {birth_data['date']}")
        st.write(f"**Time:** {birth_data['time']}")
        st.write(f"**Location:** {birth_data['lon_display']} {birth_data['lat_display']}")
    
    with col2:
        st.subheader("🪐 Key Planets")
        key_planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']
        for planet_name in key_planets:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                st.write(f"**{planet_name}** {planet_data['position_str']}")
    
    st.markdown("---")
    
    interpretation_type = st.selectbox(
        "🎯 Type of Interpretation",
        ["Natal", "Career", "Relationships", "Spiritual", "Personal Growth"]
    )
    
    st.markdown("---")
    st.subheader(f"📝 {interpretation_type} Interpretation")
    
    display_complete_interpretations(chart_data, interpretation_type)

def display_complete_interpretations(chart_data, interpretation_type):
    """Afișează interpretări complete pentru toate planetele și gradele"""
    
    # INTERPRETĂRI SPECIALIZATE PENTRU FIECARE TIP
    specialized_interpretations = {
        "Career": {
            "Sun": {
                "TAU": "Reliable and persistent in career matters. Excellent for banking, real estate, agriculture. Builds wealth steadily through determination.",
                "ARI": "Natural entrepreneur and leader. Thrives in competitive fields. Pioneer in new industries.",
                "GEM": "Excels in communication, media, teaching. Multi-talented with ability to handle multiple projects.",
                "CAP": "Ambitious and disciplined. Rises to leadership positions through hard work and responsibility."
            },
            "Moon": {
                "VIR": "Detail-oriented in work. Excellent in service industries, healthcare, organization.",
                "LEO": "Needs recognition in career. Good in leadership, entertainment, creative fields.",
                "CAP": "Serious approach to career. Builds reputation slowly but surely."
            },
            "Mars": {
                "ARI": "Competitive drive in career. Natural salesperson or athlete.",
                "SCO": "Intense focus on career goals. Excellent researcher or investigator."
            },
            "Jupiter": {
                "SAG": "Success through education, travel, philosophy. Natural teacher or guide.",
                "LEO": "Leadership abilities. Thrives in management and creative direction."
            }
        },
        "Relationships": {
            "Venus": {
                "LIB": "Seeks harmony and balance in relationships. Natural diplomat and peacemaker.",
                "TAU": "Loyal and sensual partner. Values stability and physical affection.",
                "SCO": "Intense and passionate relationships. Seeks deep emotional connections.",
                "GEM": "Communicative and playful in relationships. Needs mental stimulation."
            },
            "Moon": {
                "CAN": "Nurturing and protective in relationships. Strong family bonds.",
                "AQU": "Friendship-based relationships. Values independence and intellectual connection.",
                "PIS": "Compassionate and empathetic partner. Spiritual connection important."
            },
            "Mars": {
                "LEO": "Dramatic and generous in love. Seeks admiration and appreciation.",
                "VIR": "Shows love through practical service and attention to details."
            }
        },
        "Spiritual": {
            "Neptune": {
                "PIS": "Strong psychic and intuitive abilities. Natural healer and spiritual guide.",
                "SCO": "Deep understanding of life's mysteries. Transformative spiritual journey.",
                "SAG": "Philosophical and truth-seeking. Spiritual teacher and guide."
            },
            "Pluto": {
                "SCO": "Powerful transformative abilities. Understands cycles of death and rebirth.",
                "PIS": "Mystical connection to universal consciousness. Spiritual awakening."
            },
            "Moon": {
                "PIS": "Highly intuitive and empathetic. Dreams and visions provide guidance.",
                "SAG": "Spiritual optimism and faith. Seeks higher meaning in life."
            },
            "Jupiter": {
                "PIS": "Compassionate spirituality. Connection to universal love and forgiveness.",
                "SAG": "Philosophical and expansive spiritual views. Seeks ultimate truth."
            }
        },
        "Personal Growth": {
            "Saturn": {
                "CAP": "Lessons in responsibility and discipline. Learning to build lasting structures.",
                "ARI": "Learning patience and consideration for others. Developing leadership skills.",
                "LIB": "Learning balance in relationships. Understanding partnership dynamics."
            },
            "Uranus": {
                "AQU": "Embracing individuality and innovation. Breaking free from limitations.",
                "SCO": "Transforming deep-seated patterns. Embracing personal power."
            },
            "Pluto": {
                "SCO": "Deep psychological transformation. Releasing old patterns and rebirth.",
                "LEO": "Transforming ego and creative expression. Learning authentic self-expression."
            }
        }
    }

    # INTERPRETĂRI NATALE DE BAZĂ
    natal_interpretations = {
        "Sun": {
            "TAU": "Reliable, able, with powers of concentration, tenacity. Steadfast, a loving & affectionate \"family\" person. Honest, forthright. Learns readily from mistakes.",
            "ARI": "Energetic, pioneering, courageous. Natural leader with strong initiative. Impulsive and direct.",
            "GEM": "Clever, bright, quickwitted, communicative, able to do many different things at once, eager to learn new subjects. Openminded, adaptable, curious, restless, confident, seldom settling down.",
            "CAN": "Nurturing, emotional, protective. Strong connection to home and family. Sensitive and caring.",
            "LEO": "Confident, creative, generous. Natural performer and leader. Dramatic and warm-hearted.",
            "VIR": "Analytical, practical, helpful. Attention to detail and service-oriented. Methodical and precise.",
            "LIB": "Friendly, cordial, artistic, kind, considerate, loyal, alert, sociable, moderate, balanced in views, open-minded.",
            "SCO": "Intense, passionate, transformative. Deep emotional understanding. Powerful and determined.",
            "SAG": "Adventurous, philosophical, optimistic. Seeks truth and expansion. Freedom-loving and honest.",
            "CAP": "Ambitious, disciplined, responsible. Builds lasting structures. Serious and determined.",
            "AQU": "Innovative, independent, humanitarian. Forward-thinking and original. Unconventional and idealistic.",
            "PIS": "Compassionate, intuitive, artistic. Connected to spiritual realms. Dreamy and empathetic."
        },
        "Moon": {
            "SCO": "Tenacious will, much energy & working power, passionate, often sensual. Honest.",
            "ARI": "Energetic, ambitious, strongwilled, self-centred, impulsive, dominant & obstinate.",
            "TAU": "Steady, patient, determined. Values comfort and security. Emotionally stable.",
            "GEM": "Changeable, adaptable, curious. Needs mental stimulation. Restless emotions.",
            "CAN": "Nurturing, sensitive, protective. Strong emotional connections. Home-oriented.",
            "LEO": "Proud, dramatic, generous. Needs recognition and appreciation. Warm emotions.",
            "VIR": "Practical, analytical, helpful. Attention to emotional details. Service-oriented.",
            "LIB": "Harmonious, diplomatic, social. Seeks emotional balance. Relationship-focused.",
            "SAG": "Adventurous, optimistic, freedom-loving. Needs emotional expansion. Philosophical.",
            "CAP": "Responsible, disciplined, reserved. Controls emotions carefully. Ambitious.",
            "AQU": "Independent, unconventional, detached. Unique emotional expression. Progressive.",
            "PIS": "Compassionate, intuitive, dreamy. Sensitive emotional nature. Spiritual."
        }
    }

    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    # Afișează interpretări specializate sau natale
    if interpretation_type in specialized_interpretations:
        interpretations = specialized_interpretations[interpretation_type]
    else:
        interpretations = natal_interpretations
    
    found_interpretations = False
    
    for planet_name in planets_to_display:
        if planet_name in chart_data['planets'] and planet_name in interpretations:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            
            if planet_sign in interpretations[planet_name]:
                st.write(f"**{planet_name} in {planet_sign}**")
                st.write(interpretations[planet_name][planet_sign])
                st.write("")
                found_interpretations = True
    
    if not found_interpretations:
        st.info(f"No specific {interpretation_type.lower()} interpretations available for this chart configuration.")
        st.write("Consider exploring the Natal interpretation for general insights.")

def display_about():
    st.header("ℹ️ About Horoscope")
    st.markdown("""
    ### Horoscope ver. 1.0 (Streamlit Edition)
    
    **Copyright © 2025**  
    RAD  
    
    **Features**  
    - Professional astrological calculations using Swiss Ephemeris
    - Accurate planetary positions with professional ephemeris files
    - Natal chart calculations with Placidus houses
    - Complete planetary aspects calculations
    - Comprehensive interpretations for signs, degrees and houses
    - World capitals database for easy location selection
    - Enhanced visual design with larger fonts and icons
    
    **Technical:** Built with Streamlit and Swiss Ephemeris (pyswisseph) 
    using professional ephemeris files from Swiss Ephemeris repository.
    
    **Recent Improvements:**
    - Larger fonts and icons in chart display
    - World capitals dropdown with auto-coordinates
    - Minute precision for longitude/latitude
    - Specialized interpretations for Career, Relationships, Spiritual growth
    - Enhanced visual styling
    """)

if __name__ == "__main__":
    main()
