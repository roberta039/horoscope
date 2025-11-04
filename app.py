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
                        is_exact = exact_orb <= 1.0  # Considerat exact dacă orb <= 1°
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
        st.subheader("Birth Data")
        st.write(f"**Name:** {birth_data['name']}")
        st.write(f"**Date:** {birth_data['date']}")
        st.write(f"**Time:** {birth_data['time']}")
        st.write(f"**Position:** {birth_data['lon_display']} {birth_data['lat_display']}")
    
    with col2:
        st.subheader("Planetary Highlights")
        sun_data = chart_data['planets']['Sun']
        moon_data = chart_data['planets']['Moon']
        asc_data = chart_data['houses'][1]  # Ascendent = casa 1
        
        st.write(f"**Sun:** {sun_data['sign']} in house {sun_data['house']}")
        st.write(f"**Moon:** {moon_data['sign']} in house {moon_data['house']}")
        st.write(f"**Ascendant:** {asc_data['sign']}")
    
    st.markdown("---")
    
    # Interpretare bazată pe poziții - ACUM CU CONTENT DIFERIT
    interpretation_type = st.selectbox(
        "Interpretation Focus",
        ["Natal Profile", "Personality", "Relationships", "Career", "Spiritual"]
    )
    
    st.subheader(f"Interpretation: {interpretation_type}")
    
    sun_data = chart_data['planets']['Sun']
    moon_data = chart_data['planets']['Moon']
    sun_sign = sun_data['sign']
    moon_sign = moon_data['sign']
    
    # INTERPRETĂRI SPECIFICE PENTRU FIECARE OPȚIUNE
    if interpretation_type == "Natal Profile":
        st.write("**🌞 Sun Sign Analysis**")
        sun_interpretations = {
            'ARI': "**Aries Sun:** You are a natural leader with pioneering spirit. Your energy and courage help you initiate new projects and take risks that others might avoid.",
            'TAU': "**Taurus Sun:** You value stability and security above all. Practical and reliable, you build lasting foundations in all areas of life.",
            'GEM': "**Gemini Sun:** Your curious mind and excellent communication skills make you adaptable and versatile. You thrive on mental stimulation.",
            'CAN': "**Cancer Sun:** Family and emotional security are your priorities. You have strong nurturing instincts and deep emotional intelligence.",
            'LEO': "**Leo Sun:** Creative and confident, you naturally attract attention. Your generosity and leadership qualities shine in social situations.",
            'VIR': "**Virgo Sun:** Analytical and practical, you excel at organization and service. Your attention to detail is remarkable.",
            'LIB': "**Libra Sun:** Harmony and balance drive your decisions. You're diplomatic, social, and seek meaningful partnerships.",
            'SCO': "**Scorpio Sun:** Intense and transformative, you understand life's deeper mysteries. Your passion and determination are powerful.",
            'SAG': "**Sagittarius Sun:** Philosophical and adventurous, you seek truth and expansion. Your optimism is infectious.",
            'CAP': "**Capricorn Sun:** Ambitious and disciplined, you build lasting structures. Your sense of responsibility is strong.",
            'AQU': "**Aquarius Sun:** Innovative and independent, you think outside the box. Your humanitarian ideals guide you.",
            'PIS': "**Pisces Sun:** Compassionate and intuitive, you're connected to spiritual realms. Your artistic sensitivity is pronounced."
        }
        
        if sun_sign in sun_interpretations:
            st.write(sun_interpretations[sun_sign])
        
        st.write("**🌙 Moon Sign Influence**")
        st.write(f"With Moon in {moon_sign}, your emotional nature is influenced by this sign's characteristics, affecting how you process feelings and seek security.")
    
    elif interpretation_type == "Personality":
        st.write("**🎭 Personality Dynamics**")
        personality_interpretations = {
            'ARI': "**Dynamic Personality:** Your Aries energy makes you direct, enthusiastic, and competitive. You prefer taking action over waiting.",
            'TAU': "**Steady Personality:** Your Taurus nature gives you patience and determination. You're methodical and appreciate life's comforts.",
            'GEM': "**Versatile Personality:** Your Gemini influence makes you quick-witted and adaptable. You enjoy variety and mental challenges.",
            'CAN': "**Nurturing Personality:** Your Cancer side makes you protective and empathetic. You're deeply connected to home and family.",
            'LEO': "**Charismatic Personality:** Your Leo energy brings creativity and confidence. You naturally take center stage.",
            'VIR': "**Analytical Personality:** Your Virgo influence makes you precise and helpful. You notice details others miss.",
            'LIB': "**Diplomatic Personality:** Your Libra nature seeks harmony and fairness. You're skilled at seeing multiple perspectives.",
            'SCO': "**Intense Personality:** Your Scorpio energy brings depth and passion. You're drawn to transformation and truth.",
            'SAG': "**Adventurous Personality:** Your Sagittarius side loves freedom and exploration. You're philosophical and optimistic.",
            'CAP': "**Ambitious Personality:** Your Capricorn influence makes you responsible and goal-oriented. You value achievement.",
            'AQU': "**Innovative Personality:** Your Aquarius energy makes you original and forward-thinking. You value individuality.",
            'PIS': "**Compassionate Personality:** Your Pisces nature brings sensitivity and intuition. You're artistic and empathetic."
        }
        
        if sun_sign in personality_interpretations:
            st.write(personality_interpretations[sun_sign])
        
        st.write("**Key Traits:** Your personality combines solar initiative with lunar emotional responses, creating a unique blend of conscious expression and subconscious needs.")
    
    elif interpretation_type == "Relationships":
        st.write("**💖 Relationship Patterns**")
        relationship_interpretations = {
            'ARI': "**Relationship Style:** Direct and passionate. You appreciate partners who match your energy and independence.",
            'TAU': "**Relationship Style:** Loyal and sensual. You seek stability and physical connection in partnerships.",
            'GEM': "**Relationship Style:** Communicative and curious. Mental connection is as important as emotional bond.",
            'CAN': "**Relationship Style:** Nurturing and protective. You create deep emotional bonds and value family life.",
            'LEO': "**Relationship Style:** Generous and dramatic. You enjoy romance and appreciation in relationships.",
            'VIR': "**Relationship Style:** Helpful and analytical. You show love through practical service and attention.",
            'LIB': "**Relationship Style:** Harmonious and partnership-oriented. Balance and fairness are crucial.",
            'SCO': "**Relationship Style:** Intense and transformative. You seek deep, soul-level connections.",
            'SAG': "**Relationship Style:** Adventurous and freedom-loving. You need space and intellectual stimulation.",
            'CAP': "**Relationship Style:** Responsible and committed. You build relationships that stand the test of time.",
            'AQU': "**Relationship Style:** Independent and unconventional. You value friendship and mental connection.",
            'PIS': "**Relationship Style:** Compassionate and spiritual. You seek soulful, empathetic connections."
        }
        
        if sun_sign in relationship_interpretations:
            st.write(relationship_interpretations[sun_sign])
        
        st.write("**Venus Influence:** Your approach to love and relationships is further colored by Venus's position, affecting what you find attractive and how you express affection.")
    
    elif interpretation_type == "Career":
        st.write("**💼 Career Directions**")
        career_interpretations = {
            'ARI': "**Career Strengths:** Leadership, entrepreneurship, competitive fields. You excel in roles requiring initiative.",
            'TAU': "**Career Strengths:** Finance, agriculture, arts. You thrive in stable, tangible results-oriented work.",
            'GEM': "**Career Strengths:** Communication, teaching, media. Your adaptability serves you in dynamic environments.",
            'CAN': "**Career Strengths:** Caregiving, real estate, hospitality. Your nurturing nature shines in service roles.",
            'LEO': "**Career Strengths:** Management, entertainment, creative arts. You excel in visible, recognition-based work.",
            'VIR': "**Career Strengths:** Healthcare, analysis, organization. Your precision is valuable in detailed work.",
            'LIB': "**Career Strengths:** Law, diplomacy, arts. Your sense of balance serves mediation and aesthetics.",
            'SCO': "**Career Strengths:** Psychology, research, crisis management. You handle intensity and transformation.",
            'SAG': "**Career Strengths:** Education, travel, philosophy. Your love of learning guides your path.",
            'CAP': "**Career Strengths:** Management, architecture, government. You build lasting structures and systems.",
            'AQU': "**Career Strengths:** Technology, innovation, social causes. Your vision shapes future directions.",
            'PIS': "**Career Strengths:** Arts, healing, spirituality. Your intuition guides creative and compassionate work."
        }
        
        if sun_sign in career_interpretations:
            st.write(career_interpretations[sun_sign])
        
        st.write("**Midheaven Influence:** Your career path and public image are also influenced by your Midheaven (10th house), indicating your vocational calling and life direction.")
    
    elif interpretation_type == "Spiritual":
        st.write("**🌌 Spiritual Path**")
        spiritual_interpretations = {
            'ARI': "**Spiritual Focus:** Courage and initiation. Your path involves learning to lead with compassion.",
            'TAU': "**Spiritual Focus:** Grounding and manifestation. You learn to balance material and spiritual worlds.",
            'GEM': "**Spiritual Focus:** Communication and learning. Your path involves integrating diverse knowledge.",
            'CAN': "**Spiritual Focus:** Emotional healing and nurturing. You develop unconditional compassion.",
            'LEO': "**Spiritual Focus:** Creative expression and heart opening. You learn authentic self-expression.",
            'VIR': "**Spiritual Focus:** Service and purification. Your path involves seeing divinity in details.",
            'LIB': "**Spiritual Focus:** Harmony and relationship balance. You learn the art of peaceful coexistence.",
            'SCO': "**Spiritual Focus:** Transformation and rebirth. Your path involves deep psychological healing.",
            'SAG': "**Spiritual Focus:** Truth-seeking and expansion. You explore philosophical and spiritual systems.",
            'CAP': "**Spiritual Focus:** Discipline and structure. You learn to build spiritual foundations.",
            'AQU': "**Spiritual Focus:** Innovation and collective consciousness. Your path involves future vision.",
            'PIS': "**Spiritual Focus:** Unity and compassion. You experience the interconnectedness of all life."
        }
        
        if sun_sign in spiritual_interpretations:
            st.write(spiritual_interpretations[sun_sign])
        
        st.write("**Neptune Influence:** Your spiritual development and connection to the transcendent are further shaped by Neptune's position in your chart, indicating your ideals and mystical inclinations.")

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
    - Aspect calculations
    - Detailed interpretations
    
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
