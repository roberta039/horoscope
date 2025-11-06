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

def main():
    st.set_page_config(page_title="Horoscope", layout="wide", page_icon="♈")
    
    # Inițializare session state
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    if 'transit_data' not in st.session_state:
        st.session_state.transit_data = None
    if 'progressed_data' not in st.session_state:
        st.session_state.progressed_data = None
    
    # Sidebar meniu
    with st.sidebar:
        st.title("♈ Horoscope")
        st.markdown("---")
        menu_option = st.radio("Main Menu", [
            "Data Input", 
            "Chart", 
            "Positions", 
            "Aspects", 
            "Transits",
            "Progressions",
            "Interpretation", 
            "About"
        ])
    
    if menu_option == "Data Input":
        data_input_form()
    elif menu_option == "Chart":
        display_chart()
    elif menu_option == "Positions":
        display_positions()
    elif menu_option == "Aspects":
        display_aspects()
    elif menu_option == "Transits":
        display_transits()
    elif menu_option == "Progressions":
        display_progressions()
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

@st.cache_data(ttl=3600, show_spinner="Calculating astrological chart...")
def calculate_chart_cached(birth_data):
    """Versiune cached a calculului chart-ului"""
    return calculate_chart(birth_data)

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
            'jd': jd,
            'birth_datetime': birth_datetime
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

def create_chart_wheel(chart_data, birth_data, title_suffix="Natal Chart", show_aspects=True):
    """Creează un grafic circular cu planetele în case și aspectele cu linii colorate"""
    try:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_aspect('equal')
        
        # Setări pentru cercul principal
        center_x, center_y = 0, 0
        outer_radius = 4.5
        inner_radius = 3.8
        house_radius = 3.5
        planet_radius = 3.0
        aspect_radius = 2.5  # Raza pentru liniile de aspect
        
        # Culori
        background_color = 'white'
        circle_color = '#262730'
        text_color = 'black'
        house_color = 'black'
        
        # Culori pentru aspecte
        aspect_colors = {
            'Conjunction': '#FF6B6B',    # Roșu
            'Opposition': '#4ECDC4',     # Turcoaz
            'Trine': '#45B7D1',          # Albastru deschis
            'Square': '#FFA500',         # Portocaliu
            'Sextile': '#96CEB4'         # Verde deschis
        }
        
        planet_colors = {
            'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mercury': '#A9A9A9',
            'Venus': '#FFB6C1', 'Mars': '#FF4500', 'Jupiter': '#FFA500',
            'Saturn': '#DAA520', 'Uranus': '#40E0D0', 'Neptune': '#1E90FF',
            'Pluto': '#8B008B', 'Nod': '#FF69B4', 'Chi': '#32CD32'
        }
        
        # Setează fundalul
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)
        
        # Desenează cercurile principale
        outer_circle = Circle((center_x, center_y), outer_radius, fill=True, color=circle_color, alpha=0.3)
        inner_circle = Circle((center_x, center_y), inner_radius, fill=True, color=background_color)
        ax.add_patch(outer_circle)
        ax.add_patch(inner_circle)
        
        # Semnele zodiacale și simbolurile
        signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
        sign_names = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
        
        # Desenează casele și semnele
        for i in range(12):
            angle = i * 30 - 90  # Începe de la 9 o'clock (Aries)
            rad_angle = np.radians(angle)
            
            # Linii pentru case
            x_outer = center_x + outer_radius * np.cos(rad_angle)
            y_outer = center_y + outer_radius * np.sin(rad_angle)
            x_inner = center_x + inner_radius * np.cos(rad_angle)
            y_inner = center_y + inner_radius * np.sin(rad_angle)
            
            ax.plot([x_inner, x_outer], [y_inner, y_outer], color=house_color, linewidth=1, alpha=0.5)
            
            # Numerele caselor
            house_text_angle = angle + 15  # Centrul casei
            house_rad_angle = np.radians(house_text_angle)
            x_house = center_x + house_radius * np.cos(house_rad_angle)
            y_house = center_y + house_radius * np.sin(house_rad_angle)
            
            ax.text(x_house, y_house, str(i+1), ha='center', va='center', 
                   color=house_color, fontsize=10, fontweight='bold')
            
            # Semnele zodiacale
            sign_angle = i * 30 - 75  # Poziționare pentru semne
            sign_rad_angle = np.radians(sign_angle)
            x_sign = center_x + (outer_radius + 0.3) * np.cos(sign_rad_angle)
            y_sign = center_y + (outer_radius + 0.3) * np.sin(sign_rad_angle)
            
            ax.text(x_sign, y_sign, signs[i], ha='center', va='center', 
                   color=house_color, fontsize=14)
            
            # Numele semnului
            x_name = center_x + (outer_radius + 0.7) * np.cos(sign_rad_angle)
            y_name = center_y + (outer_radius + 0.7) * np.sin(sign_rad_angle)
            
            ax.text(x_name, y_name, sign_names[i], ha='center', va='center', 
                   color=house_color, fontsize=8, rotation=angle+90)
        
        # Calculează aspectele dacă este necesar
        if show_aspects:
            aspects = calculate_aspects(chart_data)
            
            # Desenează liniile pentru aspecte
            for aspect in aspects:
                planet1 = aspect['planet1']
                planet2 = aspect['planet2']
                aspect_name = aspect['aspect_name']
                
                if (planet1 in chart_data['planets'] and 
                    planet2 in chart_data['planets']):
                    
                    # Coordonatele planetelor
                    long1 = chart_data['planets'][planet1]['longitude']
                    long2 = chart_data['planets'][planet2]['longitude']
                    
                    # Calculează unghiurile pentru planete
                    angle1 = long1 - 90
                    angle2 = long2 - 90
                    
                    rad_angle1 = np.radians(angle1)
                    rad_angle2 = np.radians(angle2)
                    
                    # Pozițiile planetelor pe cerc
                    x1 = center_x + aspect_radius * np.cos(rad_angle1)
                    y1 = center_y + aspect_radius * np.sin(rad_angle1)
                    x2 = center_x + aspect_radius * np.cos(rad_angle2)
                    y2 = center_y + aspect_radius * np.sin(rad_angle2)
                    
                    # Alege culoarea pentru aspect
                    color = aspect_colors.get(aspect_name, '#888888')
                    
                    # Grosimea liniei în funcție de puterea aspectului
                    linewidth = 2.0 if aspect['strength'] == 'Strong' else 1.0
                    
                    # Desenează linia aspectului
                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, 
                           alpha=0.7, linestyle='-')
        
        # Plasează planetele în chart
        planets = chart_data['planets']
        planet_symbols = {
            'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀',
            'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅',
            'Neptune': '♆', 'Pluto': '♇', 'Nod': '☊', 'Chi': '⚷'
        }
        
        for planet_name, planet_data in planets.items():
            longitude = planet_data['longitude']
            house = planet_data.get('house', 1)
            is_retrograde = planet_data.get('retrograde', False)
            
            # Calculează unghiul pentru planetă
            planet_angle = longitude - 90  # Ajustare pentru a începe de la Aries
            planet_rad_angle = np.radians(planet_angle)
            
            # Poziția planetei
            x_planet = center_x + planet_radius * np.cos(planet_rad_angle)
            y_planet = center_y + planet_radius * np.sin(planet_rad_angle)
            
            # Simbolul planetei
            symbol = planet_symbols.get(planet_name, '•')
            color = planet_colors.get(planet_name, 'white')
            
            # Afișează planeta
            ax.text(x_planet, y_planet, symbol, ha='center', va='center', 
                   color=color, fontsize=12, fontweight='bold')
            
            # Numele planetei (scurtat)
            abbrev = planet_name[:3] if planet_name not in ['Sun', 'Moon'] else planet_name
            if is_retrograde:
                abbrev += " R"
                
            # Poziția pentru nume
            name_angle = planet_angle + 5
            name_rad_angle = np.radians(name_angle)
            x_name = center_x + (planet_radius - 0.3) * np.cos(name_rad_angle)
            y_name = center_y + (planet_radius - 0.3) * np.sin(name_rad_angle)
            
            ax.text(x_name, y_name, abbrev, ha='center', va='center', 
                   color=color, fontsize=7, alpha=0.8)
        
        # Titlul chart-ului
        name = birth_data.get('name', 'Natal Chart')
        date_str = birth_data.get('date', '').strftime('%Y-%m-%d')
        ax.set_title(f'{name} - {date_str}\n{title_suffix}', 
                    color=text_color, fontsize=16, pad=20)
        
        # Legenda pentru aspecte (dacă sunt afișate)
        if show_aspects and aspects:
            legend_elements = []
            for aspect_name, color in aspect_colors.items():
                legend_elements.append(plt.Line2D([0], [0], color=color, lw=2, label=aspect_name))
            
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1), 
                     fontsize=8, framealpha=0.7)
        
        # Elimină axele
        ax.set_xlim(-outer_radius-1, outer_radius+1)
        ax.set_ylim(-outer_radius-1, outer_radius+1)
        ax.axis('off')
        
        # Legenda
        legend_text = "Planets in Houses - Placidus System"
        ax.text(0, -outer_radius-0.8, legend_text, ha='center', va='center',
               color=text_color, fontsize=10, style='italic')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Eroare la crearea graficului: {e}")
        return None

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

def calculate_transits(birth_jd, transit_date, birth_lat, birth_lon):
    """Calculează transitele pentru o dată specifică"""
    try:
        # Converteste data de transit în Julian Day
        transit_datetime = datetime.combine(transit_date, datetime.min.time())
        transit_jd = swe.julday(transit_datetime.year, transit_datetime.month, 
                               transit_datetime.day, 12.0)  # La amiază
        
        # Calculează pozițiile planetare pentru data de transit
        transit_planets = calculate_planetary_positions_swiss(transit_jd)
        
        # Calculează casele pentru data de transit (folosind coordonatele natale)
        transit_houses = calculate_houses_placidus_swiss(transit_jd, birth_lat, birth_lon)
        
        # Asociem planetele cu casele
        for planet_name, planet_data in transit_planets.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_swiss(planet_longitude, transit_houses)
            
            retro_symbol = "R" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']}){retro_symbol}"
        
        return {
            'planets': transit_planets,
            'houses': transit_houses,
            'jd': transit_jd,
            'date': transit_date
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea transitelor: {e}")
        return None

def calculate_progressions(birth_data, progression_date, method='secondary'):
    """Calculează progresiile (Secondary/ Solar Arc)"""
    try:
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        progression_datetime = datetime.combine(progression_date, datetime.min.time())
        
        # Obține JD-ul natal din session_state
        if st.session_state.chart_data is None:
            st.error("Natal chart not calculated yet!")
            return None
            
        natal_jd = st.session_state.chart_data['jd']
        
        # Calcul pentru Secondary Progression (1 zi = 1 an)
        if method == 'secondary':
            days_diff = (progression_datetime - birth_datetime).days
            progressed_jd = natal_jd + days_diff
            
        # Calcul pentru Solar Arc
        elif method == 'solar_arc':
            # Poziția Soarelui progresat
            days_diff = (progression_datetime - birth_datetime).days
            solar_arc = (days_diff / 365.25) * 0.9856  # Mișcarea medie zilnică a Soarelui
            
            # Calculează harta natală pentru a aplica Solar Arc
            natal_chart = st.session_state.chart_data
            progressed_planets = {}
            
            for planet_name, planet_data in natal_chart['planets'].items():
                progressed_longitude = (planet_data['longitude'] + solar_arc) % 360
                
                # Convertire în semn zodiacal
                signs = ['ARI', 'TAU', 'GEM', 'CAN', 'LEO', 'VIR', 
                        'LIB', 'SCO', 'SAG', 'CAP', 'AQU', 'PIS']
                sign_num = int(progressed_longitude / 30)
                sign_pos = progressed_longitude % 30
                degrees = int(sign_pos)
                minutes = int((sign_pos - degrees) * 60)
                
                progressed_planets[planet_name] = {
                    'longitude': progressed_longitude,
                    'sign': signs[sign_num],
                    'degrees': degrees,
                    'minutes': minutes,
                    'retrograde': planet_data['retrograde'],
                    'position_str': f"{degrees:02d}°{minutes:02d}' {signs[sign_num]}"
                }
            
            return {
                'planets': progressed_planets,
                'houses': natal_chart['houses'],  # Casele rămân aceleași
                'solar_arc': solar_arc,
                'date': progression_date,
                'method': 'Solar Arc'
            }
        
        # Pentru Secondary Progression, calculează pozițiile reale
        progressed_planets = calculate_planetary_positions_swiss(progressed_jd)
        if progressed_planets is None:
            st.error("Failed to calculate progressed planetary positions")
            return None
            
        progressed_houses = calculate_houses_placidus_swiss(progressed_jd, 
                                                          birth_data['lat_deg'], 
                                                          birth_data['lon_deg'])
        if progressed_houses is None:
            st.error("Failed to calculate progressed houses")
            return None
        
        # Asociem planetele cu casele
        for planet_name, planet_data in progressed_planets.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_swiss(planet_longitude, progressed_houses)
            
            retro_symbol = "R" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']}){retro_symbol}"
        
        return {
            'planets': progressed_planets,
            'houses': progressed_houses,
            'jd': progressed_jd,
            'date': progression_date,
            'method': 'Secondary Progression'
        }
        
    except Exception as e:
        st.error(f"Eroare la calcularea progresiilor: {e}")
        return None

def calculate_transit_aspects(natal_chart, transit_chart):
    """Calculează aspectele dintre planetele natale și cele în transit"""
    try:
        aspects = []
        
        major_aspects = [
            {'name': 'Conjunction', 'angle': 0, 'orb': 3},
            {'name': 'Opposition', 'angle': 180, 'orb': 3},
            {'name': 'Trine', 'angle': 120, 'orb': 3},
            {'name': 'Square', 'angle': 90, 'orb': 3},
            {'name': 'Sextile', 'angle': 60, 'orb': 2}
        ]
        
        natal_planets = natal_chart['planets']
        transit_planets = transit_chart['planets']
        
        for natal_planet in natal_planets.keys():
            for transit_planet in transit_planets.keys():
                # Evită aspectele între aceeași planetă (sunt mereu conjunctie)
                if natal_planet == transit_planet:
                    continue
                
                natal_long = natal_planets[natal_planet]['longitude']
                transit_long = transit_planets[transit_planet]['longitude']
                
                diff = abs(natal_long - transit_long)
                if diff > 180:
                    diff = 360 - diff
                
                for aspect in major_aspects:
                    aspect_angle = aspect['angle']
                    orb = aspect['orb']
                    
                    if abs(diff - aspect_angle) <= orb:
                        exact_orb = abs(diff - aspect_angle)
                        is_exact = exact_orb <= 0.5
                        strength = 'Strong' if exact_orb <= 1.0 else 'Medium'
                        
                        aspects.append({
                            'natal_planet': natal_planet,
                            'transit_planet': transit_planet,
                            'aspect_name': aspect['name'],
                            'angle': aspect_angle,
                            'orb': exact_orb,
                            'exact': is_exact,
                            'strength': strength
                        })
        
        return aspects
        
    except Exception as e:
        st.error(f"Eroare la calcularea aspectelor de transit: {e}")
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
            # Longitude cu grade și minute
            st.write("**Longitude**")
            col_lon_deg, col_lon_min = st.columns(2)
            with col_lon_deg:
                longitude_deg = st.number_input("Longitude (°)", min_value=0.0, max_value=180.0, value=16.0, step=1.0, key="lon_deg")
            with col_lon_min:
                longitude_min = st.number_input("Longitude (')", min_value=0.0, max_value=59.9, value=0.0, step=1.0, key="lon_min")
            longitude_dir = st.selectbox("Longitude Direction", ["East", "West"], index=0, key="lon_dir")
            
        with col2b:
            # Latitude cu grade și minute
            st.write("**Latitude**")
            col_lat_deg, col_lat_min = st.columns(2)
            with col_lat_deg:
                latitude_deg = st.number_input("Latitude (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="lat_deg")
            with col_lat_min:
                latitude_min = st.number_input("Latitude (')", min_value=0.0, max_value=59.9, value=51.0, step=1.0, key="lat_min")
            latitude_dir = st.selectbox("Latitude Direction", ["North", "South"], index=0, key="lat_dir")
        
        # Calcul coordonate finale
        lon = longitude_deg + (longitude_min / 60.0)
        lon = lon if longitude_dir == "East" else -lon
        
        lat = latitude_deg + (latitude_min / 60.0)
        lat = lat if latitude_dir == "North" else -lat
        
        st.write(f"**Coordinates:** {abs(lat):.2f}°{latitude_dir[0]}, {abs(lon):.2f}°{longitude_dir[0]}")
        st.write(f"**Decimal:** {lat:.6f}°N, {lon:.6f}°E")
    
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
                'lon_display': f"{longitude_deg}°{longitude_min:.0f}'{longitude_dir}"
            }
            
            chart_data = calculate_chart_cached(birth_data)
            
            if chart_data:
                st.session_state.chart_data = chart_data
                st.session_state.birth_data = birth_data
                st.success("✅ Chart calculated successfully using Swiss Ephemeris!")
            else:
                st.error("Failed to calculate chart. Please check your input data.")

def display_chart():
    st.header("♈ Astrological Chart")
    
    if st.session_state.chart_data is None:
        st.warning("Please enter birth data and calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    # Opțiune pentru afișarea aspectelor
    col1, col2 = st.columns([3, 1])
    
    with col2:
        show_aspect_lines = st.checkbox("Show Aspect Lines", value=True, help="Display colored lines between planets showing astrological aspects")
    
    # Afișează graficul circular
    st.subheader("🎯 Chart Wheel")
    fig = create_chart_wheel(chart_data, birth_data, "Natal Chart", show_aspect_lines)
    if fig:
        st.pyplot(fig)
    else:
        st.error("Could not generate chart wheel")
    
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
                'Longitude': f"{int(planet_data['longitude'])}°{int((planet_data['longitude'] % 1) * 60)}'",
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

def display_transits():
    st.header("🔄 Planetary Transits")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate natal chart first!")
        return
    
    natal_chart = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    st.subheader("Transit Date Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        transit_date = st.date_input("Select Transit Date", 
                                   datetime.now().date(),
                                   min_value=datetime(1900, 1, 1).date(),
                                   max_value=datetime(2100, 12, 31).date())
    
    with col2:
        show_aspects = st.checkbox("Show Aspects to Natal Chart", value=True)
        show_chart = st.checkbox("Show Transit Chart Wheel", value=True)
        show_aspect_lines = st.checkbox("Show Aspect Lines in Chart", value=True)
    
    if st.button("Calculate Transits", type="primary"):
        with st.spinner("Calculating transits..."):
            transit_data = calculate_transits(
                natal_chart['jd'], 
                transit_date, 
                birth_data['lat_deg'], 
                birth_data['lon_deg']
            )
            
            if transit_data:
                st.session_state.transit_data = transit_data
                st.success(f"✅ Transits calculated for {transit_date}")
            else:
                st.error("Failed to calculate transits")
    
    if st.session_state.transit_data:
        transit_data = st.session_state.transit_data
        
        st.markdown("---")
        st.subheader(f"Transits for {transit_data['date']}")
        
        # Afișează graficul transitelor
        if show_chart:
            fig = create_chart_wheel(transit_data, birth_data, "Transit Chart", show_aspect_lines)
            if fig:
                st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Transit Positions")
            display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                            'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
            
            for planet_name in display_order:
                if planet_name in transit_data['planets']:
                    planet_data = transit_data['planets'][planet_name]
                    st.write(f"**{planet_name}** {planet_data['position_str']}")
        
        with col2:
            st.subheader("🏠 Transit Houses")
            for house_num in range(1, 13):
                if house_num in transit_data['houses']:
                    house_data = transit_data['houses'][house_num]
                    st.write(f"**{house_num}** {house_data['position_str']}")
        
        # Afișează aspectele dintre transite și harta natală
        if show_aspects:
            st.markdown("---")
            st.subheader("🔗 Transit Aspects to Natal Chart")
            
            transit_aspects = calculate_transit_aspects(natal_chart, transit_data)
            
            if transit_aspects:
                aspect_data = []
                for i, aspect in enumerate(transit_aspects, 1):
                    aspect_data.append({
                        "#": f"{i:02d}",
                        "Natal Planet": aspect['natal_planet'],
                        "Transit Planet": aspect['transit_planet'],
                        "Aspect": aspect['aspect_name'],
                        "Orb": f"{aspect['orb']:.2f}°",
                        "Strength": aspect['strength']
                    })
                
                df = pd.DataFrame(aspect_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No significant transit aspects found.")

def display_progressions():
    st.header("📈 Progressed Chart")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate natal chart first!")
        return
    
    natal_chart = st.session_state.chart_data
    birth_data = st.session_state.birth_data
    
    st.subheader("Progression Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        progression_date = st.date_input("Select Progression Date", 
                                       datetime.now().date(),
                                       min_value=birth_data['date'],
                                       max_value=datetime(2100, 12, 31).date())
    
    with col2:
        progression_method = st.selectbox(
            "Progression Method",
            ["Secondary", "Solar Arc"],
            help="Secondary: 1 day = 1 year | Solar Arc: Based on Sun's movement"
        )
        show_aspect_lines = st.checkbox("Show Aspect Lines in Chart", value=True)
    
    if st.button("Calculate Progressions", type="primary"):
        with st.spinner("Calculating progressions..."):
            progressed_data = calculate_progressions(
                birth_data, 
                progression_date, 
                progression_method.lower().replace(' ', '_')
            )
            
            if progressed_data:
                st.session_state.progressed_data = progressed_data
                st.success(f"✅ Progressions calculated for {progression_date}")
            else:
                st.error("Failed to calculate progressions")
    
    if st.session_state.progressed_data:
        progressed_data = st.session_state.progressed_data
        
        st.markdown("---")
        st.subheader(f"Progressed Chart - {progressed_data['method']}")
        
        # Afișează graficul progresat
        fig = create_chart_wheel(progressed_data, birth_data, f"Progressed Chart - {progressed_data['method']}", show_aspect_lines)
        if fig:
            st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Progressed Positions")
            display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                            'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Nod', 'Chi']
            
            for planet_name in display_order:
                if planet_name in progressed_data['planets']:
                    planet_data = progressed_data['planets'][planet_name]
                    st.write(f"**{planet_name}** {planet_data['position_str']}")
            
            if 'solar_arc' in progressed_data:
                st.info(f"Solar Arc: {progressed_data['solar_arc']:.2f}°")
        
        with col2:
            st.subheader("🏠 Progressed Houses")
            for house_num in range(1, 13):
                if house_num in progressed_data['houses']:
                    house_data = progressed_data['houses'][house_num]
                    st.write(f"**{house_num}** {house_data['position_str']}")
        
        # Afișează aspectele dintre harta progresată și natală
        st.markdown("---")
        st.subheader("🔗 Progressed Aspects to Natal Chart")
        
        progressed_aspects = calculate_transit_aspects(natal_chart, progressed_data)
        
        if progressed_aspects:
            aspect_data = []
            for i, aspect in enumerate(progressed_aspects, 1):
                aspect_data.append({
                    "#": f"{i:02d}",
                    "Natal Planet": aspect['natal_planet'],
                    "Progressed Planet": aspect['transit_planet'],
                    "Aspect": aspect['aspect_name'],
                    "Orb": f"{aspect['orb']:.2f}°",
                    "Strength": aspect['strength']
                })
            
            df = pd.DataFrame(aspect_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No significant progressed aspects found.")

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
        ["Natal", "Career", "Relationships", "Spiritual", "Sexual"]
    )
    
    st.markdown("---")
    st.subheader(f"Interpretation: {interpretation_type}")
    
    display_complete_interpretations(chart_data, interpretation_type)

def display_complete_interpretations(chart_data, interpretation_type):
    """Afișează interpretări complete pentru toate planetele și gradele"""
    
    # INTERPRETĂRI COMPLETE PENTRU SEMNE - NATAL (EXTINS)
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
        },
        "Mercury": {
            "TAU": "Thorough, persevering. Good at working with the hands. Inflexible, steady, obstinate, self-opinionated, conventional, limited in interests.",
            "ARI": "Quick-thinking, direct, innovative. Expresses ideas boldly and spontaneously.",
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
            "ARI": "Enthusiastic, confident, generous. Natural leadership abilities.",
            "TAU": "Practical, steady growth. Values material security and comfort.",
            "GEM": "Curious, communicative, versatile. Expands through learning and connections.",
            "CAN": "Nurturing, protective growth. Expands family and home life.",
            "VIR": "Analytical, service-oriented growth. Improves through attention to detail.",
            "LIB": "Harmonious, diplomatic expansion. Grows through relationships and beauty.",
            "SCO": "Intense, transformative growth. Expands through deep investigation.",
            "SAG": "Philosophical, adventurous expansion. Seeks truth and meaning.",
            "CAP": "Ambitious, disciplined growth. Builds lasting structures and authority.",
            "AQU": "Innovative, humanitarian expansion. Progress through originality.",
            "PIS": "Compassionate, spiritual growth. Expands through intuition and service."
        },
        "Saturn": {
            "SAG": "Upright, open, courageous, honourable, grave, dignified, very capable.",
            "ARI": "Ambitious, disciplined pioneer. Builds structures with initiative.",
            "TAU": "Practical, patient builder. Creates lasting material security.",
            "GEM": "Serious, organized communicator. Structures thinking and learning.",
            "CAN": "Responsible, protective authority. Builds family traditions.",
            "LEO": "Dignified, authoritative leader. Structures creative expression.",
            "VIR": "Precise, efficient organizer. Creates order through service.",
            "LIB": "Balanced, diplomatic judge. Structures relationships fairly.",
            "SCO": "Intense, transformative discipline. Builds through deep investigation.",
            "CAP": "Ambitious, responsible builder. Creates lasting institutions.",
            "AQU": "Innovative, disciplined reformer. Structures progressive ideas.",
            "PIS": "Compassionate, spiritual discipline. Builds through faith."
        },
        "Uranus": {
            "CAN": "Rather passive, compassionate, sensitive, impressionable, intuitive.",
            "ARI": "Innovative, independent pioneer. Sudden changes and breakthroughs.",
            "TAU": "Unconventional values and financial ideas. Slow but revolutionary change.",
            "GEM": "Revolutionary thinking and communication. Sudden insights.",
            "LEO": "Creative innovation and dramatic self-expression.",
            "VIR": "Unconventional approaches to health and service.",
            "LIB": "Revolutionary relationships and artistic expression.",
            "SCO": "Transformative insights and psychological breakthroughs.",
            "SAG": "Philosophical innovation and expansion of consciousness.",
            "CAP": "Structural reforms and institutional changes.",
            "AQU": "Humanitarian vision and technological innovation.",
            "PIS": "Spiritual insights and mystical revelations."
        },
        "Neptune": {
            "LIB": "Idealistic, often a bit out of touch with reality. Has only a hazy view & understanding of real life & the world.",
            "ARI": "Spiritual pioneering and inspired action.",
            "TAU": "Dreamy values and idealized security.",
            "GEM": "Imaginative communication and inspired ideas.",
            "CAN": "Mystical home life and spiritual nurturing.",
            "LEO": "Creative inspiration and dramatic spirituality.",
            "VIR": "Service through inspiration and healing.",
            "SCO": "Deep spiritual transformation and psychic sensitivity.",
            "SAG": "Philosophical idealism and spiritual expansion.",
            "CAP": "Structured spirituality and institutional faith.",
            "AQU": "Collective ideals and humanitarian dreams.",
            "PIS": "Spiritual connection and mystical understanding."
        },
        "Pluto": {
            "LEO": "Strong creative desires. Uncontrollable sexual appetite. Determined to win.",
            "ARI": "Transformative initiative and rebirth through action.",
            "TAU": "Deep financial transformation and value regeneration.",
            "GEM": "Psychological communication and mental transformation.",
            "CAN": "Emotional rebirth and family transformation.",
            "VIR": "Service transformation and health regeneration.",
            "LIB": "Relationship transformation and artistic rebirth.",
            "SCO": "Deep psychological transformation and rebirth.",
            "SAG": "Philosophical transformation and belief regeneration.",
            "CAP": "Structural transformation and power rebirth.",
            "AQU": "Collective transformation and social regeneration.",
            "PIS": "Spiritual transformation and mystical rebirth."
        }
    }

    # INTERPRETĂRI SPECIFICE PENTRU CAREER (EXTINSE)
    career_interpretations = {
        "Sun": {
            "ARI": "Natural entrepreneur and pioneer. Thrives in competitive environments. Excellent at starting new projects.",
            "TAU": "Steady and reliable worker. Excellent in finance, real estate, and stable professions.",
            "GEM": "Communicator and networker. Excels in sales, teaching, writing, and multi-tasking roles.",
            "CAN": "Nurturing careers in healthcare, education, hospitality. Strong in family businesses.",
            "LEO": "Natural leader and performer. Thrives in management, entertainment, and creative fields.",
            "VIR": "Analytical and detail-oriented. Excellent in research, accounting, healthcare, and service industries.",
            "LIB": "Diplomatic and artistic. Successful in law, design, public relations, and partnership-based businesses.",
            "SCO": "Intense and investigative. Excels in research, psychology, finance, and transformative roles.",
            "SAG": "Adventurous and philosophical. Thrives in travel, education, publishing, and international business.",
            "CAP": "Ambitious and disciplined. Natural executive material. Excels in corporate leadership and long-term planning.",
            "AQU": "Innovative and humanitarian. Successful in technology, science, social work, and progressive fields.",
            "PIS": "Compassionate and creative. Excels in arts, healing professions, spirituality, and service-oriented work."
        },
        "Moon": {
            "ARI": "Career success through initiative and emotional drive. Needs variety and challenge.",
            "TAU": "Stable career growth through persistence. Values financial security and comfort.",
            "GEM": "Versatile career with multiple interests. Success in communication and networking.",
            "CAN": "Career tied to emotional security. Success in nurturing and protective roles.",
            "LEO": "Career recognition through creative expression. Needs appreciation and leadership roles.",
            "VIR": "Career excellence through attention to detail. Success in service and analytical work.",
            "LIB": "Career success through partnerships and diplomacy. Values harmony and beauty.",
            "SCO": "Career transformation through intense focus. Success in research and investigative work.",
            "SAG": "Career expansion through adventure and learning. Philosophical approach to work.",
            "CAP": "Career ambition through emotional discipline. Builds professional reputation carefully.",
            "AQU": "Innovative career through unique emotional expression. Progressive work environments.",
            "PIS": "Compassionate career through intuitive service. Success in healing and creative fields."
        },
        "Mercury": {
            "ARI": "Quick-thinking and innovative in career. Excellent at starting projects and initiatives.",
            "TAU": "Practical and persistent communicator. Success in finance and stable professions.",
            "GEM": "Versatile and adaptable in career. Excels in multi-tasking and communication roles.",
            "CAN": "Intuitive and emotional thinking. Success in nurturing and memory-oriented work.",
            "LEO": "Confident and creative communication. Leadership in expressive and authoritative roles.",
            "VIR": "Analytical and precise thinking. Excellence in detail-oriented and service work.",
            "LIB": "Diplomatic and balanced communication. Success in partnership-based businesses.",
            "SCO": "Investigative and profound thinking. Excellence in research and transformative work.",
            "SAG": "Philosophical and broad-minded thinking. Success in education and expansive fields.",
            "CAP": "Organized and ambitious thinking. Strategic planning and long-term career goals.",
            "AQU": "Innovative and original thinking. Success in technology and progressive fields.",
            "PIS": "Intuitive and imaginative thinking. Excellence in creative and compassionate work."
        },
        "Venus": {
            "ARI": "Direct approach to career values. Success in competitive and pioneering fields.",
            "TAU": "Stable and sensual career values. Excellence in finance and comfort-oriented work.",
            "GEM": "Versatile and communicative values. Success in networking and multi-faceted roles.",
            "CAN": "Nurturing and protective values. Career success through emotional security.",
            "LEO": "Generous and dramatic values. Success in creative and recognition-based work.",
            "VIR": "Practical and helpful values. Excellence in service and detail-oriented professions.",
            "LIB": "Harmonious and artistic values. Success in partnerships and beauty-related fields.",
            "SCO": "Intense and passionate values. Career transformation through deep commitment.",
            "SAG": "Adventurous and expansive values. Success in travel and philosophical work.",
            "CAP": "Serious and responsible values. Long-term career stability and achievement.",
            "AQU": "Unconventional and friendly values. Success in innovative and social fields.",
            "PIS": "Compassionate and romantic values. Excellence in creative and healing professions."
        },
        "Mars": {
            "ARI": "Energetic and competitive career drive. Natural pioneer and initiator.",
            "TAU": "Persistent and determined work ethic. Slow but steady career growth.",
            "GEM": "Versatile and communicative action. Success in multi-tasking roles.",
            "CAN": "Protective and emotional drive. Career success through nurturing actions.",
            "LEO": "Confident and dramatic initiative. Leadership in creative fields.",
            "VIR": "Precise and analytical action. Excellence in detail-oriented work.",
            "LIB": "Diplomatic and balanced drive. Success through partnership and harmony.",
            "SCO": "Intense and transformative action. Power in investigative work.",
            "SAG": "Adventurous and optimistic drive. Success through expansion and learning.",
            "CAP": "Ambitious and disciplined action. Strategic career advancement.",
            "AQU": "Innovative and independent drive. Success in progressive fields.",
            "PIS": "Compassionate and intuitive action. Success through inspired service."
        },
        "Jupiter": {
            "ARI": "Expansive career through initiative. Natural leadership and confidence.",
            "TAU": "Steady growth through persistence. Financial expansion and security.",
            "GEM": "Versatile expansion through communication. Success in learning and teaching.",
            "CAN": "Nurturing growth through emotional security. Family business success.",
            "LEO": "Creative expansion through recognition. Leadership in expressive fields.",
            "VIR": "Analytical growth through service. Improvement through attention to detail.",
            "LIB": "Harmonious expansion through partnerships. Success in artistic fields.",
            "SCO": "Transformative growth through investigation. Deep professional development.",
            "SAG": "Philosophical expansion through adventure. Natural teacher and explorer.",
            "CAP": "Ambitious growth through discipline. Long-term career building.",
            "AQU": "Innovative expansion through originality. Success in technology fields.",
            "PIS": "Compassionate growth through intuition. Success in healing and arts."
        },
        "Saturn": {
            "ARI": "Career discipline through initiative. Learning responsibility through risk-taking.",
            "TAU": "Stable career structure through persistence. Financial responsibility.",
            "GEM": "Organized communication skills. Responsibility in teaching and writing.",
            "CAN": "Emotional career responsibility. Building family security.",
            "LEO": "Creative leadership responsibility. Structured self-expression.",
            "VIR": "Analytical service discipline. Excellence through attention to detail.",
            "LIB": "Partnership responsibility. Balanced professional relationships.",
            "SCO": "Transformative discipline. Deep professional commitment.",
            "SAG": "Philosophical responsibility. Structured expansion and learning.",
            "CAP": "Natural career ambition and discipline. Built for professional success.",
            "AQU": "Innovative responsibility. Structured progressive thinking.",
            "PIS": "Compassionate discipline. Structured service and creativity."
        },
        "Uranus": {
            "ARI": "Innovative career breakthroughs. Pioneering new professional fields.",
            "TAU": "Unconventional financial ideas. Slow but revolutionary changes.",
            "GEM": "Revolutionary communication. Sudden insights in networking.",
            "CAN": "Innovative emotional security. New approaches to nurturing work.",
            "LEO": "Creative breakthroughs. Unique self-expression in career.",
            "VIR": "Unconventional service approaches. Innovative health and analysis.",
            "LIB": "Revolutionary partnerships. New approaches to artistic work.",
            "SCO": "Transformative insights. Psychological breakthroughs in career.",
            "SAG": "Philosophical innovation. Expanding consciousness in work.",
            "CAP": "Structural reforms. Institutional changes in career.",
            "AQU": "Natural innovator. Humanitarian vision in technology.",
            "PIS": "Spiritual insights. Mystical revelations in creative work."
        },
        "Neptune": {
            "ARI": "Spiritual pioneering in career. Inspired action and vision.",
            "TAU": "Dreamy financial values. Idealized security and comfort.",
            "GEM": "Imaginative communication. Inspired ideas and networking.",
            "CAN": "Mystical emotional security. Spiritual nurturing in work.",
            "LEO": "Creative inspiration. Dramatic spiritual expression.",
            "VIR": "Service through inspiration. Healing and analytical compassion.",
            "LIB": "Harmonious ideals. Spiritual partnerships and beauty.",
            "SCO": "Deep spiritual transformation. Psychic sensitivity in work.",
            "SAG": "Philosophical idealism. Spiritual expansion and learning.",
            "CAP": "Structured spirituality. Institutional faith in career.",
            "AQU": "Collective ideals. Humanitarian dreams and vision.",
            "PIS": "Natural mystic. Spiritual connection in creative work."
        },
        "Pluto": {
            "ARI": "Transformative career initiative. Rebirth through action.",
            "TAU": "Deep financial transformation. Value regeneration in work.",
            "GEM": "Psychological communication. Mental transformation in career.",
            "CAN": "Emotional career rebirth. Family transformation.",
            "LEO": "Creative transformation. Rebirth through self-expression.",
            "VIR": "Service transformation. Health regeneration in work.",
            "LIB": "Relationship transformation. Artistic rebirth in career.",
            "SCO": "Deep psychological transformation. Natural rebirth in work.",
            "SAG": "Philosophical transformation. Belief regeneration.",
            "CAP": "Structural transformation. Power rebirth in institutions.",
            "AQU": "Collective transformation. Social regeneration.",
            "PIS": "Spiritual transformation. Mystical rebirth in work."
        }
    }

    # INTERPRETĂRI SPECIFICE PENTRU RELATIONSHIPS (EXTINSE)
    relationships_interpretations = {
        "Sun": {
            "ARI": "Direct and passionate in relationships. Natural leader who values independence.",
            "TAU": "Loyal and stable partner. Values security and physical comfort in relationships.",
            "GEM": "Communicative and curious in love. Needs mental stimulation and variety.",
            "CAN": "Nurturing and protective partner. Strong family orientation and emotional bonds.",
            "LEO": "Generous and dramatic in relationships. Needs admiration and recognition.",
            "VIR": "Practical and helpful partner. Shows love through service and attention.",
            "LIB": "Harmonious and diplomatic. Seeks balance and partnership in relationships.",
            "SCO": "Intense and passionate. Seeks deep emotional transformation in love.",
            "SAG": "Adventurous and philosophical. Values freedom and honesty in relationships.",
            "CAP": "Serious and responsible partner. Seeks stability and long-term commitment.",
            "AQU": "Independent and unconventional. Values friendship and intellectual connection.",
            "PIS": "Compassionate and romantic. Seeks spiritual connection and soulmates."
        },
        "Moon": {
            "ARI": "Emotionally direct and passionate. Needs independence and excitement in relationships.",
            "TAU": "Emotionally stable and loyal. Values security and physical comfort.",
            "GEM": "Emotionally communicative and curious. Needs mental connection and variety.",
            "CAN": "Deeply nurturing and protective. Strong emotional bonds and family orientation.",
            "LEO": "Emotionally generous and proud. Needs recognition and appreciation.",
            "VIR": "Emotionally practical and helpful. Shows care through service and attention.",
            "LIB": "Emotionally harmonious and diplomatic. Seeks balance and partnership.",
            "SCO": "Emotionally intense and passionate. Deep emotional connections and transformation.",
            "SAG": "Emotionally adventurous and optimistic. Needs freedom and philosophical connection.",
            "CAP": "Emotionally responsible and reserved. Controls feelings carefully.",
            "AQU": "Emotionally independent and unconventional. Unique emotional expression.",
            "PIS": "Emotionally compassionate and intuitive. Deep spiritual connections."
        },
        "Mercury": {
            "ARI": "Direct and spontaneous communication. Expresses love ideas boldly.",
            "TAU": "Practical and persistent communication. Values stable and honest dialogue.",
            "GEM": "Versatile and curious communication. Needs mental stimulation in relationships.",
            "CAN": "Intuitive and emotional communication. Thinks with heart and memory.",
            "LEO": "Confident and dramatic communication. Expresses love with flair.",
            "VIR": "Analytical and precise communication. Shows care through thoughtful words.",
            "LIB": "Diplomatic and balanced communication. Seeks harmony in dialogue.",
            "SCO": "Investigative and profound communication. Seeks deep truth in relationships.",
            "SAG": "Philosophical and honest communication. Values expansive discussions.",
            "CAP": "Practical and organized communication. Builds relationships carefully.",
            "AQU": "Innovative and original communication. Unique way of expressing love.",
            "PIS": "Intuitive and compassionate communication. Romantic and dreamy expression."
        },
        "Venus": {
            "ARI": "Direct and passionate in love. Attracted to challenge and excitement.",
            "TAU": "Sensual and loyal partner. Values stability and physical pleasure.",
            "GEM": "Playful and communicative in relationships. Needs mental connection.",
            "CAN": "Nurturing and protective. Seeks emotional security and deep bonding.",
            "LEO": "Generous and dramatic in love. Needs romance and admiration.",
            "VIR": "Practical and helpful partner. Shows love through service and care.",
            "LIB": "Harmonious and artistic. Seeks balance and partnership in love.",
            "SCO": "Intense and passionate. Seeks deep emotional bonds and transformation.",
            "SAG": "Adventurous and freedom-loving. Values honesty and philosophical connection.",
            "CAP": "Serious and responsible. Seeks stability and long-term commitment.",
            "AQU": "Unconventional and friendly. Values independence and intellectual connection.",
            "PIS": "Romantic and compassionate. Seeks spiritual connection and soulmates."
        },
        "Mars": {
            "ARI": "Direct and passionate pursuit. Competitive and enthusiastic in relationships.",
            "TAU": "Persistent and determined approach. Slow but steady in building love.",
            "GEM": "Playful and communicative action. Enjoys mental stimulation in partnerships.",
            "CAN": "Protective and emotional drive. Actions driven by deep feelings.",
            "LEO": "Confident and dramatic pursuit. Generous and proud in relationships.",
            "VIR": "Practical and helpful approach. Shows care through service.",
            "LIB": "Diplomatic and balanced action. Seeks harmony and partnership.",
            "SCO": "Intense and transformative approach. Powerful and determined in love.",
            "SAG": "Adventurous and optimistic pursuit. Values freedom and honesty.",
            "CAP": "Ambitious and disciplined approach. Builds relationships carefully.",
            "AQU": "Innovative and independent action. Unconventional approach to love.",
            "PIS": "Compassionate and intuitive pursuit. Romantic and dreamy approach."
        },
        "Jupiter": {
            "ARI": "Expansive and confident in relationships. Natural optimism and enthusiasm.",
            "TAU": "Steady growth in love. Values security and comfort expansion.",
            "GEM": "Versatile expansion through communication. Enjoys learning in partnerships.",
            "CAN": "Nurturing growth through emotional security. Family-oriented expansion.",
            "LEO": "Creative expansion through recognition. Generous and warm-hearted.",
            "VIR": "Analytical growth through service. Improvement in practical love.",
            "LIB": "Harmonious expansion through partnerships. Seeks beauty and balance.",
            "SCO": "Transformative growth through depth. Philosophical approach to intimacy.",
            "SAG": "Natural expansion through adventure. Optimistic and freedom-loving.",
            "CAP": "Ambitious growth through discipline. Builds long-term relationships.",
            "AQU": "Innovative expansion through originality. Progressive relationship values.",
            "PIS": "Compassionate growth through intuition. Spiritual connection in love."
        },
        "Saturn": {
            "ARI": "Disciplined approach to relationships. Learning responsibility through independence.",
            "TAU": "Stable and persistent in love. Builds security through commitment.",
            "GEM": "Organized communication in relationships. Responsibility in dialogue.",
            "CAN": "Emotional responsibility in love. Building family security.",
            "LEO": "Creative leadership responsibility. Structured self-expression in relationships.",
            "VIR": "Analytical service discipline. Practical approach to love.",
            "LIB": "Partnership responsibility. Balanced and committed relationships.",
            "SCO": "Transformative discipline. Deep commitment in intimate relationships.",
            "SAG": "Philosophical responsibility. Structured expansion in love.",
            "CAP": "Natural responsibility in relationships. Built for long-term commitment.",
            "AQU": "Innovative responsibility. Structured progressive relationship values.",
            "PIS": "Compassionate discipline. Structured spiritual connection."
        },
        "Uranus": {
            "ARI": "Innovative relationship breakthroughs. Pioneering new forms of partnership.",
            "TAU": "Unconventional values in love. Slow but revolutionary changes.",
            "GEM": "Revolutionary communication. Sudden insights in relationships.",
            "CAN": "Innovative emotional security. New approaches to family and nurturing.",
            "LEO": "Creative breakthroughs in love. Unique self-expression.",
            "VIR": "Unconventional service approaches. Innovative practical care.",
            "LIB": "Revolutionary partnerships. New approaches to balance and harmony.",
            "SCO": "Transformative insights. Psychological breakthroughs in intimacy.",
            "SAG": "Philosophical innovation. Expanding consciousness in relationships.",
            "CAP": "Structural reforms. Institutional changes in partnership.",
            "AQU": "Natural innovator in relationships. Humanitarian vision in love.",
            "PIS": "Spiritual insights. Mystical revelations in romantic connections."
        },
        "Neptune": {
            "ARI": "Spiritual pioneering in relationships. Inspired action and vision in love.",
            "TAU": "Dreamy values in partnerships. Idealized security and comfort.",
            "GEM": "Imaginative communication. Inspired ideas in relationships.",
            "CAN": "Mystical emotional security. Spiritual nurturing in love.",
            "LEO": "Creative inspiration. Dramatic spiritual expression in relationships.",
            "VIR": "Service through inspiration. Healing and compassionate care.",
            "LIB": "Harmonious ideals. Spiritual partnerships and beauty.",
            "SCO": "Deep spiritual transformation. Psychic sensitivity in intimacy.",
            "SAG": "Philosophical idealism. Spiritual expansion in relationships.",
            "CAP": "Structured spirituality. Institutional faith in partnership.",
            "AQU": "Collective ideals. Humanitarian dreams in love.",
            "PIS": "Natural mystic. Spiritual connection in romantic relationships."
        },
        "Pluto": {
            "ARI": "Transformative relationship initiative. Rebirth through passionate action.",
            "TAU": "Deep value transformation. Regeneration of security in love.",
            "GEM": "Psychological communication. Mental transformation in relationships.",
            "CAN": "Emotional rebirth in partnerships. Family transformation.",
            "LEO": "Creative transformation. Rebirth through self-expression in love.",
            "VIR": "Service transformation. Health regeneration in relationships.",
            "LIB": "Relationship transformation. Artistic rebirth in partnership.",
            "SCO": "Deep psychological transformation. Natural rebirth in intimacy.",
            "SAG": "Philosophical transformation. Belief regeneration in love.",
            "CAP": "Structural transformation. Power rebirth in committed relationships.",
            "AQU": "Collective transformation. Social regeneration in partnerships.",
            "PIS": "Spiritual transformation. Mystical rebirth in romantic connections."
        }
    }

    # INTERPRETĂRI SPECIFICE PENTRU SPIRITUAL (EXTINSE)
    spiritual_interpretations = {
        "Sun": {
            "ARI": "Spiritual pioneer and warrior. Direct connection to divine energy.",
            "TAU": "Grounded spirituality. Connection to earth energies and practical mysticism.",
            "GEM": "Communicative spirituality. Channel for divine messages and teachings.",
            "CAN": "Nurturing spiritual path. Connection to ancestral wisdom and emotional healing.",
            "LEO": "Creative spirituality. Divine expression through art and performance.",
            "VIR": "Service-oriented spirituality. Healing through practical service and analysis.",
            "LIB": "Harmonious spirituality. Connection to beauty, balance, and divine partnership.",
            "SCO": "Transformative spirituality. Deep psychic abilities and rebirth.",
            "SAG": "Philosophical spirituality. Expansion through truth-seeking and adventure.",
            "CAP": "Structured spirituality. Building spiritual foundations and discipline.",
            "AQU": "Innovative spirituality. Connection to collective consciousness and futurism.",
            "PIS": "Compassionate spirituality. Deep connection to universal love and mercy."
        },
        "Moon": {
            "ARI": "Emotional spiritual pioneer. Direct intuitive connection to divine.",
            "TAU": "Grounded emotional spirituality. Practical mystical experiences.",
            "GEM": "Communicative emotional spirituality. Learning and teaching spiritual concepts.",
            "CAN": "Nurturing emotional path. Connection to ancestral spiritual wisdom.",
            "LEO": "Creative emotional spirituality. Dramatic spiritual expression.",
            "VIR": "Service-oriented emotional spirituality. Healing through practical compassion.",
            "LIB": "Harmonious emotional spirituality. Balanced spiritual partnerships.",
            "SCO": "Transformative emotional spirituality. Deep psychic emotional connections.",
            "SAG": "Philosophical emotional spirituality. Expansion through emotional truth.",
            "CAP": "Structured emotional spirituality. Disciplined emotional spiritual practice.",
            "AQU": "Innovative emotional spirituality. Progressive spiritual emotions.",
            "PIS": "Compassionate emotional spirituality. Deep spiritual emotional connections."
        },
        "Mercury": {
            "ARI": "Direct spiritual communication. Pioneering spiritual ideas and concepts.",
            "TAU": "Practical spiritual thinking. Grounded mystical communication.",
            "GEM": "Versatile spiritual communication. Learning and teaching divine wisdom.",
            "CAN": "Intuitive spiritual thinking. Emotional connection to spiritual concepts.",
            "LEO": "Creative spiritual communication. Expressive divine teachings.",
            "VIR": "Analytical spiritual thinking. Service-oriented spiritual analysis.",
            "LIB": "Harmonious spiritual communication. Balanced spiritual dialogue.",
            "SCO": "Transformative spiritual thinking. Deep psychological spiritual insights.",
            "SAG": "Philosophical spiritual communication. Expansive spiritual learning.",
            "CAP": "Structured spiritual thinking. Organized spiritual concepts.",
            "AQU": "Innovative spiritual communication. Progressive spiritual ideas.",
            "PIS": "Intuitive spiritual thinking. Compassionate spiritual insights."
        },
        "Venus": {
            "ARI": "Direct spiritual values. Pioneering approach to divine love.",
            "TAU": "Grounded spiritual values. Practical mystical appreciation.",
            "GEM": "Communicative spiritual values. Learning through spiritual relationships.",
            "CAN": "Nurturing spiritual values. Emotional connection to divine love.",
            "LEO": "Creative spiritual values. Expressive divine beauty.",
            "VIR": "Service-oriented spiritual values. Practical spiritual harmony.",
            "LIB": "Harmonious spiritual values. Balanced divine partnerships.",
            "SCO": "Transformative spiritual values. Deep psychological spiritual connections.",
            "SAG": "Philosophical spiritual values. Expansive spiritual appreciation.",
            "CAP": "Structured spiritual values. Disciplined spiritual love.",
            "AQU": "Innovative spiritual values. Progressive spiritual relationships.",
            "PIS": "Compassionate spiritual values. Deep connection to universal love."
        },
        "Mars": {
            "ARI": "Direct spiritual action. Pioneering spiritual initiatives.",
            "TAU": "Grounded spiritual drive. Practical mystical persistence.",
            "GEM": "Communicative spiritual action. Learning through spiritual doing.",
            "CAN": "Nurturing spiritual drive. Emotional spiritual protection.",
            "LEO": "Creative spiritual action. Expressive spiritual leadership.",
            "VIR": "Service-oriented spiritual drive. Practical spiritual service.",
            "LIB": "Harmonious spiritual action. Balanced spiritual partnerships.",
            "SCO": "Transformative spiritual drive. Deep psychological spiritual power.",
            "SAG": "Philosophical spiritual action. Expansive spiritual adventure.",
            "CAP": "Structured spiritual drive. Disciplined spiritual work.",
            "AQU": "Innovative spiritual action. Progressive spiritual initiatives.",
            "PIS": "Compassionate spiritual drive. Inspired spiritual service."
        },
        "Jupiter": {
            "ARI": "Expansive spiritual seeking. Philosophical exploration and truth-seeking.",
            "TAU": "Grounded spiritual growth. Expansion through practical wisdom.",
            "GEM": "Communicative spirituality. Learning and teaching spiritual concepts.",
            "CAN": "Nurturing spiritual path. Expansion through emotional wisdom.",
            "LEO": "Creative spiritual expression. Expansion through divine creativity.",
            "VIR": "Service-oriented spirituality. Growth through healing and analysis.",
            "LIB": "Harmonious spiritual path. Expansion through beauty and partnership.",
            "SCO": "Transformative spiritual growth. Expansion through deep investigation.",
            "SAG": "Natural spiritual seeker. Philosophical expansion and adventure.",
            "CAP": "Structured spiritual growth. Expansion through discipline and tradition.",
            "AQU": "Innovative spirituality. Expansion through universal consciousness.",
            "PIS": "Compassionate spiritual path. Expansion through universal love."
        },
        "Saturn": {
            "ARI": "Spiritual discipline through initiative. Learning responsibility through risk.",
            "TAU": "Grounded spiritual structure. Practical mystical discipline.",
            "GEM": "Organized spiritual communication. Responsibility in teaching wisdom.",
            "CAN": "Emotional spiritual responsibility. Building family spiritual security.",
            "LEO": "Creative spiritual leadership. Structured divine expression.",
            "VIR": "Analytical spiritual service. Discipline in healing work.",
            "LIB": "Partnership spiritual responsibility. Balanced spiritual commitments.",
            "SCO": "Transformative spiritual discipline. Deep psychological commitment.",
            "SAG": "Philosophical spiritual responsibility. Structured expansion.",
            "CAP": "Natural spiritual discipline. Built for spiritual mastery.",
            "AQU": "Innovative spiritual responsibility. Structured progressive thinking.",
            "PIS": "Compassionate spiritual discipline. Structured universal love."
        },
        "Uranus": {
            "ARI": "Innovative spiritual breakthroughs. Pioneering new spiritual paths.",
            "TAU": "Unconventional spiritual values. Slow but revolutionary changes.",
            "GEM": "Revolutionary spiritual communication. Sudden spiritual insights.",
            "CAN": "Innovative emotional spirituality. New approaches to nurturing.",
            "LEO": "Creative spiritual breakthroughs. Unique divine expression.",
            "VIR": "Unconventional service spirituality. Innovative healing approaches.",
            "LIB": "Revolutionary spiritual partnerships. New approaches to harmony.",
            "SCO": "Transformative spiritual insights. Psychological breakthroughs.",
            "SAG": "Philosophical spiritual innovation. Expanding consciousness.",
            "CAP": "Structural spiritual reforms. Institutional changes in spirituality.",
            "AQU": "Natural spiritual innovator. Humanitarian spiritual vision.",
            "PIS": "Spiritual insights and revelations. Mystical breakthroughs."
        },
        "Neptune": {
            "ARI": "Spiritual pioneering and vision. Inspired action and divine connection.",
            "TAU": "Grounded spiritual dreams. Practical mystical ideals.",
            "GEM": "Communicative spiritual inspiration. Learning through divine messages.",
            "CAN": "Nurturing spiritual dreams. Emotional connection to universal love.",
            "LEO": "Creative spiritual inspiration. Dramatic divine expression.",
            "VIR": "Service-oriented spiritual dreams. Healing through inspired compassion.",
            "LIB": "Harmonious spiritual ideals. Balanced divine partnerships.",
            "SCO": "Transformative spiritual dreams. Deep psychic connections.",
            "SAG": "Philosophical spiritual ideals. Expansive spiritual vision.",
            "CAP": "Structured spiritual dreams. Institutional faith and discipline.",
            "AQU": "Collective spiritual ideals. Humanitarian dreams and vision.",
            "PIS": "Natural spiritual mystic. Deep connection to universal consciousness."
        },
        "Pluto": {
            "ARI": "Transformative spiritual initiative. Rebirth through divine action.",
            "TAU": "Deep spiritual value transformation. Regeneration of earthly spirituality.",
            "GEM": "Psychological spiritual communication. Mental transformation through wisdom.",
            "CAN": "Emotional spiritual rebirth. Family and ancestral transformation.",
            "LEO": "Creative spiritual transformation. Rebirth through divine expression.",
            "VIR": "Service spiritual transformation. Health and healing regeneration.",
            "LIB": "Relationship spiritual transformation. Artistic divine rebirth.",
            "SCO": "Deep psychological spiritual transformation. Natural rebirth and power.",
            "SAG": "Philosophical spiritual transformation. Belief regeneration and expansion.",
            "CAP": "Structural spiritual transformation. Power rebirth in institutions.",
            "AQU": "Collective spiritual transformation. Social and humanitarian regeneration.",
            "PIS": "Complete spiritual transformation. Ultimate surrender and enlightenment."
        }
    }

    # INTERPRETĂRI PENTRU SEXUAL (EXTINSE)
    sexual_interpretations = {
        "Sun": {
            "ARI": "Direct and passionate sexual energy. Natural initiator and explorer.",
            "TAU": "Sensual and persistent sexual nature. Values physical pleasure and stability.",
            "GEM": "Playful and communicative sexuality. Enjoys variety and mental stimulation.",
            "CAN": "Nurturing and emotional sexual nature. Deep emotional connections in intimacy.",
            "LEO": "Dramatic and generous sexuality. Needs admiration and creative expression.",
            "VIR": "Practical and attentive lover. Shows care through service and attention.",
            "LIB": "Harmonious and artistic sexuality. Values beauty and partnership.",
            "SCO": "Intense and transformative sexual energy. Deep psychological connections.",
            "SAG": "Adventurous and optimistic sexuality. Values freedom and exploration.",
            "CAP": "Disciplined and ambitious sexual nature. Builds intimacy carefully.",
            "AQU": "Innovative and unconventional sexuality. Experimental and freedom-loving.",
            "PIS": "Compassionate and intuitive sexuality. Spiritual and romantic connections."
        },
        "Moon": {
            "ARI": "Emotionally direct and passionate. Needs excitement and independence.",
            "TAU": "Emotionally stable and sensual. Values security and physical comfort.",
            "GEM": "Emotionally communicative and curious. Needs mental connection.",
            "CAN": "Deeply nurturing and emotional. Strong emotional bonds in intimacy.",
            "LEO": "Emotionally generous and proud. Needs recognition and appreciation.",
            "VIR": "Emotionally practical and helpful. Shows care through attention.",
            "LIB": "Emotionally harmonious and diplomatic. Seeks balance in intimacy.",
            "SCO": "Emotionally intense and passionate. Deep emotional transformation.",
            "SAG": "Emotionally adventurous and optimistic. Needs freedom and exploration.",
            "CAP": "Emotionally responsible and reserved. Controls feelings carefully.",
            "AQU": "Emotionally independent and unconventional. Unique emotional expression.",
            "PIS": "Emotionally compassionate and intuitive. Deep spiritual connections."
        },
        "Mercury": {
            "ARI": "Direct and spontaneous sexual communication. Expresses desires boldly.",
            "TAU": "Practical and persistent communication. Values honest and stable dialogue.",
            "GEM": "Playful and curious communication. Enjoys mental stimulation.",
            "CAN": "Intuitive and emotional communication. Expresses with heart and memory.",
            "LEO": "Confident and dramatic communication. Expressive and authoritative.",
            "VIR": "Analytical and precise communication. Thoughtful and attentive words.",
            "LIB": "Diplomatic and balanced communication. Seeks harmony in dialogue.",
            "SCO": "Investigative and profound communication. Seeks deep truth.",
            "SAG": "Philosophical and honest communication. Values expansive discussions.",
            "CAP": "Practical and organized communication. Builds intimacy carefully.",
            "AQU": "Innovative and original communication. Unique way of expressing desires.",
            "PIS": "Intuitive and compassionate communication. Romantic and dreamy expression."
        },
        "Venus": {
            "ARI": "Direct and passionate in love. Attracted to challenge and excitement.",
            "TAU": "Sensual and loyal. Values stability and physical pleasure.",
            "GEM": "Playful and communicative. Needs mental connection and variety.",
            "CAN": "Nurturing and emotional. Seeks security and deep bonding.",
            "LEO": "Generous and dramatic. Needs romance and admiration.",
            "VIR": "Practical and helpful. Shows love through service and care.",
            "LIB": "Harmonious and artistic. Seeks balance and partnership.",
            "SCO": "Intense and passionate. Seeks deep emotional transformation.",
            "SAG": "Adventurous and freedom-loving. Values honesty and exploration.",
            "CAP": "Serious and responsible. Seeks stability and commitment.",
            "AQU": "Unconventional and friendly. Values independence and intellectual connection.",
            "PIS": "Romantic and compassionate. Seeks spiritual connection."
        },
        "Mars": {
            "ARI": "Passionate and direct sexual energy. Enthusiastic and competitive.",
            "TAU": "Sensual and persistent. Values physical pleasure and stability.",
            "GEM": "Playful and communicative. Enjoys variety and mental stimulation.",
            "CAN": "Protective and emotional. Deep emotional connections.",
            "LEO": "Confident and dramatic. Needs admiration and creative expression.",
            "VIR": "Precise and attentive. Shows care through service.",
            "LIB": "Diplomatic and balanced. Seeks harmony and partnership.",
            "SCO": "Intense and transformative. Deep psychological connections.",
            "SAG": "Adventurous and optimistic. Values freedom and exploration.",
            "CAP": "Ambitious and disciplined. Builds intimacy carefully.",
            "AQU": "Innovative and unconventional. Experimental and freedom-loving.",
            "PIS": "Compassionate and intuitive. Spiritual and romantic approach."
        },
        "Jupiter": {
            "ARI": "Expansive and confident sexuality. Natural optimism and enthusiasm.",
            "TAU": "Steady sensual growth. Values security and comfort expansion.",
            "GEM": "Versatile sexual expansion. Enjoys learning and variety.",
            "CAN": "Nurturing emotional growth. Family-oriented expansion.",
            "LEO": "Creative sexual expression. Generous and warm-hearted.",
            "VIR": "Analytical service growth. Improvement in practical intimacy.",
            "LIB": "Harmonious expansion. Seeks beauty and balance.",
            "SCO": "Transformative depth. Philosophical approach to intimacy.",
            "SAG": "Natural adventurous expansion. Optimistic and freedom-loving.",
            "CAP": "Ambitious disciplined growth. Builds long-term intimacy.",
            "AQU": "Innovative progressive values. Experimental and original.",
            "PIS": "Compassionate intuitive growth. Spiritual connection."
        },
        "Saturn": {
            "ARI": "Disciplined sexual approach. Learning responsibility through independence.",
            "TAU": "Stable and persistent. Builds security through commitment.",
            "GEM": "Organized communication. Responsibility in intimate dialogue.",
            "CAN": "Emotional responsibility. Building family security.",
            "LEO": "Creative leadership. Structured self-expression.",
            "VIR": "Analytical service discipline. Practical approach.",
            "LIB": "Partnership responsibility. Balanced and committed.",
            "SCO": "Transformative discipline. Deep commitment.",
            "SAG": "Philosophical responsibility. Structured expansion.",
            "CAP": "Natural responsibility. Built for long-term commitment.",
            "AQU": "Innovative responsibility. Structured progressive values.",
            "PIS": "Compassionate discipline. Structured spiritual connection."
        },
        "Uranus": {
            "ARI": "Innovative sexual breakthroughs. Pioneering new forms of intimacy.",
            "TAU": "Unconventional values. Slow but revolutionary changes.",
            "GEM": "Revolutionary communication. Sudden insights in sexuality.",
            "CAN": "Innovative emotional security. New approaches to nurturing.",
            "LEO": "Creative breakthroughs. Unique self-expression.",
            "VIR": "Unconventional service approaches. Innovative practical care.",
            "LIB": "Revolutionary partnerships. New approaches to harmony.",
            "SCO": "Transformative insights. Psychological breakthroughs.",
            "SAG": "Philosophical innovation. Expanding consciousness.",
            "CAP": "Structural reforms. Institutional changes in intimacy.",
            "AQU": "Natural innovator. Humanitarian vision in sexuality.",
            "PIS": "Spiritual insights. Mystical revelations."
        },
        "Neptune": {
            "ARI": "Spiritual pioneering. Inspired action and vision.",
            "TAU": "Dreamy values. Idealized security and comfort.",
            "GEM": "Imaginative communication. Inspired ideas.",
            "CAN": "Mystical emotional security. Spiritual nurturing.",
            "LEO": "Creative inspiration. Dramatic spiritual expression.",
            "VIR": "Service through inspiration. Healing compassion.",
            "LIB": "Harmonious ideals. Spiritual partnerships.",
            "SCO": "Deep spiritual transformation. Psychic sensitivity.",
            "SAG": "Philosophical idealism. Spiritual expansion.",
            "CAP": "Structured spirituality. Institutional faith.",
            "AQU": "Collective ideals. Humanitarian dreams.",
            "PIS": "Natural mystic. Spiritual connection."
        },
        "Pluto": {
            "ARI": "Transformative sexual initiative. Rebirth through action.",
            "TAU": "Deep value transformation. Regeneration of security.",
            "GEM": "Psychological communication. Mental transformation.",
            "CAN": "Emotional rebirth. Family transformation.",
            "LEO": "Creative transformation. Rebirth through expression.",
            "VIR": "Service transformation. Health regeneration.",
            "LIB": "Relationship transformation. Artistic rebirth.",
            "SCO": "Deep psychological transformation. Natural rebirth.",
            "SAG": "Philosophical transformation. Belief regeneration.",
            "CAP": "Structural transformation. Power rebirth.",
            "AQU": "Collective transformation. Social regeneration.",
            "PIS": "Spiritual transformation. Mystical rebirth."
        }
    }

    # Alege dicționarul de interpretări în funcție de tip
    if interpretation_type == "Career":
        interpretations = career_interpretations
    elif interpretation_type == "Relationships":
        interpretations = relationships_interpretations
    elif interpretation_type == "Spiritual":
        interpretations = spiritual_interpretations
    elif interpretation_type == "Sexual":
        interpretations = sexual_interpretations
    else:  # Natal
        interpretations = natal_interpretations
    
    # TOATE PLANETELE pentru TOATE tipurile de interpretare
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"]
    
    for planet_name in planets_to_display:
        if planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            
            # Afișează interpretarea pentru semn
            if (planet_name in interpretations and 
                planet_sign in interpretations[planet_name]):
                
                st.write(f"**{planet_name} in {planet_sign}**")
                st.write(interpretations[planet_name][planet_sign])
                st.write("")

def display_about():
    st.header("ℹ️ About Horoscope")
    st.markdown("""
    ### Horoscope ver. 2.0 (Streamlit Edition)
    
    **Copyright © 2025**  
    RAD  
    
    **Features**  
    - Professional astrological calculations using Swiss Ephemeris
    - Interactive chart wheel visualization
    - Accurate planetary positions with professional ephemeris files
    - Natal chart calculations with Placidus houses
    - Complete planetary aspects calculations
    - **Transits and Progressions** (Secondary & Solar Arc)
    - Comprehensive interpretations for signs, degrees and houses
    
    **Technical:** Built with Streamlit, Swiss Ephemeris (pyswisseph), and Matplotlib
    for professional astrological charting.
    """)

if __name__ == "__main__":
    main()
