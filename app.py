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
            
        # Calcul Julian Day
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
            
            positions[name] = {
                'longitude': longitude,
                'sign': signs[sign_num],
                'degrees': degrees,
                'minutes': minutes,
                'position_str': f"{degrees:02d}°{minutes:02d}' {signs[sign_num]}"
            }
        
        # CALCUL CASE AVANSAT CU PLACIDUS
        houses = calculate_houses_placidus(julian_day, birth_data['lat_deg'], birth_data['lon_deg'])
        
        # Calcul case pentru planete
        for name, planet_data in positions.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude(planet_longitude, houses)
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']})"
        
        return {
            'planets': positions,
            'houses': houses,
            'julian_day': julian_day
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {str(e)}")
        return None

def calculate_houses_placidus(julian_day, lat, lon):
    """Calcul case astrologice folosind sistemul Placidus"""
    try:
        # Calcul case cu Swiss Ephemeris
        houses_result = swe.houses(julian_day, lat, lon, b'P')  # 'P' = Placidus
        
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        for i in range(12):
            house_longitude = math.degrees(houses_result[0][i]) % 360
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
        return calculate_houses_equal(julian_day, lat, lon)

def calculate_houses_equal(julian_day, lat, lon):
    """Calcul case egale ca fallback"""
    try:
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        # Calcul ascendent pentru case egale
        houses_result = swe.houses(julian_day, lat, lon, b'P')
        asc_longitude = math.degrees(houses_result[0][0]) % 360
        
        for i in range(12):
            house_longitude = (asc_longitude + (i * 30)) % 360
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
        st.error(f"Eroare la calcularea caselor egale: {e}")
        return {}

def get_house_for_longitude(longitude, houses):
    """Determină casa pentru o longitudine dată"""
    try:
        longitude = longitude % 360
        
        # Găsește casa corespunzătoare
        house_numbers = list(houses.keys())
        for i in range(len(house_numbers)):
            current_house = house_numbers[i]
            next_house = house_numbers[(i + 1) % 12]
            
            current_long = houses[current_house]['longitude']
            next_long = houses[next_house]['longitude']
            
            # Ajustare pentru trecerea prin 0 grade
            if next_long < current_long:
                next_long += 360
                adj_longitude = longitude if longitude >= current_long else longitude + 360
            else:
                adj_longitude = longitude
            
            if current_long <= adj_longitude < next_long:
                return current_house
        
        return 1  # Fallback la casa 1
        
    except Exception as e:
        return 1

def calculate_aspects(chart_data):
    """Calculează aspectele astrologice dintre planete"""
    try:
        planets = chart_data['planets']
        aspects = []
        
        # Aspecte majore și orb-uri permise
        major_aspects = [
            {'name': 'Conjunction', 'angle': 0, 'orb': 8},
            {'name': 'Opposition', 'angle': 180, 'orb': 8},
            {'name': 'Trine', 'angle': 120, 'orb': 8},
            {'name': 'Square', 'angle': 90, 'orb': 8},
            {'name': 'Sextile', 'angle': 60, 'orb': 6}
        ]
        
        # Aspecte minore
        minor_aspects = [
            {'name': 'Quincunx', 'angle': 150, 'orb': 3},
            {'name': 'Semi-Sextile', 'angle': 30, 'orb': 3},
            {'name': 'Semi-Square', 'angle': 45, 'orb': 3},
            {'name': 'Sesqui-Square', 'angle': 135, 'orb': 3}
        ]
        
        all_aspects = major_aspects + minor_aspects
        
        # Listează toate planetele
        planet_list = list(planets.keys())
        
        # Calculează aspecte pentru fiecare pereche de planete
        for i in range(len(planet_list)):
            for j in range(i + 1, len(planet_list)):
                planet1 = planet_list[i]
                planet2 = planet_list[j]
                
                long1 = planets[planet1]['longitude']
                long2 = planets[planet2]['longitude']
                
                # Calculează diferența unghiulară
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verifică fiecare aspect posibil
                for aspect in all_aspects:
                    aspect_angle = aspect['angle']
                    orb = aspect['orb']
                    
                    if abs(diff - aspect_angle) <= orb:
                        exact_orb = abs(diff - aspect_angle)
                        is_exact = exact_orb <= 1.0
                        strength = 'Strong' if aspect in major_aspects else 'Weak'
                        
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
        st.subheader("🏠 Houses (Placidus)")
        for house_num, house_data in chart_data['houses'].items():
            st.write(f"**{house_num}** {house_data['position_str']}")
    
    # Butoane de navigare
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
    
    # Calcul aspecte
    aspects = calculate_aspects(chart_data)
    
    if aspects:
        # Afișare aspecte în tabel
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
        
        # Statistici aspecte
        st.subheader("Aspect Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_aspects = len(aspects)
        major_aspects = len([a for a in aspects if a['strength'] == 'Strong'])
        exact_aspects = len([a for a in aspects if a['exact']])
        
        with col1:
            st.metric("Total Aspects", total_aspects)
        with col2:
            st.metric("Major Aspects", major_aspects)
        with col3:
            st.metric("Exact Aspects", exact_aspects)
        with col4:
            st.metric("Average Orb", f"{sum(a['orb'] for a in aspects)/len(aspects):.2f}°")
        
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
    
    # Selector tip interpretare
    interpretation_type = st.selectbox(
        "Type of interpretation",
        ["Natal", "Sexual", "Career", "Relationships", "Spiritual"]
    )
    
    st.markdown("---")
    st.subheader(f"Interpretation: {interpretation_type}")
    
    # INTERPRETĂRI SPECIFICE PENTRU TOATE PLANETELE
    display_planet_interpretations(chart_data, interpretation_type)

def display_planet_interpretations(chart_data, interpretation_type):
    """Afișează interpretări specifice pentru toate planetele - exact ca în original"""
    
    # INTERPRETĂRI NATALE COMPLETE PENTRU SEMNE ȘI GRADE
    natal_interpretations = {
        "Sun": {
            "TAU": "Reliable, able, with powers of concentration, tenacity. Steadfast, a loving & affectionate \"family\" person. Honest, forthright. Learns readily from mistakes.",
            "ARI": "Energetic, pioneering, courageous. Natural leader with strong initiative.",
            "GEM": "Clever, bright, quickwitted, communicative, able to do many different things at once.",
            "CAN": "Nurturing, emotional, protective. Strong connection to home and family.",
            "LEO": "Confident, creative, generous. Natural performer and leader.",
            "VIR": "Analytical, practical, helpful. Attention to detail and service-oriented.",
            "LIB": "Friendly, cordial, artistic, kind, considerate, loyal, sociable.",
            "SCO": "Intense, passionate, transformative. Deep emotional understanding.",
            "SAG": "Adventurous, philosophical, optimistic. Seeks truth and expansion.",
            "CAP": "Ambitious, disciplined, responsible. Builds lasting structures.",
            "AQU": "Innovative, independent, humanitarian. Forward-thinking and original.",
            "PIS": "Compassionate, intuitive, artistic. Connected to spiritual realms."
        },
        "Moon": {
            "SCO": "Tenacious will, much energy & working power, passionate, often sensual. Honest.",
            "ARI": "Energetic, ambitious, strongwilled, self-centred, impulsive.",
            "TAU": "Steady, patient, determined. Values comfort and security.",
            "GEM": "Changeable, adaptable, curious. Needs mental stimulation.",
            "CAN": "Nurturing, sensitive, protective. Strong emotional connections.",
            "LEO": "Proud, dramatic, generous. Needs recognition and appreciation.",
            "VIR": "Practical, analytical, helpful. Attention to emotional details.",
            "LIB": "Harmonious, diplomatic, social. Seeks emotional balance.",
            "SAG": "Adventurous, optimistic, freedom-loving. Needs emotional expansion.",
            "CAP": "Responsible, disciplined, reserved. Controls emotions carefully.",
            "AQU": "Independent, unconventional, detached. Unique emotional expression.",
            "PIS": "Compassionate, intuitive, dreamy. Sensitive emotional nature."
        },
        "Mercury": {
            "TAU": "Thorough, persevering. Good at working with the hands. Inflexible, steady, obstinate, self-opinionated, conventional, limited in interests.",
            "ARI": "Quick-thinking, direct, innovative. Expresses ideas boldly.",
            "GEM": "Versatile, communicative, curious. Learns quickly and shares knowledge.",
            "CAN": "Intuitive, emotional, memory-oriented. Thinks with heart and nostalgia.",
            "LEO": "Confident, dramatic, creative. Expresses ideas with flair and authority.",
            "VIR": "Analytical, precise, detail-oriented. Excellent at critical thinking.",
            "LIB": "Diplomatic, balanced, artistic. Seeks harmony in communication.",
            "SCO": "Penetrating, investigative, profound. Seeks hidden truths.",
            "SAG": "Philosophical, broad-minded, honest. Thinks in big pictures.",
            "CAP": "Practical, organized, ambitious. Strategic and disciplined thinking.",
            "AQU": "Innovative, original, detached. Thinks outside conventional boxes.",
            "PIS": "Intuitive, imaginative, compassionate. Thinks with psychic sensitivity."
        },
        "Venus": {
            "GEM": "Flirtatious. Makes friends very easily. Has multifaceted relationships.",
            "ARI": "Direct, passionate, impulsive in love. Attracted to challenge and excitement.",
            "TAU": "Sensual, loyal, comfort-seeking. Values stability and physical pleasure.",
            "CAN": "Nurturing, protective, home-oriented. Seeks emotional security.",
            "LEO": "Dramatic, generous, proud. Loves romance and admiration.",
            "VIR": "Practical, helpful, discerning. Shows love through service.",
            "LIB": "Harmonious, diplomatic, artistic. Seeks balance and partnership.",
            "SCO": "Intense, passionate, possessive. Seeks deep emotional bonds.",
            "SAG": "Adventurous, freedom-loving, honest. Values independence in relationships.",
            "CAP": "Serious, responsible, ambitious. Seeks stability and commitment.",
            "AQU": "Unconventional, friendly, detached. Values friendship and independence.",
            "PIS": "Romantic, compassionate, dreamy. Seeks spiritual connection."
        },
        "Mars": {
            "AQU": "Strong reasoning powers. Often interested in science. Fond of freedom & independence.",
            "ARI": "Energetic, competitive, pioneering. Direct and assertive action.",
            "TAU": "Persistent, determined, practical. Slow but steady approach.",
            "GEM": "Versatile, quick, communicative. Action through words and ideas.",
            "CAN": "Protective, emotional, defensive. Actions driven by feelings.",
            "LEO": "Confident, dramatic, creative. Actions with flair and leadership.",
            "VIR": "Precise, analytical, efficient. Methodical and careful action.",
            "LIB": "Diplomatic, balanced, cooperative. Seeks harmony in action.",
            "SCO": "Intense, determined, transformative. Powerful and secretive action.",
            "SAG": "Adventurous, optimistic, freedom-loving. Action with purpose.",
            "CAP": "Ambitious, disciplined, patient. Strategic and persistent action.",
            "PIS": "Compassionate, intuitive, adaptable. Action through inspiration."
        },
        "Jupiter": {
            "LEO": "Has a talent for organizing & leading. Open & ready to help anyone in need - magnanimous & affectionate.",
            "ARI": "Pioneering, enthusiastic expansion. Growth through initiative.",
            "TAU": "Practical, material expansion. Growth through stability.",
            "GEM": "Intellectual, communicative growth. Expansion through learning.",
            "CAN": "Emotional, protective growth. Expansion through family.",
            "VIR": "Analytical, service-oriented growth. Expansion through improvement.",
            "LIB": "Social, harmonious expansion. Growth through relationships.",
            "SCO": "Intense, transformative growth. Expansion through depth.",
            "SAG": "Philosophical, adventurous expansion. Growth through exploration.",
            "CAP": "Ambitious, structured growth. Expansion through discipline.",
            "AQU": "Innovative, humanitarian growth. Expansion through ideas.",
            "PIS": "Spiritual, compassionate growth. Expansion through faith."
        },
        "Saturn": {
            "SAG": "Upright, open, courageous, honourable, grave, dignified, very capable.",
            "ARI": "Disciplined initiative. Lessons in leadership and patience.",
            "TAU": "Practical responsibility. Lessons in security and values.",
            "GEM": "Structured communication. Lessons in learning and focus.",
            "CAN": "Emotional maturity. Lessons in family and security.",
            "LEO": "Responsible creativity. Lessons in authority and humility.",
            "VIR": "Organized service. Lessons in health and perfectionism.",
            "LIB": "Balanced relationships. Lessons in partnership and fairness.",
            "SCO": "Transformative discipline. Lessons in power and control.",
            "CAP": "Ambitious discipline. Lessons in achievement and structure.",
            "AQU": "Innovative responsibility. Lessons in individuality and groups.",
            "PIS": "Spiritual discipline. Lessons in boundaries and compassion."
        },
        "Uranus": {
            "CAN": "Rather passive, compassionate, sensitive, impressionable, intuitive.",
            "ARI": "Revolutionary innovation. Sudden changes in identity.",
            "TAU": "Unconventional values. Changes in material security.",
            "GEM": "Revolutionary ideas. Changes in communication.",
            "LEO": "Innovative creativity. Changes in self-expression.",
            "VIR": "Revolutionary service. Changes in health and work.",
            "LIB": "Unconventional relationships. Changes in partnerships.",
            "SCO": "Transformative innovation. Changes in power dynamics.",
            "SAG": "Revolutionary beliefs. Changes in philosophy.",
            "CAP": "Innovative structures. Changes in career and authority.",
            "AQU": "Original individuality. Changes in groups and friends.",
            "PIS": "Spiritual innovation. Changes in dreams and intuition."
        },
        "Neptune": {
            "LIB": "Idealistic, often a bit out of touch with reality. Has only a hazy view & understanding of real life & the world.",
            "ARI": "Inspired action. Dreams and illusions about identity.",
            "TAU": "Spiritual values. Dreams about security and possessions.",
            "GEM": "Inspired communication. Dreams about learning and ideas.",
            "CAN": "Mystical emotions. Dreams about home and family.",
            "LEO": "Visionary creativity. Dreams about self-expression.",
            "VIR": "Spiritual service. Dreams about health and work.",
            "SCO": "Mystical transformation. Dreams about power and sex.",
            "SAG": "Visionary beliefs. Dreams about philosophy and travel.",
            "CAP": "Spiritual ambition. Dreams about career and status.",
            "AQU": "Inspired innovation. Dreams about groups and future.",
            "PIS": "Divine compassion. Dreams about spirituality and unity."
        },
        "Pluto": {
            "LEO": "Strong creative desires. Uncontrollable sexual appetite. Determined to win.",
            "ARI": "Transformative identity. Power struggles with self.",
            "TAU": "Deep values transformation. Power issues with possessions.",
            "GEM": "Profound mental change. Power in communication.",
            "CAN": "Emotional rebirth. Power struggles in family.",
            "VIR": "Service revolution. Power in health and work.",
            "LIB": "Relationship transformation. Power struggles in partnerships.",
            "SCO": "Intense rebirth. Power and control issues.",
            "SAG": "Belief system transformation. Power in philosophy.",
            "CAP": "Structural revolution. Power struggles in career.",
            "AQU": "Collective transformation. Power in groups and friends.",
            "PIS": "Spiritual rebirth. Power in dreams and intuition."
        }
    }

    # INTERPRETĂRI PENTRU GRADE SPECIFICE
    degree_interpretations = {
        "Sun": {
            5: "As a child energetic, noisy, overactive, fond of taking risks.",
            1: "Usually warmhearted & lovable but also vain, hedonistic & flirtatious.",
            9: "Has very wide-ranging interests."
        },
        "Moon": {
            12: "Sentimental, moody, shy, very impressionable & hypersensitive.",
            6: "Conscientious & easily influenced. Moody. Ready to help others. Illnesses of the nervous system."
        },
        "Mercury": {
            6: "Anxious about health - may travel for health reasons.",
            8: "Systematic, capable of concentrated thinking & planning. Feels things very deeply."
        },
        "Venus": {
            7: "Loves a cheerful, relaxed atmosphere. Fond of music, art & beautiful houses.",
            8: "Strong desire to possess another person. Strongly erotic."
        },
        "Mars": {
            2: "Ambitious, energetic, competitive, tenacious, practical, financially competent, obstinate, persistent & fearless.",
            11: "Enterprising, energetic. A good organizer of club & social activities."
        },
        "Jupiter": {
            2: "Has a very great deal of material luck, gaining much money by contact with foreign countries.",
            9: "Good-natured, upright, frequently talented in languages & law."
        },
        "Saturn": {
            1: "Subject to constraints & uncertainties. Serious by nature. Slow but persistent & unchanging.",
            5: "Often puritanical & sexually restrained. Serious by nature."
        },
        "Uranus": {
            4: "No desire to stay in the same place forever - fond of travel.",
            8: "Trouble through a legacy or through the money of a partnership. Has unusual views on sexuality."
        },
        "Neptune": {
            3: "Inhabits a world rich in fantasy. Can become a prisoner of own thoughts.",
            11: "Prefers artistic friends. Idealistic but quite practical."
        },
        "Pluto": {
            2: "Desires security both materially & personally.",
            9: "Attracted by far away places."
        }
    }

    # INTERPRETĂRI SEXUALE
    sexual_interpretations = {
        "Sun": {
            "GEM": "Active, likes variety. Can try out any new technique, but gets bored easily. Sex is more fun & communication than hot passion.",
            "ARI": "Quick response, instant turn-on or turn-off. Won't pull punch. Can reach peaks quickly.",
            "LIB": "Seeks change in sex, not for variety but for its own sake. Will rarely beat around the bush."
        },
        "Venus": {
            "GEM": "Wants a delicate, varied touch from sensitive lover. Tickling, stroking beats hard and heavy."
        },
        "Mars": {
            "VIR": "Highly specific lover, refines technique to the hilt, but may get hung up on only one or two."
        }
    }

    # INTERPRETĂRI CARRIER
    career_interpretations = {
        "Sun": {
            "ARI": "Natural leader, entrepreneur, pioneer. Excels in competitive fields and startups.",
            "TAU": "Excellent in finance, real estate, agriculture. Builds lasting business structures.",
            "GEM": "Communicator, teacher, journalist. Thrives in media and information fields."
        },
        "Midheaven": {
            "ARI": "Career requires initiative and independence. Leadership roles suit you best.",
            "TAU": "Stable, secure careers with tangible results. Finance or building industries.",
            "GEM": "Communications, teaching, or multi-faceted careers that offer variety."
        }
    }

    # SELECTEAZĂ SETUL CORESPUNZĂTOR
    if interpretation_type == "Natal":
        interpretations = natal_interpretations
        degree_interps = degree_interpretations
    elif interpretation_type == "Sexual":
        interpretations = sexual_interpretations
        degree_interps = {}
    elif interpretation_type == "Career":
        interpretations = career_interpretations
        degree_interps = {}
    else:
        interpretations = natal_interpretations
        degree_interps = degree_interpretations

    # AFIȘEAZĂ INTERPRETĂRILE PENTRU TOATE PLANETELE
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    if interpretation_type == "Career":
        planets_to_display.append("Midheaven")

    for planet_name in planets_to_display:
        if planet_name == "Midheaven":
            planet_data = chart_data['houses'][10]
            planet_sign = planet_data['sign']
            planet_degrees = planet_data['degrees']
        elif planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            planet_degrees = planet_data['degrees']
        else:
            continue

        # Afișează interpretarea pentru semn
        if (planet_name in interpretations and 
            planet_sign in interpretations[planet_name]):
            
            st.write(f"****  {planet_name}{planet_sign}")
            st.write(interpretations[planet_name][planet_sign])
            st.write("")

        # Afișează interpretarea pentru grad (doar pentru Natal)
        if (interpretation_type == "Natal" and 
            planet_name in degree_interps and 
            planet_degrees in degree_interps[planet_name]):
            
            st.write(f"****  {planet_name}{planet_degrees:02d}")
            st.write(degree_interps[planet_name][planet_degrees])
            st.write("")

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
    - Natal chart calculations with Placidus houses
    - Aspect calculations
    - Detailed interpretations for signs AND degrees
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
