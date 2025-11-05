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
    """Afișează interpretări specifice pentru toate planetele"""
    
    # INTERPRETĂRI NATALE COMPLETE PENTRU TOATE PLANETELE
    natal_interpretations = {
        "Sun": {
            "ARI": "Energetic, pioneering, courageous. Natural leader with strong initiative. Impulsive and direct in approach.",
            "TAU": "Practical, reliable, patient. Values security and comfort. Determined and persistent.",
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
            "ARI": "Energetic, ambitious, strongwilled, self-centred, impulsive, dominant & obstinate.",
            "TAU": "Steady, patient, determined. Values comfort and security. Emotionally stable.",
            "GEM": "Changeable, adaptable, curious. Needs mental stimulation. Restless emotions.",
            "CAN": "Nurturing, sensitive, protective. Strong emotional connections. Home-oriented.",
            "LEO": "Proud, dramatic, generous. Needs recognition and appreciation. Warm emotions.",
            "VIR": "Practical, analytical, helpful. Attention to emotional details. Service-oriented.",
            "LIB": "Harmonious, diplomatic, social. Seeks emotional balance. Relationship-focused.",
            "SCO": "Intense, passionate, secretive. Deep emotional currents. Transformative.",
            "SAG": "Adventurous, optimistic, freedom-loving. Needs emotional expansion. Philosophical.",
            "CAP": "Responsible, disciplined, reserved. Controls emotions carefully. Ambitious.",
            "AQU": "Independent, unconventional, detached. Unique emotional expression. Progressive.",
            "PIS": "Compassionate, intuitive, dreamy. Sensitive emotional nature. Spiritual."
        },
        "Mercury": {
            "ARI": "Quick-thinking, direct, innovative. Expresses ideas boldly and spontaneously.",
            "TAU": "Practical, methodical, persistent. Thinks carefully before speaking.",
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
            "ARI": "Direct, passionate, impulsive in love. Attracted to challenge and excitement.",
            "TAU": "Sensual, loyal, comfort-seeking. Values stability and physical pleasure.",
            "GEM": "Social, flirtatious, communicative. Needs mental connection in relationships.",
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
            "AQU": "Innovative, rebellious, independent. Unconventional action.",
            "PIS": "Compassionate, intuitive, adaptable. Action through inspiration."
        },
        "Jupiter": {
            "ARI": "Pioneering, enthusiastic expansion. Growth through initiative and new beginnings.",
            "TAU": "Practical, material expansion. Growth through stability and tangible results.",
            "GEM": "Intellectual, communicative growth. Expansion through learning and connections.",
            "CAN": "Emotional, protective growth. Expansion through family and security.",
            "LEO": "Creative, confident expansion. Growth through self-expression and leadership.",
            "VIR": "Analytical, service-oriented growth. Expansion through improvement and health.",
            "LIB": "Social, harmonious expansion. Growth through relationships and beauty.",
            "SCO": "Intense, transformative growth. Expansion through depth and investigation.",
            "SAG": "Philosophical, adventurous expansion. Growth through exploration and truth.",
            "CAP": "Ambitious, structured growth. Expansion through discipline and achievement.",
            "AQU": "Innovative, humanitarian growth. Expansion through ideas and progress.",
            "PIS": "Spiritual, compassionate growth. Expansion through faith and intuition."
        },
        "Saturn": {
            "ARI": "Disciplined initiative. Lessons in leadership, courage and patience.",
            "TAU": "Practical responsibility. Lessons in security, values and persistence.",
            "GEM": "Structured communication. Lessons in learning, focus and reliability.",
            "CAN": "Emotional maturity. Lessons in family, security and nurturing.",
            "LEO": "Responsible creativity. Lessons in authority, humility and self-expression.",
            "VIR": "Organized service. Lessons in health, perfectionism and efficiency.",
            "LIB": "Balanced relationships. Lessons in partnership, fairness and diplomacy.",
            "SCO": "Transformative discipline. Lessons in power, control and regeneration.",
            "SAG": "Structured beliefs. Lessons in freedom, responsibility and truth.",
            "CAP": "Ambitious discipline. Lessons in achievement, structure and authority.",
            "AQU": "Innovative responsibility. Lessons in individuality, groups and progress.",
            "PIS": "Spiritual discipline. Lessons in boundaries, compassion and faith."
        }
    }

    # INTERPRETĂRI SEXUALE COMPLETE
    sexual_interpretations = {
        "Sun": {
            "ARI": "Quick response, instant turn-on or turn-off. Won't pull punch. Can reach peaks quickly. Capable of multiple orgasms, but impatient with long foreplay. Once aroused, wants to get down to business. Super intense, but burns out quickly.",
            "TAU": "Sensual and patient lover. Enjoys prolonged foreplay and physical touch. Very tactile, appreciates comfort and luxury in sexual settings. Slow to arousal but deeply passionate once engaged.",
            "GEM": "Active, likes variety. Can try out any new technique, but gets bored easily. Sex is more fun & communication than hot passion. Sex is more mental than physical. Good at fantasy games, manual and oral techniques.",
            "CAN": "Nurturing and emotional lover. Sex is deeply connected to feelings and security. Needs emotional bond for best sexual experience. Very protective of partner.",
            "LEO": "Dramatic and generous lover. Enjoys being the center of attention in bed. Warm-hearted and passionate. Needs admiration and appreciation.",
            "VIR": "Attentive and perfectionist lover. Very concerned with technique and partner's satisfaction. May be overly critical or anxious about performance.",
            "LIB": "Seeks change in sex, not for variety but for its own sake. Will rarely beat around the bush; insists partner deliver the goods. Can play all sides of a menage-a-trois well.",
            "SCO": "Intense and transformative lover. Deeply passionate and investigative about sexuality. Powerful sexual energy that can be overwhelming.",
            "SAG": "Adventurous and experimental lover. Views sex as another form of exploration and learning. Enjoys variety and new experiences.",
            "CAP": "Serious and disciplined lover. Approaches sex with responsibility and control. May be reserved but deeply committed.",
            "AQU": "Innovative and unconventional lover. Enjoys experimenting with new ideas and techniques. Values friendship in sexual relationships.",
            "PIS": "Romantic and intuitive lover. Very sensitive to partner's needs and energy. Spiritual approach to sexuality."
        },
        "Moon": {
            "ARI": "Quick emotional responses in intimacy. Needs constant new stimulation. Impatient with slow pace. Emotionally demanding in relationships.",
            "TAU": "Steady emotional needs. Requires physical comfort and security. Very loyal and possessive in intimate relationships.",
            "GEM": "Curious and communicative about emotions. Needs mental connection for emotional satisfaction. Restless emotional nature.",
            "CAN": "Deeply nurturing and protective. Strong emotional bonds are essential. Very sensitive to partner's emotional state.",
            "LEO": "Dramatic emotional expression. Needs admiration and recognition. Warm and generous with emotions.",
            "VIR": "Analytical about emotions. Service-oriented in expressing care. May worry excessively about relationships.",
            "LIB": "Seeks emotional harmony and balance. Very diplomatic in expressing feelings. Needs partnership for emotional fulfillment.",
            "SCO": "Intense emotional depth. Transformative emotional experiences. Very private about true feelings.",
            "SAG": "Optimistic and freedom-loving emotionally. Needs space for emotional expression. Philosophical about relationships.",
            "CAP": "Reserved emotional expression. Disciplined approach to feelings. Serious about emotional commitments.",
            "AQU": "Unconventional emotional needs. Values friendship in emotional connections. Detached emotional style.",
            "PIS": "Compassionate and empathetic. Very sensitive emotionally. Spiritual emotional connections."
        },
        "Venus": {
            "ARI": "Direct and passionate in love. Attracted to challenge and excitement. Impulsive in romantic decisions.",
            "TAU": "Sensual and loyal in relationships. Values physical comfort and stability. Very determined in love.",
            "GEM": "Flirtatious and communicative. Needs mental stimulation in relationships. Enjoys variety in partners.",
            "CAN": "Nurturing and protective in love. Seeks emotional security. Very home and family oriented.",
            "LEO": "Dramatic and generous in relationships. Loves romance and admiration. Very proud in love.",
            "VIR": "Practical and discerning in love. Shows affection through service. Very attentive to details.",
            "LIB": "Harmonious and diplomatic. Seeks balance and partnership. Very artistic in expression of love.",
            "SCO": "Intense and passionate in relationships. Seeks deep emotional bonds. Very possessive in love.",
            "SAG": "Adventurous and freedom-loving. Values honesty in relationships. Philosophical about love.",
            "CAP": "Serious and responsible in love. Seeks stability and commitment. Very ambitious in relationships.",
            "AQU": "Unconventional and friendly. Values independence in relationships. Very innovative in love.",
            "PIS": "Romantic and compassionate. Seeks spiritual connection. Very dreamy in love."
        },
        "Mars": {
            "ARI": "Energetic and direct in sexual expression. Very competitive and pioneering. Quick to action.",
            "TAU": "Persistent and determined in sexuality. Very sensual and physical. Slow but steady approach.",
            "GEM": "Versatile and communicative in sexual expression. Enjoys variety and mental stimulation.",
            "CAN": "Protective and emotional in sexuality. Very nurturing and sensitive. Actions driven by feelings.",
            "LEO": "Confident and dramatic in sexual expression. Very creative and proud. Enjoys being center of attention.",
            "VIR": "Precise and analytical in sexuality. Very methodical and attentive to details.",
            "LIB": "Diplomatic and balanced in sexual expression. Seeks harmony and partnership.",
            "SCO": "Intense and transformative in sexuality. Very powerful and investigative. Seeks deep connections.",
            "SAG": "Adventurous and optimistic in sexual expression. Enjoys exploration and freedom.",
            "CAP": "Ambitious and disciplined in sexuality. Very strategic and patient. Seeks long-term goals.",
            "AQU": "Innovative and rebellious in sexual expression. Very unconventional and independent.",
            "PIS": "Compassionate and intuitive in sexuality. Very adaptable and inspired by feelings."
        }
    }

    # INTERPRETĂRI CARRIER
    career_interpretations = {
        "Sun": {
            "ARI": "Natural leader, entrepreneur, pioneer. Excels in competitive fields and startups. Military, sports, emergency services.",
            "TAU": "Excellent in finance, real estate, agriculture. Builds lasting business structures. Banking, construction, luxury goods.",
            "GEM": "Communicator, teacher, journalist. Thrives in media and information fields. Writing, sales, transportation.",
            "CAN": "Nurturing careers: healthcare, hospitality, real estate. Strong business intuition. Nursing, cooking, history.",
            "LEO": "Management, entertainment, creative arts. Natural performer and leader. Theater, fashion, children's fields.",
            "VIR": "Healthcare, analysis, organization. Excellent with details and service. Research, editing, nutrition.",
            "LIB": "Law, diplomacy, arts. Natural mediator and relationship builder. Design, counseling, public relations.",
            "SCO": "Psychology, research, finance. Excellent in crisis management. Detective work, surgery, inheritance.",
            "SAG": "Education, travel, philosophy. Natural teacher and explorer. Publishing, law, foreign affairs.",
            "CAP": "Management, architecture, government. Builds lasting career structures. Engineering, mining, administration.",
            "AQU": "Technology, innovation, social causes. Visionary and forward-thinking. Science, aviation, humanitarian work.",
            "PIS": "Arts, healing, spirituality. Creative and compassionate careers. Music, photography, charity work."
        },
        "Midheaven": {
            "ARI": "Career requires initiative and independence. Leadership roles suit you best. Entrepreneurship, military, sports.",
            "TAU": "Stable, secure careers with tangible results. Finance or building industries. Banking, agriculture, arts.",
            "GEM": "Communications, teaching, or multi-faceted careers that offer variety. Media, writing, transportation.",
            "CAN": "Careers involving nurturing, protection, or domestic matters. Real estate, history, culinary arts.",
            "LEO": "Creative leadership roles where you can shine and receive recognition. Entertainment, management, sports.",
            "VIR": "Service-oriented careers requiring attention to detail and analysis. Healthcare, research, editing.",
            "LIB": "Partnership-based careers in law, arts, or diplomacy. Design, counseling, public relations.",
            "SCO": "Careers involving transformation, research, or depth psychology. Medicine, investigation, finance.",
            "SAG": "Expansive careers involving travel, education, or philosophy. Law, publishing, foreign service.",
            "CAP": "Structured careers with clear hierarchy and long-term goals. Government, engineering, administration.",
            "AQU": "Innovative careers in technology, science, or social reform. Aviation, electronics, humanitarian work.",
            "PIS": "Creative or healing careers that allow spiritual expression. Arts, music, therapy, charity work."
        }
    }

    # INTERPRETĂRI RELATIONSHIPS
    relationships_interpretations = {
        "Venus": {
            "ARI": "Passionate and direct in relationships. Needs excitement and challenge. Falls in love quickly.",
            "TAU": "Loyal and sensual partner. Values stability and physical connection. Very committed.",
            "GEM": "Communicative and social. Needs mental stimulation in relationships. Enjoys variety.",
            "CAN": "Nurturing and protective. Seeks emotional security and family. Very devoted.",
            "LEO": "Generous and dramatic. Needs admiration and romance. Very loyal.",
            "VIR": "Practical and helpful. Shows love through service and attention. Very devoted.",
            "LIB": "Harmonious and partnership-oriented. Seeks balance and fairness. Natural diplomat.",
            "SCO": "Intense and transformative. Seeks deep, soul-level connections. Very passionate.",
            "SAG": "Adventurous and freedom-loving. Needs space and intellectual connection. Honest partner.",
            "CAP": "Responsible and committed. Builds relationships that last. Very reliable.",
            "AQU": "Independent and unconventional. Values friendship and mental connection. Progressive thinker.",
            "PIS": "Compassionate and spiritual. Seeks soulful, empathetic connections. Romantic dreamer."
        },
        "Mars": {
            "ARI": "Direct and assertive in relationships. Needs action and initiative. Very passionate.",
            "TAU": "Persistent and determined. Slow to anger but very steadfast. Very sensual.",
            "GEM": "Communicative and versatile. Expresses desires through words. Mentally stimulating.",
            "CAN": "Protective and emotional. Actions driven by deep feelings. Very nurturing.",
            "LEO": "Confident and dramatic. Needs recognition and appreciation. Very generous.",
            "VIR": "Analytical and precise. Very attentive to partner's needs. Service-oriented.",
            "LIB": "Diplomatic and cooperative. Seeks harmony in interactions. Very considerate.",
            "SCO": "Intense and powerful. Very determined in pursuing desires. Transformative.",
            "SAG": "Adventurous and optimistic. Needs freedom and expansion. Philosophical.",
            "CAP": "Ambitious and disciplined. Very responsible in commitments. Reliable.",
            "AQU": "Innovative and independent. Unconventional in approach. Progressive.",
            "PIS": "Compassionate and intuitive. Very adaptable and sensitive. Spiritual."
        }
    }

    # INTERPRETĂRI SPIRITUALE
    spiritual_interpretations = {
        "Sun": {
            "ARI": "Spiritual warrior. Learns courage and compassionate leadership. Pioneer of new spiritual paths.",
            "TAU": "Earth spirituality. Connects divine through nature and senses. Grounded spiritual practice.",
            "GEM": "Messenger spirit. Integrates diverse knowledge and communication. Spiritual teacher.",
            "CAN": "Nurturing spirit. Develops unconditional love and compassion. Emotional spirituality.",
            "LEO": "Radiant spirit. Expresses creative divine energy. Heart-centered spirituality.",
            "VIR": "Healing spirit. Sees sacredness in service and details. Practical spirituality.",
            "LIB": "Harmonious spirit. Masters balance and relationship wisdom. Diplomatic spirituality.",
            "SCO": "Transformative spirit. Explores life-death-rebirth mysteries. Deep spiritual investigation.",
            "SAG": "Seeker spirit. Explores philosophical and spiritual truth. Spiritual adventurer.",
            "CAP": "Mountain spirit. Builds spiritual structures and discipline. Traditional spirituality.",
            "AQU": "Visionary spirit. Connects to collective consciousness. Innovative spirituality.",
            "PIS": "Mystic spirit. Experiences unity and divine compassion. Universal spirituality."
        },
        "Neptune": {
            "ARI": "Inspired action and spiritual initiative. Dreams about leadership and courage.",
            "TAU": "Spiritual values and divine manifestation. Dreams about security and beauty.",
            "GEM": "Inspired communication and spiritual learning. Dreams about knowledge and connection.",
            "CAN": "Mystical emotions and spiritual home. Dreams about family and emotional security.",
            "LEO": "Visionary creativity and spiritual self-expression. Dreams about recognition and creativity.",
            "VIR": "Spiritual service and healing work. Dreams about health and perfection.",
            "LIB": "Idealized relationships and spiritual partnership. Dreams about harmony and beauty.",
            "SCO": "Mystical transformation and spiritual depth. Dreams about power and regeneration.",
            "SAG": "Visionary beliefs and spiritual exploration. Dreams about truth and adventure.",
            "CAP": "Spiritual ambition and divine structure. Dreams about achievement and authority.",
            "AQU": "Inspired innovation and collective spirituality. Dreams about progress and friendship.",
            "PIS": "Divine compassion and spiritual unity. Dreams about healing and transcendence."
        }
    }

    # SELECTEAZĂ SETUL CORESPUNZĂTOR
    if interpretation_type == "Natal":
        interpretations = natal_interpretations
    elif interpretation_type == "Sexual":
        interpretations = sexual_interpretations
    elif interpretation_type == "Career":
        interpretations = career_interpretations
    elif interpretation_type == "Relationships":
        interpretations = relationships_interpretations
    elif interpretation_type == "Spiritual":
        interpretations = spiritual_interpretations
    else:
        interpretations = natal_interpretations  # Fallback

    # AFIȘEAZĂ INTERPRETĂRILE PENTRU TOATE PLANETELE RELEVANTE
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
    
    # Adaugă planete speciale în funcție de tipul de interpretare
    if interpretation_type == "Career":
        planets_to_display.append("Midheaven")
    elif interpretation_type == "Spiritual":
        planets_to_display.extend(["Jupiter", "Neptune"])
    elif interpretation_type == "Natal":
        planets_to_display.extend(["Jupiter", "Saturn"])

    for planet_name in planets_to_display:
        if planet_name == "Midheaven":
            # Pentru Midheaven, folosim casa a 10-a
            planet_data = chart_data['houses'][10]
            planet_sign = planet_data['sign']
        elif planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
        else:
            continue
            
        if (planet_name in interpretations and 
            planet_sign in interpretations[planet_name]):
            
            st.write(f"**** {planet_name}{planet_sign}")
            st.write(interpretations[planet_name][planet_sign])
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
    - Detailed interpretations for all categories:
      - Natal (general personality)
      - Sexual (intimacy and relationships)
      - Career (professional life)
      - Relationships (partnerships)
      - Spiritual (inner development)
    
    **House System**  
    Placidus - the most widely used house system in Western astrology
    
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
