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
        
        # Selector pentru capitale
        world_capitals = {
            "București, România": {"lat": 44.4268, "lon": 26.1025},
            "Budapesta, Ungaria": {"lat": 47.4979, "lon": 19.0402},
            "Belgrad, Serbia": {"lat": 44.7866, "lon": 20.4489},
            "Sofia, Bulgaria": {"lat": 42.6977, "lon": 23.3219},
            "Praga, Cehia": {"lat": 50.0755, "lon": 14.4378},
            "Varșovia, Polonia": {"lat": 52.2297, "lon": 21.0122},
            "Berlin, Germania": {"lat": 52.5200, "lon": 13.4050},
            "Paris, Franța": {"lat": 48.8566, "lon": 2.3522},
            "Londra, Marea Britanie": {"lat": 51.5074, "lon": -0.1278},
            "Madrid, Spania": {"lat": 40.4168, "lon": -3.7038},
            "Roma, Italia": {"lat": 41.9028, "lon": 12.4964},
            "Viena, Austria": {"lat": 48.2082, "lon": 16.3738},
            "Atena, Grecia": {"lat": 37.9838, "lon": 23.7275},
            "Lisabona, Portugalia": {"lat": 38.7223, "lon": -9.1393},
            "Amsterdam, Olanda": {"lat": 52.3676, "lon": 4.9041},
            "Bruxelles, Belgia": {"lat": 50.8503, "lon": 4.3517},
            "Copenhaga, Danemarca": {"lat": 55.6761, "lon": 12.5683},
            "Stockholm, Suedia": {"lat": 59.3293, "lon": 18.0686},
            "Oslo, Norvegia": {"lat": 59.9139, "lon": 10.7522},
            "Helsinki, Finlanda": {"lat": 60.1699, "lon": 24.9384},
            "Moscova, Rusia": {"lat": 55.7558, "lon": 37.6173},
            "Kiev, Ucraina": {"lat": 50.4501, "lon": 30.5234},
            "Ankara, Turcia": {"lat": 39.9334, "lon": 32.8597},
            "Beijing, China": {"lat": 39.9042, "lon": 116.4074},
            "Tokyo, Japonia": {"lat": 35.6762, "lon": 139.6503},
            "New Delhi, India": {"lat": 28.6139, "lon": 77.2090},
            "Washington D.C., SUA": {"lat": 38.9072, "lon": -77.0369},
            "Ottawa, Canada": {"lat": 45.4215, "lon": -75.6972},
            "Canberra, Australia": {"lat": -35.2809, "lon": 149.1300},
            "Wellington, Noua Zeelandă": {"lat": -41.2865, "lon": 174.7762},
            "Brasília, Brazilia": {"lat": -15.7975, "lon": -47.8919},
            "Buenos Aires, Argentina": {"lat": -34.6037, "lon": -58.3816},
            "Santiago, Chile": {"lat": -33.4489, "lon": -70.6693},
            "Lima, Peru": {"lat": -12.0464, "lon": -77.0428},
            "Bogotá, Columbia": {"lat": 4.7110, "lon": -74.0721},
            "Mexico City, Mexic": {"lat": 19.4326, "lon": -99.1332},
            "Cairo, Egipt": {"lat": 30.0444, "lon": 31.2357},
            "Johannesburg, Africa de Sud": {"lat": -26.2041, "lon": 28.0473},
            "Nairobi, Kenya": {"lat": -1.2921, "lon": 36.8219},
            "Riyadh, Arabia Saudită": {"lat": 24.7136, "lon": 46.6753},
            "Tel Aviv, Israel": {"lat": 32.0853, "lon": 34.7818},
            "Dubai, UAE": {"lat": 25.2048, "lon": 55.2708},
            "Seoul, Coreea de Sud": {"lat": 37.5665, "lon": 126.9780},
            "Bangkok, Thailanda": {"lat": 13.7563, "lon": 100.5018},
            "Hanoi, Vietnam": {"lat": 21.0278, "lon": 105.8342},
            "Jakarta, Indonezia": {"lat": -6.2088, "lon": 106.8456},
            "Manila, Filipine": {"lat": 14.5995, "lon": 120.9842},
            "Kuala Lumpur, Malaysia": {"lat": 3.1390, "lon": 101.6869},
            "Singapore, Singapore": {"lat": 1.3521, "lon": 103.8198},
        }
        
        selected_capital = st.selectbox(
            "Select World Capital (optional)",
            [""] + list(world_capitals.keys()),
            help="Select a world capital to automatically fill coordinates"
        )
        
        # Folosim session state pentru a memora valorile auto-completate
        if 'auto_coords' not in st.session_state:
            st.session_state.auto_coords = None
        
        if selected_capital:
            capital_data = world_capitals[selected_capital]
            st.session_state.auto_coords = {
                "lat": capital_data["lat"],
                "lon": capital_data["lon"]
            }
            st.info(f"📍 {selected_capital}: {abs(capital_data['lat']):.4f}°{'N' if capital_data['lat'] >= 0 else 'S'}, {abs(capital_data['lon']):.4f}°{'E' if capital_data['lon'] >= 0 else 'W'}")
        elif st.session_state.auto_coords and selected_capital == "":
            # Reset auto coordinates when no capital is selected
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
                    default_lon_deg = 16
                    default_lon_dir = "East"
                
                longitude_deg = st.number_input("Longitude (°)", min_value=0, max_value=180, 
                                              value=default_lon_deg, 
                                              step=1, key="lon_deg")
            with col_lon_min:
                if st.session_state.auto_coords:
                    default_lon_min = round((abs(st.session_state.auto_coords["lon"]) - default_lon_deg) * 60)
                else:
                    default_lon_min = 0
                
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
                    default_lat_deg = 45
                    default_lat_dir = "North"
                
                latitude_deg = st.number_input("Latitude (°)", min_value=0, max_value=90, 
                                             value=default_lat_deg, 
                                             step=1, key="lat_deg")
            with col_lat_min:
                if st.session_state.auto_coords:
                    default_lat_min = round((abs(st.session_state.auto_coords["lat"]) - default_lat_deg) * 60)
                else:
                    default_lat_min = 51
                
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
    """Display comprehensive interpretations in English for all categories"""
    
    # COMPLETE INTERPRETATION DATABASE - ALL PLANETS IN ALL CATEGORIES

    # NATAL INTERPRETATIONS (Complete for all planets)
    natal_interpretations = {
        "Sun": {
            "ARI": """**Sun in Aries**: The pioneer and warrior. Natural leader with incredible energy and initiative. Competitive spirit and need to be first. Impulsive and direct. Learns through action. Inspires others with enthusiasm and courage. Life purpose involves pioneering new paths and demonstrating courage.""",
            "TAU": """**Sun in Taurus**: The builder and sustainer. Reliable, stable, with remarkable concentration. Values security and comfort. Practical and patient. Deep connection with nature and physical senses. Life purpose involves creating stability and appreciating beauty in the material world.""",
            "GEM": """**Sun in Gemini**: The communicator and networker. Quick-witted, adaptable, and curious. Master of communication and intellectual pursuits. Restless and always learning. Sees connections between diverse ideas. Life purpose involves gathering and disseminating information.""",
            "CAN": """**Sun in Cancer**: The nurturer and protector. Deeply emotional and intuitive. Strong family connections and need for emotional security. Excellent memory and protective nature. Life purpose involves nurturing others and creating emotional security.""",
            "LEO": """**Sun in Leo**: The performer and king. Confident, creative, and generous. Natural leader who thrives on recognition. Inspires through creativity and warmth. Loyal and proud. Life purpose involves creative self-expression and inspiring others.""",
            "VIR": """**Sun in Virgo**: The analyst and perfectionist. Practical, service-oriented, and detail-focused. Finds fulfillment in being useful. Critical thinker and problem-solver. Life purpose involves serving others through practical skills and analysis.""",
            "LIB": """**Sun in Libra**: The diplomat and artist. Seeks harmony and balance in all relationships. Natural sense of justice and fairness. Artistic and sociable. Life purpose involves creating harmony and beauty in relationships.""",
            "SCO": """**Sun in Scorpio**: The transformer and investigator. Intense, passionate, and deeply emotional. Seeks truth and psychological depth. Powerful regenerative abilities. Life purpose involves transformation and uncovering hidden truths.""",
            "SAG": """**Sun in Sagittarius**: The explorer and philosopher. Adventurous, optimistic, and freedom-loving. Seeks truth and meaning. Natural teacher and traveler. Life purpose involves seeking higher knowledge and expanding horizons.""",
            "CAP": """**Sun in Capricorn**: The architect and authority. Ambitious, disciplined, and responsible. Builds lasting structures. Success through hard work and patience. Life purpose involves achieving mastery and building enduring structures.""",
            "AQU": """**Sun in Aquarius**: The innovator and humanitarian. Forward-thinking, independent, and original. Values freedom and social justice. Visionary perspective. Life purpose involves innovation and serving humanity.""",
            "PIS": """**Sun in Pisces**: The mystic and healer. Compassionate, intuitive, and artistic. Connected to spiritual realms. Creative and empathetic. Life purpose involves spiritual service and compassionate healing."""
        },

        "Moon": {
            "ARI": """**Moon in Aries**: Emotionally direct and passionate. Quick reactions and need for independence. Competitive in emotional expression. Leads with emotions and acts on impulses. Needs constant new emotional stimulation. Comfort found in action and challenge.""",
            "TAU": """**Moon in Taurus**: Emotionally stable and steady. Needs comfort, security, and sensory pleasure. Resistant to change but incredibly loyal. Practical emotional approach. Finds comfort in routine and physical pleasures.""",
            "GEM": """**Moon in Gemini**: Changeable and curious. Needs mental stimulation and variety. Processes emotions through talking and intellectual analysis. Restless emotions. Comfort found in learning and communication.""",
            "CAN": """**Moon in Cancer**: Deeply nurturing and protective. Strong emotional bonds and family orientation. Powerful intuition and emotional memory. Needs security and familiarity. Comfort found in home and family.""",
            "LEO": """**Moon in Leo**: Proud and dramatic. Needs recognition and appreciation. Warm emotions and creative expression. Nurtures through encouragement and celebration. Comfort found in creative expression and recognition.""",
            "VIR": """**Moon in Virgo**: Practical and analytical. Shows care through practical service. Needs order and routine. Critical and perfectionist in emotional expression. Comfort found in organization and useful service.""",
            "LIB": """**Moon in Libra**: Harmonious and diplomatic. Seeks emotional balance and partnership. Avoids conflict. Makes decisions based on feelings and relationships. Comfort found in beauty and harmonious relationships.""",
            "SCO": """**Moon in Scorpio**: Intense and passionate. Deep emotional connections and need for intimacy. Powerful intuition and psychological insight. Experiences emotions with extreme depth. Comfort found in deep emotional bonds.""",
            "SAG": """**Moon in Sagittarius**: Adventurous and optimistic. Needs emotional expansion and philosophical understanding. Processes emotions through travel and learning. Comfort found in adventure and learning.""",
            "CAP": """**Moon in Capricorn**: Responsible and disciplined. Controls emotions carefully. Ambitious emotional needs and respect for tradition. Builds emotional security slowly. Comfort found in achievement and structure.""",
            "AQU": """**Moon in Aquarius**: Independent and unconventional. Unique emotional expression. Friendly yet emotionally detached. Needs freedom and individuality. Comfort found in innovation and friendship.""",
            "PIS": """**Moon in Pisces**: Compassionate and dreamy. Sensitive emotional nature and spiritual connection. Strong empathy and psychic sensitivity. Comfort found in spiritual connection and creative expression."""
        },

        "Mercury": {
            "ARI": """**Mercury in Aries**: Quick-thinking and direct. Expresses ideas boldly. Makes decisions rapidly. Pioneer in thinking. Competitive intellectually. Learning style: hands-on and immediate application.""",
            "TAU": """**Mercury in Taurus**: Thorough and practical. Slow but sure mental processes. Good with hands and practical applications. Steady and persistent thinking. Learning style: repetition and practical experience.""",
            "GEM": """**Mercury in Gemini**: Versatile and communicative. Learns quickly and shares knowledge effectively. Mental restlessness drives continuous learning. Learning style: variety and social interaction.""",
            "CAN": """**Mercury in Cancer**: Intuitive and emotional. Thinks with heart and nostalgia. Strong emotional memory. Learning through emotional connection. Learning style: stories and personal experience.""",
            "LEO": """**Mercury in Leo**: Confident and dramatic. Expresses ideas with flair. Natural persuader and performer. Thoughts are grand and inspiring. Learning style: creative expression and teaching.""",
            "VIR": """**Mercury in Virgo**: Analytical and precise. Excellent at critical thinking. Organized and meticulous. Attention to details and practical thinking. Learning style: analysis and practical application.""",
            "LIB": """**Mercury in Libra**: Diplomatic and balanced. Seeks harmony in communication. Beautiful expression and weighed decisions. Avoids confrontation. Learning style: discussion and partnership.""",
            "SCO": """**Mercury in Scorpio**: Penetrating and investigative. Seeks hidden truths. Intense thinking and psychological penetration. Excellent research abilities. Learning style: research and deep investigation.""",
            "SAG": """**Mercury in Sagittarius**: Philosophical and broad-minded. Thinks in big pictures. Direct honesty in communication. Natural teacher and truth-seeker. Learning style: travel and higher education.""",
            "CAP": """**Mercury in Capricorn**: Practical and organized. Strategic and disciplined thinking. Long-term planning. Respect for structure and tradition. Learning style: systematic study and practice.""",
            "AQU": """**Mercury in Aquarius**: Innovative and original. Thinks outside conventional boxes. Revolutionary ideas and visionary thinking. Mental independence. Learning style: innovation and group discussion.""",
            "PIS": """**Mercury in Pisces**: Intuitive and imaginative. Thinks with psychic sensitivity. Creative and artistic thinking. Symbolic understanding. Learning style: intuition and creative expression."""
        },

        "Venus": {
            "ARI": """**Venus in Aries**: Direct and passionate in love. Attracted to challenge and excitement. Independent in relationships. Bold pursuit of desires. Love language: adventurous experiences and spontaneous affection.""",
            "TAU": """**Venus in Taurus**: Sensual and loyal. Values stability and physical pleasure. Patient and devoted. Expresses love through physical presence. Love language: physical touch and quality time.""",
            "GEM": """**Venus in Gemini**: Flirtatious and communicative. Needs mental stimulation. Versatile in affection. Expresses love through conversation. Love language: deep conversations and intellectual connection.""",
            "CAN": """**Venus in Cancer**: Nurturing and protective. Seeks emotional security. Devoted to family. Creates emotional safety in relationships. Love language: emotional support and caregiving.""",
            "LEO": """**Venus in Leo**: Generous and dramatic. Loves romance and admiration. Creative expression of affection. Seeks appreciation. Love language: grand gestures and public admiration.""",
            "VIR": """**Venus in Virgo**: Practical and helpful. Shows love through service. Attention to details. Perfectionist in relationships. Love language: acts of service and practical help.""",
            "LIB": """**Venus in Libra**: Harmonious and artistic. Seeks balance and partnership. Beautiful expression. Talent for harmonizing relationships. Love language: beauty and harmony creation.""",
            "SCO": """**Venus in Scorpio**: Intense and passionate. Seeks deep emotional bonds. Magnetic passion and total devotion. Transformative in relationships. Love language: deep emotional intimacy and loyalty.""",
            "SAG": """**Venus in Sagittarius**: Adventurous and freedom-loving. Values independence. Honest and direct. Expresses love through shared adventures. Love language: shared adventures and philosophical discussions.""",
            "CAP": """**Venus in Capricorn**: Serious and responsible. Seeks stability and commitment. Practical in love. Builds durable relationships. Love language: commitment and practical support.""",
            "AQU": """**Venus in Aquarius**: Unconventional and friendly. Values friendship and independence. Original expression of love. Friendship before romance. Love language: intellectual connection and friendship.""",
            "PIS": """**Venus in Pisces**: Romantic and compassionate. Seeks spiritual connection. Empathic and sensitive. Unconditional love approach. Love language: spiritual connection and creative expression."""
        },

        "Mars": {
            "ARI": """**Mars in Aries**: Energetic and competitive. Direct and assertive action. Natural leader. Impulsive and courageous. Need for challenges. Best expression: leadership roles and competitive sports.""",
            "TAU": """**Mars in Taurus**: Persistent and determined. Slow but steady approach. Stubborn and stable. Methodical action. Patient in achieving goals. Best expression: building projects and financial management.""",
            "GEM": """**Mars in Gemini**: Versatile and quick. Action through words and ideas. Multi-tasking. Need for variety. Agile mental and physical action. Best expression: communication projects and teaching.""",
            "CAN": """**Mars in Cancer**: Protective and emotional. Actions driven by feelings. Defensive approach. Fights for family and emotional security. Best expression: caregiving and protective roles.""",
            "LEO": """**Mars in Leo**: Confident and dramatic. Actions with style and leadership. Generous in action. Seeks recognition and appreciation. Best expression: creative projects and leadership positions.""",
            "VIR": """**Mars in Virgo**: Precise and analytical. Meticulous and careful action. Service through action. Practical and useful approach. Best expression: healthcare and detailed work.""",
            "LIB": """**Mars in Libra**: Diplomatic and balanced. Seeks harmony in action. Action through partnership. Avoids conflicts and seeks peaceful solutions. Best expression: mediation and partnership building.""",
            "SCO": """**Mars in Scorpio**: Intense and determined. Powerful and secretive action. Strong internal resources. Persistent and strategic. Best expression: research and investigative work.""",
            "SAG": """**Mars in Sagittarius**: Adventurous and optimistic. Action with purpose. Natural explorer. Expansive action and philosophical approach. Best expression: travel and education.""",
            "CAP": """**Mars in Capricorn**: Ambitious and disciplined. Strategic and persistent action. Success through hard work. Respects hierarchy and structure. Best expression: business and management.""",
            "AQU": """**Mars in Aquarius**: Innovative and independent. Strong reasoning powers. Interested in science and technology. Fond of freedom and independence. Best expression: technology and social innovation.""",
            "PIS": """**Mars in Pisces**: Compassionate and intuitive. Action through inspiration. Sensitive and empathetic. Artistic action and compassionate service. Best expression: arts and healing professions."""
        },

        "Jupiter": {
            "ARI": """**Jupiter in Aries**: Expansive and confident. Natural leadership abilities. Expansion through action. Pioneer in thinking. Optimistic and enthusiastic. Areas of growth: entrepreneurship and leadership.""",
            "TAU": """**Jupiter in Taurus**: Practical and steady growth. Values material security. Financial expansion. Stable approach. Connected to earth. Areas of growth: finance and material abundance.""",
            "GEM": """**Jupiter in Gemini**: Curious and communicative. Expands through learning and connections. Varied knowledge. Talent for teaching. Adaptable and open. Areas of growth: education and communication.""",
            "CAN": """**Jupiter in Cancer**: Nurturing and protective growth. Expands family and home life. Family traditions. Emotional security. Extended intuition. Areas of growth: family and emotional intelligence.""",
            "LEO": """**Jupiter in Leo**: Talent for organizing and leading. Open and ready to help anyone in need - magnanimous and affectionate. Creative expansion. Areas of growth: creative leadership and generosity.""",
            "VIR": """**Jupiter in Virgo**: Analytical and service-oriented growth. Improves through attention to detail. Service through knowledge. Practical and useful. Areas of growth: health and service industries.""",
            "LIB": """**Jupiter in Libra**: Harmonious and diplomatic expansion. Grows through relationships and beauty. Beneficial partnerships. Balance in expansion. Areas of growth: relationships and arts.""",
            "SCO": """**Jupiter in Scorpio**: Intense and transformative growth. Expands through deep investigation. Psychological resources. Regenerative power. Areas of growth: psychology and finance.""",
            "SAG": """**Jupiter in Sagittarius**: Philosophical and adventurous expansion. Seeks truth and meaning. Natural traveler. Natural optimism and faith. Areas of growth: philosophy and travel.""",
            "CAP": """**Jupiter in Capricorn**: Ambitious and disciplined growth. Builds lasting structures and authority. Success through work. Respect for tradition. Areas of growth: career and authority.""",
            "AQU": """**Jupiter in Aquarius**: Innovative and humanitarian expansion. Progress through originality. Collective vision. Friendly and objective. Areas of growth: technology and social progress.""",
            "PIS": """**Jupiter in Pisces**: Compassionate and spiritual growth. Expands through intuition and service. Spiritual faith. Extended empathy. Areas of growth: spirituality and creative arts."""
        },

        "Saturn": {
            "ARI": """**Saturn in Aries**: Ambitious and disciplined pioneer. Builds structures with initiative. Responsibility through action. Leadership and courage. Life lessons: patience and consideration for others.""",
            "TAU": """**Saturn in Taurus**: Practical and patient builder. Creates lasting material security. Financial responsibility. Stability through perseverance. Life lessons: flexibility and embracing change.""",
            "GEM": """**Saturn in Gemini**: Serious and organized communicator. Structures thinking and learning. Responsibility in communication. Structured knowledge. Life lessons: depth over breadth in learning.""",
            "CAN": """**Saturn in Cancer**: Responsible and protective authority. Builds family traditions. Emotional security. Family responsibility. Life lessons: emotional boundaries and objectivity.""",
            "LEO": """**Saturn in Leo**: Dignified and authoritative leader. Structures creative expression. Creative responsibility. Mature leadership. Life lessons: humility and sharing recognition.""",
            "VIR": """**Saturn in Virgo**: Precise and efficient organizer. Creates order through service. Work discipline. Health and routine responsibility. Life lessons: accepting imperfection.""",
            "LIB": """**Saturn in Libra**: Balanced and diplomatic judge. Structures relationships fairly. Partnership responsibility. Justice and balance. Life lessons: independent decision-making.""",
            "SCO": """**Saturn in Scorpio**: Intense and transformative discipline. Builds through deep investigation. Psychological responsibility. Deep commitment. Life lessons: trust and emotional vulnerability.""",
            "SAG": """**Saturn in Sagittarius**: Upright, open, courageous, honorable, grave, dignified, very capable. Philosophical responsibility. Life lessons: commitment and attention to details.""",
            "CAP": """**Saturn in Capricorn**: Natural career ambition and discipline. Built for professional success. Responsibility and authority. Life lessons: enjoying the journey, not just destination.""",
            "AQU": """**Saturn in Aquarius**: Innovative responsibility. Structured progressive thinking. Social responsibility. Progressive structures. Life lessons: emotional connection and intimacy.""",
            "PIS": """**Saturn in Pisces**: Compassionate discipline. Structured service and creativity. Spiritual responsibility. Disciplined faith. Life lessons: practical boundaries and self-protection."""
        },

        "Uranus": {
            "ARI": """**Uranus in Aries**: Innovative career breakthroughs. Pioneering new professional fields. Revolutionary action. Technological pioneer. Sudden changes in: career direction and personal identity.""",
            "TAU": """**Uranus in Taurus**: Unconventional financial ideas. Slow but revolutionary changes. Innovation in resources. Financial freedom. Sudden changes in: values and financial security.""",
            "GEM": """**Uranus in Gemini**: Revolutionary communication. Sudden insights in networking. Communication technology. Freedom of expression. Sudden changes in: thinking and communication patterns.""",
            "CAN": """**Uranus in Cancer**: Rather passive, compassionate, sensitive, impressionable, intuitive. Emotional innovation. Unconventional security. Sudden changes in: home and family life.""",
            "LEO": """**Uranus in Leo**: Creative innovation and dramatic self-expression. Unique creativity. Freedom in expression. Artistic revolution. Sudden changes in: creative expression and romance.""",
            "VIR": """**Uranus in Virgo**: Unconventional approaches to health and service. Innovative health. Freedom through service. Technology and health. Sudden changes in: health routines and work methods.""",
            "LIB": """**Uranus in Libra**: Revolutionary relationships and artistic expression. Innovative partnerships. Freedom in relationships. Social justice. Sudden changes in: relationships and social circles.""",
            "SCO": """**Uranus in Scorpio**: Transformative insights and psychological breakthroughs. Psychological revolution. Sexual freedom. Technological transformation. Sudden changes in: psychological understanding and intimacy.""",
            "SAG": """**Uranus in Sagittarius**: Philosophical innovation and expansion of consciousness. Philosophical freedom. Space travel. Progressive education. Sudden changes in: beliefs and travel opportunities.""",
            "CAP": """**Uranus in Capricorn**: Structural reforms and institutional changes. Structural revolution. Organizational freedom. Innovative government. Sudden changes in: career structures and authority.""",
            "AQU": """**Uranus in Aquarius**: Humanitarian vision and technological innovation. Natural innovator. Collective consciousness. Futuristic vision. Sudden changes in: social networks and technology.""",
            "PIS": """**Uranus in Pisces**: Spiritual insights and mystical revelations. Spiritual breakthroughs. Universal connection. Mystical innovation. Sudden changes in: spiritual understanding and creative inspiration."""
        },

        "Neptune": {
            "ARI": """**Neptune in Aries**: Spiritual pioneering and inspired action. Visionary action. Inspired leadership. Spiritual courage. Spiritual challenges: balancing idealism with practical action.""",
            "TAU": """**Neptune in Taurus**: Dreamy values and idealized security. Mystical appreciation. Idealized comfort. Spiritual values. Spiritual challenges: grounding spiritual visions in reality.""",
            "GEM": """**Neptune in Gemini**: Imaginative communication and inspired ideas. Inspired learning. Spiritual communication. Visionary ideas. Spiritual challenges: distinguishing truth from illusion in information.""",
            "CAN": """**Neptune in Cancer**: Mystical home life and spiritual nurturing. Spiritual emotions. Psychic sensitivity. Family spirituality. Spiritual challenges: maintaining emotional boundaries while being empathetic.""",
            "LEO": """**Neptune in Leo**: Creative inspiration and dramatic spirituality. Inspired creativity. Spiritual expression. Visionary art. Spiritual challenges: balancing ego needs with spiritual humility.""",
            "VIR": """**Neptune in Virgo**: Service through inspiration and healing. Healing compassion. Inspired service. Spiritual health. Spiritual challenges: practical application of spiritual ideals.""",
            "LIB": """**Neptune in Libra**: Idealistic, often a bit out of touch with reality. Has only a hazy view of real life. Spiritual partnerships. Spiritual challenges: maintaining relationship boundaries while seeking spiritual union.""",
            "SCO": """**Neptune in Scorpio**: Deep spiritual transformation and psychic sensitivity. Psychological spirituality. Mystical depth. Transformative visions. Spiritual challenges: transforming illusions without losing spiritual connection.""",
            "SAG": """**Neptune in Sagittarius**: Philosophical idealism and spiritual expansion. Spiritual philosophy. Visionary travel. Expanded consciousness. Spiritual challenges: grounding spiritual expansion in practical wisdom.""",
            "CAP": """**Neptune in Capricorn**: Structured spirituality and institutional faith. Spiritual discipline. Visionary structures. Institutional spirituality. Spiritual challenges: maintaining spiritual integrity within structures.""",
            "AQU": """**Neptune in Aquarius**: Collective ideals and humanitarian dreams. Universal vision. Spiritual innovation. Humanitarian spirituality. Spiritual challenges: balancing individual freedom with collective spiritual vision.""",
            "PIS": """**Neptune in Pisces**: Spiritual connection and mystical understanding. Natural mystic. Universal love. Deep spiritual connection. Spiritual challenges: maintaining identity while experiencing universal oneness."""
        },

        "Pluto": {
            "ARI": """**Pluto in Aries**: Transformative initiative and rebirth through action. Revolutionary action. Personal transformation. Powerful new beginnings. Transformation areas: personal identity and leadership style.""",
            "TAU": """**Pluto in Taurus**: Deep financial transformation and value regeneration. Economic revolution. Value transformation. Resource regeneration. Transformation areas: values and financial security.""",
            "GEM": """**Pluto in Gemini**: Psychological communication and mental transformation. Communication revolution. Mental rebirth. Information transformation. Transformation areas: thinking patterns and communication style.""",
            "CAN": """**Pluto in Cancer**: Emotional rebirth and family transformation. Family revolution. Emotional regeneration. Ancestral healing. Transformation areas: emotional patterns and family dynamics.""",
            "LEO": """**Pluto in Leo**: Strong creative desires. Uncontrollable sexual appetite. Determined to win. Creative transformation. Expressive rebirth. Transformation areas: creative expression and romantic relationships.""",
            "VIR": """**Pluto in Virgo**: Service transformation and health regeneration. Health revolution. Service rebirth. Practical transformation. Transformation areas: health routines and service approach.""",
            "LIB": """**Pluto in Libra**: Relationship transformation and artistic rebirth. Relationship revolution. Artistic regeneration. Social transformation. Transformation areas: relationships and artistic expression.""",
            "SCO": """**Pluto in Scorpio**: Deep psychological transformation and rebirth. Natural transformation. Psychological depth. Complete regeneration. Transformation areas: psychological patterns and intimate relationships.""",
            "SAG": """**Pluto in Sagittarius**: Philosophical transformation and belief regeneration. Belief revolution. Philosophical rebirth. Truth transformation. Transformation areas: beliefs and philosophical outlook.""",
            "CAP": """**Pluto in Capricorn**: Structural transformation and power rebirth. Power revolution. Structural regeneration. Institutional transformation. Transformation areas: career structures and authority relationships.""",
            "AQU": """**Pluto in Aquarius**: Collective transformation and social regeneration. Social revolution. Collective rebirth. Humanitarian transformation. Transformation areas: social networks and group affiliations.""",
            "PIS": """**Pluto in Pisces**: Spiritual transformation and mystical rebirth. Spiritual revolution. Universal rebirth. Mystical transformation. Transformation areas: spiritual understanding and creative inspiration."""
        }
    }

    # CAREER INTERPRETATIONS - ALL 10 PLANETS
    career_interpretations = {
        "Sun": {
            "ARI": """**Career - Sun in Aries**: Natural entrepreneur and pioneer. Thrives in competitive environments. Excellent at starting new projects and initiatives. Leadership roles in dynamic fields. Best careers: entrepreneurship, athletics, military, surgery, exploration. Success through bold action and initiative.""",
            "TAU": """**Career - Sun in Taurus**: Steady and reliable worker. Excellent in finance, real estate, and stable professions. Builds lasting career foundations. Best careers: banking, agriculture, art, finance, real estate. Success through persistence and practical approach.""",
            "GEM": """**Career - Sun in Gemini**: Communicator and networker. Excels in sales, teaching, writing, and multi-tasking roles. Adapts to various career paths. Best careers: writing, teaching, journalism, sales, media. Success through communication and versatility.""",
            "CAN": """**Career - Sun in Cancer**: Nurturing careers in healthcare, education, hospitality. Strong in family businesses and caregiving professions. Best careers: healthcare, hospitality, psychology, real estate. Success through emotional intelligence and care.""",
            "LEO": """**Career - Sun in Leo**: Natural leader and performer. Thrives in management, entertainment, and creative fields. Needs recognition and appreciation. Best careers: management, entertainment, teaching, politics. Success through creativity and leadership.""",
            "VIR": """**Career - Sun in Virgo**: Analytical and detail-oriented. Excellent in research, accounting, healthcare, and service industries. Best careers: healthcare, research, editing, accounting. Success through precision and service.""",
            "LIB": """**Career - Sun in Libra**: Diplomatic and artistic. Successful in law, design, public relations, and partnership-based businesses. Best careers: law, design, counseling, public relations. Success through harmony and partnership.""",
            "SCO": """**Career - Sun in Scorpio**: Intense and investigative. Excels in research, psychology, finance, and transformative roles. Best careers: research, psychology, detective work, finance. Success through depth and transformation.""",
            "SAG": """**Career - Sun in Sagittarius**: Adventurous and philosophical. Thrives in travel, education, publishing, and international business. Best careers: education, travel, publishing, ministry. Success through expansion and wisdom.""",
            "CAP": """**Career - Sun in Capricorn**: Ambitious and disciplined. Natural executive material. Excels in corporate leadership and long-term planning. Best careers: management, government, engineering, finance. Success through discipline and structure.""",
            "AQU": """**Career - Sun in Aquarius**: Innovative and humanitarian. Successful in technology, science, social work, and progressive fields. Best careers: technology, science, social work, invention. Success through innovation and vision.""",
            "PIS": """**Career - Sun in Pisces**: Compassionate and creative. Excels in arts, healing professions, spirituality, and service-oriented work. Best careers: arts, healing, spirituality, charity work. Success through compassion and creativity."""
        },

        "Moon": {
            "ARI": """**Career - Moon in Aries**: Career success through initiative and emotional drive. Needs variety and challenge. Thrives in competitive environments. Best in: startup companies, sports, emergency services. Emotional satisfaction through achievement and recognition.""",
            "TAU": """**Career - Moon in Taurus**: Stable career growth through persistence. Values financial security and comfort. Builds career slowly but surely. Best in: finance, agriculture, luxury goods. Emotional satisfaction through stability and material comfort.""",
            "GEM": """**Career - Moon in Gemini**: Versatile career with multiple interests. Success in communication and networking. Adapts to changing work environments. Best in: media, teaching, writing, sales. Emotional satisfaction through learning and variety.""",
            "CAN": """**Career - Moon in Cancer**: Career tied to emotional security. Success in nurturing and protective roles. Family business potential. Best in: healthcare, real estate, hospitality, parenting. Emotional satisfaction through caregiving and emotional connection.""",
            "LEO": """**Career - Moon in Leo**: Career recognition through creative expression. Needs appreciation and leadership roles. Performs well under recognition. Best in: entertainment, management, teaching. Emotional satisfaction through recognition and creative expression.""",
            "VIR": """**Career - Moon in Virgo**: Career excellence through attention to detail. Success in service and analytical work. Health-related fields. Best in: healthcare, research, editing, organization. Emotional satisfaction through useful service and order.""",
            "LIB": """**Career - Moon in Libra**: Career success through partnerships and diplomacy. Values harmony and beauty in work environment. Best in: law, design, counseling, public relations. Emotional satisfaction through harmony and beautiful work.""",
            "SCO": """**Career - Moon in Scorpio**: Career transformation through intense focus. Success in research and investigative work. Resource management. Best in: psychology, research, finance, detective work. Emotional satisfaction through depth and transformation.""",
            "SAG": """**Career - Moon in Sagittarius**: Career expansion through adventure and learning. Philosophical approach to work. International opportunities. Best in: education, travel, publishing, philosophy. Emotional satisfaction through adventure and learning.""",
            "CAP": """**Career - Moon in Capricorn**: Career ambition through emotional discipline. Builds professional reputation carefully. Traditional careers. Best in: management, government, finance, engineering. Emotional satisfaction through achievement and respect.""",
            "AQU": """**Career - Moon in Aquarius**: Innovative career through unique emotional expression. Progressive work environments. Technology fields. Best in: technology, science, social innovation. Emotional satisfaction through innovation and progress.""",
            "PIS": """**Career - Moon in Pisces**: Compassionate career through intuitive service. Success in healing and creative fields. Spiritual vocations. Best in: arts, healing, spirituality, charity. Emotional satisfaction through compassion and spiritual service."""
        },

        "Mercury": {
            "ARI": """**Career - Mercury in Aries**: Quick-thinking and innovative in career. Excellent at starting projects and initiatives. Competitive in business communication. Best in: entrepreneurship, sales, marketing. Career success through bold ideas and rapid execution.""",
            "TAU": """**Career - Mercury in Taurus**: Practical and persistent communicator. Success in finance and stable professions. Steady and reliable in business communications. Best in: finance, real estate, agriculture. Career success through practical thinking and persistence.""",
            "GEM": """**Career - Mercury in Gemini**: Versatile and adaptable in career. Excels in multi-tasking and communication roles. Natural networker and information processor. Best in: media, teaching, writing, technology. Career success through communication and adaptability.""",
            "CAN": """**Career - Mercury in Cancer**: Intuitive and emotional thinking. Success in nurturing and memory-oriented work. Strong in customer relations. Best in: counseling, real estate, history, caregiving. Career success through emotional intelligence and memory.""",
            "LEO": """**Career - Mercury in Leo**: Confident and creative communication. Leadership in expressive and authoritative roles. Excellent public speaker. Best in: management, entertainment, teaching, politics. Career success through expressive communication and leadership.""",
            "VIR": """**Career - Mercury in Virgo**: Analytical and precise thinking. Excellence in detail-oriented and service work. Excellent researcher and analyst. Best in: research, healthcare, editing, accounting. Career success through analysis and attention to detail.""",
            "LIB": """**Career - Mercury in Libra**: Diplomatic and balanced communication. Success in partnership-based businesses. Excellent mediator and negotiator. Best in: law, diplomacy, public relations, design. Career success through diplomacy and partnership.""",
            "SCO": """**Career - Mercury in Scorpio**: Investigative and profound thinking. Excellence in research and transformative work. Uncovers hidden information. Best in: research, psychology, investigation, finance. Career success through research and psychological insight.""",
            "SAG": """**Career - Mercury in Sagittarius**: Philosophical and broad-minded thinking. Success in education and expansive fields. Natural teacher and visionary. Best in: education, travel, publishing, philosophy. Career success through teaching and visionary thinking.""",
            "CAP": """**Career - Mercury in Capricorn**: Organized and ambitious thinking. Strategic planning and long-term career goals. Excellent business strategist. Best in: management, finance, engineering, planning. Career success through strategy and organization.""",
            "AQU": """**Career - Mercury in Aquarius**: Innovative and original thinking. Success in technology and progressive fields. Visionary ideas and futuristic planning. Best in: technology, science, innovation, social media. Career success through innovation and vision.""",
            "PIS": """**Career - Mercury in Pisces**: Intuitive and imaginative thinking. Excellence in creative and compassionate work. Creative problem-solving. Best in: arts, healing, spirituality, counseling. Career success through intuition and creativity."""
        },

        "Venus": {
            "ARI": """**Career - Venus in Aries**: Career success through bold relationships and partnerships. Natural negotiator with direct approach. Values independence in business relationships. Best in: sales, entrepreneurship, sports management. Financial success through initiative.""",
            "TAU": """**Career - Venus in Taurus**: Career success through stable partnerships and financial management. Values security and comfort in work environment. Best in: finance, art, real estate, luxury goods. Financial success through persistence.""",
            "GEM": """**Career - Venus in Gemini**: Career success through communication and networking. Versatile in business relationships and partnerships. Best in: media, teaching, writing, public relations. Financial success through communication.""",
            "CAN": """**Career - Venus in Cancer**: Career success through nurturing relationships and emotional intelligence. Strong in family businesses and caregiving fields. Best in: real estate, hospitality, healthcare, parenting. Financial success through emotional connection.""",
            "LEO": """**Career - Venus in Leo**: Career success through creative partnerships and leadership. Needs appreciation and recognition in work relationships. Best in: management, entertainment, teaching, luxury brands. Financial success through creativity.""",
            "VIR": """**Career - Venus in Virgo**: Career success through practical service and attention to detail. Values health and organization in work environment. Best in: healthcare, research, editing, service industries. Financial success through practical service.""",
            "LIB": """**Career - Venus in Libra**: Career success through harmonious partnerships and artistic expression. Natural diplomat and peacemaker in business. Best in: law, design, counseling, public relations. Financial success through partnership.""",
            "SCO": """**Career - Venus in Scorpio**: Career success through intense partnerships and transformative relationships. Powerful in business negotiations and investments. Best in: finance, psychology, research, detective work. Financial success through depth.""",
            "SAG": """**Career - Venus in Sagittarius**: Career success through adventurous partnerships and philosophical approach. Values freedom and honesty in business relationships. Best in: education, travel, publishing, international business. Financial success through expansion.""",
            "CAP": """**Career - Venus in Capricorn**: Career success through serious partnerships and long-term planning. Values stability and commitment in business relationships. Best in: management, government, finance, engineering. Financial success through discipline.""",
            "AQU": """**Career - Venus in Aquarius**: Career success through innovative partnerships and progressive ideas. Values friendship and independence in work relationships. Best in: technology, science, social work, innovation. Financial success through innovation.""",
            "PIS": """**Career - Venus in Pisces**: Career success through compassionate partnerships and creative expression. Spiritual approach to business relationships. Best in: arts, healing, spirituality, charity work. Financial success through compassion."""
        },

        "Mars": {
            "ARI": """**Career - Mars in Aries**: Energetic and competitive career drive. Natural pioneer and initiator. Thrives under pressure and competition. Best in: entrepreneurship, athletics, military, emergency services. Career action: bold initiatives and leadership.""",
            "TAU": """**Career - Mars in Taurus**: Persistent and determined work ethic. Slow but steady career growth. Builds lasting career foundations. Best in: finance, construction, agriculture, art. Career action: persistent effort and practical projects.""",
            "GEM": """**Career - Mars in Gemini**: Versatile and communicative action. Success in multi-tasking roles. Adapts quickly to changing work demands. Best in: sales, teaching, writing, technology. Career action: communication projects and versatile approaches.""",
            "CAN": """**Career - Mars in Cancer**: Protective and emotional drive. Career success through nurturing actions. Strong in caregiving professions. Best in: healthcare, real estate, hospitality, parenting. Career action: protective service and emotional work.""",
            "LEO": """**Career - Mars in Leo**: Confident and dramatic initiative. Leadership in creative fields. Thrives in visible leadership roles. Best in: management, entertainment, teaching, politics. Career action: creative leadership and dramatic projects.""",
            "VIR": """**Career - Mars in Virgo**: Precise and analytical action. Excellence in detail-oriented work. Meticulous and efficient worker. Best in: healthcare, research, editing, organization. Career action: detailed work and practical service.""",
            "LIB": """**Career - Mars in Libra**: Diplomatic and balanced drive. Success through partnership and harmony. Excellent team player and mediator. Best in: law, design, counseling, public relations. Career action: partnership building and harmonious work.""",
            "SCO": """**Career - Mars in Scorpio**: Intense and transformative action. Power in investigative work. Persistent and determined in career goals. Best in: research, psychology, finance, detective work. Career action: research and transformative projects.""",
            "SAG": """**Career - Mars in Sagittarius**: Adventurous and optimistic drive. Success through expansion and learning. Thrives in international or educational fields. Best in: education, travel, publishing, sports. Career action: adventurous projects and expansion.""",
            "CAP": """**Career - Mars in Capricorn**: Ambitious and disciplined action. Strategic career advancement. Builds career step by step with determination. Best in: management, government, finance, engineering. Career action: strategic planning and disciplined work.""",
            "AQU": """**Career - Mars in Aquarius**: Innovative and independent drive. Success in progressive fields. Pioneers new approaches in career. Best in: technology, science, social innovation, invention. Career action: innovative projects and social change.""",
            "PIS": """**Career - Mars in Pisces**: Compassionate and intuitive action. Success through inspired service. Works well in healing or creative fields. Best in: arts, healing, spirituality, charity work. Career action: compassionate service and creative work."""
        },

        "Jupiter": {
            "ARI": """**Career - Jupiter in Aries**: Expansive career through initiative. Natural leadership and confidence. Success through bold actions and pioneering spirit. Best in: entrepreneurship, leadership roles, sports. Career growth: through risk-taking and innovation.""",
            "TAU": """**Career - Jupiter in Taurus**: Steady growth through persistence. Financial expansion and security. Builds wealth through consistent effort. Best in: finance, real estate, agriculture, luxury goods. Career growth: through practical investments and stability.""",
            "GEM": """**Career - Jupiter in Gemini**: Versatile expansion through communication. Success in learning and teaching. Growth through networking and information sharing. Best in: teaching, writing, media, sales. Career growth: through learning and communication.""",
            "CAN": """**Career - Jupiter in Cancer**: Nurturing growth through emotional security. Family business success. Expansion through caregiving and hospitality. Best in: real estate, hospitality, healthcare, parenting. Career growth: through emotional intelligence and care.""",
            "LEO": """**Career - Jupiter in Leo**: Creative expansion through recognition. Leadership in expressive fields. Growth through inspiration and generosity. Best in: management, entertainment, teaching, politics. Career growth: through creativity and leadership.""",
            "VIR": """**Career - Jupiter in Virgo**: Analytical growth through service. Improvement through attention to detail. Expansion through practical service and health. Best in: healthcare, research, organization, service. Career growth: through practical service and health.""",
            "LIB": """**Career - Jupiter in Libra**: Harmonious expansion through partnerships. Success in artistic fields. Growth through beautiful collaborations. Best in: law, design, counseling, public relations. Career growth: through partnership and beauty.""",
            "SCO": """**Career - Jupiter in Scorpio**: Transformative growth through investigation. Deep professional development. Expansion through research and transformation. Best in: psychology, research, finance, healing. Career growth: through research and transformation.""",
            "SAG": """**Career - Jupiter in Sagittarius**: Philosophical expansion through adventure. Natural teacher and explorer. Growth through education and travel. Best in: education, travel, publishing, philosophy. Career growth: through education and adventure.""",
            "CAP": """**Career - Jupiter in Capricorn**: Ambitious growth through discipline. Long-term career building. Expansion through traditional structures and authority. Best in: management, government, finance, engineering. Career growth: through discipline and structure.""",
            "AQU": """**Career - Jupiter in Aquarius**: Innovative expansion through originality. Success in technology fields. Growth through social progress and innovation. Best in: technology, science, social work, invention. Career growth: through innovation and social change.""",
            "PIS": """**Career - Jupiter in Pisces**: Compassionate growth through intuition. Success in healing and arts. Expansion through spiritual service and creativity. Best in: arts, healing, spirituality, charity. Career growth: through compassion and creativity."""
        },

        "Saturn": {
            "ARI": """**Career - Saturn in Aries**: Career discipline through initiative. Learning responsibility through risk-taking. Builds career through courageous actions. Career challenges: impatience and learning teamwork. Career mastery: leadership and pioneering.""",
            "TAU": """**Career - Saturn in Taurus**: Career stability through persistence. Financial responsibility and practical building. Builds career through consistent effort. Career challenges: resistance to change and flexibility. Career mastery: financial security and practical skills.""",
            "GEM": """**Career - Saturn in Gemini**: Career organization through communication. Responsibility in teaching and information sharing. Builds career through structured learning. Career challenges: superficiality and focus. Career mastery: communication and education.""",
            "CAN": """**Career - Saturn in Cancer**: Career responsibility through emotional security. Building family business and traditions. Builds career through nurturing approach. Career challenges: emotional boundaries and objectivity. Career mastery: emotional intelligence and care.""",
            "LEO": """**Career - Saturn in Leo**: Career leadership through creative expression. Responsibility in entertainment and management. Builds career through disciplined creativity. Career challenges: ego and sharing recognition. Career mastery: creative leadership and generosity.""",
            "VIR": """**Career - Saturn in Virgo**: Career excellence through service. Responsibility in health and detailed work. Builds career through practical service. Career challenges: perfectionism and criticism. Career mastery: health service and practical skills.""",
            "LIB": """**Career - Saturn in Libra**: Career success through partnership. Responsibility in law and diplomacy. Builds career through balanced relationships. Career challenges: indecision and dependency. Career mastery: partnership and justice.""",
            "SCO": """**Career - Saturn in Scorpio**: Career transformation through investigation. Responsibility in research and psychology. Builds career through deep work. Career challenges: trust and emotional vulnerability. Career mastery: research and transformation.""",
            "SAG": """**Career - Saturn in Sagittarius**: Career expansion through philosophy. Responsibility in education and travel. Builds career through wisdom and teaching. Career challenges: commitment and details. Career mastery: education and philosophy.""",
            "CAP": """**Career - Saturn in Capricorn**: Natural career ambition and discipline. Built for professional success and authority. Builds career through traditional structures. Career challenges: work-life balance and enjoyment. Career mastery: leadership and structure.""",
            "AQU": """**Career - Saturn in Aquarius**: Career innovation through progressive thinking. Responsibility in technology and social change. Builds career through unique approaches. Career challenges: emotional connection and tradition. Career mastery: innovation and social progress.""",
            "PIS": """**Career - Saturn in Pisces**: Career compassion through spiritual service. Responsibility in arts and healing. Builds career through creative service. Career challenges: boundaries and practicality. Career mastery: spiritual service and creativity."""
        },

        "Uranus": {
            "ARI": """**Career - Uranus in Aries**: Innovative career breakthroughs. Pioneering new professional fields. Revolutionary action in career choices. Career changes: sudden shifts in direction and innovation. Career genius: entrepreneurship and leadership innovation.""",
            "TAU": """**Career - Uranus in Taurus**: Unconventional financial ideas. Slow but revolutionary changes in values. Innovation in resources and finance. Career changes: financial innovation and value shifts. Career genius: financial technology and sustainable business.""",
            "GEM": """**Career - Uranus in Gemini**: Revolutionary communication in career. Sudden insights in networking and information. Career changes: communication technology and media innovation. Career genius: digital communication and information technology.""",
            "CAN": """**Career - Uranus in Cancer**: Innovative approaches to emotional security. Unconventional family businesses and home-based work. Career changes: emotional security innovation and family business revolution. Career genius: emotional intelligence technology and care innovation.""",
            "LEO": """**Career - Uranus in Leo**: Creative innovation in career. Unique self-expression and dramatic changes. Career changes: creative revolution and entertainment innovation. Career genius: creative technology and performance innovation.""",
            "VIR": """**Career - Uranus in Virgo**: Unconventional approaches to health and service. Innovative health practices and work methods. Career changes: health technology and service innovation. Career genius: health innovation and practical technology.""",
            "LIB": """**Career - Uranus in Libra**: Revolutionary relationships in career. Innovative partnerships and artistic expression. Career changes: relationship innovation and artistic revolution. Career genius: partnership technology and design innovation.""",
            "SCO": """**Career - Uranus in Scorpio**: Transformative insights in career. Psychological breakthroughs and investigative innovation. Career changes: psychological technology and research revolution. Career genius: psychological innovation and investigative technology.""",
            "SAG": """**Career - Uranus in Sagittarius**: Philosophical innovation in career. Expansion of consciousness in education and travel. Career changes: educational technology and travel innovation. Career genius: educational innovation and philosophical technology.""",
            "CAP": """**Career - Uranus in Capricorn**: Structural reforms in career. Institutional changes and authority innovation. Career changes: structural revolution and institutional technology. Career genius: organizational innovation and structural technology.""",
            "AQU": """**Career - Uranus in Aquarius**: Natural innovator in career. Humanitarian vision and technological breakthrough. Career changes: social technology and humanitarian innovation. Career genius: social innovation and future technology.""",
            "PIS": """**Career - Uranus in Pisces**: Spiritual insights in career. Mystical revelations and creative inspiration. Career changes: spiritual technology and creative innovation. Career genius: spiritual innovation and creative technology."""
        },

        "Neptune": {
            "ARI": """**Career - Neptune in Aries**: Spiritual pioneering in career. Inspired action and visionary leadership. Career dreams: inspirational leadership and spiritual entrepreneurship. Career inspiration: pioneering spiritual businesses and inspired action.""",
            "TAU": """**Career - Neptune in Taurus**: Dreamy values in career. Idealized security and mystical appreciation. Career dreams: beautiful businesses and spiritual values. Career inspiration: sustainable beauty businesses and spiritual finance.""",
            "GEM": """**Career - Neptune in Gemini**: Imaginative communication in career. Inspired ideas and spiritual learning. Career dreams: inspirational communication and spiritual teaching. Career inspiration: spiritual media and inspired education.""",
            "CAN": """**Career - Neptune in Cancer**: Mystical home life in career. Spiritual nurturing and emotional healing. Career dreams: spiritual caregiving and emotional healing businesses. Career inspiration: spiritual real estate and healing hospitality.""",
            "LEO": """**Career - Neptune in Leo**: Creative inspiration in career. Dramatic spirituality and expressive healing. Career dreams: spiritual entertainment and creative healing. Career inspiration: spiritual arts and inspirational leadership.""",
            "VIR": """**Career - Neptune in Virgo**: Service through inspiration in career. Healing compassion and practical spirituality. Career dreams: spiritual health service and inspired practical work. Career inspiration: spiritual healthcare and compassionate service.""",
            "LIB": """**Career - Neptune in Libra**: Idealistic partnerships in career. Spiritual harmony and beautiful relationships. Career dreams: spiritual design and harmonious partnerships. Career inspiration: spiritual law and beautiful healing.""",
            "SCO": """**Career - Neptune in Scorpio**: Deep spiritual transformation in career. Psychic sensitivity and mystical depth. Career dreams: spiritual psychology and transformative healing. Career inspiration: spiritual research and psychic healing.""",
            "SAG": """**Career - Neptune in Sagittarius**: Philosophical idealism in career. Spiritual expansion and visionary travel. Career dreams: spiritual education and philosophical travel. Career inspiration: spiritual publishing and visionary education.""",
            "CAP": """**Career - Neptune in Capricorn**: Structured spirituality in career. Institutional faith and disciplined vision. Career dreams: spiritual institutions and structured healing. Career inspiration: spiritual government and organized compassion.""",
            "AQU": """**Career - Neptune in Aquarius**: Collective ideals in career. Humanitarian dreams and universal vision. Career dreams: spiritual technology and humanitarian innovation. Career inspiration: social spirituality and collective healing.""",
            "PIS": """**Career - Neptune in Pisces**: Natural mystic in career. Spiritual connection and universal compassion. Career dreams: spiritual arts and universal healing. Career inspiration: compassionate creativity and mystical service."""
        },

        "Pluto": {
            "ARI": """**Career - Pluto in Aries**: Transformative career initiative. Rebirth through action and leadership. Career transformation: personal leadership style and career identity. Career power: revolutionary leadership and transformative action.""",
            "TAU": """**Career - Pluto in Taurus**: Deep financial transformation. Value regeneration and economic revolution. Career transformation: financial values and resource management. Career power: financial transformation and value revolution.""",
            "GEM": """**Career - Pluto in Gemini**: Psychological communication in career. Mental transformation and information revolution. Career transformation: communication style and information processing. Career power: communication transformation and mental revolution.""",
            "CAN": """**Career - Pluto in Cancer**: Emotional rebirth in career. Family transformation and emotional revolution. Career transformation: emotional patterns and family business. Career power: emotional transformation and family healing.""",
            "LEO": """**Career - Pluto in Leo**: Creative transformation in career. Expressive rebirth and dramatic revolution. Career transformation: creative expression and romantic relationships at work. Career power: creative revolution and expressive transformation.""",
            "VIR": """**Career - Pluto in Virgo**: Service transformation in career. Health regeneration and practical revolution. Career transformation: health routines and service approach. Career power: health transformation and service revolution.""",
            "LIB": """**Career - Pluto in Libra**: Relationship transformation in career. Artistic rebirth and social revolution. Career transformation: partnerships and artistic expression. Career power: relationship revolution and artistic transformation.""",
            "SCO": """**Career - Pluto in Scorpio**: Deep psychological transformation in career. Natural rebirth and complete regeneration. Career transformation: psychological patterns and intimate work relationships. Career power: psychological revolution and complete transformation.""",
            "SAG": """**Career - Pluto in Sagittarius**: Philosophical transformation in career. Belief regeneration and truth revolution. Career transformation: beliefs and philosophical outlook. Career power: philosophical revolution and truth transformation.""",
            "CAP": """**Career - Pluto in Capricorn**: Structural transformation in career. Power rebirth and institutional revolution. Career transformation: career structures and authority relationships. Career power: structural revolution and power transformation.""",
            "AQU": """**Career - Pluto in Aquarius**: Collective transformation in career. Social regeneration and group revolution. Career transformation: social networks and group affiliations. Career power: social revolution and collective transformation.""",
            "PIS": """**Career - Pluto in Pisces**: Spiritual transformation in career. Mystical rebirth and universal revolution. Career transformation: spiritual understanding and creative inspiration. Career power: spiritual revolution and universal transformation."""
        }
    }

    # RELATIONSHIPS INTERPRETATIONS - ALL 10 PLANETS
    relationships_interpretations = {
        "Sun": {
            "ARI": """**Relationships - Sun in Aries**: Direct and passionate in relationships. Natural leader who values independence. Needs excitement and challenge in partnerships. Seeks dynamic and adventurous partners. Relationship style: independent and enthusiastic.""",
            "TAU": """**Relationships - Sun in Taurus**: Loyal and stable partner. Values security and physical comfort in relationships. Builds lasting bonds. Seeks reliable and sensual partners. Relationship style: steady and devoted.""",
            "GEM": """**Relationships - Sun in Gemini**: Communicative and curious in love. Needs mental stimulation and variety. Enjoys intellectual connection. Seeks intelligent and versatile partners. Relationship style: communicative and adaptable.""",
            "CAN": """**Relationships - Sun in Cancer**: Nurturing and protective partner. Strong family orientation and emotional bonds. Creates emotional security. Seeks caring and family-oriented partners. Relationship style: emotional and protective.""",
            "LEO": """**Relationships - Sun in Leo**: Generous and dramatic in relationships. Needs admiration and recognition. Romantic and loyal. Seeks appreciative and confident partners. Relationship style: generous and romantic.""",
            "VIR": """**Relationships - Sun in Virgo**: Practical and helpful partner. Shows love through service and attention. Analytical in relationships. Seeks reliable and health-conscious partners. Relationship style: practical and attentive.""",
            "LIB": """**Relationships - Sun in Libra**: Harmonious and diplomatic. Seeks balance and partnership in relationships. Values beauty and harmony. Seeks beautiful and balanced partners. Relationship style: harmonious and fair.""",
            "SCO": """**Relationships - Sun in Scorpio**: Intense and passionate. Seeks deep emotional transformation in love. Loyal and committed. Seeks deeply emotional and loyal partners. Relationship style: intense and transformative.""",
            "SAG": """**Relationships - Sun in Sagittarius**: Adventurous and philosophical. Values freedom and honesty in relationships. Needs space and adventure. Seeks adventurous and philosophical partners. Relationship style: adventurous and honest.""",
            "CAP": """**Relationships - Sun in Capricorn**: Serious and responsible partner. Seeks stability and long-term commitment. Builds relationships carefully. Seeks ambitious and reliable partners. Relationship style: serious and committed.""",
            "AQU": """**Relationships - Sun in Aquarius**: Independent and unconventional. Values friendship and intellectual connection. Needs freedom in relationships. Seeks unique and independent partners. Relationship style: independent and friendly.""",
            "PIS": """**Relationships - Sun in Pisces**: Compassionate and romantic. Seeks spiritual connection and soulmates. Unconditional love approach. Seeks sensitive and spiritual partners. Relationship style: compassionate and spiritual."""
        },

        "Moon": {
            "ARI": """**Relationships - Moon in Aries**: Emotionally direct and passionate. Needs independence and excitement in relationships. Quick to react emotionally. Seeks partners who respect independence. Emotional needs: excitement and recognition.""",
            "TAU": """**Relationships - Moon in Taurus**: Emotionally stable and loyal. Values security and physical comfort. Resistant to emotional changes. Seeks reliable and comforting partners. Emotional needs: security and comfort.""",
            "GEM": """**Relationships - Moon in Gemini**: Emotionally communicative and curious. Needs mental connection and variety. Processes emotions through talking. Seeks communicative and intelligent partners. Emotional needs: mental stimulation and variety.""",
            "CAN": """**Relationships - Moon in Cancer**: Deeply nurturing and protective. Strong emotional bonds and family orientation. Needs emotional security. Seeks caring and family-focused partners. Emotional needs: emotional security and family connection.""",
            "LEO": """**Relationships - Moon in Leo**: Emotionally generous and proud. Needs recognition and appreciation. Dramatic emotional expression. Seeks admiring and generous partners. Emotional needs: recognition and appreciation.""",
            "VIR": """**Relationships - Moon in Virgo**: Emotionally practical and helpful. Shows care through service. Needs order in relationships. Seeks reliable and health-conscious partners. Emotional needs: order and practical care.""",
            "LIB": """**Relationships - Moon in Libra**: Emotionally harmonious and diplomatic. Seeks balance and partnership. Avoids emotional conflicts. Seeks beautiful and balanced partners. Emotional needs: harmony and beauty.""",
            "SCO": """**Relationships - Moon in Scorpio**: Emotionally intense and passionate. Deep emotional connections and need for intimacy. Powerful emotional bonds. Seeks deeply emotional and loyal partners. Emotional needs: depth and intensity.""",
            "SAG": """**Relationships - Moon in Sagittarius**: Emotionally adventurous and optimistic. Needs freedom and philosophical connection. Processes emotions through learning. Seeks adventurous and philosophical partners. Emotional needs: freedom and expansion.""",
            "CAP": """**Relationships - Moon in Capricorn**: Emotionally responsible and reserved. Controls feelings carefully. Builds emotional security slowly. Seeks ambitious and reliable partners. Emotional needs: security and respect.""",
            "AQU": """**Relationships - Moon in Aquarius**: Emotionally independent and unconventional. Unique emotional expression. Needs freedom in emotional life. Seeks unique and independent partners. Emotional needs: freedom and individuality.""",
            "PIS": """**Relationships - Moon in Pisces**: Emotionally compassionate and intuitive. Deep spiritual connections. Strong empathy in relationships. Seeks sensitive and spiritual partners. Emotional needs: spiritual connection and compassion."""
        },

        "Mercury": {
            "ARI": """**Relationships - Mercury in Aries**: Direct and spontaneous communication in relationships. Expresses love ideas boldly and immediately. Competitive in intellectual connection. Communication style: direct and enthusiastic.""",
            "TAU": """**Relationships - Mercury in Taurus**: Practical and persistent communication. Values stable and honest dialogue. Slow but sure in expressing feelings. Communication style: practical and reliable.""",
            "GEM": """**Relationships - Mercury in Gemini**: Playful and curious communication. Enjoys mental stimulation and variety in conversations. Natural flirt and communicator. Communication style: versatile and intellectual.""",
            "CAN": """**Relationships - Mercury in Cancer**: Intuitive and emotional communication. Expresses with heart and memory. Strong emotional memory in relationships. Communication style: emotional and nostalgic.""",
            "LEO": """**Relationships - Mercury in Leo**: Confident and dramatic communication. Expressive and authoritative in love expressions. Natural romantic communicator. Communication style: expressive and generous.""",
            "VIR": """**Relationships - Mercury in Virgo**: Analytical and precise communication. Thoughtful and attentive words. Shows care through practical advice. Communication style: practical and helpful.""",
            "LIB": """**Relationships - Mercury in Libra**: Diplomatic and balanced communication. Seeks harmony in dialogue. Beautiful and gracious expression. Communication style: harmonious and fair.""",
            "SCO": """**Relationships - Mercury in Scorpio**: Investigative and profound communication. Seeks deep truth in relationships. Intense and penetrating conversations. Communication style: intense and transformative.""",
            "SAG": """**Relationships - Mercury in Sagittarius**: Philosophical and honest communication. Values expansive discussions and truth. Natural teacher in relationships. Communication style: honest and expansive.""",
            "CAP": """**Relationships - Mercury in Capricorn**: Practical and organized communication. Builds relationships carefully with words. Serious and committed in expressions. Communication style: serious and reliable.""",
            "AQU": """**Relationships - Mercury in Aquarius**: Innovative and original communication. Unique way of expressing love. Intellectual and detached approach. Communication style: unique and intellectual.""",
            "PIS": """**Relationships - Mercury in Pisces**: Intuitive and compassionate communication. Romantic and dreamy expression. Empathic and spiritual conversations. Communication style: compassionate and imaginative."""
        },

        "Venus": {
            "ARI": """**Relationships - Venus in Aries**: Direct and passionate in love. Attracted to challenge and excitement. Independent and bold in relationships. Love style: spontaneous and adventurous. Values: independence and excitement.""",
            "TAU": """**Relationships - Venus in Taurus**: Sensual and loyal. Values stability and physical pleasure. Patient and devoted in love. Love style: steady and sensual. Values: security and comfort.""",
            "GEM": """**Relationships - Venus in Gemini**: Playful and communicative. Needs mental connection and variety. Enjoys flirtation and conversation. Love style: intellectual and versatile. Values: communication and variety.""",
            "CAN": """**Relationships - Venus in Cancer**: Nurturing and emotional. Seeks security and deep bonding. Protective and family-oriented. Love style: caring and protective. Values: emotional security and family.""",
            "LEO": """**Relationships - Venus in Leo**: Generous and dramatic. Needs romance and admiration. Creative expression of affection. Love style: romantic and generous. Values: recognition and creativity.""",
            "VIR": """**Relationships - Venus in Virgo**: Practical and helpful. Shows love through service and care. Attention to partner's needs. Love style: practical and attentive. Values: service and health.""",
            "LIB": """**Relationships - Venus in Libra**: Harmonious and artistic. Seeks balance and partnership. Creates beauty in relationships. Love style: harmonious and beautiful. Values: harmony and partnership.""",
            "SCO": """**Relationships - Venus in Scorpio**: Intense and passionate. Seeks deep emotional bonds. Magnetic passion and total devotion. Love style: intense and transformative. Values: depth and loyalty.""",
            "SAG": """**Relationships - Venus in Sagittarius**: Adventurous and freedom-loving. Values honesty and exploration. Needs space and adventure. Love style: adventurous and honest. Values: freedom and honesty.""",
            "CAP": """**Relationships - Venus in Capricorn**: Serious and responsible. Seeks stability and commitment. Practical in love. Love style: serious and committed. Values: stability and commitment.""",
            "AQU": """**Relationships - Venus in Aquarius**: Unconventional and friendly. Values friendship and independence. Original expression of love. Love style: unique and friendly. Values: friendship and independence.""",
            "PIS": """**Relationships - Venus in Pisces**: Romantic and compassionate. Seeks spiritual connection. Empathic and unconditional in love. Love style: spiritual and compassionate. Values: spiritual connection and compassion."""
        },

        "Mars": {
            "ARI": """**Relationships - Mars in Aries**: Passionate and direct sexual energy. Enthusiastic and competitive. Bold initiator in relationships. Needs excitement and challenge. Sexual style: adventurous and spontaneous.""",
            "TAU": """**Relationships - Mars in Taurus**: Sensual and persistent. Values physical pleasure and stability. Patient and thorough lover. Needs security and comfort. Sexual style: sensual and steady.""",
            "GEM": """**Relationships - Mars in Gemini**: Playful and communicative. Enjoys variety and mental stimulation. Experimental and verbal in relationships. Needs mental connection. Sexual style: versatile and communicative.""",
            "CAN": """**Relationships - Mars in Cancer**: Protective and emotional. Deep emotional connections. Nurturing and sensitive approach. Needs emotional security. Sexual style: emotional and protective.""",
            "LEO": """**Relationships - Mars in Leo**: Confident and dramatic. Needs admiration and creative expression. Generous and passionate. Needs recognition and appreciation. Sexual style: dramatic and generous.""",
            "VIR": """**Relationships - Mars in Virgo**: Precise and attentive. Shows care through attention to details. Health-conscious and practical. Needs order and cleanliness. Sexual style: attentive and practical.""",
            "LIB": """**Relationships - Mars in Libra**: Diplomatic and balanced. Seeks harmony and mutual pleasure. Artistic and considerate. Needs peace and beauty. Sexual style: harmonious and balanced.""",
            "SCO": """**Relationships - Mars in Scorpio**: Intense and transformative. Deep psychological connections. Powerful and committed. Needs deep intimacy. Sexual style: intense and powerful.""",
            "SAG": """**Relationships - Mars in Sagittarius**: Adventurous and optimistic. Values freedom and exploration. Philosophical and honest. Needs space and adventure. Sexual style: adventurous and optimistic.""",
            "CAP": """**Relationships - Mars in Capricorn**: Ambitious and disciplined. Builds intimacy carefully. Traditional and committed. Needs stability and commitment. Sexual style: disciplined and ambitious.""",
            "AQU": """**Relationships - Mars in Aquarius**: Innovative and unconventional. Experimental and freedom-loving. Intellectual and unique. Needs freedom and innovation. Sexual style: innovative and experimental.""",
            "PIS": """**Relationships - Mars in Pisces**: Compassionate and intuitive. Spiritual and romantic approach. Empathic and sensitive. Needs spiritual connection. Sexual style: compassionate and intuitive."""
        },

        "Jupiter": {
            "ARI": """**Relationships - Jupiter in Aries**: Expansive and confident in relationships. Natural optimism and enthusiasm. Growth through adventurous partnerships. Relationship expansion: through excitement and new experiences.""",
            "TAU": """**Relationships - Jupiter in Taurus**: Steady growth in love. Values security and comfort expansion. Growth through stable partnerships. Relationship expansion: through comfort and material security.""",
            "GEM": """**Relationships - Jupiter in Gemini**: Versatile expansion through communication. Enjoys learning in partnerships. Growth through intellectual connection. Relationship expansion: through communication and variety.""",
            "CAN": """**Relationships - Jupiter in Cancer**: Nurturing growth through emotional security. Family-oriented expansion. Growth through emotional connection. Relationship expansion: through family and emotional security.""",
            "LEO": """**Relationships - Jupiter in Leo**: Creative expansion through recognition. Generous and warm-hearted. Growth through appreciation. Relationship expansion: through creativity and generosity.""",
            "VIR": """**Relationships - Jupiter in Virgo**: Analytical growth through service. Improvement in practical love. Growth through helpful partnership. Relationship expansion: through practical service and health.""",
            "LIB": """**Relationships - Jupiter in Libra**: Harmonious expansion through partnerships. Seeks beauty and balance. Growth through beautiful relationships. Relationship expansion: through harmony and partnership.""",
            "SCO": """**Relationships - Jupiter in Scorpio**: Transformative growth through depth. Philosophical approach to intimacy. Growth through deep connection. Relationship expansion: through transformation and depth.""",
            "SAG": """**Relationships - Jupiter in Sagittarius**: Natural expansion through adventure. Optimistic and freedom-loving. Growth through philosophical connection. Relationship expansion: through adventure and learning.""",
            "CAP": """**Relationships - Jupiter in Capricorn**: Ambitious growth through discipline. Builds long-term relationships. Growth through commitment. Relationship expansion: through stability and tradition.""",
            "AQU": """**Relationships - Jupiter in Aquarius**: Innovative expansion through originality. Progressive relationship values. Growth through friendship. Relationship expansion: through innovation and friendship.""",
            "PIS": """**Relationships - Jupiter in Pisces**: Compassionate growth through intuition. Spiritual connection in love. Growth through unconditional love. Relationship expansion: through spirituality and compassion."""
        },

        "Saturn": {
            "ARI": """**Relationships - Saturn in Aries**: Disciplined approach to relationships. Learning responsibility through independence. Builds relationships through courage. Relationship lessons: patience and consideration.""",
            "TAU": """**Relationships - Saturn in Taurus**: Stable and persistent in love. Builds security through commitment. Values loyalty and reliability. Relationship lessons: flexibility and change.""",
            "GEM": """**Relationships - Saturn in Gemini**: Organized communication in relationships. Responsibility in dialogue and learning. Builds through intellectual connection. Relationship lessons: depth and focus.""",
            "CAN": """**Relationships - Saturn in Cancer**: Emotional responsibility in love. Building family security and traditions. Nurturing with discipline. Relationship lessons: emotional boundaries.""",
            "LEO": """**Relationships - Saturn in Leo**: Creative leadership responsibility. Structured self-expression in relationships. Generous with boundaries. Relationship lessons: humility and sharing.""",
            "VIR": """**Relationships - Saturn in Virgo**: Analytical service discipline. Practical approach to love and care. Helpful with organization. Relationship lessons: accepting imperfection.""",
            "LIB": """**Relationships - Saturn in Libra**: Partnership responsibility. Balanced and committed relationships. Diplomatic with structure. Relationship lessons: independent decision-making.""",
            "SCO": """**Relationships - Saturn in Scorpio**: Transformative discipline. Deep commitment in intimate relationships. Intense with boundaries. Relationship lessons: trust and vulnerability.""",
            "SAG": """**Relationships - Saturn in Sagittarius**: Philosophical responsibility. Structured expansion in love. Adventurous with commitment. Relationship lessons: commitment and details.""",
            "CAP": """**Relationships - Saturn in Capricorn**: Natural responsibility in relationships. Built for long-term commitment. Serious and reliable. Relationship lessons: enjoyment and spontaneity.""",
            "AQU": """**Relationships - Saturn in Aquarius**: Innovative responsibility. Structured progressive relationship values. Friendly with commitment. Relationship lessons: emotional connection.""",
            "PIS": """**Relationships - Saturn in Pisces**: Compassionate discipline. Structured spiritual connection. Empathic with boundaries. Relationship lessons: practical boundaries."""
        },

        "Uranus": {
            "ARI": """**Relationships - Uranus in Aries**: Innovative relationship breakthroughs. Pioneering new forms of partnership. Sudden attractions and changes. Relationship freedom: independence and excitement.""",
            "TAU": """**Relationships - Uranus in Taurus**: Unconventional values in love. Slow but revolutionary changes in relationships. Innovative approach to security. Relationship freedom: financial independence and values.""",
            "GEM": """**Relationships - Uranus in Gemini**: Revolutionary communication in relationships. Sudden insights and mental connections. Innovative information sharing. Relationship freedom: communication and variety.""",
            "CAN": """**Relationships - Uranus in Cancer**: Innovative emotional security. New approaches to family and nurturing. Unconventional home life. Relationship freedom: emotional independence.""",
            "LEO": """**Relationships - Uranus in Leo**: Creative breakthroughs in love. Unique self-expression and dramatic changes. Innovative romance. Relationship freedom: creative expression.""",
            "VIR": """**Relationships - Uranus in Virgo**: Unconventional service approaches. Innovative practical care and health. Revolutionary daily routines. Relationship freedom: practical independence.""",
            "LIB": """**Relationships - Uranus in Libra**: Revolutionary partnerships. New approaches to balance and harmony. Innovative beauty in relationships. Relationship freedom: partnership innovation.""",
            "SCO": """**Relationships - Uranus in Scorpio**: Transformative insights in intimacy. Psychological breakthroughs and depth. Innovative sexual expression. Relationship freedom: emotional transformation.""",
            "SAG": """**Relationships - Uranus in Sagittarius**: Philosophical innovation in relationships. Expanding consciousness through partnership. Innovative beliefs about love. Relationship freedom: philosophical expansion.""",
            "CAP": """**Relationships - Uranus in Capricorn**: Structural reforms in relationships. Institutional changes and commitment innovation. Revolutionary traditional values. Relationship freedom: structural independence.""",
            "AQU": """**Relationships - Uranus in Aquarius**: Natural innovator in relationships. Humanitarian vision in love. Progressive partnership values. Relationship freedom: social innovation.""",
            "PIS": """**Relationships - Uranus in Pisces**: Spiritual insights in relationships. Mystical revelations and creative inspiration. Innovative spiritual connection. Relationship freedom: spiritual independence."""
        },

        "Neptune": {
            "ARI": """**Relationships - Neptune in Aries**: Spiritual pioneering in relationships. Inspired action and vision in love. Dreamy idealism about partners. Relationship dreams: inspirational partnerships and spiritual adventure.""",
            "TAU": """**Relationships - Neptune in Taurus**: Dreamy values in partnerships. Idealized security and comfort. Spiritual appreciation of beauty. Relationship dreams: beautiful security and sensual spirituality.""",
            "GEM": """**Relationships - Neptune in Gemini**: Imaginative communication in relationships. Inspired ideas and spiritual learning. Dreamy intellectual connection. Relationship dreams: spiritual communication and inspired learning.""",
            "CAN": """**Relationships - Neptune in Cancer**: Mystical emotional security. Spiritual nurturing and family connection. Dreamy home life. Relationship dreams: spiritual family and emotional healing.""",
            "LEO": """**Relationships - Neptune in Leo**: Creative inspiration in relationships. Dramatic spirituality and expressive love. Dreamy romance. Relationship dreams: spiritual creativity and inspirational love.""",
            "VIR": """**Relationships - Neptune in Virgo**: Service through inspiration in relationships. Healing compassion and practical spirituality. Dreamy service. Relationship dreams: spiritual service and healing partnership.""",
            "LIB": """**Relationships - Neptune in Libra**: Idealistic spiritual partnerships. Spiritual harmony and beautiful relationships. Dreamy balance. Relationship dreams: spiritual harmony and beautiful connection.""",
            "SCO": """**Relationships - Neptune in Scorpio**: Deep spiritual transformation in relationships. Psychic sensitivity and mystical depth. Dreamy intensity. Relationship dreams: spiritual transformation and psychic connection.""",
            "SAG": """**Relationships - Neptune in Sagittarius**: Philosophical idealism in relationships. Spiritual expansion and visionary connection. Dreamy adventure. Relationship dreams: spiritual adventure and philosophical love.""",
            "CAP": """**Relationships - Neptune in Capricorn**: Structured spirituality in relationships. Institutional faith and disciplined vision. Dreamy commitment. Relationship dreams: spiritual commitment and structured love.""",
            "AQU": """**Relationships - Neptune in Aquarius**: Collective ideals in relationships. Humanitarian dreams and universal vision. Dreamy innovation. Relationship dreams: spiritual innovation and universal love.""",
            "PIS": """**Relationships - Neptune in Pisces**: Natural mystic in relationships. Spiritual connection and universal compassion. Dreamy romance. Relationship dreams: spiritual union and compassionate love."""
        },

        "Pluto": {
            "ARI": """**Relationships - Pluto in Aries**: Transformative relationship initiative. Rebirth through passionate action. Powerful new beginnings in love. Relationship transformation: personal identity and leadership in partnerships.""",
            "TAU": """**Relationships - Pluto in Taurus**: Deep value transformation in relationships. Regeneration of security and values. Economic revolution in partnerships. Relationship transformation: values and financial security.""",
            "GEM": """**Relationships - Pluto in Gemini**: Psychological communication in relationships. Mental transformation and information revolution. Deep mental connection. Relationship transformation: communication patterns and mental intimacy.""",
            "CAN": """**Relationships - Pluto in Cancer**: Emotional rebirth in partnerships. Family transformation and emotional revolution. Deep emotional healing. Relationship transformation: emotional patterns and family dynamics.""",
            "LEO": """**Relationships - Pluto in Leo**: Creative transformation in relationships. Rebirth through self-expression and romance. Dramatic love changes. Relationship transformation: creative expression and romantic identity.""",
            "VIR": """**Relationships - Pluto in Virgo**: Service transformation in relationships. Health regeneration and practical revolution. Deep practical connection. Relationship transformation: health routines and service approach.""",
            "LIB": """**Relationships - Pluto in Libra**: Relationship transformation. Artistic rebirth and social revolution. Deep partnership changes. Relationship transformation: partnership dynamics and artistic expression.""",
            "SCO": """**Relationships - Pluto in Scorpio**: Deep psychological transformation in relationships. Natural rebirth and complete regeneration. Ultimate intimacy. Relationship transformation: psychological patterns and sexual intimacy.""",
            "SAG": """**Relationships - Pluto in Sagittarius**: Philosophical transformation in relationships. Belief regeneration and truth revolution. Deep philosophical connection. Relationship transformation: beliefs and philosophical outlook.""",
            "CAP": """**Relationships - Pluto in Capricorn**: Structural transformation in relationships. Power rebirth and commitment revolution. Deep structural changes. Relationship transformation: commitment structures and authority dynamics.""",
            "AQU": """**Relationships - Pluto in Aquarius**: Collective transformation in relationships. Social regeneration and group revolution. Deep social changes. Relationship transformation: social networks and group affiliations.""",
            "PIS": """**Relationships - Pluto in Pisces**: Spiritual transformation in relationships. Mystical rebirth and universal revolution. Deep spiritual union. Relationship transformation: spiritual understanding and creative inspiration."""
        }
    }

    # SPIRITUAL INTERPRETATIONS - ALL 10 PLANETS
    spiritual_interpretations = {
        "Sun": {
            "ARI": """**Spiritual - Sun in Aries**: Spiritual pioneer and warrior. Direct connection to divine energy. Courageous spiritual seeker. Inspirational spiritual leader. Spiritual path: active service and courageous truth-seeking. Spiritual gift: inspirational leadership.""",
            "TAU": """**Spiritual - Sun in Taurus**: Grounded spirituality. Connection to earth energies and practical mysticism. Sensory spiritual experiences. Spiritual path: nature worship and practical spirituality. Spiritual gift: earthly wisdom.""",
            "GEM": """**Spiritual - Sun in Gemini**: Communicative spirituality. Channel for divine messages and teachings. Learning through spiritual concepts. Spiritual path: study and teaching of spiritual wisdom. Spiritual gift: spiritual communication.""",
            "CAN": """**Spiritual - Sun in Cancer**: Nurturing spiritual path. Connection to ancestral wisdom and emotional healing. Home-based spirituality. Spiritual path: family traditions and emotional healing. Spiritual gift: emotional healing.""",
            "LEO": """**Spiritual - Sun in Leo**: Creative spirituality. Divine expression through art and performance. Inspirational spiritual teacher. Spiritual path: creative expression and inspirational leadership. Spiritual gift: creative inspiration.""",
            "VIR": """**Spiritual - Sun in Virgo**: Service-oriented spirituality. Healing through practical service and analysis. Spiritual health practices. Spiritual path: service and healing through practical means. Spiritual gift: healing service.""",
            "LIB": """**Spiritual - Sun in Libra**: Harmonious spirituality. Connection to beauty, balance, and divine partnership. Relationship spirituality. Spiritual path: creating harmony and beautiful spaces. Spiritual gift: harmonious healing.""",
            "SCO": """**Spiritual - Sun in Scorpio**: Transformative spirituality. Deep psychic abilities and rebirth. Mystical transformation. Spiritual path: deep transformation and psychological healing. Spiritual gift: transformative power.""",
            "SAG": """**Spiritual - Sun in Sagittarius**: Philosophical spirituality. Expansion through truth-seeking and adventure. Spiritual exploration. Spiritual path: philosophical study and spiritual travel. Spiritual gift: philosophical wisdom.""",
            "CAP": """**Spiritual - Sun in Capricorn**: Structured spirituality. Building spiritual foundations and discipline. Traditional spiritual paths. Spiritual path: disciplined practice and traditional wisdom. Spiritual gift: spiritual discipline.""",
            "AQU": """**Spiritual - Sun in Aquarius**: Innovative spirituality. Connection to collective consciousness and futurism. Spiritual technology. Spiritual path: innovation and collective enlightenment. Spiritual gift: innovative vision.""",
            "PIS": """**Spiritual - Sun in Pisces**: Compassionate spirituality. Deep connection to universal love and mercy. Natural mystic and healer. Spiritual path: compassionate service and mystical union. Spiritual gift: universal compassion."""
        },

        "Moon": {
            "ARI": """**Spiritual - Moon in Aries**: Emotional spiritual pioneer. Direct intuitive connection to divine. Courageous emotional spirituality. Spiritual emotions: fiery devotion and enthusiastic practice. Spiritual intuition: immediate guidance.""",
            "TAU": """**Spiritual - Moon in Taurus**: Grounded emotional spirituality. Practical mystical experiences. Sensory spiritual connection. Spiritual emotions: stable devotion and sensory meditation. Spiritual intuition: earthly wisdom.""",
            "GEM": """**Spiritual - Moon in Gemini**: Communicative emotional spirituality. Learning and teaching spiritual concepts. Mental spiritual processing. Spiritual emotions: curious devotion and intellectual exploration. Spiritual intuition: mental guidance.""",
            "CAN": """**Spiritual - Moon in Cancer**: Nurturing emotional path. Connection to ancestral spiritual wisdom. Emotional spiritual healing. Spiritual emotions: nurturing devotion and emotional healing. Spiritual intuition: emotional guidance.""",
            "LEO": """**Spiritual - Moon in Leo**: Creative emotional spirituality. Dramatic spiritual expression. Inspirational emotional connection. Spiritual emotions: generous devotion and creative expression. Spiritual intuition: inspirational guidance.""",
            "VIR": """**Spiritual - Moon in Virgo**: Service-oriented emotional spirituality. Healing through practical compassion. Spiritual service. Spiritual emotions: practical devotion and healing service. Spiritual intuition: practical guidance.""",
            "LIB": """**Spiritual - Moon in Libra**: Harmonious emotional spirituality. Balanced spiritual partnerships. Beauty in spiritual practice. Spiritual emotions: harmonious devotion and beautiful practice. Spiritual intuition: harmonious guidance.""",
            "SCO": """**Spiritual - Moon in Scorpio**: Transformative emotional spirituality. Deep psychic emotional connections. Emotional rebirth. Spiritual emotions: intense devotion and transformative experiences. Spiritual intuition: psychic guidance.""",
            "SAG": """**Spiritual - Moon in Sagittarius**: Philosophical emotional spirituality. Expansion through emotional truth. Spiritual adventure. Spiritual emotions: adventurous devotion and philosophical exploration. Spiritual intuition: expansive guidance.""",
            "CAP": """**Spiritual - Moon in Capricorn**: Structured emotional spirituality. Disciplined emotional spiritual practice. Traditional emotional spirituality. Spiritual emotions: disciplined devotion and traditional practice. Spiritual intuition: structured guidance.""",
            "AQU": """**Spiritual - Moon in Aquarius**: Innovative emotional spirituality. Progressive spiritual emotions. Collective emotional connection. Spiritual emotions: unique devotion and collective consciousness. Spiritual intuition: innovative guidance.""",
            "PIS": """**Spiritual - Moon in Pisces**: Compassionate emotional spirituality. Deep spiritual emotional connections. Universal emotional love. Spiritual emotions: compassionate devotion and universal love. Spiritual intuition: universal guidance."""
        },

        "Mercury": {
            "ARI": """**Spiritual - Mercury in Aries**: Direct spiritual communication. Pioneering spiritual ideas and concepts. Immediate understanding of spiritual truths. Spiritual thinking: bold and innovative. Spiritual messages: urgent and direct.""",
            "TAU": """**Spiritual - Mercury in Taurus**: Practical spiritual thinking. Grounded mystical communication. Slow but deep understanding of spiritual principles. Spiritual thinking: practical and persistent. Spiritual messages: steady and reliable.""",
            "GEM": """**Spiritual - Mercury in Gemini**: Versatile spiritual communication. Learning and teaching divine wisdom. Understanding multiple spiritual perspectives. Spiritual thinking: adaptable and curious. Spiritual messages: varied and informative.""",
            "CAN": """**Spiritual - Mercury in Cancer**: Intuitive spiritual thinking. Emotional connection to spiritual concepts. Memory of spiritual experiences. Spiritual thinking: emotional and nostalgic. Spiritual messages: comforting and nurturing.""",
            "LEO": """**Spiritual - Mercury in Leo**: Creative spiritual communication. Expressive divine teachings. Grand spiritual concepts and inspiration. Spiritual thinking: creative and dramatic. Spiritual messages: inspirational and generous.""",
            "VIR": """**Spiritual - Mercury in Virgo**: Analytical spiritual thinking. Service-oriented spiritual analysis. Practical application of spiritual principles. Spiritual thinking: precise and helpful. Spiritual messages: practical and healing.""",
            "LIB": """**Spiritual - Mercury in Libra**: Harmonious spiritual communication. Balanced spiritual dialogue. Understanding spiritual balance and justice. Spiritual thinking: diplomatic and fair. Spiritual messages: harmonious and beautiful.""",
            "SCO": """**Spiritual - Mercury in Scorpio**: Transformative spiritual thinking. Deep psychological spiritual insights. Understanding hidden spiritual truths. Spiritual thinking: intense and penetrating. Spiritual messages: transformative and deep.""",
            "SAG": """**Spiritual - Mercury in Sagittarius**: Philosophical spiritual communication. Expansive spiritual learning. Understanding universal spiritual principles. Spiritual thinking: philosophical and broad. Spiritual messages: wise and expansive.""",
            "CAP": """**Spiritual - Mercury in Capricorn**: Structured spiritual thinking. Organized spiritual concepts. Practical application of spiritual discipline. Spiritual thinking: organized and traditional. Spiritual messages: structured and reliable.""",
            "AQU": """**Spiritual - Mercury in Aquarius**: Innovative spiritual communication. Progressive spiritual ideas. Understanding futuristic spiritual concepts. Spiritual thinking: innovative and original. Spiritual messages: revolutionary and visionary.""",
            "PIS": """**Spiritual - Mercury in Pisces**: Intuitive spiritual thinking. Compassionate spiritual insights. Understanding symbolic and mystical truths. Spiritual thinking: intuitive and imaginative. Spiritual messages: compassionate and mystical."""
        },

        "Venus": {
            "ARI": """**Spiritual - Venus in Aries**: Direct spiritual values. Pioneering approach to divine love. Spiritual passion and enthusiasm. Spiritual love: courageous and independent. Spiritual beauty: dynamic and inspiring.""",
            "TAU": """**Spiritual - Venus in Taurus**: Grounded spiritual values. Practical mystical appreciation. Spiritual sensuality and earthly beauty. Spiritual love: stable and devoted. Spiritual beauty: natural and sensual.""",
            "GEM": """**Spiritual - Venus in Gemini**: Communicative spiritual values. Learning through spiritual relationships. Spiritual curiosity and variety. Spiritual love: intellectual and versatile. Spiritual beauty: mental and communicative.""",
            "CAN": """**Spiritual - Venus in Cancer**: Nurturing spiritual values. Emotional connection to divine love. Spiritual family and emotional security. Spiritual love: protective and emotional. Spiritual beauty: comforting and traditional.""",
            "LEO": """**Spiritual - Venus in Leo**: Creative spiritual values. Expressive divine beauty. Spiritual generosity and recognition. Spiritual love: generous and dramatic. Spiritual beauty: magnificent and creative.""",
            "VIR": """**Spiritual - Venus in Virgo**: Service-oriented spiritual values. Practical spiritual harmony. Spiritual health and useful service. Spiritual love: practical and helpful. Spiritual beauty: pure and organized.""",
            "LIB": """**Spiritual - Venus in Libra**: Harmonious spiritual values. Balanced divine partnerships. Spiritual justice and beautiful relationships. Spiritual love: harmonious and fair. Spiritual beauty: balanced and artistic.""",
            "SCO": """**Spiritual - Venus in Scorpio**: Transformative spiritual values. Deep psychological spiritual connections. Spiritual passion and regeneration. Spiritual love: intense and transformative. Spiritual beauty: powerful and mysterious.""",
            "SAG": """**Spiritual - Venus in Sagittarius**: Philosophical spiritual values. Expansive spiritual appreciation. Spiritual adventure and truth-seeking. Spiritual love: adventurous and honest. Spiritual beauty: expansive and philosophical.""",
            "CAP": """**Spiritual - Venus in Capricorn**: Structured spiritual values. Disciplined spiritual love. Spiritual tradition and commitment. Spiritual love: serious and committed. Spiritual beauty: structured and traditional.""",
            "AQU": """**Spiritual - Venus in Aquarius**: Innovative spiritual values. Progressive spiritual relationships. Spiritual friendship and social justice. Spiritual love: unique and friendly. Spiritual beauty: innovative and universal.""",
            "PIS": """**Spiritual - Venus in Pisces**: Compassionate spiritual values. Deep connection to universal love. Spiritual romance and unconditional love. Spiritual love: compassionate and spiritual. Spiritual beauty: dreamy and mystical."""
        },

        "Mars": {
            "ARI": """**Spiritual - Mars in Aries**: Direct spiritual action. Pioneering spiritual initiatives. Spiritual courage and immediate action. Spiritual warrior: bold and enthusiastic. Spiritual mission: inspirational leadership.""",
            "TAU": """**Spiritual - Mars in Taurus**: Grounded spiritual drive. Practical mystical persistence. Spiritual building and material manifestation. Spiritual warrior: persistent and steady. Spiritual mission: earthly transformation.""",
            "GEM": """**Spiritual - Mars in Gemini**: Communicative spiritual action. Learning through spiritual doing. Spiritual teaching and information sharing. Spiritual warrior: versatile and communicative. Spiritual mission: educational expansion.""",
            "CAN": """**Spiritual - Mars in Cancer**: Nurturing spiritual drive. Emotional spiritual protection. Spiritual family and emotional healing. Spiritual warrior: protective and emotional. Spiritual mission: emotional healing.""",
            "LEO": """**Spiritual - Mars in Leo**: Creative spiritual action. Expressive spiritual leadership. Spiritual performance and generous action. Spiritual warrior: confident and generous. Spiritual mission: creative inspiration.""",
            "VIR": """**Spiritual - Mars in Virgo**: Service-oriented spiritual drive. Practical spiritual service. Spiritual health and detailed work. Spiritual warrior: precise and helpful. Spiritual mission: healing service.""",
            "LIB": """**Spiritual - Mars in Libra**: Harmonious spiritual action. Balanced spiritual partnerships. Spiritual justice and peaceful action. Spiritual warrior: diplomatic and balanced. Spiritual mission: harmonious relationships.""",
            "SCO": """**Spiritual - Mars in Scorpio**: Transformative spiritual drive. Deep psychological spiritual power. Spiritual regeneration and intense action. Spiritual warrior: powerful and transformative. Spiritual mission: deep transformation.""",
            "SAG": """**Spiritual - Mars in Sagittarius**: Philosophical spiritual action. Expansive spiritual adventure. Spiritual exploration and truth-seeking. Spiritual warrior: adventurous and optimistic. Spiritual mission: philosophical expansion.""",
            "CAP": """**Spiritual - Mars in Capricorn**: Structured spiritual drive. Disciplined spiritual work. Spiritual authority and traditional action. Spiritual warrior: ambitious and disciplined. Spiritual mission: structural transformation.""",
            "AQU": """**Spiritual - Mars in Aquarius**: Innovative spiritual action. Progressive spiritual initiatives. Spiritual revolution and social change. Spiritual warrior: innovative and independent. Spiritual mission: social innovation.""",
            "PIS": """**Spiritual - Mars in Pisces**: Compassionate spiritual drive. Inspired spiritual service. Spiritual creativity and intuitive action. Spiritual warrior: compassionate and intuitive. Spiritual mission: universal service."""
        },

        "Jupiter": {
            "ARI": """**Spiritual - Jupiter in Aries**: Expansive spiritual seeking. Philosophical exploration and truth-seeking. Spiritual confidence and pioneering wisdom. Spiritual growth: through action and leadership. Spiritual faith: courageous and enthusiastic.""",
            "TAU": """**Spiritual - Jupiter in Taurus**: Grounded spiritual growth. Expansion through practical wisdom. Spiritual abundance and earthly faith. Spiritual growth: through stability and comfort. Spiritual faith: practical and sensual.""",
            "GEM": """**Spiritual - Jupiter in Gemini**: Communicative spirituality. Learning and teaching spiritual concepts. Spiritual curiosity and varied wisdom. Spiritual growth: through learning and communication. Spiritual faith: intellectual and adaptable.""",
            "CAN": """**Spiritual - Jupiter in Cancer**: Nurturing spiritual path. Expansion through emotional wisdom. Spiritual family and emotional faith. Spiritual growth: through emotional security. Spiritual faith: emotional and protective.""",
            "LEO": """**Spiritual - Jupiter in Leo**: Creative spiritual expression. Expansion through divine creativity. Spiritual generosity and inspirational faith. Spiritual growth: through creativity and recognition. Spiritual faith: generous and dramatic.""",
            "VIR": """**Spiritual - Jupiter in Virgo**: Service-oriented spirituality. Growth through healing and analysis. Spiritual health and practical faith. Spiritual growth: through service and health. Spiritual faith: practical and helpful.""",
            "LIB": """**Spiritual - Jupiter in Libra**: Harmonious spiritual path. Expansion through beauty and partnership. Spiritual balance and beautiful faith. Spiritual growth: through harmony and partnership. Spiritual faith: harmonious and artistic.""",
            "SCO": """**Spiritual - Jupiter in Scorpio**: Transformative spiritual growth. Expansion through deep investigation. Spiritual regeneration and intense faith. Spiritual growth: through transformation and depth. Spiritual faith: powerful and regenerative.""",
            "SAG": """**Spiritual - Jupiter in Sagittarius**: Natural spiritual seeker. Philosophical expansion and adventure. Spiritual truth and expansive faith. Spiritual growth: through adventure and learning. Spiritual faith: optimistic and philosophical.""",
            "CAP": """**Spiritual - Jupiter in Capricorn**: Structured spiritual growth. Expansion through discipline and tradition. Spiritual authority and traditional faith. Spiritual growth: through structure and achievement. Spiritual faith: disciplined and traditional.""",
            "AQU": """**Spiritual - Jupiter in Aquarius**: Innovative spirituality. Expansion through universal consciousness. Spiritual progress and visionary faith. Spiritual growth: through innovation and social change. Spiritual faith: progressive and universal.""",
            "PIS": """**Spiritual - Jupiter in Pisces**: Compassionate spiritual path. Expansion through universal love. Spiritual service and unconditional faith. Spiritual growth: through compassion and creativity. Spiritual faith: compassionate and mystical."""
        },

        "Saturn": {
            "ARI": """**Spiritual - Saturn in Aries**: Spiritual discipline through initiative. Learning responsibility through risk. Spiritual courage with structure. Spiritual lessons: patience and consideration. Spiritual mastery: leadership and pioneering.""",
            "TAU": """**Spiritual - Saturn in Taurus**: Grounded spiritual structure. Practical mystical discipline. Spiritual security with responsibility. Spiritual lessons: flexibility and change. Spiritual mastery: earthly wisdom and stability.""",
            "GEM": """**Spiritual - Saturn in Gemini**: Organized spiritual communication. Responsibility in teaching wisdom. Spiritual learning with discipline. Spiritual lessons: depth over breadth. Spiritual mastery: communication and education.""",
            "CAN": """**Spiritual - Saturn in Cancer**: Emotional spiritual responsibility. Building family spiritual security. Spiritual nurturing with boundaries. Spiritual lessons: emotional boundaries. Spiritual mastery: emotional healing and family.""",
            "LEO": """**Spiritual - Saturn in Leo**: Creative spiritual leadership. Structured divine expression. Spiritual generosity with discipline. Spiritual lessons: humility and sharing. Spiritual mastery: creative leadership and inspiration.""",
            "VIR": """**Spiritual - Saturn in Virgo**: Analytical spiritual service. Discipline in healing work. Spiritual health with organization. Spiritual lessons: accepting imperfection. Spiritual mastery: healing service and practical wisdom.""",
            "LIB": """**Spiritual - Saturn in Libra**: Partnership spiritual responsibility. Balanced spiritual commitments. Spiritual harmony with structure. Spiritual lessons: independent decision-making. Spiritual mastery: harmonious relationships and justice.""",
            "SCO": """**Spiritual - Saturn in Scorpio**: Transformative spiritual discipline. Deep psychological commitment. Spiritual regeneration with boundaries. Spiritual lessons: trust and vulnerability. Spiritual mastery: transformation and psychological healing.""",
            "SAG": """**Spiritual - Saturn in Sagittarius**: Philosophical spiritual responsibility. Structured expansion and learning. Spiritual adventure with commitment. Spiritual lessons: commitment and details. Spiritual mastery: philosophical wisdom and teaching.""",
            "CAP": """**Spiritual - Saturn in Capricorn**: Natural spiritual discipline. Built for spiritual mastery. Spiritual tradition with authority. Spiritual lessons: enjoyment and spontaneity. Spiritual mastery: structural wisdom and authority.""",
            "AQU": """**Spiritual - Saturn in Aquarius**: Innovative spiritual responsibility. Structured progressive thinking. Spiritual innovation with tradition. Spiritual lessons: emotional connection. Spiritual mastery: social progress and innovation.""",
            "PIS": """**Spiritual - Saturn in Pisces**: Compassionate spiritual discipline. Structured universal love. Spiritual service with boundaries. Spiritual lessons: practical boundaries. Spiritual mastery: compassionate service and spiritual wisdom."""
        },

        "Uranus": {
            "ARI": """**Spiritual - Uranus in Aries**: Innovative spiritual breakthroughs. Pioneering new spiritual paths. Sudden spiritual insights and actions. Spiritual freedom: independent exploration. Spiritual genius: inspirational innovation.""",
            "TAU": """**Spiritual - Uranus in Taurus**: Unconventional spiritual values. Slow but revolutionary changes. Innovation in spiritual resources. Spiritual freedom: earthly independence. Spiritual genius: practical mysticism.""",
            "GEM": """**Spiritual - Uranus in Gemini**: Revolutionary spiritual communication. Sudden spiritual insights and learning. Innovation in spiritual information. Spiritual freedom: communicative independence. Spiritual genius: spiritual teaching innovation.""",
            "CAN": """**Spiritual - Uranus in Cancer**: Innovative emotional spirituality. New approaches to spiritual nurturing. Unconventional spiritual family. Spiritual freedom: emotional independence. Spiritual genius: emotional healing innovation.""",
            "LEO": """**Spiritual - Uranus in Leo**: Creative spiritual breakthroughs. Unique divine expression. Innovation in spiritual performance. Spiritual freedom: creative independence. Spiritual genius: inspirational creativity.""",
            "VIR": """**Spiritual - Uranus in Virgo**: Unconventional service spirituality. Innovative healing approaches. Revolution in spiritual health. Spiritual freedom: practical independence. Spiritual genius: healing innovation.""",
            "LIB": """**Spiritual - Uranus in Libra**: Revolutionary spiritual partnerships. New approaches to spiritual harmony. Innovation in spiritual beauty. Spiritual freedom: relational independence. Spiritual genius: harmonious innovation.""",
            "SCO": """**Spiritual - Uranus in Scorpio**: Transformative spiritual insights. Psychological breakthroughs and depth. Innovation in spiritual regeneration. Spiritual freedom: emotional transformation. Spiritual genius: transformative innovation.""",
            "SAG": """**Spiritual - Uranus in Sagittarius**: Philosophical spiritual innovation. Expanding consciousness and wisdom. Innovation in spiritual exploration. Spiritual freedom: philosophical independence. Spiritual genius: wisdom innovation.""",
            "CAP": """**Spiritual - Uranus in Capricorn**: Structural spiritual reforms. Institutional changes and authority innovation. Revolution in spiritual tradition. Spiritual freedom: structural independence. Spiritual genius: traditional innovation.""",
            "AQU": """**Spiritual - Uranus in Aquarius**: Natural spiritual innovator. Humanitarian spiritual vision. Progressive spiritual concepts. Spiritual freedom: social independence. Spiritual genius: universal innovation.""",
            "PIS": """**Spiritual - Uranus in Pisces**: Spiritual insights and revelations. Mystical breakthroughs and inspiration. Innovation in spiritual connection. Spiritual freedom: spiritual independence. Spiritual genius: mystical innovation."""
        },

        "Neptune": {
            "ARI": """**Spiritual - Neptune in Aries**: Spiritual pioneering and vision. Inspired action and divine connection. Dreamy spiritual leadership. Spiritual dreams: inspirational action and visionary leadership. Spiritual inspiration: courageous mysticism.""",
            "TAU": """**Spiritual - Neptune in Taurus**: Grounded spiritual dreams. Practical mystical ideals. Dreamy earthly spirituality. Spiritual dreams: beautiful security and sensual mysticism. Spiritual inspiration: earthly beauty.""",
            "GEM": """**Spiritual - Neptune in Gemini**: Communicative spiritual inspiration. Learning through divine messages. Dreamy intellectual spirituality. Spiritual dreams: inspired communication and spiritual learning. Spiritual inspiration: mental mysticism.""",
            "CAN": """**Spiritual - Neptune in Cancer**: Nurturing spiritual dreams. Emotional connection to universal love. Dreamy family spirituality. Spiritual dreams: spiritual family and emotional healing. Spiritual inspiration: emotional mysticism.""",
            "LEO": """**Spiritual - Neptune in Leo**: Creative spiritual inspiration. Dramatic divine expression. Dreamy performative spirituality. Spiritual dreams: spiritual creativity and inspirational expression. Spiritual inspiration: creative mysticism.""",
            "VIR": """**Spiritual - Neptune in Virgo**: Service-oriented spiritual dreams. Healing through inspired compassion. Dreamy practical spirituality. Spiritual dreams: spiritual service and healing work. Spiritual inspiration: practical mysticism.""",
            "LIB": """**Spiritual - Neptune in Libra**: Harmonious spiritual ideals. Balanced divine partnerships. Dreamy beautiful spirituality. Spiritual dreams: spiritual harmony and beautiful relationships. Spiritual inspiration: harmonious mysticism.""",
            "SCO": """**Spiritual - Neptune in Scorpio**: Deep spiritual transformation. Psychic sensitivity and mystical depth. Dreamy intense spirituality. Spiritual dreams: spiritual transformation and psychic connection. Spiritual inspiration: intense mysticism.""",
            "SAG": """**Spiritual - Neptune in Sagittarius**: Philosophical spiritual ideals. Spiritual expansion and visionary travel. Dreamy adventurous spirituality. Spiritual dreams: spiritual adventure and philosophical exploration. Spiritual inspiration: expansive mysticism.""",
            "CAP": """**Spiritual - Neptune in Capricorn**: Structured spiritual dreams. Institutional faith and disciplined vision. Dreamy traditional spirituality. Spiritual dreams: spiritual institutions and structured healing. Spiritual inspiration: traditional mysticism.""",
            "AQU": """**Spiritual - Neptune in Aquarius**: Collective spiritual ideals. Humanitarian dreams and universal vision. Dreamy innovative spirituality. Spiritual dreams: spiritual innovation and universal connection. Spiritual inspiration: innovative mysticism.""",
            "PIS": """**Spiritual - Neptune in Pisces**: Natural spiritual mystic. Deep connection to universal consciousness. Ultimate spiritual dreams. Spiritual dreams: universal love and compassionate service. Spiritual inspiration: universal mysticism."""
        },

        "Pluto": {
            "ARI": """**Spiritual - Pluto in Aries**: Transformative spiritual initiative. Rebirth through divine action. Powerful new spiritual beginnings. Spiritual transformation: personal spiritual identity. Spiritual power: revolutionary spiritual leadership.""",
            "TAU": """**Spiritual - Pluto in Taurus**: Deep spiritual value transformation. Regeneration of earthly spirituality. Economic revolution in spiritual resources. Spiritual transformation: spiritual values and resources. Spiritual power: earthly spiritual revolution.""",
            "GEM": """**Spiritual - Pluto in Gemini**: Psychological spiritual communication. Mental transformation through wisdom. Information revolution in spiritual teaching. Spiritual transformation: spiritual communication and learning. Spiritual power: mental spiritual revolution.""",
            "CAN": """**Spiritual - Pluto in Cancer**: Emotional spiritual rebirth. Family transformation and ancestral healing. Emotional revolution in spiritual nurturing. Spiritual transformation: spiritual family and emotional healing. Spiritual power: emotional spiritual revolution.""",
            "LEO": """**Spiritual - Pluto in Leo**: Creative spiritual transformation. Rebirth through divine expression. Dramatic revolution in spiritual performance. Spiritual transformation: spiritual creativity and expression. Spiritual power: creative spiritual revolution.""",
            "VIR": """**Spiritual - Pluto in Virgo**: Service spiritual transformation. Health regeneration and practical revolution. Healing revolution in spiritual service. Spiritual transformation: spiritual health and service. Spiritual power: healing spiritual revolution.""",
            "LIB": """**Spiritual - Pluto in Libra**: Relationship spiritual transformation. Artistic rebirth and social revolution. Harmony revolution in spiritual partnerships. Spiritual transformation: spiritual relationships and beauty. Spiritual power: harmonious spiritual revolution.""",
            "SCO": """**Spiritual - Pluto in Scorpio**: Deep psychological spiritual transformation. Natural rebirth and complete regeneration. Ultimate spiritual transformation. Spiritual transformation: psychological spiritual patterns. Spiritual power: complete spiritual revolution.""",
            "SAG": """**Spiritual - Pluto in Sagittarius**: Philosophical spiritual transformation. Belief regeneration and truth revolution. Wisdom revolution in spiritual exploration. Spiritual transformation: spiritual beliefs and philosophy. Spiritual power: philosophical spiritual revolution.""",
            "CAP": """**Spiritual - Pluto in Capricorn**: Structural spiritual transformation. Power rebirth in spiritual institutions. Tradition revolution in spiritual authority. Spiritual transformation: spiritual structures and authority. Spiritual power: structural spiritual revolution.""",
            "AQU": """**Spiritual - Pluto in Aquarius**: Collective spiritual transformation. Social regeneration and group revolution. Innovation revolution in spiritual progress. Spiritual transformation: spiritual social networks. Spiritual power: collective spiritual revolution.""",
            "PIS": """**Spiritual - Pluto in Pisces**: Complete spiritual transformation. Ultimate surrender and enlightenment. Universal revolution in spiritual connection. Spiritual transformation: spiritual understanding and connection. Spiritual power: universal spiritual revolution."""
        }
    }

    # SEXUAL INTERPRETATIONS - ALL 10 PLANETS
    sexual_interpretations = {
        "Sun": {
            "ARI": """**Sexual - Sun in Aries**: Direct and passionate sexual energy. Natural initiator and explorer. Competitive and enthusiastic lover. Sexual style: adventurous and spontaneous. Sexual needs: excitement and challenge.""",
            "TAU": """**Sexual - Sun in Taurus**: Sensual and persistent sexual nature. Values physical pleasure and stability. Patient and devoted lover. Sexual style: sensual and steady. Sexual needs: security and comfort.""",
            "GEM": """**Sexual - Sun in Gemini**: Playful and communicative sexuality. Enjoys variety and mental stimulation. Verbal and experimental. Sexual style: versatile and communicative. Sexual needs: mental connection and variety.""",
            "CAN": """**Sexual - Sun in Cancer**: Nurturing and emotional sexual nature. Deep emotional connections in intimacy. Protective and caring. Sexual style: emotional and protective. Sexual needs: emotional security and connection.""",
            "LEO": """**Sexual - Sun in Leo**: Dramatic and generous sexuality. Needs admiration and creative expression. Romantic and passionate. Sexual style: dramatic and generous. Sexual needs: recognition and appreciation.""",
            "VIR": """**Sexual - Sun in Virgo**: Practical and attentive lover. Shows care through service and attention. Health-conscious approach. Sexual style: attentive and practical. Sexual needs: order and health consciousness.""",
            "LIB": """**Sexual - Sun in Libra**: Harmonious and artistic sexuality. Values beauty and partnership. Seeks balance and mutual pleasure. Sexual style: harmonious and artistic. Sexual needs: beauty and harmony.""",
            "SCO": """**Sexual - Sun in Scorpio**: Intense and transformative sexual energy. Deep psychological connections. Powerful and magnetic. Sexual style: intense and transformative. Sexual needs: depth and intensity.""",
            "SAG": """**Sexual - Sun in Sagittarius**: Adventurous and optimistic sexuality. Values freedom and exploration. Philosophical approach. Sexual style: adventurous and philosophical. Sexual needs: freedom and adventure.""",
            "CAP": """**Sexual - Sun in Capricorn**: Disciplined and ambitious sexual nature. Builds intimacy carefully. Traditional values. Sexual style: disciplined and traditional. Sexual needs: stability and commitment.""",
            "AQU": """**Sexual - Sun in Aquarius**: Innovative and unconventional sexuality. Experimental and freedom-loving. Intellectual connection. Sexual style: innovative and unconventional. Sexual needs: freedom and intellectual stimulation.""",
            "PIS": """**Sexual - Sun in Pisces**: Compassionate and intuitive sexuality. Spiritual and romantic connections. Empathic and sensitive. Sexual style: compassionate and spiritual. Sexual needs: spiritual connection and romance."""
        },

        "Moon": {
            "ARI": """**Sexual - Moon in Aries**: Emotionally direct and passionate in sexuality. Needs excitement and independence. Quick emotional reactions in intimacy. Sexual emotions: enthusiastic and competitive. Emotional needs: adventure and recognition.""",
            "TAU": """**Sexual - Moon in Taurus**: Emotionally stable and sensual. Values security and physical comfort. Resistant to changes in sexual routine. Sexual emotions: steady and devoted. Emotional needs: security and comfort.""",
            "GEM": """**Sexual - Moon in Gemini**: Emotionally communicative and curious. Needs mental stimulation and variety. Processes sexual emotions through talking. Sexual emotions: versatile and intellectual. Emotional needs: variety and communication.""",
            "CAN": """**Sexual - Moon in Cancer**: Deeply nurturing and emotional. Strong emotional bonds in intimacy. Needs emotional security. Sexual emotions: protective and emotional. Emotional needs: emotional security and connection.""",
            "LEO": """**Sexual - Moon in Leo**: Emotionally generous and proud. Needs recognition and appreciation. Dramatic emotional expression in sexuality. Sexual emotions: generous and dramatic. Emotional needs: recognition and appreciation.""",
            "VIR": """**Sexual - Moon in Virgo**: Emotionally practical and helpful. Shows care through attention to details. Needs order in sexual expression. Sexual emotions: attentive and practical. Emotional needs: order and health consciousness.""",
            "LIB": """**Sexual - Moon in Libra**: Emotionally harmonious and diplomatic. Seeks balance and mutual pleasure. Avoids sexual conflicts. Sexual emotions: harmonious and fair. Emotional needs: harmony and beauty.""",
            "SCO": """**Sexual - Moon in Scorpio**: Emotionally intense and passionate. Deep emotional connections and need for intimacy. Powerful sexual emotions. Sexual emotions: intense and transformative. Emotional needs: depth and loyalty.""",
            "SAG": """**Sexual - Moon in Sagittarius**: Emotionally adventurous and optimistic. Needs freedom and philosophical connection. Processes emotions through sexual adventure. Sexual emotions: adventurous and honest. Emotional needs: freedom and expansion.""",
            "CAP": """**Sexual - Moon in Capricorn**: Emotionally responsible and reserved. Controls sexual emotions carefully. Builds emotional security slowly. Sexual emotions: serious and committed. Emotional needs: security and respect.""",
            "AQU": """**Sexual - Moon in Aquarius**: Emotionally independent and unconventional. Unique emotional expression in sexuality. Needs freedom in emotional life. Sexual emotions: unique and detached. Emotional needs: freedom and individuality.""",
            "PIS": """**Sexual - Moon in Pisces**: Emotionally compassionate and intuitive. Deep spiritual connections in sexuality. Strong empathy in intimate relationships. Sexual emotions: compassionate and spiritual. Emotional needs: spiritual connection and compassion."""
        },

        "Mercury": {
            "ARI": """**Sexual - Mercury in Aries**: Direct and spontaneous sexual communication. Expresses desires boldly and immediately. Competitive in sexual intellectual connection. Sexual communication: enthusiastic and direct. Mental needs: excitement and challenge.""",
            "TAU": """**Sexual - Mercury in Taurus**: Practical and persistent communication about desires. Values stable and honest sexual dialogue. Slow but sure in expressing sexual feelings. Sexual communication: practical and reliable. Mental needs: security and comfort.""",
            "GEM": """**Sexual - Mercury in Gemini**: Playful and curious sexual communication. Enjoys mental stimulation and variety in sexual conversations. Natural flirt and communicator. Sexual communication: versatile and intellectual. Mental needs: variety and communication.""",
            "CAN": """**Sexual - Mercury in Cancer**: Intuitive and emotional sexual communication. Expresses with heart and memory. Strong emotional memory in sexual relationships. Sexual communication: emotional and nostalgic. Mental needs: emotional connection.""",
            "LEO": """**Sexual - Mercury in Leo**: Confident and dramatic sexual communication. Expressive and authoritative in love expressions. Natural romantic communicator. Sexual communication: expressive and generous. Mental needs: recognition and creativity.""",
            "VIR": """**Sexual - Mercury in Virgo**: Analytical and precise sexual communication. Thoughtful and attentive words about desires. Shows care through practical sexual advice. Sexual communication: practical and helpful. Mental needs: order and health.""",
            "LIB": """**Sexual - Mercury in Libra**: Diplomatic and balanced sexual communication. Seeks harmony in sexual dialogue. Beautiful and gracious expression of desires. Sexual communication: harmonious and fair. Mental needs: beauty and partnership.""",
            "SCO": """**Sexual - Mercury in Scorpio**: Investigative and profound sexual communication. Seeks deep truth in sexual relationships. Intense and penetrating sexual conversations. Sexual communication: intense and transformative. Mental needs: depth and truth.""",
            "SAG": """**Sexual - Mercury in Sagittarius**: Philosophical and honest sexual communication. Values expansive discussions about sexuality. Natural teacher in sexual relationships. Sexual communication: honest and expansive. Mental needs: adventure and learning.""",
            "CAP": """**Sexual - Mercury in Capricorn**: Practical and organized sexual communication. Builds sexual relationships carefully with words. Serious and committed in sexual expressions. Sexual communication: serious and reliable. Mental needs: stability and commitment.""",
            "AQU": """**Sexual - Mercury in Aquarius**: Innovative and original sexual communication. Unique way of expressing sexual desires. Intellectual and detached approach to sexuality. Sexual communication: unique and intellectual. Mental needs: freedom and innovation.""",
            "PIS": """**Sexual - Mercury in Pisces**: Intuitive and compassionate sexual communication. Romantic and dreamy expression of desires. Empathic and spiritual sexual conversations. Sexual communication: compassionate and imaginative. Mental needs: spiritual connection."""
        },

        "Venus": {
            "ARI": """**Sexual - Venus in Aries**: Direct and passionate in sexual expression. Attracted to challenge and excitement. Independent and bold in sexual relationships. Sexual attraction: confident and adventurous partners. Values: independence and excitement.""",
            "TAU": """**Sexual - Venus in Taurus**: Sensual and loyal in sexuality. Values stability and physical pleasure. Patient and devoted in sexual expression. Sexual attraction: reliable and sensual partners. Values: security and comfort.""",
            "GEM": """**Sexual - Venus in Gemini**: Playful and communicative in sexuality. Needs mental connection and variety. Enjoys flirtation and sexual conversation. Sexual attraction: intelligent and versatile partners. Values: communication and variety.""",
            "CAN": """**Sexual - Venus in Cancer**: Nurturing and emotional in sexuality. Seeks security and deep bonding. Protective and family-oriented in intimate expression. Sexual attraction: caring and protective partners. Values: emotional security and family.""",
            "LEO": """**Sexual - Venus in Leo**: Generous and dramatic in sexual expression. Needs romance and admiration. Creative expression of sexual affection. Sexual attraction: confident and generous partners. Values: recognition and creativity.""",
            "VIR": """**Sexual - Venus in Virgo**: Practical and helpful in sexuality. Shows love through sexual service and care. Attention to partner's sexual needs. Sexual attraction: reliable and health-conscious partners. Values: service and health.""",
            "LIB": """**Sexual - Venus in Libra**: Harmonious and artistic in sexuality. Seeks balance and partnership in intimate expression. Creates beauty in sexual relationships. Sexual attraction: beautiful and balanced partners. Values: harmony and partnership.""",
            "SCO": """**Sexual - Venus in Scorpio**: Intense and passionate in sexuality. Seeks deep emotional bonds in intimacy. Magnetic passion and total sexual devotion. Sexual attraction: intense and loyal partners. Values: depth and loyalty.""",
            "SAG": """**Sexual - Venus in Sagittarius**: Adventurous and freedom-loving in sexuality. Values honesty and exploration in intimate relationships. Needs space and sexual adventure. Sexual attraction: adventurous and honest partners. Values: freedom and honesty.""",
            "CAP": """**Sexual - Venus in Capricorn**: Serious and responsible in sexuality. Seeks stability and commitment in intimate relationships. Practical in sexual expression. Sexual attraction: ambitious and reliable partners. Values: stability and commitment.""",
            "AQU": """**Sexual - Venus in Aquarius**: Unconventional and friendly in sexuality. Values friendship and independence in intimate relationships. Original expression of sexual love. Sexual attraction: unique and independent partners. Values: friendship and independence.""",
            "PIS": """**Sexual - Venus in Pisces**: Romantic and compassionate in sexuality. Seeks spiritual connection in intimate relationships. Empathic and unconditional in sexual love. Sexual attraction: sensitive and spiritual partners. Values: spiritual connection and compassion."""
        },

        "Mars": {
            "ARI": """**Sexual - Mars in Aries**: Passionate and direct sexual energy. Enthusiastic and competitive lover. Bold initiator in sexual relationships. Sexual drive: immediate and enthusiastic. Sexual expression: adventurous and spontaneous.""",
            "TAU": """**Sexual - Mars in Taurus**: Sensual and persistent sexual energy. Values physical pleasure and stability. Patient and thorough lover. Sexual drive: steady and persistent. Sexual expression: sensual and steady.""",
            "GEM": """**Sexual - Mars in Gemini**: Playful and communicative sexual energy. Enjoys variety and mental stimulation. Experimental and verbal in sexual expression. Sexual drive: versatile and curious. Sexual expression: versatile and communicative.""",
            "CAN": """**Sexual - Mars in Cancer**: Protective and emotional sexual energy. Deep emotional connections in intimacy. Nurturing and sensitive approach. Sexual drive: emotional and protective. Sexual expression: emotional and caring.""",
            "LEO": """**Sexual - Mars in Leo**: Confident and dramatic sexual energy. Needs admiration and creative expression. Generous and passionate lover. Sexual drive: confident and generous. Sexual expression: dramatic and generous.""",
            "VIR": """**Sexual - Mars in Virgo**: Precise and attentive sexual energy. Shows care through attention to details. Health-conscious and practical approach. Sexual drive: attentive and precise. Sexual expression: practical and health-conscious.""",
            "LIB": """**Sexual - Mars in Libra**: Diplomatic and balanced sexual energy. Seeks harmony and mutual pleasure. Artistic and considerate lover. Sexual drive: harmonious and balanced. Sexual expression: harmonious and artistic.""",
            "SCO": """**Sexual - Mars in Scorpio**: Intense and transformative sexual energy. Deep psychological connections in intimacy. Powerful and committed lover. Sexual drive: intense and powerful. Sexual expression: intense and transformative.""",
            "SAG": """**Sexual - Mars in Sagittarius**: Adventurous and optimistic sexual energy. Values freedom and exploration. Philosophical and honest approach. Sexual drive: adventurous and optimistic. Sexual expression: adventurous and philosophical.""",
            "CAP": """**Sexual - Mars in Capricorn**: Ambitious and disciplined sexual energy. Builds intimacy carefully. Traditional and committed lover. Sexual drive: disciplined and ambitious. Sexual expression: serious and committed.""",
            "AQU": """**Sexual - Mars in Aquarius**: Innovative and unconventional sexual energy. Experimental and freedom-loving. Intellectual and unique approach. Sexual drive: innovative and experimental. Sexual expression: innovative and unconventional.""",
            "PIS": """**Sexual - Mars in Pisces**: Compassionate and intuitive sexual energy. Spiritual and romantic approach. Empathic and sensitive lover. Sexual drive: compassionate and intuitive. Sexual expression: compassionate and spiritual."""
        },

        "Jupiter": {
            "ARI": """**Sexual - Jupiter in Aries**: Expansive and confident sexual expression. Natural optimism and enthusiasm in intimacy. Growth through adventurous sexual experiences. Sexual expansion: through excitement and new experiences. Sexual philosophy: enthusiastic exploration.""",
            "TAU": """**Sexual - Jupiter in Taurus**: Steady growth in sexual expression. Values security and comfort expansion in intimacy. Growth through stable sexual partnerships. Sexual expansion: through comfort and sensual security. Sexual philosophy: practical enjoyment.""",
            "GEM": """**Sexual - Jupiter in Gemini**: Versatile expansion through sexual communication. Enjoys learning and variety in intimate relationships. Growth through intellectual sexual connection. Sexual expansion: through communication and variety. Sexual philosophy: intellectual exploration.""",
            "CAN": """**Sexual - Jupiter in Cancer**: Nurturing growth through emotional security in sexuality. Family-oriented expansion in intimate expression. Growth through emotional sexual connection. Sexual expansion: through emotional security and family. Sexual philosophy: emotional bonding.""",
            "LEO": """**Sexual - Jupiter in Leo**: Creative expansion through sexual recognition. Generous and warm-hearted intimate expression. Growth through appreciation in sexuality. Sexual expansion: through creativity and generosity. Sexual philosophy: generous expression.""",
            "VIR": """**Sexual - Jupiter in Virgo**: Analytical growth through sexual service. Improvement in practical intimate expression. Growth through helpful sexual partnership. Sexual expansion: through practical service and health. Sexual philosophy: practical improvement.""",
            "LIB": """**Sexual - Jupiter in Libra**: Harmonious expansion through sexual partnerships. Seeks beauty and balance in intimate relationships. Growth through beautiful sexual experiences. Sexual expansion: through harmony and partnership. Sexual philosophy: beautiful balance.""",
            "SCO": """**Sexual - Jupiter in Scorpio**: Transformative growth through sexual depth. Philosophical approach to intimate connection. Growth through deep sexual experiences. Sexual expansion: through transformation and depth. Sexual philosophy: intense exploration.""",
            "SAG": """**Sexual - Jupiter in Sagittarius**: Natural expansion through sexual adventure. Optimistic and freedom-loving intimate expression. Growth through philosophical sexual connection. Sexual expansion: through adventure and learning. Sexual philosophy: adventurous exploration.""",
            "CAP": """**Sexual - Jupiter in Capricorn**: Ambitious growth through sexual discipline. Builds long-term sexual relationships. Growth through commitment in intimacy. Sexual expansion: through stability and tradition. Sexual philosophy: disciplined expression.""",
            "AQU": """**Sexual - Jupiter in Aquarius**: Innovative expansion through sexual originality. Progressive sexual values and expression. Growth through friendship in intimate relationships. Sexual expansion: through innovation and friendship. Sexual philosophy: innovative exploration.""",
            "PIS": """**Sexual - Jupiter in Pisces**: Compassionate growth through sexual intuition. Spiritual connection in intimate relationships. Growth through unconditional sexual love. Sexual expansion: through spirituality and compassion. Sexual philosophy: compassionate union."""
        },

        "Saturn": {
            "ARI": """**Sexual - Saturn in Aries**: Disciplined approach to sexual expression. Learning responsibility through sexual independence. Builds sexual relationships through courage. Sexual lessons: patience and consideration. Sexual mastery: confident leadership.""",
            "TAU": """**Sexual - Saturn in Taurus**: Stable and persistent in sexual expression. Builds security through sexual commitment. Values loyalty and reliability in intimacy. Sexual lessons: flexibility and change. Sexual mastery: sensual stability.""",
            "GEM": """**Sexual - Saturn in Gemini**: Organized communication in sexual relationships. Responsibility in sexual dialogue and learning. Builds through intellectual sexual connection. Sexual lessons: depth and focus. Sexual mastery: communicative skill.""",
            "CAN": """**Sexual - Saturn in Cancer**: Emotional responsibility in sexual expression. Building family security through intimacy. Nurturing with sexual discipline. Sexual lessons: emotional boundaries. Sexual mastery: emotional security.""",
            "LEO": """**Sexual - Saturn in Leo**: Creative leadership responsibility in sexuality. Structured self-expression in intimate relationships. Generous with sexual boundaries. Sexual lessons: humility and sharing. Sexual mastery: creative expression.""",
            "VIR": """**Sexual - Saturn in Virgo**: Analytical service discipline in sexuality. Practical approach to intimate care. Helpful with sexual organization. Sexual lessons: accepting imperfection. Sexual mastery: practical service.""",
            "LIB": """**Sexual - Saturn in Libra**: Partnership responsibility in sexuality. Balanced and committed sexual relationships. Diplomatic with sexual structure. Sexual lessons: independent decision-making. Sexual mastery: harmonious partnership.""",
            "SCO": """**Sexual - Saturn in Scorpio**: Transformative discipline in sexuality. Deep commitment in intimate relationships. Intense with sexual boundaries. Sexual lessons: trust and vulnerability. Sexual mastery: transformative depth.""",
            "SAG": """**Sexual - Saturn in Sagittarius**: Philosophical responsibility in sexuality. Structured expansion in intimate expression. Adventurous with sexual commitment. Sexual lessons: commitment and details. Sexual mastery: philosophical exploration.""",
            "CAP": """**Sexual - Saturn in Capricorn**: Natural responsibility in sexual relationships. Built for long-term sexual commitment. Serious and reliable in intimacy. Sexual lessons: enjoyment and spontaneity. Sexual mastery: committed stability.""",
            "AQU": """**Sexual - Saturn in Aquarius**: Innovative responsibility in sexuality. Structured progressive sexual values. Friendly with sexual commitment. Sexual lessons: emotional connection. Sexual mastery: innovative expression.""",
            "PIS": """**Sexual - Saturn in Pisces**: Compassionate discipline in sexuality. Structured spiritual connection in intimacy. Empathic with sexual boundaries. Sexual lessons: practical boundaries. Sexual mastery: compassionate union."""
        },

        "Uranus": {
            "ARI": """**Sexual - Uranus in Aries**: Innovative sexual breakthroughs. Pioneering new forms of sexual expression. Sudden attractions and sexual changes. Sexual freedom: independence and excitement. Sexual genius: adventurous innovation.""",
            "TAU": """**Sexual - Uranus in Taurus**: Unconventional values in sexuality. Slow but revolutionary changes in sexual expression. Innovative approach to sexual security. Sexual freedom: sensual independence. Sexual genius: practical innovation.""",
            "GEM": """**Sexual - Uranus in Gemini**: Revolutionary communication in sexuality. Sudden insights and mental sexual connections. Innovative information sharing about intimacy. Sexual freedom: communicative independence. Sexual genius: intellectual innovation.""",
            "CAN": """**Sexual - Uranus in Cancer**: Innovative emotional security in sexuality. New approaches to family and sexual nurturing. Unconventional home sexual life. Sexual freedom: emotional independence. Sexual genius: emotional innovation.""",
            "LEO": """**Sexual - Uranus in Leo**: Creative breakthroughs in sexual expression. Unique self-expression and dramatic sexual changes. Innovative romance and sexual creativity. Sexual freedom: creative independence. Sexual genius: dramatic innovation.""",
            "VIR": """**Sexual - Uranus in Virgo**: Unconventional service approaches in sexuality. Innovative practical care and sexual health. Revolutionary daily sexual routines. Sexual freedom: practical independence. Sexual genius: health innovation.""",
            "LIB": """**Sexual - Uranus in Libra**: Revolutionary sexual partnerships. New approaches to balance and sexual harmony. Innovative beauty in sexual relationships. Sexual freedom: partnership innovation. Sexual genius: harmonious innovation.""",
            "SCO": """**Sexual - Uranus in Scorpio**: Transformative insights in sexual intimacy. Psychological breakthroughs and sexual depth. Innovative sexual expression and regeneration. Sexual freedom: emotional transformation. Sexual genius: intense innovation.""",
            "SAG": """**Sexual - Uranus in Sagittarius**: Philosophical innovation in sexuality. Expanding consciousness through sexual partnership. Innovative beliefs about sexual love. Sexual freedom: philosophical expansion. Sexual genius: adventurous innovation.""",
            "CAP": """**Sexual - Uranus in Capricorn**: Structural reforms in sexual relationships. Institutional changes and commitment innovation. Revolutionary traditional sexual values. Sexual freedom: structural independence. Sexual genius: traditional innovation.""",
            "AQU": """**Sexual - Uranus in Aquarius**: Natural innovator in sexual relationships. Humanitarian vision in sexual love. Progressive sexual partnership values. Sexual freedom: social innovation. Sexual genius: universal innovation.""",
            "PIS": """**Sexual - Uranus in Pisces**: Spiritual insights in sexual relationships. Mystical revelations and sexual creative inspiration. Innovative spiritual sexual connection. Sexual freedom: spiritual independence. Sexual genius: mystical innovation."""
        },

        "Neptune": {
            "ARI": """**Sexual - Neptune in Aries**: Spiritual pioneering in sexuality. Inspired action and vision in intimate relationships. Dreamy idealism about sexual partners. Sexual dreams: inspirational partnerships and spiritual adventure. Sexual inspiration: courageous mysticism.""",
            "TAU": """**Sexual - Neptune in Taurus**: Dreamy values in sexual partnerships. Idealized security and sensual comfort. Spiritual appreciation of sexual beauty. Sexual dreams: beautiful security and sensual spirituality. Sexual inspiration: earthly beauty.""",
            "GEM": """**Sexual - Neptune in Gemini**: Imaginative communication in sexuality. Inspired ideas and spiritual learning about intimacy. Dreamy intellectual sexual connection. Sexual dreams: spiritual communication and inspired learning. Sexual inspiration: mental mysticism.""",
            "CAN": """**Sexual - Neptune in Cancer**: Mystical emotional security in sexuality. Spiritual nurturing and family sexual connection. Dreamy home sexual life. Sexual dreams: spiritual family and emotional healing. Sexual inspiration: emotional mysticism.""",
            "LEO": """**Sexual - Neptune in Leo**: Creative inspiration in sexual expression. Dramatic spirituality and expressive sexual love. Dreamy sexual romance. Sexual dreams: spiritual creativity and inspirational love. Sexual inspiration: creative mysticism.""",
            "VIR": """**Sexual - Neptune in Virgo**: Service through inspiration in sexuality. Healing compassion and practical spiritual intimacy. Dreamy sexual service. Sexual dreams: spiritual service and healing partnership. Sexual inspiration: practical mysticism.""",
            "LIB": """**Sexual - Neptune in Libra**: Idealistic spiritual sexual partnerships. Spiritual harmony and beautiful sexual relationships. Dreamy sexual balance. Sexual dreams: spiritual harmony and beautiful connection. Sexual inspiration: harmonious mysticism.""",
            "SCO": """**Sexual - Neptune in Scorpio**: Deep spiritual transformation in sexuality. Psychic sensitivity and mystical sexual depth. Dreamy sexual intensity. Sexual dreams: spiritual transformation and psychic connection. Sexual inspiration: intense mysticism.""",
            "SAG": """**Sexual - Neptune in Sagittarius**: Philosophical idealism in sexuality. Spiritual expansion and visionary sexual connection. Dreamy sexual adventure. Sexual dreams: spiritual adventure and philosophical love. Sexual inspiration: expansive mysticism.""",
            "CAP": """**Sexual - Neptune in Capricorn**: Structured spirituality in sexuality. Institutional faith and disciplined sexual vision. Dreamy sexual commitment. Sexual dreams: spiritual commitment and structured love. Sexual inspiration: traditional mysticism.""",
            "AQU": """**Sexual - Neptune in Aquarius**: Collective ideals in sexuality. Humanitarian dreams and universal sexual vision. Dreamy sexual innovation. Sexual dreams: spiritual innovation and universal love. Sexual inspiration: innovative mysticism.""",
            "PIS": """**Sexual - Neptune in Pisces**: Natural mystic in sexuality. Spiritual connection and universal sexual compassion. Ultimate sexual dreams. Sexual dreams: spiritual union and compassionate love. Sexual inspiration: universal mysticism."""
        },

        "Pluto": {
            "ARI": """**Sexual - Pluto in Aries**: Transformative sexual initiative. Rebirth through passionate sexual action. Powerful new sexual beginnings. Sexual transformation: personal sexual identity. Sexual power: revolutionary sexual leadership.""",
            "TAU": """**Sexual - Pluto in Taurus**: Deep sexual value transformation. Regeneration of sensual security and values. Economic revolution in sexual resources. Sexual transformation: sexual values and resources. Sexual power: sensual revolution.""",
            "GEM": """**Sexual - Pluto in Gemini**: Psychological sexual communication. Mental transformation and sexual information revolution. Deep mental sexual connection. Sexual transformation: sexual communication patterns. Sexual power: mental sexual revolution.""",
            "CAN": """**Sexual - Pluto in Cancer**: Emotional rebirth in sexual partnerships. Family transformation and emotional sexual revolution. Deep emotional sexual healing. Sexual transformation: emotional sexual patterns. Sexual power: emotional sexual revolution.""",
            "LEO": """**Sexual - Pluto in Leo**: Creative transformation in sexual expression. Rebirth through sexual self-expression and romance. Dramatic sexual changes. Sexual transformation: creative sexual expression. Sexual power: creative sexual revolution.""",
            "VIR": """**Sexual - Pluto in Virgo**: Service transformation in sexuality. Health regeneration and practical sexual revolution. Deep practical sexual connection. Sexual transformation: health routines and sexual service. Sexual power: healing sexual revolution.""",
            "LIB": """**Sexual - Pluto in Libra**: Relationship transformation in sexuality. Artistic rebirth and social sexual revolution. Deep partnership sexual changes. Sexual transformation: partnership dynamics and sexual expression. Sexual power: harmonious sexual revolution.""",
            "SCO": """**Sexual - Pluto in Scorpio**: Deep psychological transformation in sexuality. Natural rebirth and complete sexual regeneration. Ultimate sexual intimacy. Sexual transformation: psychological sexual patterns. Sexual power: complete sexual revolution.""",
            "SAG": """**Sexual - Pluto in Sagittarius**: Philosophical transformation in sexuality. Belief regeneration and sexual truth revolution. Deep philosophical sexual connection. Sexual transformation: sexual beliefs and philosophy. Sexual power: philosophical sexual revolution.""",
            "CAP": """**Sexual - Pluto in Capricorn**: Structural transformation in sexuality. Power rebirth and sexual commitment revolution. Deep structural sexual changes. Sexual transformation: commitment structures and sexual authority. Sexual power: structural sexual revolution.""",
            "AQU": """**Sexual - Pluto in Aquarius**: Collective transformation in sexuality. Social regeneration and group sexual revolution. Deep social sexual changes. Sexual transformation: sexual social networks. Sexual power: collective sexual revolution.""",
            "PIS": """**Sexual - Pluto in Pisces**: Spiritual transformation in sexuality. Mystical rebirth and universal sexual revolution. Deep spiritual sexual union. Sexual transformation: spiritual sexual understanding. Sexual power: universal sexual revolution."""
        }
    }

    # Choose interpretation dictionary based on type
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
    
    # Display interpretations for all planets
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", 
                         "Saturn", "Uranus", "Neptune", "Pluto"]
    
    for planet_name in planets_to_display:
        if planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            
            # Display interpretation for the sign
            if (planet_name in interpretations and 
                planet_sign in interpretations[planet_name]):
                
                st.write(f"**{planet_name} in {planet_sign}**")
                st.write(interpretations[planet_name][planet_sign])
                st.write("")

# NOW YOU HAVE COMPLETE COVERAGE: 10 planets × 12 signs × 5 categories = 600 interpretations!

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
