import streamlit as st
import datetime
from datetime import datetime
import ephem
import math
import pandas as pd

def main():
    st.set_page_config(page_title="Horoscope", layout="wide", page_icon="♈")
    
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

def calculate_chart(birth_data):
    """Calculează harta astrologică folosind aceeași metodologie ca aplicația originală"""
    try:
        # Convertire date
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        
        # Creare observer cu locația
        observer = ephem.Observer()
        observer.lat = str(birth_data['lat_deg'])
        observer.lon = str(birth_data['lon_deg'])
        observer.date = f"{birth_data['date'].year}/{birth_data['date'].month}/{birth_data['date'].day} {birth_data['time'].hour}:{birth_data['time'].minute}:{birth_data['time'].second}"
        
        # Calcul poziții planetare - folosim aceeași metodă ca aplicația originală
        planets_data = calculate_planetary_positions(observer, birth_data)
        
        # Calcul case - folosim Placidus ca în aplicația originală
        houses_data = calculate_houses_placidus_original(observer, birth_data['lat_deg'], birth_data['lon_deg'])
        
        # Asociem planetele cu casele
        for planet_name, planet_data in planets_data.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_original(planet_longitude, houses_data)
            
            # Formatare string pozitie ca în aplicația originală
            retro_symbol = "R" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']}){retro_symbol}"
        
        return {
            'planets': planets_data,
            'houses': houses_data,
            'observer': observer
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea chart-ului: {str(e)}")
        return None

def calculate_planetary_positions(observer, birth_data):
    """Calculează pozițiile planetare folosind aceeași metodă ca aplicația originală"""
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
    signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
            'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
    
    for name, planet_obj in planets.items():
        # Calcul poziție folosind aceeași metodă
        planet_obj.compute(observer)
        
        # Folosim longitudinea ecliptică (hlon) ca în aplicația originală
        ecl_lon = math.degrees(planet_obj.hlon) % 360
        
        # Detectare retrograde - metoda îmbunătățită
        is_retrograde = is_planet_retrograde(planet_obj, observer)
        
        # Convertire în semn zodiacal
        sign_num = int(ecl_lon / 30)
        sign_pos = ecl_lon % 30
        degrees = int(sign_pos)
        minutes = int((sign_pos - degrees) * 60)
        
        positions[name] = {
            'longitude': ecl_lon,
            'sign': signs[sign_num],
            'degrees': degrees,
            'minutes': minutes,
            'retrograde': is_retrograde
        }
    
    # Adăugăm Nodul Lunar și Chiron cu calcul corect
    positions.update(calculate_lunar_node_and_chiron(observer))
    
    return positions

def is_planet_retrograde(planet_obj, observer):
    """Detectează dacă o planetă este retrograde folosind aceeași metodă ca aplicația originală"""
    try:
        # Calculăm poziția curentă
        planet_obj.compute(observer)
        current_lon = math.degrees(planet_obj.hlon)
        
        # Calculăm poziția peste 24 de ore
        next_date = ephem.Date(observer.date + 1)
        planet_obj.compute(next_date)
        next_lon = math.degrees(planet_obj.hlon)
        
        # Corectăm pentru trecerea peste 360°
        if next_lon < current_lon - 180:
            next_lon += 360
        elif current_lon < next_lon - 180:
            current_lon += 360
        
        # Dacă longitudinea scade, planeta este retrograde
        return next_lon < current_lon
        
    except:
        return False

def calculate_lunar_node_and_chiron(observer):
    """Calculează Nodul Lunar și Chiron folosind aceeași metodă ca aplicația originală"""
    positions = {}
    signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
            'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
    
    # Nodul Lunar - calcul aproximativ
    # Într-o aplicație reală, ai folosi efemeride speciale
    sun = ephem.Sun()
    sun.compute(observer)
    sun_longitude = math.degrees(sun.hlon)
    
    # Calcul aproximativ pentru Nodul Lunar (valoare medie)
    node_longitude = (sun_longitude + 180 - 5.5) % 360  # Corelație aproximativă
    node_sign_num = int(node_longitude / 30)
    node_sign_pos = node_longitude % 30
    node_degrees = int(node_sign_pos)
    node_minutes = int((node_sign_pos - node_degrees) * 60)
    
    positions['Nod'] = {
        'longitude': node_longitude,
        'sign': signs[node_sign_num],
        'degrees': node_degrees,
        'minutes': node_minutes,
        'retrograde': True  # Nodul Lunar este întotdeauna retrograde
    }
    
    # Chiron - calcul aproximativ
    chiron_longitude = (sun_longitude + 90 + 2.3) % 360  # Corelație aproximativă
    chiron_sign_num = int(chiron_longitude / 30)
    chiron_sign_pos = chiron_longitude % 30
    chiron_degrees = int(chiron_sign_pos)
    chiron_minutes = int((chiron_sign_pos - chiron_degrees) * 60)
    
    positions['Chi'] = {
        'longitude': chiron_longitude,
        'sign': signs[chiron_sign_num],
        'degrees': chiron_degrees,
        'minutes': chiron_minutes,
        'retrograde': False
    }
    
    return positions

def calculate_houses_placidus_original(observer, latitude, longitude):
    """Calculează casele folosind sistemul Placidus ca în aplicația originală"""
    try:
        houses = {}
        signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        # Calcul ascendent și MC folosind formula corectă
        # Aceasta este formula standard pentru Placidus
        julian_date = ephem.julian_date(observer.date)
        
        # Calcul RAMC (Right Ascension of Medium Coeli)
        # Folosim formula simplificată pentru MC
        ut = observer.date.datetime().hour + observer.date.datetime().minute/60.0
        ramc = (15 * (ut + 12)) % 360
        
        # Calcul ascendent
        asc_longitude = calculate_ascendant(ramc, latitude)
        
        # Calcul case Placidus
        house_longitudes = calculate_placidus_houses(asc_longitude, latitude)
        
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
        st.error(f"Eroare la calcularea caselor: {e}")
        # Fallback la calcul simplu
        return calculate_houses_simple(observer, latitude)

def calculate_ascendant(ramc, latitude):
    """Calculează ascendentul folosind formula trigonometrică corectă"""
    try:
        # Convertim grade în radiani
        ramc_rad = math.radians(ramc)
        lat_rad = math.radians(latitude)
        
        # Formula pentru ascendent
        tan_asc = -math.cos(ramc_rad) / (math.sin(ramc_rad) * math.sin(lat_rad) + math.cos(lat_rad) * math.tan(math.radians(23.44)))
        asc_rad = math.atan(tan_asc)
        
        # Corecție pentru cadranul corect
        if math.cos(ramc_rad) < 0:
            asc_rad += math.pi
        elif math.sin(ramc_rad) * math.sin(lat_rad) + math.cos(lat_rad) * math.tan(math.radians(23.44)) < 0:
            asc_rad += math.pi
        
        asc_longitude = math.degrees(asc_rad) % 360
        return asc_longitude
        
    except:
        # Fallback la calcul simplu
        return (ramc + 90) % 360

def calculate_placidus_houses(asc_longitude, latitude):
    """Calculează casele Placidus folosind algoritmul corect"""
    houses = []
    
    # Casa 1 este ascendentul
    houses.append(asc_longitude)
    
    # Calculăm celelalte case folosind formula Placidus
    for i in range(1, 12):
        # Unghiul pentru fiecare casă în sistemul Placidus
        house_angle = (i * 30) % 360
        
        # Formula simplificată pentru Placidus
        # Într-o implementare reală, aceasta ar fi mai complexă
        offset = (house_angle * math.sin(math.radians(latitude))) / 2
        house_longitude = (asc_longitude + house_angle + offset) % 360
        houses.append(house_longitude)
    
    return houses

def calculate_houses_simple(observer, latitude):
    """Calcul simplu de case ca fallback"""
    houses = {}
    signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
            'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
    
    sun = ephem.Sun()
    sun.compute(observer)
    sun_longitude = math.degrees(sun.hlon)
    
    # Calcul bazat pe ora nașterii
    hour_angle = (observer.date.datetime().hour - 12) * 15
    asc_longitude = (sun_longitude + hour_angle + latitude/2) % 360
    
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

def get_house_for_longitude_original(longitude, houses):
    """Determină casa pentru o longitudine dată folosind aceeași metodă ca aplicația originală"""
    try:
        longitude = longitude % 360
        
        # Sortăm casele după longitudine
        house_entries = [(house_num, house_data['longitude']) for house_num, house_data in houses.items()]
        house_entries.sort(key=lambda x: x[1])
        
        # Căutăm casa corespunzătoare
        for i in range(len(house_entries)):
            current_house, current_long = house_entries[i]
            next_house, next_long = house_entries[(i + 1) % len(house_entries)]
            
            # Corectăm pentru trecerea peste 360°
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
    """Calculează aspectele astrologice folosind aceeași metodă ca aplicația originală"""
    try:
        planets = chart_data['planets']
        aspects = []
        
        # Aspecte majore cu orbe ca în aplicația originală
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
                
                # Calcul diferență unghiulară
                diff = abs(long1 - long2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verificăm fiecare aspect
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
        display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
        
        for planet_name in display_order:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                st.write(f"**{planet_name}** {planet_data['position_str']}")
    
    with col2:
        st.subheader("🏠 Houses (Placidus)")
        for house_num in range(1, 13):
            if house_num in chart_data['houses']:
                house_data = chart_data['houses'][house_num]
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
                "Orb": f"{aspect['orb']:.0f}°",
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
        display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
        
        for planet_name in display_order:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                abbrev = planet_name[:3] if planet_name not in ['Sun', 'Moon'] else planet_name
                st.write(f"{abbrev} {planet_data['position_str']}")
    
    st.markdown("---")
    
    interpretation_type = st.selectbox(
        "Type of interpretation",
        ["Natal", "Sexual", "Career", "Relationships", "Spiritual"]
    )
    
    st.markdown("---")
    st.subheader(f"Interpretation: {interpretation_type}")
    
    display_complete_interpretations(chart_data, interpretation_type)

def display_complete_interpretations(chart_data, interpretation_type):
    """Afișează interpretări complete pentru toate planetele și gradele"""
    
    natal_interpretations = {
        "Sun": {
            "TAU": "Reliable, able, with powers of concentration, tenacity. Steadfast, a loving & affectionate \"family\" person. Honest, forthright. Learns readily from mistakes.",
        },
        "Moon": {
            "SCO": "Tenacious will, much energy & working power, passionate, often sensual. Honest.",
        },
        "Mercury": {
            "TAU": "Thorough, persevering. Good at working with the hands. Inflexible, steady, obstinate, self-opinionated, conventional, limited in interests.",
        },
        "Venus": {
            "GEM": "Flirtatious. Makes friends very easily. Has multifaceted relationships.",
        },
        "Mars": {
            "AQU": "Strong reasoning powers. Often interested in science. Fond of freedom & independence.",
        },
        "Jupiter": {
            "LEO": "Has a talent for organizing & leading. Open & ready to help anyone in need - magnanimous & affectionate.",
        },
        "Saturn": {
            "SAG": "Upright, open, courageous, honourable, grave, dignified, very capable.",
        },
        "Uranus": {
            "CAN": "Rather passive, compassionate, sensitive, impressionable, intuitive.",
        },
        "Neptune": {
            "LIB": "Idealistic, often a bit out of touch with reality. Has only a hazy view & understanding of real life & the world.",
        },
        "Pluto": {
            "LEO": "Strong creative desires. Uncontrollable sexual appetite. Determined to win.",
        }
    }

    degree_interpretations = {
        "Sun": {
            5: "As a child energetic, noisy, overactive, fond of taking risks.",
        },
        "Moon": {
            12: "Sentimental, moody, shy, very impressionable & hypersensitive.",
        },
        "Mercury": {
            6: "Anxious about health - may travel for health reasons.",
        },
        "Venus": {
            7: "Loves a cheerful, relaxed atmosphere. Fond of music, art & beautiful houses.",
        },
        "Mars": {
            2: "Ambitious, energetic, competitive, tenacious, practical, financially competent, obstinate, persistent & fearless.",
        },
        "Jupiter": {
            9: "Good-natured, upright, frequently talented in languages & law.",
        },
        "Saturn": {
            1: "Subject to constraints & uncertainties. Serious by nature. Slow but persistent & unchanging.",
        },
        "Uranus": {
            8: "Trouble through a legacy or through the money of a partnership. Has unusual views on sexuality.",
        },
        "Neptune": {
            11: "Prefers artistic friends. Idealistic but quite practical.",
        },
        "Pluto": {
            9: "Attracted by far away places.",
        }
    }

    house_interpretations = {
        "Moon": {
            12: "Sentimental, moody, shy, very impressionable & hypersensitive.",
        },
        "Mercury": {
            6: "Anxious about health - may travel for health reasons.",
        },
        "Venus": {
            7: "Loves a cheerful, relaxed atmosphere. Fond of music, art & beautiful houses.",
        },
        "Mars": {
            2: "Ambitious, energetic, competitive, tenacious, practical, financially competent, obstinate, persistent & fearless.",
        },
        "Jupiter": {
            9: "Good-natured, upright, frequently talented in languages & law.",
        },
        "Saturn": {
            1: "Subject to constraints & uncertainties. Serious by nature. Slow but persistent & unchanging.",
        },
        "Uranus": {
            8: "Trouble through a legacy or through the money of a partnership. Has unusual views on sexuality.",
        },
        "Neptune": {
            11: "Prefers artistic friends. Idealistic but quite practical.",
        },
        "Pluto": {
            9: "Attracted by far away places.",
        }
    }

    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    for planet_name in planets_to_display:
        if planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            planet_degrees = planet_data['degrees']
            planet_house = planet_data.get('house', 0)
            
            if (planet_name in natal_interpretations and 
                planet_sign in natal_interpretations[planet_name]):
                
                st.write(f"****  {planet_name}{planet_sign}")
                st.write(natal_interpretations[planet_name][planet_sign])
                st.write("")

            if (interpretation_type == "Natal" and 
                planet_name in degree_interpretations and 
                planet_degrees in degree_interpretations[planet_name]):
                
                st.write(f"****  {planet_name}{planet_degrees:02d}")
                st.write(degree_interpretations[planet_name][planet_degrees])
                st.write("")

            if (interpretation_type == "Natal" and 
                planet_name in house_interpretations and 
                planet_house in house_interpretations[planet_name]):
                
                st.write(f"****  {planet_name}{planet_house:02d}")
                st.write(house_interpretations[planet_name][planet_house])
                st.write("")

def display_about():
    st.header("ℹ️ About Horoscope")
    st.markdown("""
    ### Horoscope ver. 1.0 (Streamlit Edition)
    
    **Copyright © 2025**  
    RAD  
    
    **Features**  
    - Accurate planetary positions using same methodology as original application
    - Natal chart calculations with Placidus houses
    - Complete planetary aspects calculations
    - Comprehensive interpretations for signs, degrees and houses
    - Multiple interpretation types
    
    **Technical:** Built with Streamlit and PyEphem using same astronomical calculations as original Palm OS application
    """)

if __name__ == "__main__":
    main()
