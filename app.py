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
        aspect_radius = 2.5
        
        # Culori
        background_color = 'white'
        circle_color = '#262730'
        text_color = 'black'
        house_color = 'black'
        
        # Culori pentru aspecte
        aspect_colors = {
            'Conjunction': '#FF6B6B', 'Opposition': '#4ECDC4', 'Trine': '#45B7D1',
            'Square': '#FFA500', 'Sextile': '#96CEB4'
        }
        
        planet_colors = {
            'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mercury': '#A9A9A9', 'Venus': '#FFB6C1',
            'Mars': '#FF4500', 'Jupiter': '#FFA500', 'Saturn': '#DAA520', 'Uranus': '#40E0D0',
            'Neptune': '#1E90FF', 'Pluto': '#8B008B', 'Nod': '#FF69B4', 'Chi': '#32CD32'
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
        
        # MODIFICARE CRUCIALĂ: Găsim longitudinea Ascendentului (casa 1) și rotim totul
        asc_longitude = chart_data['houses'][1]['longitude']
        rotation_offset = asc_longitude + 90  # Rotim astfel încât Ascendentul să fie în stânga
        
        for i in range(12):
            # Calculăm unghiul casei rotite corect
            house_num = i + 1
            house_longitude = chart_data['houses'][house_num]['longitude']
            angle = house_longitude - rotation_offset
            rad_angle = np.radians(angle)
            
            # Linii pentru case (cuspide)
            x_outer = center_x + outer_radius * np.cos(rad_angle)
            y_outer = center_y + outer_radius * np.sin(rad_angle)
            x_inner = center_x + inner_radius * np.cos(rad_angle)
            y_inner = center_y + inner_radius * np.sin(rad_angle)
            
            ax.plot([x_inner, x_outer], [y_inner, y_outer], color=house_color, linewidth=1, alpha=0.5)
            
            # Numerele caselor - centrul fiecărei case
            house_center_angle = angle + 15
            house_rad_angle = np.radians(house_center_angle)
            x_house = center_x + house_radius * np.cos(house_rad_angle)
            y_house = center_y + house_radius * np.sin(house_rad_angle)
            
            ax.text(x_house, y_house, str(house_num), ha='center', va='center', 
                   color=house_color, fontsize=10, fontweight='bold')
        
        # Semnele zodiacale - plasate pe circumferința exterioară
        for i in range(12):
            sign_angle = i * 30 - rotation_offset  # Poziția semnului
            sign_rad_angle = np.radians(sign_angle)
            
            # Simbolul semnului
            x_sign = center_x + (outer_radius + 0.3) * np.cos(sign_rad_angle)
            y_sign = center_y + (outer_radius + 0.3) * np.sin(sign_rad_angle)
            
            ax.text(x_sign, y_sign, signs[i], ha='center', va='center', 
                   color=house_color, fontsize=14)
            
            # Numele semnului
            x_name = center_x + (outer_radius + 0.7) * np.cos(sign_rad_angle)
            y_name = center_y + (outer_radius + 0.7) * np.sin(sign_rad_angle)
            
            ax.text(x_name, y_name, sign_names[i], ha='center', va='center', 
                   color=house_color, fontsize=8, rotation=sign_angle + 90)
        
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
                    
                    # Coordonatele planetelor rotite corect
                    long1 = chart_data['planets'][planet1]['longitude'] - rotation_offset
                    long2 = chart_data['planets'][planet2]['longitude'] - rotation_offset
                    
                    rad_angle1 = np.radians(long1)
                    rad_angle2 = np.radians(long2)
                    
                    # Pozițiile planetelor pe cerc
                    x1 = center_x + aspect_radius * np.cos(rad_angle1)
                    y1 = center_y + aspect_radius * np.sin(rad_angle1)
                    x2 = center_x + aspect_radius * np.cos(rad_angle2)
                    y2 = center_y + aspect_radius * np.sin(rad_angle2)
                    
                    # Alege culoarea pentru aspect
                    color = aspect_colors.get(aspect_name, '#888888')
                    linewidth = 2.0 if aspect['strength'] == 'Strong' else 1.0
                    
                    # Desenează linia aspectului
                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, 
                           alpha=0.7, linestyle='-')
        
        # Plasează planetele în chart
        planets = chart_data['planets']
        planet_symbols = {
            'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
            'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅', 'Neptune': '♆', 
            'Pluto': '♇', 'Nod': '☊', 'Chi': '⚷'
        }
        
        for planet_name, planet_data in planets.items():
            longitude = planet_data['longitude']
            is_retrograde = planet_data.get('retrograde', False)
            
            # Poziția planetei rotită corect
            planet_angle = longitude - rotation_offset
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
        
        # Legenda pentru aspecte
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
        name = st.text_input("Name", "Your Name")
        
        col1a, col1b = st.columns(2)
        with col1a:
            birth_date = st.date_input("Birth Date", 
                                     datetime(1986, 4, 25).date(),
                                     min_value=datetime(1800, 1, 1).date(),
                                     max_value=datetime(2100, 12, 31).date())
        with col1b:
            birth_time = st.time_input("Birth Time", datetime(1986, 4, 25, 21, 0).time())
        
        time_zone = st.selectbox("Time Zone", [f"GMT{i:+d}" for i in range(-12, 13)], index=12)
        
    with col2:
        st.subheader("Birth Place Coordinates")
        
        # Selector pentru orașe și capitale (în engleză)
        world_cities = {
            # Romania
            "Bucharest, Romania": {"lat": 44.4268, "lon": 26.1025},
            "Tecuci, Romania": {"lat": 45.8497, "lon": 27.4344},
            "Ploiesti, Romania": {"lat": 44.9416, "lon": 26.0227},
            "Cluj-Napoca, Romania": {"lat": 46.7712, "lon": 23.6236},
            "Timisoara, Romania": {"lat": 45.7489, "lon": 21.2087},
            "Iasi, Romania": {"lat": 47.1585, "lon": 27.6014},
            "Constanta, Romania": {"lat": 44.1598, "lon": 28.6348},
            "Craiova, Romania": {"lat": 44.3302, "lon": 23.7949},
            "Brasov, Romania": {"lat": 45.6576, "lon": 25.6012},
            "Galati, Romania": {"lat": 45.4353, "lon": 28.0070},
            
            # Neighboring countries
            "Budapest, Hungary": {"lat": 47.4979, "lon": 19.0402},
            "Belgrade, Serbia": {"lat": 44.7866, "lon": 20.4489},
            "Sofia, Bulgaria": {"lat": 42.6977, "lon": 23.3219},
            "Chisinau, Moldova": {"lat": 47.0105, "lon": 28.8638},
            "Kyiv, Ukraine": {"lat": 50.4501, "lon": 30.5234},
            
            # Other European capitals
            "Prague, Czech Republic": {"lat": 50.0755, "lon": 14.4378},
            "Warsaw, Poland": {"lat": 52.2297, "lon": 21.0122},
            "Berlin, Germany": {"lat": 52.5200, "lon": 13.4050},
            "Paris, France": {"lat": 48.8566, "lon": 2.3522},
            "London, UK": {"lat": 51.5074, "lon": -0.1278},
            "Madrid, Spain": {"lat": 40.4168, "lon": -3.7038},
            "Rome, Italy": {"lat": 41.9028, "lon": 12.4964},
            "Vienna, Austria": {"lat": 48.2082, "lon": 16.3738},
            "Athens, Greece": {"lat": 37.9838, "lon": 23.7275},
            "Lisbon, Portugal": {"lat": 38.7223, "lon": -9.1393},
            "Amsterdam, Netherlands": {"lat": 52.3676, "lon": 4.9041},
            "Brussels, Belgium": {"lat": 50.8503, "lon": 4.3517},
            "Copenhagen, Denmark": {"lat": 55.6761, "lon": 12.5683},
            "Stockholm, Sweden": {"lat": 59.3293, "lon": 18.0686},
            "Oslo, Norway": {"lat": 59.9139, "lon": 10.7522},
            "Helsinki, Finland": {"lat": 60.1699, "lon": 24.9384},
            "Moscow, Russia": {"lat": 55.7558, "lon": 37.6173},
            "Ankara, Turkey": {"lat": 39.9334, "lon": 32.8597},
            
            # Rest of the world
            "Beijing, China": {"lat": 39.9042, "lon": 116.4074},
            "Tokyo, Japan": {"lat": 35.6762, "lon": 139.6503},
            "New Delhi, India": {"lat": 28.6139, "lon": 77.2090},
            "Washington D.C., USA": {"lat": 38.9072, "lon": -77.0369},
            "Ottawa, Canada": {"lat": 45.4215, "lon": -75.6972},
            "Canberra, Australia": {"lat": -35.2809, "lon": 149.1300},
            "Wellington, New Zealand": {"lat": -41.2865, "lon": 174.7762},
            "Brasilia, Brazil": {"lat": -15.7975, "lon": -47.8919},
            "Buenos Aires, Argentina": {"lat": -34.6037, "lon": -58.3816},
            "Santiago, Chile": {"lat": -33.4489, "lon": -70.6693},
            "Lima, Peru": {"lat": -12.0464, "lon": -77.0428},
            "Bogota, Colombia": {"lat": 4.7110, "lon": -74.0721},
            "Mexico City, Mexico": {"lat": 19.4326, "lon": -99.1332},
            "Cairo, Egypt": {"lat": 30.0444, "lon": 31.2357},
            "Johannesburg, South Africa": {"lat": -26.2041, "lon": 28.0473},
            "Nairobi, Kenya": {"lat": -1.2921, "lon": 36.8219},
            "Riyadh, Saudi Arabia": {"lat": 24.7136, "lon": 46.6753},
            "Tel Aviv, Israel": {"lat": 32.0853, "lon": 34.7818},
            "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
            "Seoul, South Korea": {"lat": 37.5665, "lon": 126.9780},
            "Bangkok, Thailand": {"lat": 13.7563, "lon": 100.5018},
            "Hanoi, Vietnam": {"lat": 21.0278, "lon": 105.8342},
            "Jakarta, Indonesia": {"lat": -6.2088, "lon": 106.8456},
            "Manila, Philippines": {"lat": 14.5995, "lon": 120.9842},
            "Kuala Lumpur, Malaysia": {"lat": 3.1390, "lon": 101.6869},
            "Singapore, Singapore": {"lat": 1.3521, "lon": 103.8198},
        }
        
        selected_city = st.selectbox(
            "Select City (optional)",
            [""] + list(world_cities.keys()),
            help="Select a city to automatically fill coordinates"
        )
        
        # Folosim session state pentru a memora valorile auto-completate
        if 'auto_coords' not in st.session_state:
            st.session_state.auto_coords = None
        
        if selected_city:
            city_data = world_cities[selected_city]
            st.session_state.auto_coords = {
                "lat": city_data["lat"],
                "lon": city_data["lon"]
            }
            st.info(f"📍 {selected_city}: {abs(city_data['lat']):.4f}°{'N' if city_data['lat'] >= 0 else 'S'}, {abs(city_data['lon']):.4f}°{'E' if city_data['lon'] >= 0 else 'W'}")
        elif st.session_state.auto_coords and selected_city == "":
            # Reset auto coordinates when no city is selected
            st.session_state.auto_coords = None
        
        col2a, col2b = st.columns(2)
        with col2a:
            # Longitude cu grade și minute
            st.write("**Longitude**")
            col_lon_deg, col_lon_min = st.columns(2)
            with col_lon_deg:
                # Set default values based on auto-coordinates or manual input
                if st.session_state.auto_coords:
                    default_lon_deg = int(abs(st.session_state.auto_coords["lon"]))
                    default_lon_dir = "East" if st.session_state.auto_coords["lon"] >= 0 else "West"
                else:
                    default_lon_deg = 26
                    default_lon_dir = "East"
                
                longitude_deg = st.number_input("Longitude (°)", min_value=0, max_value=180, 
                                              value=default_lon_deg, 
                                              step=1, key="lon_deg")
            with col_lon_min:
                if st.session_state.auto_coords:
                    default_lon_min = round((abs(st.session_state.auto_coords["lon"]) - default_lon_deg) * 60)
                else:
                    default_lon_min = 6  # București are 26°06'
                
                longitude_min = st.number_input("Longitude (')", min_value=0, max_value=59, 
                                              value=default_lon_min, 
                                              step=1, key="lon_min")
            longitude_dir = st.selectbox("Longitude Direction", ["East", "West"], 
                                       index=0 if default_lon_dir == "East" else 1, 
                                       key="lon_dir")
            
        with col2b:
            # Latitude cu grade și minute
            st.write("**Latitude**")
            col_lat_deg, col_lat_min = st.columns(2)
            with col_lat_deg:
                # Set default values based on auto-coordinates or manual input
                if st.session_state.auto_coords:
                    default_lat_deg = int(abs(st.session_state.auto_coords["lat"]))
                    default_lat_dir = "North" if st.session_state.auto_coords["lat"] >= 0 else "South"
                else:
                    default_lat_deg = 44
                    default_lat_dir = "North"
                
                latitude_deg = st.number_input("Latitude (°)", min_value=0, max_value=90, 
                                             value=default_lat_deg, 
                                             step=1, key="lat_deg")
            with col_lat_min:
                if st.session_state.auto_coords:
                    default_lat_min = round((abs(st.session_state.auto_coords["lat"]) - default_lat_deg) * 60)
                else:
                    default_lat_min = 26  # București are 44°26'
                
                latitude_min = st.number_input("Latitude (')", min_value=0, max_value=59, 
                                             value=default_lat_min, 
                                             step=1, key="lat_min")
            latitude_dir = st.selectbox("Latitude Direction", ["North", "South"], 
                                      index=0 if default_lat_dir == "North" else 1, 
                                      key="lat_dir")
        
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
                'lat_display': f"{latitude_deg}°{latitude_min}'{latitude_dir}",
                'lon_display': f"{longitude_deg}°{longitude_min}'{longitude_dir}"
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
        
        # ORDINEA PROFESIONALĂ pentru planete - structura standard a charturilor
        planets_order = [
            'Sun', 'Moon', 'Mercury', 'Venus', 'Mars',           # Planete personale
            'Jupiter', 'Saturn',                                 # Planete sociale
            'Uranus', 'Neptune', 'Pluto',                        # Planete transpersonale
            'Nod', 'Chi'                                         # Puncte sensibile
        ]
        
        for planet_name in planets_order:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                retro_symbol = " 🔄" if planet_data['retrograde'] else ""
                st.write(f"**{planet_name}** {planet_data['position_str']}{retro_symbol}")
    
    with col2:
        st.subheader("🏠 Houses (Placidus)")
        
        # Casele în ordinea naturală 1-12
        for house_num in range(1, 13):
            if house_num in chart_data['houses']:
                house_data = chart_data['houses'][house_num]
                
                # Adăugăm simboluri speciale pentru casele importante
                house_symbol = ""
                if house_num == 1:
                    house_symbol = " 🏁"  # Ascendent
                elif house_num == 10:
                    house_symbol = " ⬆️"  # Medium Coeli
                    
                st.write(f"**House {house_num}** {house_data['position_str']}{house_symbol}")
    
    # Adăugăm o secțiune suplimentară cu informații importante
    st.markdown("---")
    st.subheader("📊 Chart Information")
    
    info_cols = st.columns(4)
    
    with info_cols[0]:
        # Ascendent
        if 1 in chart_data['houses']:
            asc_data = chart_data['houses'][1]
            st.write(f"**Ascendant:** {asc_data['position_str']}")
    
    with info_cols[1]:
        # Medium Coeli
        if 10 in chart_data['houses']:
            mc_data = chart_data['houses'][10]
            st.write(f"**Midheaven:** {mc_data['position_str']}")
    
    with info_cols[2]:
        # Planete retrograde
        retrograde_planets = [p for p, data in chart_data['planets'].items() if data.get('retrograde', False)]
        st.write(f"**Retrograde:** {len(retrograde_planets)} planets")
    
    with info_cols[3]:
        # Elemente dominante etc. (poate fi extins)
        st.write(f"**System:** Placidus")
    
    st.markdown("---")
    
    # Butoane de navigare
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
    
    # Calculează automat tranzitele pentru data nașterii la prima afișare
    if st.session_state.transit_data is None:
        with st.spinner("Calculating transits for birth date..."):
            transit_data = calculate_transits(
                natal_chart['jd'], 
                birth_data['date'],  # Folosește automat data nașterii
                birth_data['lat_deg'], 
                birth_data['lon_deg']
            )
            st.session_state.transit_data = transit_data
    
    st.subheader("Transit Date Selection")
    col1, col2 = st.columns(2)
    
    with col1:
        transit_date = st.date_input("Select Transit Date", 
                                   birth_data['date'],  # Default este data nașterii
                                   min_value=datetime(1900, 1, 1).date(),
                                   max_value=datetime(2100, 12, 31).date())
    
    with col2:
        show_aspects = st.checkbox("Show Aspects to Natal Chart", value=True)
        show_chart = st.checkbox("Show Transit Chart Wheel", value=True)
        show_aspect_lines = st.checkbox("Show Aspect Lines in Chart", value=True)
    
    # Recalculează doar dacă data a fost schimbată sau la apăsarea butonului
    current_transit_date = st.session_state.transit_data.get('date') if st.session_state.transit_data else None
    
    if st.button("Calculate Transits", type="primary") or (current_transit_date and transit_date != current_transit_date):
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
    
    # Calculează automat progresiile pentru data nașterii la prima afișare
    if st.session_state.progressed_data is None:
        with st.spinner("Calculating progressions for birth date..."):
            progressed_data = calculate_progressions(
                birth_data, 
                birth_data['date'],  # Folosește automat data nașterii
                'secondary'  # Metoda implicită
            )
            st.session_state.progressed_data = progressed_data
    
    st.subheader("Progression Settings")
    col1, col2 = st.columns(2)
    
    with col1:
        progression_date = st.date_input("Select Progression Date", 
                                       birth_data['date'],  # Default este data nașterii
                                       min_value=birth_data['date'],
                                       max_value=datetime(2100, 12, 31).date())
    
    with col2:
        progression_method = st.selectbox(
            "Progression Method",
            ["Secondary", "Solar Arc"],
            help="Secondary: 1 day = 1 year | Solar Arc: Based on Sun's movement"
        )
        show_aspect_lines = st.checkbox("Show Aspect Lines in Chart", value=True)
    
    # Recalculează doar dacă data sau metoda au fost schimbate
    current_progressed_data = st.session_state.progressed_data
    current_progression_date = current_progressed_data.get('date') if current_progressed_data else None
    current_method = current_progressed_data.get('method', '') if current_progressed_data else ''
    
    should_recalculate = (
        st.button("Calculate Progressions", type="primary") or 
        (current_progression_date and progression_date != current_progression_date) or
        (current_method and progression_method not in current_method)
    )
    
    if should_recalculate:
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
        st.write(f"**Position:** {birth_data.get('lon_display', 'N/A')} {birth_data.get('lat_display', 'N/A')}")
    
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
    
    # DOAR 3 opțiuni de interpretare
    interpretation_type = st.selectbox(
        "Type of interpretation",
        ["Natal", "Natal Aspects", "Sexual"]  # Doar aceste 3 opțiuni
    )
    
    st.markdown("---")
    st.subheader(f"Interpretation: {interpretation_type}")
    
    display_complete_interpretations(chart_data, interpretation_type)

def display_complete_interpretations(chart_data, interpretation_type):
    """Display interpretations for Natal, Natal Aspects, and Sexual only"""
    
    # Dicționar pentru maparea abreviere -> nume complete
    sign_full_names = {
        "ARI": "Aries", "TAU": "Taurus", "GEM": "Gemini", "CAN": "Cancer",
        "LEO": "Leo", "VIR": "Virgo", "LIB": "Libra", "SCO": "Scorpio",
        "SAG": "Sagittarius", "CAP": "Capricorn", "AQU": "Aquarius", "PIS": "Pisces"
    }
    
    planet_full_names = {
        "Sun": "Sun", "Moon": "Moon", "Mercury": "Mercury", "Venus": "Venus",
        "Mars": "Mars", "Jupiter": "Jupiter", "Saturn": "Saturn", "Uranus": "Uranus",
        "Neptune": "Neptune", "Pluto": "Pluto", "Nod": "North Node", "Chi": "Chiron"
    }

    # COMPLETE Natal Interpretations (Planets in Signs) - TOATE PLANETELE CU NUME COMPLETE
    natal_interpretations = {
        "Sun": {
            "Aries": "Open, energetic, strong, enthusiastic, forward looking, positive, determined, inventive, bright, filled with a zest for life.",
            "Taurus": "Reliable, able, with powers of concentration, tenacity. Steadfast, a loving & affectionate 'family' person. Honest, forthright. Learns readily from mistakes.",
            "Gemini": "Clever, bright, quickwitted, communicative, able to do many different things at once, eager to learn new subjects. Openminded, adaptable, curious, restless, confident, seldom settling down.",
            "Cancer": "Emotional,complex,loving, sympathetic, understanding, humanitarian, kind, tender, respectful of the rights of others.",
            "Leo": "Self reliant, popular, good at leading others & at administration. Lots of directed energy & drive - good at achieving that which is desired. Very confident.",
            "Virgo": "Cool, critical, idealistic but practical, hardworking & a good planner. Sees things through to the finish. Trustworthy, dependable, never shirks responsibilities. Perfectionist for the sake of perfection.",
            "Libra": "Friendly, cordial, artistic, kind, considerate, loyal, alert, sociable, moderate, balanced in views, open-minded.",
            "Scorpio": "Determined, direct, confident, sincere, brave, courageous, strongwilled, unafraid of setbacks or hard work. Principled & unswerving once a path has been decided on - has very clear goals.",
            "Sagittarius": "Forthright, freedom loving, honest, tolerant, broadminded, open, frank, fair, dependable, trusting (seldom suspicious), optimistic, generous, intelligent, respected, earnest, funloving & trustworthy.",
            "Capricorn": "Orderly, patient, serious, stable, persevering, careful, prudent, just, ( justice usually being more important to this person than mercy ). Will always repay favours - self-reliant.",
            "Aquarius": "Independent, tolerant, honest, forthright, considerate, helpful, sincere, generous, unprejudiced, broadminded, reliable, refined & humanitarian. An intense kinship with nature. Not much practical common sense.",
            "Pisces": "Sensitive, sympathetic, understanding, kind, sentimental, dedicated, broadminded, uncritical of the shortcomings of others. Quite earnest & trustworthy. Generous."
        },
        "Moon": {
            "Aries": "Energetic, ambitious, strongwilled, self-centred, impulsive, dominant & obstinate.",
            "Taurus": "Gregarious, sociable, sensuous, sometimes strongly possessive.",
            "Gemini": "Quickwitted. Hungry for new experiences - a traveller. Impressionable.",
            "Cancer": "Sensitive, friendly, but reserved; tradition loving; lives in fantasy.",
            "Leo": "A cheerful nature, with strong ego, which could lead to vanity, pride & conceit.",
            "Virgo": "Often speaks too much & too hastily. Closed book to others.",
            "Libra": "Polite, diplomatic, good social manners. Eloquent.",
            "Scorpio": "Tenacious will, much energy & working power, passionate, often sensual. Honest.",
            "Sagittarius": "Active or restless (a roving spirit), easily inspired, but not at all persevering.",
            "Capricorn": "Reserved, careful, sly. Learns by experience - reacts slowly to new things. Common sense.",
            "Aquarius": "Openminded, loves freedom, original even eccentric. Individualistic.",
            "Pisces": "Rich fantasy, deep feeling, impressionable. Easy to discourage. Receptive."
        },
        "Mercury": {
            "Aries": "Open & self-reliant, speaks fluently & too much. Ready to fight, full of new ideas.",
            "Taurus": "Thorough, persevering. Good at working with the hands. Inflexible,steady, obstinate, self-opinionated, conventional, limited in interests.",
            "Gemini": "Combative. Many-sided, interested in many subjects, well read, mentally swift.",
            "Cancer": "Dreamy, fantasises & lives in the past. Tactful, diplomatic.",
            "Leo": "Sociable, optimistic, enjoys life. Self-confident (too much?).",
            "Virgo": "Quickwitted. Thinks realistically. Has an eye for detail. Can be fussy.",
            "Libra": "Rational, appreciative, ready to compromise. Observant. Lacking in thoroughness.",
            "Scorpio": "A shrewd & thorough thinker, taciturn, acute, penetrating, with a deep & silent personality.",
            "Sagittarius": "Frank, sincere, humanitarian, justice loving, rich in ideas.",
            "Capricorn": "Logical, systematic, critical, shrewd, often a slow thinker/mover.",
            "Aquarius": "Original, full of ideas, intuitive, usually good memory.",
            "Pisces": "Emotional, impressionable. Always fantasising, dreaming."
        },
        "Venus": {
            "Aries": "Impulsive, passionate, self reliant, extroverted. Sometimes sociable.",
            "Taurus": "Often tender, sensual. Overpossessive & sometimes jealous. A good mixer.",
            "Gemini": "Flirtatious. Makes friends very easily. Has multifaceted relationships.",
            "Cancer": "Homeloving. Wary of others- generally cautious. A good host.",
            "Leo": "Magnanimous, self-centred, often creative. An exhibitionist - loves acting.",
            "Virgo": "Appears cool & closed: really passionate. Shy, restrained, scheming.",
            "Libra": "Very sociable, many friendships but few deep or enduring ones.",
            "Scorpio": "Passionate, intense, sensual, exacting, highly sensitive to any slight or neglect.",
            "Sagittarius": "Freedom-loving: hence unstable, changeful in friendships & marriage.",
            "Capricorn": "Faithful & usually reliable, but capricious at times.",
            "Aquarius": "Impersonal but friendly, makes contacts easily.",
            "Pisces": "Tolerant, compassionate, always ready to help. Self-sacrificing."
        },
        "Mars": {
            "Aries": "Energetic, enterprising, vital, open, fond of independence.",
            "Taurus": "Determined, often unyielding, persevering in work, quite self reliant.",
            "Gemini": "Interested in many things, quick, perceptive, eloquent, acute, sarcastic argumentative.",
            "Cancer": "Domestic life is very important - in this, practical & constructive.",
            "Leo": "Ambitious, enthusiastic, persevering. Powerful, generous, hot-tempered.",
            "Virgo": "Considerate, appreciative, prudent, careful, meticulous, persevering, a natural worrier.",
            "Libra": "Seldom angry or ill-natured. Temperamental, moody & vain.",
            "Scorpio": "Dynamic. Extremely strong willed. Capable of anything when determined.",
            "Sagittarius": "Energetic, fond of travelling & adventure. Often not very persevering. Hasty, inconsiderate.",
            "Capricorn": "Ambitious, strongwilled, persevering. Strives for rise, power, fame.",
            "Aquarius": "Strong reasoning powers. Often interested in science. Fond of freedom & independence.",
            "Pisces": "Failure because of multifarious aims. Prefers compromise. Restless. No self confidence."
        },
        "Jupiter": {
            "Aries": "Optimistic, energetic, fond of freedom & justice, stands up for ideas & ideals.High-spirited & self-willed.",
            "Taurus": "Reliable, good-natured, in search of success through constancy, builds up future in lots of little steps. Usually good judgement.",
            "Gemini": "Quickwitted, interested in many things, intent on expanding horizons through travel & study. Often superficial.",
            "Cancer": "Appreciative of others. Plans life carefully. Intuitive, but lives in a fantasy world.",
            "Leo": "Has a talent for organizing & leading. Open & ready to help anyone in need - magnanimous & affectionate.",
            "Virgo": "Objectively critical, conscientious, overskeptical, quiet, kind, rather too matter-of-fact, reliable",
            "Libra": "Gregarious, well-loved, fair, ethical, good. Convincing at conversation.",
            "Scorpio": "Strongwilled, ambitious, persevering, determined & smart.",
            "Sagittarius": "Optimistic, always interested in learning something new.",
            "Capricorn": "Has a sense of responsibility. Ambitious. Conventional, economical,honest sometimes avaricious. Persevering & stubborn.",
            "Aquarius": "Idealistic, sociable, interested in teaching or philosophy. Tolerant.",
            "Pisces": "Compassionate, hospitable, ready to help others, jolly, pleasant, very easy-going."
        },
        "Saturn": {
            "Aries": "Some talent for organizing, strives for leadership: however, lacks the necessary sense of responsibility & depth.",
            "Taurus": "Realistic, strongwilled, persevering, careful.",
            "Gemini": "Concentrates, a thinker. Profound, well-ordered, disciplined, logical, austere, serious.",
            "Cancer": "Sense of responsibility for the family. Conservative, economical.",
            "Leo": "Talent for organizing, strongwilled, self-confident. Pursues objectives obstinately, heedless of others. Jealous, possessive.",
            "Virgo": "A methodical & logical thinker: sometimes a ponderer. Careful, practical, conscientious, sometimes pedantic, severe, overprudent.",
            "Libra": "Sociable, reliable, patient, fond of justice, rational, tactful, usually diplomatic.",
            "Scorpio": "Determined, persevering, pursues professional objectives tenaciously. Usually inflexible.",
            "Sagittarius": "Upright, open, courageous, honourable, grave, dignified, very capable.",
            "Capricorn": "Highly ambitious, serious, usually introverted. Conventional.",
            "Aquarius": "Pragmatic, observant. Able to influence others. Overpowering desire for independence.",
            "Pisces": "Sympathetic, adaptable, ready to sacrifice self for others, but often indecisive, cowardly, sad, moody, worrying."
        },
        "Uranus": {
            "Aries": "Original, strongwilled, insists on personal freedom & independence. Proud, courageous, rebellious, dogmatic.",
            "Taurus": "Determined, self-willed, industrious, self-reliant, practical, a dogged pursuer of goals.",
            "Gemini": "Rich in ideas, inventive, versatile, gifted, able, an original thinker.",
            "Cancer": "Rather passive, compassionate, sensitive, impressionable, intuitive.",
            "Leo": "Eccentric, original, artistic, quite self-reliant - a loner. Sometimes arrogant, wilful.",
            "Virgo": "Hypercritical, clever, whimsical. Peculiar views on health & nutrition. Emotionally unreliable.",
            "Libra": "Fond of justice, fair. Original, unorthodox views on law. Restless, romantic.",
            "Scorpio": "Strongwilled, intelligent, malicious, sly, vengeful. Intent on bodily & sensual enjoyment.",
            "Sagittarius": "Active, sociable. Purposeful, methodical but reckless, highly-strung, rebellious, excitable, adventurous.",
            "Capricorn": "Talent for organizing, with a strong will, a fierce warlike nature, often a very strong personality.",
            "Aquarius": "Original, rich in ideas, independent, usually interested in science.",
            "Pisces": "Sensitive, appreciative, adaptable, often passive. Frequently idealistic, visionary, religious, impractical."
        },
        "Neptune": {
            "Aries": "Lives in fantasy. Perseveres in finding solutions for problems.",
            "Taurus": "Likes spiritual things. Very secretive. Impractical, overly traditional.",
            "Gemini": "Complex, worrying, fantasising, has many impractical ideas but sometimes flashes of brilliance too. Muddle-headed.",
            "Cancer": "Dreamy, inclined to escape from reality. Loves luxuries & comforts that life can offer.",
            "Leo": "Fond of freedom. Takes risks. Conceited. Often stands up for own beliefs & ideals.",
            "Virgo": "Humble. Sometimes has prophetic foresight. Is very critical, sceptical about orthodox religion, tradition & received opinions in general.",
            "Libra": "Idealistic, often a bit out of touch with reality. Has only a hazy view & understanding of real life & the world.",
            "Scorpio": "Emotionally intense. Has ideals of social justice & morality. Secretive.",
            "Sagittarius": "Shrewd, wide-awake intellect. Interested in an unattainable Utopia.",
            "Capricorn": "Can intuitively grasp things.",
            "Aquarius": "Often has obscure & quixotic ideas.",
            "Pisces": "Gentle, loving, sociable, honest & reliable."
        },
        "Pluto": {
            "Aries": "Straightforward, sometimes a little bit egotistical. Very assertive. Pioneering leader.",
            "Taurus": "Very interested in modern technology. Materially acquisitive.",
            "Gemini": "Strong & self-reliant, able to appraise people & situations very quickly & correctly.",
            "Cancer": "Rich inner life, often active dreams & fantasy.",
            "Leo": "Strong creative desires. Uncontrollable sexual appetite. Determined to win.",
            "Virgo": "Prone to soul-searching & self-criticism. Thinks & acts to the point.",
            "Libra": "Often ruled by the intellect: tries to solve problems logically. Interested in justice & the law.",
            "Scorpio": "Tenacious, exceptionally enduring. Can lead the way, however difficult. Emotionally intense, highly sexual.",
            "Sagittarius": "Interested in the study of racial & ethnic differences & origins & of traditional beliefs.",
            "Capricorn": "Fascinated by new things. Dictatorial, impatient, lacking in consideration, dedicated to own profession.",
            "Aquarius": "Has many friends. Original, has many ideas. Demanding in personal relationships.",
            "Pisces": "Profound, intellectual, introverted - does not like crowds.Investigative, patient. Creative & artistic"
        }
    }

    # COMPLETE Aspect Interpretations - TOATE COMBINAȚIILE CU NOD ȘI CHIRON
    aspect_interpretations = {
        # Sun aspects
        "SUN = MOON": "a feeling or moody nature",
        "SUN + MOON": "emotionally well-balanced", 
        "SUN - MOON": "feels a split between emotions and will",
        "SUN = MERCURY": "mentally active",
        "SUN = VENUS": "kind, gentle, warmhearted",
        "SUN = MARS": "strong, energetic, assertive",
        "SUN + MARS": "a developed efficiency of action",
        "SUN - MARS": "overly aggressive, misuse of energy",
        "SUN = JUPITER": "divinely blessed",
        "SUN + JUPITER": "exceedingly blessed",
        "SUN - JUPITER": "indulgent, unduly confident",
        "SUN = SATURN": "conservative, hard working, cautious",
        "SUN + SATURN": "disciplined, mature, practical",
        "SUN - SATURN": "experiences restrictiveness of spirit, inferiority complex",
        "SUN = URANUS": "lives a life of excitement, insatiable zest",
        "SUN + URANUS": "inspired, spirited, ahead of the times",
        "SUN - URANUS": "independent, rebellious, self-willed",
        "SUN = NEPTUNE": "a mystic in the truest sense",
        "SUN + NEPTUNE": "lives from the heart",
        "SUN - NEPTUNE": "weak or diffused self-image",
        "SUN = PLUTO": "experiences life in an emotionally concentrated way",
        "SUN + PLUTO": "has the greatest ability to improve, raise their consciousness, and transform any psychological complex they may have",
        "SUN - PLUTO": "tries to control all of life",
        "SUN = NOD": "aligned with life purpose and destiny",
        "SUN + NOD": "strong sense of destiny and life direction",
        "SUN - NOD": "struggles with life purpose and direction",
        "SUN = CHIRON": "wounded healer archetype activated",
        "SUN + CHIRON": "healing through self-expression and creativity",
        "SUN - CHIRON": "struggles with self-worth and healing",
        
        # Moon aspects
        "MOON = MERCURY": "emotionally expressive",
        "MOON + MERCURY": "articulate, optimistic, great mental clarity",
        "MOON - MERCURY": "struggles to find balance between feelings and intellect",
        "MOON = VENUS": "sensual",
        "MOON + VENUS": "sweet, charming", 
        "MOON - VENUS": "pursues the needs of the heart, a sensualist",
        "MOON = MARS": "brave, bold, energetic",
        "MOON + MARS": "thrives on activity",
        "MOON - MARS": "selfish",
        "MOON = JUPITER": "emotionally buoyant",
        "MOON + JUPITER": "emotionally blessed",
        "MOON - JUPITER": "emotionally excessive",
        "MOON = SATURN": "emotionally inhibited",
        "MOON + SATURN": "emotionally mature",
        "MOON - SATURN": "an emotionally karmic lifetime",
        "MOON = URANUS": "emotionally high-strung",
        "MOON + URANUS": "emotionally free",
        "MOON - URANUS": "an individualist",
        "MOON = NEPTUNE": "lives in their feelings",
        "MOON + NEPTUNE": "suffers from emotional deception, disillusionment",
        "MOON - NEPTUNE": "kind hearted, emotionally inspired",
        "MOON = PLUTO": "emotionally compulsive",
        "MOON + PLUTO": "blessed in the art of living",
        "MOON - PLUTO": "lives a cathartic emotional life",
        "MOON = NOD": "emotional alignment with destiny",
        "MOON + NOD": "emotional fulfillment through life purpose",
        "MOON - NOD": "emotional conflicts with life path",
        "MOON = CHIRON": "emotional wounds and healing",
        "MOON + CHIRON": "healing through emotional expression",
        "MOON - CHIRON": "struggles with emotional wounds",
        
        # Mercury aspects
        "MERCURY = VENUS": "lives a life of refinement and culture",
        "MERCURY + VENUS": "artistic potential",
        "MERCURY = MARS": "mentally aggressive",
        "MERCURY + MARS": "intelligent, incisive, the best attitude",
        "MERCURY - MARS": "a professional critic",
        "MERCURY = JUPITER": "mentally exuberant",
        "MERCURY + JUPITER": "the best learner", 
        "MERCURY - JUPITER": "no sense of mental proportion",
        "MERCURY = SATURN": "lives a life of concentrated thought",
        "MERCURY + SATURN": "the most conscientious",
        "MERCURY - SATURN": "nervous system under constant pressure, confidence adversely affected",
        "MERCURY = URANUS": "lives a life of independent thinking",
        "MERCURY + URANUS": "inspired, experimental thinker",
        "MERCURY - URANUS": "a revolutionary thinker",
        "MERCURY = NEPTUNE": "the most imaginative",
        "MERCURY + NEPTUNE": "acutely sensitive, delicate mind",
        "MERCURY - NEPTUNE": "mentally unfocused",
        "MERCURY = PLUTO": "lives a life of probing and observing",
        "MERCURY + PLUTO": "balanced and whole in your thinking",
        "MERCURY - PLUTO": "too intense and subjective in their thinking",
        "MERCURY = NOD": "mental alignment with destiny",
        "MERCURY + NOD": "communicating life purpose effectively",
        "MERCURY - NOD": "mental conflicts with life direction",
        "MERCURY = CHIRON": "healing through communication",
        "MERCURY + CHIRON": "teaching and healing through words",
        "MERCURY - CHIRON": "communication wounds and challenges",
        
        # Venus aspects
        "VENUS = MARS": "thrives on passion",
        "VENUS + MARS": "romantically healthy",
        "VENUS - MARS": "difficulties in relationships",
        "VENUS = JUPITER": "supremely lucky",
        "VENUS + JUPITER": "lives a life of abundant pleasure, opulence, and good fortune",
        "VENUS - JUPITER": "too indulgent in comforts and luxuries",
        "VENUS = SATURN": "overly cautious in love matters",
        "VENUS + SATURN": "excellent marriage partner, brings form and structure to aesthetic principles",
        "VENUS - SATURN": "suffers in love life due to past life abusive and harmful actions",
        "VENUS = URANUS": "excited about love",
        "VENUS + URANUS": "thrilled with life, excited about love", 
        "VENUS - URANUS": "fickle, divorce prone",
        "VENUS = NEPTUNE": "idealizes love",
        "VENUS + NEPTUNE": "the consummate love partner",
        "VENUS - NEPTUNE": "romanticizes love",
        "VENUS = PLUTO": "the greatest desire is to love intensely and completely",
        "VENUS + PLUTO": "the healthiest love partner",
        "VENUS - PLUTO": "at the mercy of uncontrollable passions",
        "VENUS = NOD": "relationship alignment with destiny",
        "VENUS + NOD": "relationships support life purpose",
        "VENUS - NOD": "relationship conflicts with life path",
        "VENUS = CHIRON": "healing through relationships",
        "VENUS + CHIRON": "healing love and beauty",
        "VENUS - CHIRON": "relationship wounds and challenges",
        
        # Mars aspects
        "MARS = JUPITER": "ambitious and motivated",
        "MARS + JUPITER": "enthusiastic, spirited, buoyant",
        "MARS - JUPITER": "extremist",
        "MARS = SATURN": "lives a life of restrained impulses",
        "MARS + SATURN": "feels a sense of purpose and direction, consistently actualizes dreams",
        "MARS - SATURN": "desires and impulses are subject to immediate restriction and censorship",
        "MARS = URANUS": "lives a life of untamed energy and audacious activity",
        "MARS + URANUS": "inspired ambitions, successful",
        "MARS - URANUS": "overly independent, individualistic, unconstrained",
        "MARS = NEPTUNE": "psychically animated",
        "MARS + NEPTUNE": "wants to help",
        "MARS - NEPTUNE": "little ability to put desires above those of others",
        "MARS = PLUTO": "a reservoir of unlimited energy",
        "MARS + PLUTO": "great potential, combined with the most potent energy", 
        "MARS - PLUTO": "driven by compulsive cravings to dominate and win",
        "MARS = NOD": "action aligned with destiny",
        "MARS + NOD": "taking action toward life purpose",
        "MARS - NOD": "action conflicts with life direction",
        "MARS = CHIRON": "healing through action",
        "MARS + CHIRON": "courageous healing and initiative",
        "MARS - CHIRON": "action wounds and challenges",
        
        # Jupiter aspects
        "JUPITER = SATURN": "the strongest character and depth of soul",
        "JUPITER + SATURN": "the best judgment",
        "JUPITER - SATURN": "overly concerned with the meaning of existence",
        "JUPITER = URANUS": "thrives on knowledge, truth, freedom",
        "JUPITER + URANUS": "extremist",
        "JUPITER - URANUS": "an inspired lover of truth",
        "JUPITER = NEPTUNE": "devotional, pious, pure hearted",
        "JUPITER + NEPTUNE": "saintly",
        "JUPITER - NEPTUNE": "confused in your judgment",
        "JUPITER = PLUTO": "compelled to find the truth, and have their life make a major impact",
        "JUPITER + PLUTO": "honorable, of the best morals",
        "JUPITER - PLUTO": "extreme in judgment, compulsive about philosophical and religious beliefs",
        "JUPITER = NOD": "expansion aligned with destiny",
        "JUPITER + NOD": "growth and opportunity through life purpose",
        "JUPITER - NOD": "expansion conflicts with life path",
        "JUPITER = CHIRON": "healing through wisdom",
        "JUPITER + CHIRON": "teaching and healing through wisdom",
        "JUPITER - CHIRON": "philosophical wounds and challenges",
        
        # Saturn aspects
        "SATURN = URANUS": "an agent for change",
        "SATURN + URANUS": "good at implementing progressive plans and actions",
        "SATURN - URANUS": "struggles to be both authoritarian and revolutionary",
        "SATURN = NEPTUNE": "a practical idealist",
        "SATURN + NEPTUNE": "outstanding example of responsibility", 
        "SATURN - NEPTUNE": "dissatisfied and uncertain of yourself",
        "SATURN = PLUTO": "compulsive about responsibility",
        "SATURN + PLUTO": "a mature human being",
        "SATURN - PLUTO": "life theme is karmic repayment of past life debts, an inordinate amount of difficulty, hardship, and suffering",
        "SATURN = NOD": "responsibility aligned with destiny",
        "SATURN + NOD": "structured approach to life purpose",
        "SATURN - NOD": "responsibility conflicts with life direction",
        "SATURN = CHIRON": "healing through discipline",
        "SATURN + CHIRON": "mastery through healing challenges",
        "SATURN - CHIRON": "structural wounds and limitations",
        
        # Uranus aspects
        "URANUS = NEPTUNE": "intense confusion regarding your independence, self reliance, and individuality (once every 190 years; last in 1993)",
        "URANUS = PLUTO": "highly clairvoyant, metaphysical, extremely devotional, evolved",
        "URANUS = NOD": "innovation aligned with destiny",
        "URANUS + NOD": "revolutionary approach to life purpose",
        "URANUS - NOD": "rebellion against life direction",
        "URANUS = CHIRON": "healing through innovation",
        "URANUS + CHIRON": "breakthrough healing and awakening",
        "URANUS - CHIRON": "unconventional wounds and healing",
        
        # Neptune aspects
        "NEPTUNE = PLUTO": "spiritual transformation and evolution",
        "NEPTUNE + PLUTO": "profound spiritual awakening",
        "NEPTUNE - PLUTO": "spiritual confusion and disillusionment",
        "NEPTUNE = NOD": "spiritual alignment with destiny",
        "NEPTUNE + NOD": "spiritual fulfillment of life purpose",
        "NEPTUNE - NOD": "spiritual confusion about life path",
        "NEPTUNE = CHIRON": "healing through spirituality",
        "NEPTUNE + CHIRON": "spiritual healing and compassion",
        "NEPTUNE - CHIRON": "spiritual wounds and disillusionment",
        
        # Pluto aspects
        "PLUTO = NOD": "transformation aligned with destiny",
        "PLUTO + NOD": "powerful transformation through life purpose",
        "PLUTO - NOD": "power struggles with life direction",
        "PLUTO = CHIRON": "healing through transformation",
        "PLUTO + CHIRON": "profound healing and rebirth",
        "PLUTO - CHIRON": "transformative wounds and power issues",
        
        # Nod aspects
        "NOD = CHIRON": "healing aligned with destiny",
        "NOD + CHIRON": "healing through life purpose",
        "NOD - CHIRON": "healing challenges on life path"
    }

    # COMPLETE Sexual Interpretations - TOATE PLANETELE ȘI CASELE CU NUME COMPLETE
    sexual_interpretations = {
        # Ascendant interpretations
        "ASC Aries": "Quick, aggressive, makes the first move. Immediately noticed in a room. Gets to the point fast, sometimes too fast intense, physical, heats up in in a hurry, cools quickly after sex, but can charge up again soon afterwards for more. Dispenses with foreplay in favor of the nitty-gritty. Comes in a flash, with super-high peak. Needs to study patience & sensitivity to avoid putting off slower, easy-going partners. Should lay back, come on less strong to get long-range love.",
        "ASC Taurus": "Earthy, animal magnetism that grows on you. Slow at moving, but persistent once aroused. Good at foreplay with practice but takes some time to learn technique. Leans toward physical affection. Warm, friendly loving rather than fiery passion. Smouldering intensity with banked fires that burn hotter as time goes on. Sex requires cultivation, development to reach its peak. Steady and strong, lots of staying power. Can keep it up all night with a willing & imaginative partner.",
        "ASC Gemini": "Talented, varied in sex technique. Likes change and imagination in sex, will try anything for its own sake or just to please a partner. May get hung up in method alone & forget the pleasure motive behind it. A delicate touch. Is bored with heavy, repetitive sex, & tires out if partner uses just brawn & not brains. Likes fantasy games, basic scenes laid out in advance and filled in spontaneously as the situation presents itself. Likes the unusual, but not deeply kinky.",
        "ASC Cancer": "A strong, determined lover who can be very demanding once involved. Tends to take things to heart, doesn't rush into lightweight scenes, likes strong commitment up front. May be a bit hesitant & suspicious sticks toe in water before plunge, then all the way. Puts great care and loving into sex, treats partner like on a pedestal, which can be hard to live up to. Can take things too seriously on first involvement or not seriously enough. Easily hurt once exposed, so careful.",
        "ASC Leo": "Playful, outgoing, full of fun and very much in the moment, with little immediate need for commitment. Sex is play, happy amusement to please the body, emotions & commitment are separate, come later, depending. Radiant, sunny disposition may belie other needs underneath, but physical sex drive is likely strong & needs satisfaction before inner self can be examined. Open and honest. Looks more for affection than technique. The spirit of the thing is what counts, not details.",
        "ASC Virgo": "Extreme in appearance, very neat or very messy, no in betweens. Needs just the right trappings to get into sex, fantasy lived out in detail. Good at structured scenes, set up ahead of time, no freewheeling. Technique can be extreme, very developed, but may be limiting by exclusion of techniques not favored. Good for fetishy scenes with the right props. Physically kinky though might not think so. May miss the forest for the trees, lose inner emotions amid details of sex.",
        "ASC Libra": "Always in motion, hard to keep up with as one scene moves to another. Can be overcritical, a high sexual achiever who demands the same of a partner. Never languishes in the backwaters, always into the latest in what makes a relationship tick. Wants the best and can get it, but needs a little patience to develop and enjoy the best out of a partner. A forceful lover, even when not taking the initiative. Needs more than the physical, goes for the mind and the heart to possess them.",
        "ASC Scorpio": "Cautious, scopes out all the possibilities before moving or taking a chance. Likes to be in control, know what the next move is, be one step ahead of a partner. Once the decision to let go is made, commitments are 'all the way'. Can be an extremist, pushes sex to the brink, likes certain dangerous thrills to be involved. Sex is more than amusement, it's life itself, and death, too, an explosive miniature of the ecstasy of human existence, in which the individual vanishes.",
        "ASC Sagittarius": "Sex is a sport, to be played for the game's own sake, not to win or gain conquest. Generous & active, not fixed on details but upon the spirit of the thing, the sheer joy of mating. Energy abounds, may wear out partner before reaching climax, so banking fires is advisable. Carefree, but may be careless as well. Should watch out for unexpected needs from partner, tend to them. Free with friendship as well as sex, makes a loyal companion even after affair is done -no grudges.",
        "ASC Capricorn": "Seeks a serious affair, no lightweight playing around. Can be too serious about partners. Tends to hang onto an affair after it is already over. Won't take no for an answer or won't say yes, not much in between. May get stuck in same groove so should look to partner to suggest sexual variety. Once has the hang of it, simply won't quit, hangs in there. Good for no-nonsense, don't-stop sex sessions, but will use sex as a weapon when pressed so don't get involved lightly.",
        "ASC Aquarius": "A cool, calm, and collected lover. Knows what to do & does it, but can become emotionally quite distant while physically deep in the fray. Takes careful stock and wants to taste & test everything before settling down to one form of expression -then may become quite conservative. Very even-handed with a lover, can't understand jealousy, turnabout is fair play. Analytic surface may belie a warm heart & a sensuous touch. A deeply satisfying emotional tie will form if patient.",
        "ASC Pisces": "Sensitive, feels lover's needs & desires. Supple and able to please and adjust to any situation. May play passive or dominant role -an easy switcher if partner is too. Seeks to make sex a channel of higher communication to transform the personality to spiritual realms through totally shared emotion. Can participate in technique but doesn't value them except as a come-on to more personal intimacy that goes beyond sex. A good role-player, but may get lost in role, lose contact.",
        
        # Sun sign interpretations
        "Sun Aries": "Fiery, intense, aggressive in all aspects of sex. Makes first move naturally, or would like to. Finishes off too quickly. Partner is left exhausted, wanting more time, care in loving.",
        "Sun Taurus": "Thoughtful, reliable lover. A hearty appetite for sex. Sees sex as a loving, not just craving, appetite. Hard to get into kinky sex or purely recreational sex. Determined. Good staying power.",
        "Sun Gemini": "Active, likes variety. Can try out any new technique, but gets bored easily. Sex is more fun & communication than hot passion. Sex is more mental than physical. Good at fantasy games, manual and oral techniques. Can be a good swinger.",
        "Sun Cancer": "Intense, private, hard to reach at first. Sex is a back-to-the-womb, nurturing experience. Can be clinging, devoted, possessive. Not the freewheeling type, but pays off triple in sheer passion once aroused.",
        "Sun Leo": "Generous, warm-hearted, sunny, but can get too boisterous or overbearing. Love and sex are natural events. Very loyal once attached, but sex and devotion do not necessarily go together.",
        "Sun Virgo": "Highly adept lover. Very demanding in technique. Can be fetishy or kinky, attaching sex to objects and ritual, releasing orgasm at right moment. Likes sex trappings: costumes, erotic toys.",
        "Sun Libra": "Seeks change in sex, not for variety but for its own sake. Will rarely beat around the bush; insists partner deliver the goods. Can play all sides of a menage-a-trois well.",
        "Sun Scorpio": "The classic sexy sign, often lives up to its reputation. A deep, physical need for sex is prevalent, but may be repressed & channeled elsewhere. When attracted to someone, it's never say die until consummation.",
        "Sun Sagittarius": "Enthusiastic, ardent, romantic. Likes classic scenarios that frame sex like a picture. Love on the ground, in the woods, under the sky, on the open sea. Wild turn-ons, if not always practical.",
        "Sun Capricorn": "Conservative about sex but will go along with most anything to please a partner, if committed to one. Lots of staying power and can keep it up all night, though sex can get repetitive, hung up on one style or technique.",
        "Sun Aquarius": "Even-handed lover, careful and often skilled at technique. Will try anything, taste and savor partner or sex skill. Makes a good swinger, knows all the rules, but exposes inner passions rarely.",
        "Sun Pisces": "Psychic. Anticipates needs and aims to please. Very fantasy-oriented, more emotional than physical. Needs a partner communicative but firm and practical to guide through reality. Due to high empathy, voyeurism is natural.",
        
        # Moon sign interpretations
        "Moon Aries": "Quick response, instant turn-on or turn-off. Won't pull punch. Can reach peaks quickly. Capable of multiple orgasms, but impatient with long foreplay. Once aroused, wants to get down to business. Super intense, but burns out quickly. May come too fast for partner. Needs slowing down to fully enjoy experience. Ready for anything, can get in over head if not careful. May burn out relationships when partner can't keep up pace. Needs constant new stimulation to keep sex stimulating, alive.",
        "Moon Taurus": "Slow and steady to respond, but once aroused stays that way. A reliable partner, good to lean on, but can't be rushed. Requires honesty: no flirting or coy game-playing. No frills, decorations, wants down-to-earth stuff. Stays friends even after affairs are over, treasures people for themselves, not just as sex turn-on. Should not be deceived--as good and longlasting an enemy as friend. Not a swinger at heart, likes longrange affairs that mean friendship & deep inner commitment.",
        "Moon Gemini": "Flexible, experiments. Reaction is likely to be 'why not?' can make a good swinger, but may not take sex very seriously or associate it with deep involvement. Free & easy lover, likes new or interesting sex for its own sake. Thrives on variety; not intensity or depth. A very good sense of humor. Skillful at fantasy role-playing as long as it stays light. Shuns heavyweight scenes like real s/m, emotional melodrama, and the like. A sex friend and playmate who doesn't need to push it.",
        "Moon Cancer": "Oversensitive at times, but doesn't show it. May seem hard or cynical at first, but wants tender, family-style loving underneath. Very sympathetic to others' troubles. A good shoulder to cry on, but takes a while to open up. Sex must be emotional, not too mechanical. Technicalities hinder. A oneperson lover, retreats if other appears on scene. Wants to envelop lover totally, dissolve into emotions of love. Gives & needs lots of attention. Total involvement once committed.",
        "Moon Leo": "Mellow, good-time partner who exudes enthusiasm, particularly in company. Once aroused, has big sex appetite, can handle more than one partner. Jealousy a no-no, has room for everyone who wants to play while still truly loyal to own partner in long run. Sees good in life even when on hard times. Can rebound -ready for more. An all-night lovemaker, may be too much for some. Can miss technical details in spirited hearty sex play. A friend always, a child at heart, full of fun.",
        "Moon Virgo": "A stickler for details: the right time, place, atmosphere, surroundings. Good for fetishes & fantasies, but demanding. Insists on real McCoy. Good role player, if roles are carefully defined. May respond to intricate, kinky scenes and play them to the hilt, while missing inner emotional message. For emotional closeness, simplicity is needed: cut away details and go heart-to-heart. Should set the scene for sex, get comfortable before any real involvement can begin on the inside.",
        "Moon Libra": "Changeable, always makes unexpected moves. Likes things in constant motion. Hard to pin down emotionally, always sees what's missing & heads for it. Creates sexual growth by not sitting still; no moss grows on this rolling stone. Insists on involvement and commitment, but only if it keeps things moving, never static. A truth-seeker who will try anything but will just as easily reject it as accept it. Turned on easily but hard to keep that way. Needs perseverant partner to keep up.",
        "Moon Scorpio": "A slow, smoldering fire which is hotter than it looks, and once it takes hold, consumes. Can sustain sex if partner can hold up. Sees sex as an all-enveloping fire to get lost in. A heavyweight: a night's fun is not the goal--plays for keeps. Not to be slighted, has an elephant's memory & finds revenge sweet. Very jealous, best in single partner, long-range relationships that can develop to peaks of mutual sexual selfimmolation. Ultimately sees sex as ecstatic, transcendant.",
        "Moon Sagittarius": "Roly-poly, fun lover with a ready laugh, can play sex for passionate romance or for just an evening's good-time play. Sees brighter side of things, but may be too cheery & optimistic. Hard to pin down to specific promises. Likes plenty of space & may dissemble somewhat artlessly to get it. A voluble fantasy life, paints outrageous scenarios but forgets to fill in the details--half the fun is in the creation, not the enactment. A friendly, mellow lover, who grows richer with age.",
        "Moon Capricorn": "Careful, consistent, determined in response. Unflagging lover when committed -not the frivolous type. Strong on performance, less so on variety or imagination. Needs to be led by the hand to try out new things. Likes commitment, security, not a freeswinger. A lover who starts slow but will go all the way with love and coaxing. Needs reassurance that everything's o.k., then will leap into the middle with a will. Not an easy, overnight bedpal; but a life long lover & friend.",
        "Moon Aquarius": "Even-tempered but a bit cold, views sex with an analytic eye and experiments for interest more than pleasure. Prefers tactile to oral stimulation but will give what's necessary to keep the ball rolling. Will play many roles, but finds real closeness hard to get. Wants lover with many techniques who keeps moving. Likes to see what is happening--sex with the lights on. Takes a long time to develop intimacy. The main sex organ is the mind, to which the body plays second fiddle.",
        "Moon Pisces": "Supple, adaptable lover. Sparks with insight, intuition. Lets a lover handle details, goes to the heart of the emotion. Can get lost in fantasy of moment, adapt to any lover's personal scene, though may interpret it completely differently from partner. Very emotional, needs sensitive, gentle treatment to bring out full love potential. Can spot lies but may not tell; honesty is essential. Fantasies may go beyond the practical -fulfillable only in mind. Needs partner to adapt fantasies.",
        
        # Mercury sign interpretations
        "Mercury Aries": "Thinks fast, comes up with spur of the moment moves that mean spontaneous fun. Spells out needs crisp and clear, but does not elaborate makes point, then moves on, never lingers.",
        "Mercury Taurus": "Down-to-earth about sex needs, but not elaborate or overdemanding, just positive and firm. With mind made up, sticks to guns, hangs onto sex preferences & favorite techniques.",
        "Mercury Gemini": "Very verbal about sex needs & desires. Willing to let it all hang out in detail, but doesn't dwell much on any one thing. Talk during sex guides & clarifies what goes on, avoids time wasted on acts that turn off. Mouth & mind are sex organs.",
        "Mercury Cancer": "Shares sexual secrets and inner desires only with very special friends. Makes gift of unwrapping and exposing inner needs like a striptease act. Likes emotional privacy, quiet.",
        "Mercury Leo": "Open, devil-may-care attitude about sex. Lets details take care of themselves, or be taken care of by partner. May like noisy, vocal sex, lets emotions out through direct cries. Straight-on, open, no hang-ups.",
        "Mercury Virgo": "Elaborate fantasy life and very specific details. Either very inhibited or very kinky, not a lot in between. Must articulate sex needs, outline night's game plan before making love. Likes fetishes and sex toys, special clothing, underwear, tattoos.",
        "Mercury Libra": "Quick and active imagination. Loves to talk about changeable affairs. Tends to compare lovers & techniques to gain improvement, but may lose touch with the moment doing so. Very talkative. Can be a real tease while leading lover to the top.",
        "Mercury Scorpio": "Sex is a deep, compelling mystery that demands exploration and revelation. A secretive explorer, lets it all out only when it's all nailed down. Enjoys covert sex games, sex that endangers through risk of exposure undercover artist.",
        "Mercury Sagittarius": "Mixes laughter with sex, won't take it over-seriously. Prefers a laughing fun time to deep enthralling passion, or at least claims so. Open and accepting of new ideas, directions, but not a technical inventor. Loves frolicking for it's own sake.",
        "Mercury Capricorn": "Likes security, direction in sex scenes. Not too spontaneous, but once the game plan is clear, performs like a trooper. Needs direction to know just what to do, then does it in spades. A thoughtful lover, if at first reticent.",
        "Mercury Aquarius": "A sexual scientist who analyzes every technique. Likes to be sure of everything, tends to organize before making a move. Visually oriented, makes a good voyeur, likes far-out ideas but may prefer to explore them only from the sidelines first.",
        "Mercury Pisces": "Sensitive to subtle clues and hints. Understands body language of love but may find it hard to but into words. Will cooperate verbally, but may not give inner self until just the right situation arrives then seizes it with instant ardor.",
        
        # Venus sign interpretations
        "Venus Aries": "Likes immediate, fast gratification eats up a lover in no time. Intense desire that may go to extremes to be satisfied but doesn't last long in and out & over with as soon as the need is gone. One-nighters can be quite satisfying, intense.",
        "Venus Taurus": "Slow, burning desire that takes lovers with stamina to satisfy. A quickie is not enough, wants long, skilled attention like playing a big game fish.",
        "Venus Gemini": "Wants a delicate, varied touch from sensitive lover. Tickling, stroking beats hard and heavy. Appreciates artful loving for its own sake more than getting swept away in flash orgasm. Likes a verbal partner, lots of talk during sex.",
        "Venus Cancer": "Aching desire, not quickly or easily satified, wants to dissolve in passion but needs just the right scene to accomplish it. Looks for total devotion, commitment, enveloping love that fills every crevice.",
        "Venus Leo": "Open, outgoing desire, a hearty sexual appetite, honest about physical needs and pleasure. Likes playful, roly-poly sex that heightens to hot passion. Any surroundings will do, if in the mood, pleasure is its own reward.",
        "Venus Virgo": "Potentially an ideal fetishist, revels in every detail of sex, the more elaborate the scene, the greater the satisfaction. Needs it all just right to get off, though, and one false move can spoil it.",
        "Venus Libra": "Likes an affair that is moving, never gets into a rut. Likes things just so, but never the same twice, can enjoy multiple lovers if one can't keep the pace. May thrive on conflict, fight way to orgasm.",
        "Venus Scorpio": "Raw sex desire, focused in the belly, may be buried until it suddenly explodes with need. Wants overwhelming sex that washes away consciousness, dissolves personality in desire.",
        "Venus Sagittarius": "Craves adventure, sex that elevates and enhances knowledge, personality. Enthusiasm! Likes a happy time. Sex must be fun and laughter. Motivation, not technique, a must, communication & feeling are everything.",
        "Venus Capricorn": "Must have certainty in sex, not freewheeling experimentation or swinging unless very well defined. Wants well-honed technique, pursued relentlessly to orgasm. Goal-oriented desire, sex must get results to satisfy.",
        "Venus Aquarius": "Likes sexual experiments, but treats them like a science, desire comes from the mind more than the body. Can try out the ultimately kinky without ever really being kinky. Excellent material for a swinger!",
        "Venus Pisces": "Wants inner communication, unspoken link with partner. Sex should be uplifting, a medium for inner revelation. Treasures selfless sex, a giving partner, returns in kind.",
        
        # Mars sign interpretations
        "Mars Aries": "Good at quick, decisive action, intense energy output burns hot & quick, but may fade fast as well. Easily aroused & easily satisfied. Needs tempering to give partner full measure of lingering satisfaction.",
        "Mars Taurus": "Even, strong energy flow, but takes a while to warm up. Needs steady sexual outlet or gets jammed up. Details less important than basic thrust, inner drive toward release. Once in motion, must find satisfaction.",
        "Mars Gemini": "Light, skillful touch, can achieve high technique. Restless energy, wants and can provide constant exercise and change. May lose sight of goal in the process, too much fore or after play.",
        "Mars Cancer": "A careful, cautious touch but very intense once let go. Puts everything into it, perhaps too much; disappointed if partner can't do same. Particular about satisfying lover perfectly, but may be too oversolicitous.",
        "Mars Leo": "Full of gusto, once begun it's carte blanche all the way, a spread in every way fit for royalty. Bountiful energy may overwhelm the timid, but generous to a fault when involved.",
        "Mars Virgo": "Highly specific lover, refines technique to the hilt, but may get hung up on only one or two. Skillful at using surroundings to fit in with sex. Best in known territory, however complex less of an improvisor.",
        "Mars Libra": "A mover and a shaker, can't let things be but must change them & keep things in flux. An activator. Hard to keep up with and good at hit-and-run love.",
        "Mars Scorpio": "Strong, smouldering energies lie beneath surface, come out explosively if repressed too long. Likes extremes, but may fear them. Challenge of sex is to lose each other in a fiery flame.",
        "Mars Sagittarius": "Broad, open energy that piles into bed with a laugh, splashes sex around with a will, but may miss some details in process. Can be athletic, enthusiastic, but needs channelling for best effect.",
        "Mars Capricorn": "Careful and determined in expression, tops where skill is known, needs educating though to expand variety. A diamond in the rough, tops if experienced but needs molding early on.",
        "Mars Aquarius": "Seeks many different opportunities for sexual expression. Likes multiple partners & will need many different methods to have sex. Explores partner's fantasies to make sex perfect.",
        "Mars Pisces": "Adaptive & subtle, needs drawing out to realize extent of abilities. Capable of extremes, particularly in giving. Best at using sexual energies to relay higher communication ulterior love or devotion.",
        
        # Jupiter sign interpretations
        "Jupiter Aries": "Expansive, adventurous in sexual expression. Seeks growth through sexual experiences. Enjoys variety and new adventures in intimacy.",
        "Jupiter Taurus": "Sensual and generous lover. Believes in abundance and pleasure. Creates a comfortable, luxurious sexual environment.",
        "Jupiter Gemini": "Curious and communicative in sex. Enjoys intellectual stimulation and variety. Seeks mental connection through sexuality.",
        "Jupiter Cancer": "Nurturing and protective in sexual relationships. Creates emotional security and family-like bonds through intimacy.",
        "Jupiter Leo": "Dramatic and generous lover. Enjoys romance and grand gestures. Seeks recognition and admiration in sexual expression.",
        "Jupiter Virgo": "Discerning and service-oriented in sex. Values hygiene and technique. Seeks perfection and improvement in sexual experiences.",
        "Jupiter Libra": "Harmonious and aesthetic in sexual expression. Values beauty, balance and partnership in intimate relationships.",
        "Jupiter Scorpio": "Intense and transformative in sexuality. Seeks deep, soul-level connections. Powerful sexual energy and magnetism.",
        "Jupiter Sagittarius": "Adventurous and philosophical in sex. Values freedom and exploration. Enjoys sexual experiences as spiritual journeys.",
        "Jupiter Capricorn": "Responsible and ambitious in sexual expression. Values tradition and achievement. Seeks long-term security in relationships.",
        "Jupiter Aquarius": "Unconventional and freedom-loving in sex. Values intellectual connection and innovation. Experimental and open-minded.",
        "Jupiter Pisces": "Compassionate and spiritual in sexuality. Seeks union and transcendence through sex. Sensitive and empathetic lover.",
        
        # Saturn sign interpretations
        "Saturn Aries": "Disciplined and controlled in sexual expression. May have fears around initiation. Learns sexual confidence through experience.",
        "Saturn Taurus": "Patient and reliable in sexuality. Values security and commitment. Develops sensual mastery over time.",
        "Saturn Gemini": "Serious about sexual communication. May overthink intimacy. Develops verbal intimacy through maturity.",
        "Saturn Cancer": "Protective and traditional in sexual relationships. Values emotional security. Develops deep emotional bonds slowly.",
        "Saturn Leo": "Responsible and loyal in sexual expression. Values respect and commitment. Develops creative sexual expression with age.",
        "Saturn Virgo": "Disciplined and health-conscious in sex. Values purity and service. Develops technical skill through practice.",
        "Saturn Libra": "Committed and balanced in relationships. Values fairness and partnership. Develops harmonious sexual expression over time.",
        "Saturn Scorpio": "Intense and controlled in sexuality. Powerful but restrained. Develops deep sexual wisdom through life experience.",
        "Saturn Sagittarius": "Philosophical and responsible in sexual expression. Values truth and integrity. Develops sexual freedom through maturity.",
        "Saturn Capricorn": "Ambitious and traditional in sexuality. Values structure and achievement. Sexual expression improves with age and success.",
        "Saturn Aquarius": "Disciplined yet unconventional in sex. Values freedom within structure. Develops unique sexual expression through life lessons.",
        "Saturn Pisces": "Compassionate yet boundaried in sexuality. Spiritual but practical. Develops transcendent sexual connection through maturity.",
        
        # Uranus sign interpretations
        "Uranus Aries": "Innovative and spontaneous in sex. Enjoys experimentation and freedom. Sudden attractions and unexpected encounters.",
        "Uranus Taurus": "Unconventional yet sensual in sexual expression. Combines tradition with innovation. Unique approach to physical pleasure.",
        "Uranus Gemini": "Intellectually experimental in sex. Enjoys variety and mental stimulation. Unconventional communication styles in intimacy.",
        "Uranus Cancer": "Innovative in emotional expression. Combines tradition with new approaches to family and security in relationships.",
        "Uranus Leo": "Dramatic and original in sexual expression. Creative and rebellious approach to romance and self-expression.",
        "Uranus Virgo": "Unconventional yet practical in sex. Innovative approaches to health and service. Unique sexual techniques.",
        "Uranus Libra": "Revolutionary in relationships. Seeks equality and freedom in partnerships. Unconventional approach to beauty and harmony.",
        "Uranus Scorpio": "Intense and transformative in sexual innovation. Powerful breakthroughs in intimacy. Revolutionary approach to power and sexuality.",
        "Uranus Sagittarius": "Philosophically revolutionary in sex. Seeks freedom and truth in sexual expression. Adventurous and unconventional beliefs.",
        "Uranus Capricorn": "Innovative within structure. Combines tradition with progress in sexual expression. Unconventional approach to authority.",
        "Uranus Aquarius": "Extremely unconventional and free in sexual expression. Experimental and detached. Seeks intellectual and spiritual connection.",
        "Uranus Pisces": "Mystical and innovative in sexuality. Combines spirituality with experimentation. Unique approach to transcendence through sex.",
        
        # Neptune sign interpretations
        "Neptune Aries": "Dreamy and idealistic in sexual expression. Romantic fantasies and spiritual connections. May confuse reality with illusion.",
        "Neptune Taurus": "Sensual and mystical in sexuality. Idealizes physical pleasure and beauty. Spiritual approach to material pleasure.",
        "Neptune Gemini": "Imaginative and communicative in sex. Romantic fantasies and idealistic conversations. May idealize partners.",
        "Neptune Cancer": "Emotionally dreamy in sexuality. Idealizes home and family. Spiritual approach to emotional security.",
        "Neptune Leo": "Romantic and idealistic in sexual expression. Dramatic fantasies and spiritual creativity. May idealize love.",
        "Neptune Virgo": "Idealistic about purity and service in sex. Spiritual approach to health and perfection. May have unrealistic expectations.",
        "Neptune Libra": "Romantic and idealistic about relationships. Seeks perfect harmony and beauty. May idealize partners and love.",
        "Neptune Scorpio": "Mystical and intense in sexuality. Seeks spiritual transformation through sex. Powerful psychic and emotional connections.",
        "Neptune Sagittarius": "Philosophical and idealistic in sexual expression. Seeks spiritual truth through intimacy. May idealize sexual freedom.",
        "Neptune Capricorn": "Spiritual yet practical in sexuality. Combines tradition with idealism. Seeks meaningful structure in relationships.",
        "Neptune Aquarius": "Visionary and unconventional in sex. Seeks spiritual connection through innovation. Idealistic about freedom.",
        "Neptune Pisces": "Extremely spiritual and compassionate in sexuality. Seeks union and transcendence. May blur boundaries between reality and fantasy.",
        
        # Pluto sign interpretations
        "Pluto Aries": "Intense and transformative in sexual initiation. Powerful sexual energy that seeks new beginnings. Revolutionary approach to sexuality.",
        "Pluto Taurus": "Deeply sensual and transformative in physical expression. Seeks security through intense sexual experiences. Powerful material desires.",
        "Pluto Gemini": "Transformative in sexual communication. Seeks truth and depth through intellectual intimacy. Powerful mental connections.",
        "Pluto Cancer": "Intensely emotional and transformative in sexuality. Seeks emotional security through deep bonds. Powerful family dynamics.",
        "Pluto Leo": "Dramatic and powerful in sexual expression. Seeks creative transformation through intimacy. Intense need for recognition.",
        "Pluto Virgo": "Transformative in sexual service and health. Seeks perfection through intense experiences. Powerful attention to detail.",
        "Pluto Libra": "Intense and transformative in relationships. Seeks balance through powerful partnerships. Deep need for harmony.",
        "Pluto Scorpio": "Extremely intense and powerful in sexuality. Seeks total transformation through intimacy. Life-changing sexual experiences.",
        "Pluto Sagittarius": "Philosophically transformative in sex. Seeks truth and expansion through intense experiences. Powerful beliefs about freedom.",
        "Pluto Capricorn": "Ambitious and powerful in sexual expression. Seeks transformation through structure and achievement. Intense career and status desires.",
        "Pluto Aquarius": "Revolutionary and transformative in sexuality. Seeks freedom through intense innovation. Powerful need for individuality.",
        "Pluto Pisces": "Spiritually transformative in sexuality. Seeks transcendence through intense emotional connections. Powerful psychic and mystical experiences.",
        
        # North Node sign interpretations
        "North Node Aries": "Learning to initiate and be independent in sexuality. Developing courage and self-assertion in intimate relationships.",
        "North Node Taurus": "Learning sensual mastery and stability in sexuality. Developing physical security and reliability in relationships.",
        "North Node Gemini": "Learning communication and variety in sexuality. Developing intellectual connection and adaptability in intimacy.",
        "North Node Cancer": "Learning emotional security and nurturing in sexuality. Developing family bonds and emotional protection.",
        "North Node Leo": "Learning creative self-expression and confidence in sexuality. Developing romance and leadership in relationships.",
        "North Node Virgo": "Learning service and perfection in sexuality. Developing health consciousness and practical skills in intimacy.",
        "North Node Libra": "Learning partnership and harmony in sexuality. Developing balance and fairness in relationships.",
        "North Node Scorpio": "Learning intensity and transformation in sexuality. Developing deep emotional bonds and psychological insight.",
        "North Node Sagittarius": "Learning adventure and philosophy in sexuality. Developing freedom and truth-seeking in relationships.",
        "North Node Capricorn": "Learning responsibility and achievement in sexuality. Developing structure and long-term security in relationships.",
        "North Node Aquarius": "Learning innovation and freedom in sexuality. Developing individuality and intellectual connection in relationships.",
        "North Node Pisces": "Learning compassion and spirituality in sexuality. Developing emotional unity and transcendence in relationships.",
        
        # Chiron sign interpretations
        "Chiron Aries": "Healing through sexual initiation and independence. Learning to balance assertiveness with sensitivity in intimacy.",
        "Chiron Taurus": "Healing through sensual expression and security. Learning to balance possessiveness with generosity in relationships.",
        "Chiron Gemini": "Healing through sexual communication and variety. Learning to balance restlessness with commitment in intimacy.",
        "Chiron Cancer": "Healing through emotional security and nurturing. Learning to balance dependency with independence in relationships.",
        "Chiron Leo": "Healing through creative self-expression in sexuality. Learning to balance ego with humility in intimate relationships.",
        "Chiron Virgo": "Healing through service and perfection in sexuality. Learning to balance criticism with acceptance in relationships.",
        "Chiron Libra": "Healing through partnership and harmony in sexuality. Learning to balance dependence with independence in relationships.",
        "Chiron Scorpio": "Healing through intensity and transformation in sexuality. Learning to balance power with surrender in intimate relationships.",
        "Chiron Sagittarius": "Healing through adventure and philosophy in sexuality. Learning to balance freedom with commitment in relationships.",
        "Chiron Capricorn": "Healing through responsibility and achievement in sexuality. Learning to balance control with spontaneity in relationships.",
        "Chiron Aquarius": "Healing through innovation and freedom in sexuality. Learning to balance detachment with emotional connection in relationships.",
        "Chiron Pisces": "Healing through compassion and spirituality in sexuality. Learning to balance boundaries with unity in relationships."
    }

    # Display based on interpretation type
    st.subheader(f"📖 {interpretation_type} Interpretation")
    
    if interpretation_type == "Natal":
        # Display ALL planetary interpretations
        planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", 
                             "Saturn", "Uranus", "Neptune", "Pluto"]
        
        for planet_name in planets_to_display:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                planet_sign_abbr = planet_data['sign']
                planet_sign_full = sign_full_names.get(planet_sign_abbr, planet_sign_abbr)
                planet_full_name = planet_full_names.get(planet_name, planet_name)
                
                if (planet_name in natal_interpretations and 
                    planet_sign_full in natal_interpretations[planet_name]):
                    
                    st.write(f"**{planet_full_name} in {planet_sign_full}**")
                    st.write(f"{natal_interpretations[planet_name][planet_sign_full]}")
                    st.write(f"*Position: {planet_data['position_str']}*")
                    st.markdown("---")

    elif interpretation_type == "Natal Aspects":
        # Display ALL aspect interpretations
        aspects = calculate_aspects(chart_data)
        if aspects:
            st.write(f"**Found {len(aspects)} significant aspects**")
            
            for aspect in aspects:
                planet1 = aspect['planet1']
                planet2 = aspect['planet2']
                aspect_name = aspect['aspect_name']
                
                # Convert Nod and Chi to full names for lookup
                planet1_key = "NOD" if planet1 == "Nod" else "CHIRON" if planet1 == "Chi" else planet1.upper()
                planet2_key = "NOD" if planet2 == "Nod" else "CHIRON" if planet2 == "Chi" else planet2.upper()
                
                # Create aspect key for lookup
                aspect_key = f"{planet1_key} = {planet2_key}"
                
                # Get full names for display
                planet1_full = planet_full_names.get(planet1, planet1)
                planet2_full = planet_full_names.get(planet2, planet2)
                
                st.write(f"**{planet1_full} {aspect_name} {planet2_full}**")
                st.write(f"*Orb: {aspect['orb']:.2f}° | Strength: {aspect['strength']}*")
                
                if aspect_key in aspect_interpretations:
                    st.write(f"{aspect_interpretations[aspect_key]}")
                else:
                    # Try alternative aspect keys
                    alt_key1 = f"{planet1_key} + {planet2_key}"
                    alt_key2 = f"{planet1_key} - {planet2_key}"
                    
                    if alt_key1 in aspect_interpretations:
                        st.write(f"{aspect_interpretations[alt_key1]}")
                    elif alt_key2 in aspect_interpretations:
                        st.write(f"{aspect_interpretations[alt_key2]}")
                    else:
                        # Generic interpretation based on aspect type
                        generic_interpretations = {
                            "Conjunction": "Planets work together, blending their energies",
                            "Opposition": "Tension and balance between opposing forces",
                            "Trine": "Harmonious flow of energy and natural talent",
                            "Square": "Challenges and growth through conflict",
                            "Sextile": "Opportunities and positive connections"
                        }
                        generic = generic_interpretations.get(aspect_name, "Significant planetary interaction")
                        st.write(f"{generic}")
                st.markdown("---")
        else:
            st.info("No significant aspects found within allowed orb.")

    elif interpretation_type == "Sexual":
        # Display COMPLETE sexual interpretations for ALL relevant placements
        st.write("**Sexual Energy & Expression**")
        
        # 1. Ascendant interpretation
        if 1 in chart_data['houses']:
            asc_data = chart_data['houses'][1]
            asc_sign_abbr = asc_data['sign']
            asc_sign_full = sign_full_names.get(asc_sign_abbr, asc_sign_abbr)
            asc_key = f"ASC {asc_sign_full}"
            
            if asc_key in sexual_interpretations:
                st.write(f"**Ascendant in {asc_sign_full}**")
                st.write(f"{sexual_interpretations[asc_key]}")
                st.markdown("---")
        
        # 2. ALL planet interpretations - TOATE PLANETELE
        sexual_planets = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", 
                         "Saturn", "Uranus", "Neptune", "Pluto", "Nod", "Chi"]
        
        for planet_name in sexual_planets:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                planet_sign_abbr = planet_data['sign']
                planet_sign_full = sign_full_names.get(planet_sign_abbr, planet_sign_abbr)
                planet_full_name = planet_full_names.get(planet_name, planet_name)
                planet_key = f"{planet_full_name} {planet_sign_full}"
                
                if planet_key in sexual_interpretations:
                    st.write(f"**{planet_full_name} in {planet_sign_full}**")
                    st.write(f"{sexual_interpretations[planet_key]}")
                    st.markdown("---")

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
