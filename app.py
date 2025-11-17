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
import sys

# Configurare matplotlib pentru compatibilitate
import matplotlib
matplotlib.use('Agg')  # Important pentru Streamlit Cloud
plt.rcParams['figure.max_open_warning'] = 0

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

# Restul funcțiilor rămân la fel ca în codul original...
# (păstrează funcțiile: calculate_transits, calculate_progressions, calculate_transit_aspects,
# data_input_form, display_chart, display_positions, display_aspects, display_transits,
# display_progressions, display_interpretation, display_about)

if __name__ == "__main__":
    main()
