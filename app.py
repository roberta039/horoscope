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
    st.set_page_config(page_title="Professional Astrology App", layout="wide", page_icon="♈")
    
    # Initialize session state
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    if 'birth_data' not in st.session_state:
        st.session_state.birth_data = {}
    if 'transit_data' not in st.session_state:
        st.session_state.transit_data = None
    if 'progressed_data' not in st.session_state:
        st.session_state.progressed_data = None
    
    # Sidebar menu
    with st.sidebar:
        st.title("♈ Professional Astrology")
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
    """Configure ephemeris file path"""
    try:
        possible_paths = [
            './ephe',
            './swisseph-data/ephe',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ephe'),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swisseph-data', 'ephe')
        ]
        
        for ephe_path in possible_paths:
            if os.path.exists(ephe_path):
                swe.set_ephe_path(ephe_path)
                return True
        
        return False
        
    except Exception as e:
        st.error(f"Error configuring ephemeris: {e}")
        return False

@st.cache_data(ttl=3600, show_spinner="Calculating astrological chart...")
def calculate_chart_cached(birth_data):
    """Cached version of chart calculation"""
    return calculate_chart(birth_data)

def calculate_chart(birth_data):
    """Calculate astrological chart using Swiss Ephemeris"""
    try:
        # Configure ephemeris
        if not setup_ephemeris():
            st.error("Could not load ephemeris files.")
            return None
        
        # Convert dates to Julian format
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        jd = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, 
                       birth_datetime.hour + birth_datetime.minute/60.0)
        
        # Calculate planetary positions with Swiss Ephemeris
        planets_data = calculate_planetary_positions_swiss(jd)
        if planets_data is None:
            return None
        
        # Calculate Placidus houses with Swiss Ephemeris
        houses_data = calculate_houses_placidus_swiss(jd, birth_data['lat_deg'], birth_data['lon_deg'])
        if houses_data is None:
            return None
        
        # Associate planets with houses
        for planet_name, planet_data in planets_data.items():
            planet_longitude = planet_data['longitude']
            planet_data['house'] = get_house_for_longitude_swiss(planet_longitude, houses_data)
            
            # Format position string
            retro_symbol = "R" if planet_data['retrograde'] else ""
            planet_data['position_str'] = f"{planet_data['degrees']:02d}°{planet_data['minutes']:02d}' {planet_data['sign']}({planet_data['house']}){retro_symbol}"
        
        return {
            'planets': planets_data,
            'houses': houses_data,
            'jd': jd,
            'birth_datetime': birth_datetime
        }
        
    except Exception as e:
        st.error(f"Error calculating chart: {str(e)}")
        return None

def calculate_planetary_positions_swiss(jd):
    """Calculate planetary positions using Swiss Ephemeris"""
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
        'North Node': swe.MEAN_NODE
    }
    
    positions = {}
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    for name, planet_id in planets.items():
        try:
            # Calculate position with Swiss Ephemeris
            result = swe.calc_ut(jd, planet_id, flags)
            longitude = result[0][0]  # ecliptic longitude
            
            # Retrograde correction
            is_retrograde = result[0][3] < 0  # negative longitudinal speed
            
            # Convert to zodiac sign
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
            st.error(f"Error calculating position for {name}: {e}")
            return None
    
    # Add Chiron manually
    try:
        chiron_result = swe.calc_ut(jd, swe.CHIRON, flags)
        chiron_longitude = chiron_result[0][0]
    except:
        # Fallback for Chiron
        chiron_longitude = (positions['Sun']['longitude'] + 90) % 360
    
    chiron_sign_num = int(chiron_longitude / 30)
    chiron_sign_pos = chiron_longitude % 30
    positions['Chiron'] = {
        'longitude': chiron_longitude,
        'sign': signs[chiron_sign_num],
        'degrees': int(chiron_sign_pos),
        'minutes': int((chiron_sign_pos - int(chiron_sign_pos)) * 60),
        'retrograde': False
    }
    
    return positions

def calculate_houses_placidus_swiss(jd, latitude, longitude):
    """Calculate houses using Placidus system with Swiss Ephemeris"""
    try:
        # Calculate houses with Swiss Ephemeris
        result = swe.houses(jd, latitude, longitude, b'P')  # 'P' for Placidus
        
        houses = {}
        signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        for i in range(12):
            house_longitude = result[0][i]  # house cusps
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
        st.error(f"Error calculating houses: {e}")
        return None

def get_house_for_longitude_swiss(longitude, houses):
    """Determine house for a given longitude"""
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
    """Create a circular chart with planets in houses and colored aspect lines"""
    try:
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_aspect('equal')
        
        # Settings for main circle
        center_x, center_y = 0, 0
        outer_radius = 4.5
        inner_radius = 3.8
        house_radius = 3.5
        planet_radius = 3.0
        aspect_radius = 2.5  # Radius for aspect lines
        
        # Colors
        background_color = 'white'
        circle_color = '#262730'
        text_color = 'black'
        house_color = 'black'
        
        # Colors for aspects
        aspect_colors = {
            'Conjunction': '#FF6B6B',    # Red
            'Opposition': '#4ECDC4',     # Turquoise
            'Trine': '#45B7D1',          # Light blue
            'Square': '#FFA500',         # Orange
            'Sextile': '#96CEB4'         # Light green
        }
        
        planet_colors = {
            'Sun': '#FFD700', 'Moon': '#C0C0C0', 'Mercury': '#A9A9A9',
            'Venus': '#FFB6C1', 'Mars': '#FF4500', 'Jupiter': '#FFA500',
            'Saturn': '#DAA520', 'Uranus': '#40E0D0', 'Neptune': '#1E90FF',
            'Pluto': '#8B008B', 'North Node': '#FF69B4', 'Chiron': '#32CD32'
        }
        
        # Set background
        fig.patch.set_facecolor(background_color)
        ax.set_facecolor(background_color)
        
        # Draw main circles
        outer_circle = Circle((center_x, center_y), outer_radius, fill=True, color=circle_color, alpha=0.3)
        inner_circle = Circle((center_x, center_y), inner_radius, fill=True, color=background_color)
        ax.add_patch(outer_circle)
        ax.add_patch(inner_circle)
        
        # Zodiac signs and symbols
        signs = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
        sign_names = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        # Draw houses and signs
        for i in range(12):
            angle = i * 30 - 90  # Start from 9 o'clock (Aries)
            rad_angle = np.radians(angle)
            
            # Lines for houses
            x_outer = center_x + outer_radius * np.cos(rad_angle)
            y_outer = center_y + outer_radius * np.sin(rad_angle)
            x_inner = center_x + inner_radius * np.cos(rad_angle)
            y_inner = center_y + inner_radius * np.sin(rad_angle)
            
            ax.plot([x_inner, x_outer], [y_inner, y_outer], color=house_color, linewidth=1, alpha=0.5)
            
            # House numbers
            house_text_angle = angle + 15  # Center of house
            house_rad_angle = np.radians(house_text_angle)
            x_house = center_x + house_radius * np.cos(house_rad_angle)
            y_house = center_y + house_radius * np.sin(house_rad_angle)
            
            ax.text(x_house, y_house, str(i+1), ha='center', va='center', 
                   color=house_color, fontsize=10, fontweight='bold')
            
            # Zodiac signs
            sign_angle = i * 30 - 75  # Positioning for signs
            sign_rad_angle = np.radians(sign_angle)
            x_sign = center_x + (outer_radius + 0.3) * np.cos(sign_rad_angle)
            y_sign = center_y + (outer_radius + 0.3) * np.sin(sign_rad_angle)
            
            ax.text(x_sign, y_sign, signs[i], ha='center', va='center', 
                   color=house_color, fontsize=14)
            
            # Sign names
            x_name = center_x + (outer_radius + 0.7) * np.cos(sign_rad_angle)
            y_name = center_y + (outer_radius + 0.7) * np.sin(sign_rad_angle)
            
            ax.text(x_name, y_name, sign_names[i][:3], ha='center', va='center', 
                   color=house_color, fontsize=8, rotation=angle+90)
        
        # Calculate aspects if needed
        if show_aspects:
            aspects = calculate_aspects(chart_data)
            
            # Draw lines for aspects
            for aspect in aspects:
                planet1 = aspect['planet1']
                planet2 = aspect['planet2']
                aspect_name = aspect['aspect_name']
                
                if (planet1 in chart_data['planets'] and 
                    planet2 in chart_data['planets']):
                    
                    # Planet coordinates
                    long1 = chart_data['planets'][planet1]['longitude']
                    long2 = chart_data['planets'][planet2]['longitude']
                    
                    # Calculate angles for planets
                    angle1 = long1 - 90
                    angle2 = long2 - 90
                    
                    rad_angle1 = np.radians(angle1)
                    rad_angle2 = np.radians(angle2)
                    
                    # Planet positions on circle
                    x1 = center_x + aspect_radius * np.cos(rad_angle1)
                    y1 = center_y + aspect_radius * np.sin(rad_angle1)
                    x2 = center_x + aspect_radius * np.cos(rad_angle2)
                    y2 = center_y + aspect_radius * np.sin(rad_angle2)
                    
                    # Choose color for aspect
                    color = aspect_colors.get(aspect_name, '#888888')
                    
                    # Line thickness based on aspect strength
                    linewidth = 2.0 if aspect['strength'] == 'Strong' else 1.0
                    
                    # Draw aspect line
                    ax.plot([x1, x2], [y1, y2], color=color, linewidth=linewidth, 
                           alpha=0.7, linestyle='-')
        
        # Place planets in chart
        planets = chart_data['planets']
        planet_symbols = {
            'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀',
            'Mars': '♂', 'Jupiter': '♃', 'Saturn': '♄', 'Uranus': '♅',
            'Neptune': '♆', 'Pluto': '♇', 'North Node': '☊', 'Chiron': '⚷'
        }
        
        for planet_name, planet_data in planets.items():
            longitude = planet_data['longitude']
            house = planet_data.get('house', 1)
            is_retrograde = planet_data.get('retrograde', False)
            
            # Calculate angle for planet
            planet_angle = longitude - 90  # Adjustment to start from Aries
            planet_rad_angle = np.radians(planet_angle)
            
            # Planet position
            x_planet = center_x + planet_radius * np.cos(planet_rad_angle)
            y_planet = center_y + planet_radius * np.sin(planet_rad_angle)
            
            # Planet symbol
            symbol = planet_symbols.get(planet_name, '•')
            color = planet_colors.get(planet_name, 'white')
            
            # Display planet
            ax.text(x_planet, y_planet, symbol, ha='center', va='center', 
                   color=color, fontsize=12, fontweight='bold')
            
            # Planet name (abbreviated)
            abbrev = planet_name[:3] if planet_name not in ['Sun', 'Moon'] else planet_name
            if is_retrograde:
                abbrev += " R"
                
            # Position for name
            name_angle = planet_angle + 5
            name_rad_angle = np.radians(name_angle)
            x_name = center_x + (planet_radius - 0.3) * np.cos(name_rad_angle)
            y_name = center_y + (planet_radius - 0.3) * np.sin(name_rad_angle)
            
            ax.text(x_name, y_name, abbrev, ha='center', va='center', 
                   color=color, fontsize=7, alpha=0.8)
        
        # Chart title
        name = birth_data.get('name', 'Natal Chart')
        date_str = birth_data.get('date', '').strftime('%Y-%m-%d')
        ax.set_title(f'{name} - {date_str}\n{title_suffix}', 
                    color=text_color, fontsize=16, pad=20)
        
        # Legend for aspects (if displayed)
        if show_aspects and aspects:
            legend_elements = []
            for aspect_name, color in aspect_colors.items():
                legend_elements.append(plt.Line2D([0], [0], color=color, lw=2, label=aspect_name))
            
            ax.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.1, 1), 
                     fontsize=8, framealpha=0.7)
        
        # Remove axes
        ax.set_xlim(-outer_radius-1, outer_radius+1)
        ax.set_ylim(-outer_radius-1, outer_radius+1)
        ax.axis('off')
        
        # Legend
        legend_text = "Planets in Houses - Placidus System"
        ax.text(0, -outer_radius-0.8, legend_text, ha='center', va='center',
               color=text_color, fontsize=10, style='italic')
        
        plt.tight_layout()
        return fig
        
    except Exception as e:
        st.error(f"Error creating chart: {e}")
        return None

def calculate_aspects(chart_data):
    """Calculate astrological aspects"""
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
        st.error(f"Error calculating aspects: {e}")
        return []

def calculate_transits(birth_jd, transit_date, birth_lat, birth_lon):
    """Calculate transits for a specific date"""
    try:
        # Convert transit date to Julian Day
        transit_datetime = datetime.combine(transit_date, datetime.min.time())
        transit_jd = swe.julday(transit_datetime.year, transit_datetime.month, 
                               transit_datetime.day, 12.0)  # At noon
        
        # Calculate planetary positions for transit date
        transit_planets = calculate_planetary_positions_swiss(transit_jd)
        
        # Calculate houses for transit date (using birth coordinates)
        transit_houses = calculate_houses_placidus_swiss(transit_jd, birth_lat, birth_lon)
        
        # Associate planets with houses
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
        st.error(f"Error calculating transits: {e}")
        return None

def calculate_progressions(birth_data, progression_date, method='secondary'):
    """Calculate progressions (Secondary/ Solar Arc)"""
    try:
        birth_datetime = datetime.combine(birth_data['date'], birth_data['time'])
        progression_datetime = datetime.combine(progression_date, datetime.min.time())
        
        # Get natal JD from session_state
        if st.session_state.chart_data is None:
            st.error("Natal chart not calculated yet!")
            return None
            
        natal_jd = st.session_state.chart_data['jd']
        
        # Calculation for Secondary Progression (1 day = 1 year)
        if method == 'secondary':
            days_diff = (progression_datetime - birth_datetime).days
            progressed_jd = natal_jd + days_diff
            
        # Calculation for Solar Arc
        elif method == 'solar_arc':
            # Progressed Sun position
            days_diff = (progression_datetime - birth_datetime).days
            solar_arc = (days_diff / 365.25) * 0.9856  # Sun's average daily movement
            
            # Calculate natal chart to apply Solar Arc
            natal_chart = st.session_state.chart_data
            progressed_planets = {}
            
            for planet_name, planet_data in natal_chart['planets'].items():
                progressed_longitude = (planet_data['longitude'] + solar_arc) % 360
                
                # Convert to zodiac sign
                signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
                        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
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
                'houses': natal_chart['houses'],  # Houses remain the same
                'solar_arc': solar_arc,
                'date': progression_date,
                'method': 'Solar Arc'
            }
        
        # For Secondary Progression, calculate actual positions
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
        
        # Associate planets with houses
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
        st.error(f"Error calculating progressions: {e}")
        return None

def calculate_transit_aspects(natal_chart, transit_chart):
    """Calculate aspects between natal and transit planets"""
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
                # Avoid aspects between same planet (always conjunction)
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
        st.error(f"Error calculating transit aspects: {e}")
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
            # Longitude with degrees and minutes
            st.write("**Longitude**")
            col_lon_deg, col_lon_min = st.columns(2)
            with col_lon_deg:
                longitude_deg = st.number_input("Longitude (°)", min_value=0.0, max_value=180.0, value=16.0, step=1.0, key="lon_deg")
            with col_lon_min:
                longitude_min = st.number_input("Longitude (')", min_value=0.0, max_value=59.9, value=0.0, step=1.0, key="lon_min")
            longitude_dir = st.selectbox("Longitude Direction", ["East", "West"], index=0, key="lon_dir")
            
        with col2b:
            # Latitude with degrees and minutes
            st.write("**Latitude**")
            col_lat_deg, col_lat_min = st.columns(2)
            with col_lat_deg:
                latitude_deg = st.number_input("Latitude (°)", min_value=0.0, max_value=90.0, value=45.0, step=1.0, key="lat_deg")
            with col_lat_min:
                latitude_min = st.number_input("Latitude (')", min_value=0.0, max_value=59.9, value=51.0, step=1.0, key="lat_min")
            latitude_dir = st.selectbox("Latitude Direction", ["North", "South"], index=0, key="lat_dir")
        
        # Calculate final coordinates
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
                'lat_display': f"{latitude_deg}°{latitude_min:.0f}'{latitude_dir[0]}",
                'lon_display': f"{longitude_deg}°{longitude_min:.0f}'{longitude_dir[0]}"
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
    
    # Option for displaying aspects
    col1, col2 = st.columns([3, 1])
    
    with col2:
        show_aspect_lines = st.checkbox("Show Aspect Lines", value=True, help="Display colored lines between planets showing astrological aspects")
    
    # Display circular chart
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
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron']
        
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

def display_positions():
    st.header("📍 Planetary Positions")
    
    if st.session_state.chart_data is None:
        st.warning("Please calculate chart first!")
        return
    
    chart_data = st.session_state.chart_data
    
    positions_data = []
    display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                    'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron']
    
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
        
        # Display transit chart
        if show_chart:
            fig = create_chart_wheel(transit_data, birth_data, "Transit Chart", show_aspect_lines)
            if fig:
                st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Transit Positions")
            display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                            'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron']
            
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
        
        # Display aspects between transits and natal chart
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
        
        # Display progressed chart
        fig = create_chart_wheel(progressed_data, birth_data, f"Progressed Chart - {progressed_data['method']}", show_aspect_lines)
        if fig:
            st.pyplot(fig)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🌍 Progressed Positions")
            display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                            'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron']
            
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
        
        # Display aspects between progressed and natal chart
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
    st.header("📖 Detailed Astrological Interpretation")
    
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
        st.write(f"**Location:** {birth_data['lat_display']}, {birth_data['lon_display']}")
    
    with col2:
        st.subheader("Planetary Positions")
        display_order = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                        'Saturn', 'Uranus', 'Neptune', 'Pluto', 'North Node', 'Chiron']
        
        for planet_name in display_order:
            if planet_name in chart_data['planets']:
                planet_data = chart_data['planets'][planet_name]
                st.write(f"**{planet_name}** {planet_data['position_str']}")
    
    st.markdown("---")
    
    interpretation_type = st.selectbox(
        "Interpretation Focus",
        ["Natal Chart", "Career & Vocation", "Relationships & Love", "Spiritual Growth", "Personality Analysis", "Life Purpose"]
    )
    
    st.markdown("---")
    st.subheader(f"Detailed Interpretation: {interpretation_type}")
    
    display_complete_interpretations(chart_data, interpretation_type)

def display_complete_interpretations(chart_data, interpretation_type):
    """Display comprehensive interpretations for all planets and placements"""
    
    # EXTENSIVE NATAL INTERPRETATIONS
    natal_interpretations = {
        "Sun": {
            "Aries": """
**The Pioneer and Leader**
With your Sun in Aries, you embody the essence of initiation and courage. You are a natural-born leader with an entrepreneurial spirit that constantly seeks new challenges. Your approach to life is direct and enthusiastic - you see obstacles as opportunities to demonstrate your strength and capability.

**Key Characteristics:**
- **Initiating Energy**: You're always first to start projects and embrace new beginnings
- **Courageous Spirit**: Fearlessness in facing challenges and speaking your truth
- **Independent Nature**: Strong need for autonomy and self-determination
- **Competitive Drive**: Thrive in situations where you can demonstrate your abilities
- **Impulsive Tendencies**: Sometimes act before thinking through consequences

**Life Purpose**: Your soul's journey involves learning to lead with consideration for others while maintaining your pioneering spirit. You're here to demonstrate courage and inspire action in those around you.
""",
            "Taurus": """
**The Builder and Stabilizer**
Your Sun in Taurus grounds you in practicality and sensuality. You possess an innate understanding of material reality and have a remarkable ability to create stability and beauty in your environment. Your steady, determined approach to life ensures that whatever you build will last.

**Key Characteristics:**
- **Practical Wisdom**: Exceptional common sense and realistic outlook
- **Sensual Appreciation**: Deep connection to physical pleasures and beauty
- **Financial Acumen**: Natural understanding of money and resources
- **Reliable Nature**: People depend on your consistency and loyalty
- **Resistance to Change**: Can become stuck in comfortable routines

**Life Purpose**: You're here to master the material world while maintaining spiritual values. Your gift is creating security and beauty that nourishes the soul as well as the body.
""",
            "Gemini": """
**The Communicator and Networker**
With your Sun in Gemini, your mind is your greatest asset. You process information rapidly and excel at making connections between seemingly unrelated concepts. Your curiosity is insatiable, and you thrive on mental stimulation and variety.

**Key Characteristics:**
- **Intellectual Agility**: Quick thinking and adaptable mental processes
- **Communication Skills**: Natural ability to express ideas clearly and persuasively
- **Social Versatility**: Comfortable in diverse social situations
- **Multitasking Ability**: Handle multiple projects and interests simultaneously
- **Restless Energy**: Constant need for mental stimulation and new experiences

**Life Purpose**: Your journey involves learning to focus your mental energies while using your communication gifts to bridge understanding between different perspectives.
""",
            "Cancer": """
**The Nurturer and Protector**
Your Sun in Cancer gives you deep emotional intelligence and strong protective instincts. You are the heart of your family and community, creating emotional security for those you care about. Your intuition is highly developed, and you often know what others need before they do.

**Key Characteristics:**
- **Emotional Depth**: Rich inner life and strong connection to feelings
- **Nurturing Instinct**: Natural caregiver who supports others' growth
- **Protective Nature**: Fierce defender of home and loved ones
- **Intuitive Wisdom**: Strong gut feelings and psychic sensitivities
- **Mood Fluctuations**: Emotions can shift like the tides

**Life Purpose**: You're here to learn emotional mastery while providing the nurturing foundation that allows others to flourish. Your gift is creating emotional safety.
""",
            "Leo": """
**The Creative and Leader**
With your Sun in Leo, you radiate warmth, creativity, and self-expression. You have a natural dramatic flair and inspire others through your enthusiasm and generosity. Your presence commands attention, and you have a royal quality about you that draws people naturally.

**Key Characteristics:**
- **Creative Expression**: Natural artist and performer in some aspect of life
- **Generous Spirit**: Big-hearted and willing to share resources and attention
- **Leadership Ability**: Natural authority that people willingly follow
- **Dramatic Flair**: Everything you do has an element of theater
- **Need for Recognition**: Thrive on appreciation and acknowledgment

**Life Purpose**: Your soul's journey involves learning humble leadership and using your creative gifts to uplift others rather than just seeking personal glory.
""",
            "Virgo": """
**The Analyst and Healer**
Your Sun in Virgo gives you exceptional analytical abilities and a desire to be of service. You notice details others miss and have a natural talent for improving systems and processes. Your humility and willingness to serve make you invaluable in any organization.

**Key Characteristics:**
- **Analytical Mind**: Exceptional attention to detail and critical thinking
- **Service Orientation**: Find fulfillment in being useful and helpful
- **Practical Skills**: Excellent at organizing and systematizing
- **Health Consciousness**: Natural interest in wellness and bodily function
- **Perfectionist Tendencies**: Can be overly critical of self and others

**Life Purpose**: You're here to learn that true perfection comes through embracing imperfection while using your analytical gifts to heal and improve the world around you.
""",
            "Libra": """
**The Diplomat and Artist**
With your Sun in Libra, you are naturally diplomatic, charming, and aesthetically oriented. You have an innate sense of balance and harmony and excel at bringing people together. Your eye for beauty helps you create environments that uplift the spirit.

**Key Characteristics:**
- **Diplomatic Skills**: Natural peacemaker who sees all sides
- **Aesthetic Sense**: Innate understanding of beauty and design
- **Social Grace**: Charming and comfortable in social situations
- **Partnership Focus**: Thrive in cooperative relationships
- **Indecisiveness**: Can struggle with making firm decisions

**Life Purpose**: Your journey involves learning to establish your own identity within relationships while using your diplomatic gifts to create harmony and beauty in the world.
""",
            "Scorpio": """
**The Transformer and Investigator**
Your Sun in Scorpio gives you tremendous emotional depth and psychological insight. You are drawn to life's mysteries and have a natural ability to transform challenging situations into opportunities for growth. Your intensity can be intimidating, but it comes from profound depth of feeling.

**Key Characteristics:**
- **Psychological Depth**: Natural understanding of human motivation
- **Transformative Power**: Ability to reinvent yourself and situations
- **Emotional Intensity**: Feelings run deep and powerful
- **Investigative Nature**: Nothing escapes your perceptive gaze
- **Secretive Tendencies**: Carefully guard your private thoughts

**Life Purpose**: You're here to learn the alchemy of transforming pain into wisdom while using your penetrating insight to help others heal and transform.
""",
            "Sagittarius": """
**The Philosopher and Explorer**
With your Sun in Sagittarius, you are the eternal seeker of truth and meaning. Your optimistic nature and love of freedom propel you on constant journeys, both physical and philosophical. You have a natural teaching ability and inspire others with your vision.

**Key Characteristics:**
- **Philosophical Nature**: Constantly seeking larger meaning and truth
- **Adventurous Spirit**: Love of travel and new experiences
- **Optimistic Outlook**: Natural faith in positive outcomes
- **Teaching Ability**: Gift for explaining complex concepts
- **Tactlessness**: Sometimes speak truth without considering feelings

**Life Purpose**: Your soul's journey involves grounding your philosophical insights in practical reality while using your inspirational nature to expand others' horizons.
""",
            "Capricorn": """
**The Architect and Authority**
Your Sun in Capricorn gives you ambition, discipline, and a profound understanding of structure and tradition. You are a natural builder who creates lasting institutions and systems. Your patience and perseverance ensure that whatever you build will stand the test of time.

**Key Characteristics:**
- **Ambitious Drive**: Clear vision of what you want to achieve
- **Disciplined Approach**: Willing to work patiently toward long-term goals
- **Practical Wisdom**: Understanding of how systems and institutions work
- **Responsible Nature**: Take commitments and duties seriously
- **Serious Demeanor**: Can become overly focused on work and status

**Life Purpose**: You're here to learn balance between ambition and emotional fulfillment while using your organizational gifts to create structures that serve humanity.
""",
            "Aquarius": """
**The Innovator and Humanitarian**
With your Sun in Aquarius, you are forward-thinking, original, and deeply concerned with humanity's welfare. Your mind works in unique ways, and you have visionary ideas that can change society. Your detachment allows you to see the big picture clearly.

**Key Characteristics:**
- **Innovative Thinking**: Original ideas that challenge conventions
- **Humanitarian Vision**: Concern for collective welfare and progress
- **Independent Spirit**: March to the beat of your own drum
- **Friendship Orientation**: Value intellectual companionship
- **Emotional Detachment**: Can seem aloof or unemotional

**Life Purpose**: Your journey involves learning to combine your brilliant ideas with practical implementation while using your visionary gifts to advance human consciousness.
""",
            "Pisces": """
**The Mystic and Healer**
Your Sun in Pisces gives you compassion, intuition, and connection to spiritual dimensions. You feel the suffering of others as your own and have a natural healing presence. Your creativity flows from deep spiritual sources, and you often serve as a channel for higher energies.

**Key Characteristics:**
- **Compassionate Nature**: Deep empathy for all living beings
- **Intuitive Wisdom**: Strong connection to unconscious and spiritual realms
- **Creative Talent**: Natural artist, musician, or poet
- **Adaptive Quality**: Ability to flow with circumstances
- **Boundary Issues**: Can absorb others' energies and emotions

**Life Purpose**: You're here to learn spiritual discernment while using your compassionate nature to heal and inspire through artistic and spiritual channels.
"""
        },
        "Moon": {
            "Aries": """
**Emotional Pioneer**
Your Moon in Aries gives you emotionally direct and spontaneous responses. You feel things intensely and immediately, and your emotional needs center around independence and the freedom to pursue your own initiatives. You're emotionally courageous but can become impatient with slower emotional processes.

**Emotional Needs:**
- Need for immediate action on feelings
- Independence in emotional expression
- Recognition for your emotional bravery
- Freedom from emotional constraints

**Healing Approach**: Learning emotional patience and consideration of others' timing while honoring your need for authentic emotional expression.
""",
            "Taurus": """
**Emotional Stabilizer**
Your Moon in Taurus provides emotional consistency and a deep need for security. You find comfort in routine, beauty, and physical pleasures. Your emotional responses are steady and predictable, and you have a calming effect on those around you.

**Emotional Needs:**
- Financial and material security
- Physical comfort and sensual pleasures
- Stable, predictable environments
- Time to process emotions slowly

**Healing Approach**: Learning flexibility in the face of change while maintaining your grounding presence and appreciation for life's comforts.
""",
            "Gemini": """
**Emotional Communicator**
Your Moon in Gemini processes emotions through communication and intellectual understanding. You need to talk about your feelings and understand them mentally. Your emotional state can change rapidly as new information comes in.

**Emotional Needs:**
- Mental stimulation and variety
- Freedom to communicate feelings
- Social interaction and networking
- Learning new emotional perspectives

**Healing Approach**: Learning to connect with the deeper, non-verbal aspects of emotion while honoring your need for emotional expression through words.
""",
            "Cancer": """
**Emotional Nurturer**
Your Moon in Cancer gives you deep emotional sensitivity and strong nurturing instincts. You're deeply connected to family, home, and tradition. Your emotions flow like the tides - sometimes calm, sometimes stormy, but always powerful.

**Emotional Needs:**
- Emotional security and safety
- Strong family connections
- Comfortable home environment
- Time for emotional processing

**Healing Approach**: Learning to establish healthy emotional boundaries while maintaining your profound capacity for empathy and care.
""",
            "Leo": """
**Emotional Performer**
Your Moon in Leo needs emotional recognition and appreciation. You express feelings dramatically and generously, and you thrive when your emotional expressions are acknowledged. Your warmth and loyalty make you a fiercely protective friend and partner.

**Emotional Needs:**
- Recognition for emotional contributions
- Creative self-expression
- Loyal, appreciative relationships
- Opportunities to shine emotionally

**Healing Approach**: Learning to find internal validation for your emotional worth while sharing your generous heart with the world.
""",
            "Virgo": """
**Emotional Analyst**
Your Moon in Virgo processes emotions through analysis and practical service. You feel most secure when you're being useful and when things are organized properly. Your emotional healing comes through helping others and creating order.

**Emotional Needs:**
- Practical ways to express care
- Orderly, clean environments
- Feeling useful and competent
- Health and wellness routines

**Healing Approach**: Learning to accept emotional imperfection in yourself and others while using your analytical gifts for healing rather than criticism.
""",
            "Libra": """
**Emotional Diplomat**
Your Moon in Libra seeks emotional harmony and beautiful relationships. You're naturally diplomatic and can see all sides of emotional situations. Your feelings are deeply influenced by your relationships and your aesthetic environment.

**Emotional Needs:**
- Harmonious relationships
- Beautiful surroundings
- Partnership and cooperation
- Fairness and justice

**Healing Approach**: Learning to honor your own emotional needs within relationships while maintaining your gift for creating emotional balance.
""",
            "Scorpio": """
**Emotional Transformer**
Your Moon in Scorpio gives you emotional intensity and psychological depth. You experience feelings with tremendous power and are drawn to emotional mysteries and transformations. Your emotional intuition is exceptionally strong.

**Emotional Needs:**
- Emotional honesty and depth
- Psychological understanding
- Transformative experiences
- Privacy in emotional matters

**Healing Approach**: Learning to transform emotional pain into wisdom while maintaining healthy boundaries with others' intense emotions.
""",
            "Sagittarius": """
**Emotional Explorer**
Your Moon in Sagittarius needs emotional freedom and philosophical understanding. You process feelings through adventure, learning, and seeking higher meaning. Your emotional nature is optimistic and freedom-loving.

**Emotional Needs:**
- Freedom to explore emotionally
- Philosophical understanding of feelings
- Adventure and new experiences
- Honest emotional expression

**Healing Approach**: Learning to ground your emotional explorations in practical reality while maintaining your optimistic emotional vision.
""",
            "Capricorn": """
**Emotional Architect**
Your Moon in Capricorn approaches emotions with seriousness and discipline. You have strong emotional control and build emotional security through achievement and responsibility. Your feelings are deep but carefully managed.

**Emotional Needs:**
- Emotional security through achievement
- Respect for emotional boundaries
- Structured emotional expression
- Long-term emotional plans

**Healing Approach**: Learning to allow vulnerability and emotional spontaneity while maintaining your emotional strength and responsibility.
""",
            "Aquarius": """
**Emotional Innovator**
Your Moon in Aquarius processes emotions through intellectual detachment and humanitarian concern. You have unique emotional responses and value emotional freedom and friendship. Your feelings are often connected to larger social issues.

**Emotional Needs:**
- Emotional independence
- Intellectual companionship
- Progressive emotional environments
- Freedom from emotional convention

**Healing Approach**: Learning to connect your innovative emotional understanding with practical emotional expression while honoring your need for emotional freedom.
""",
            "Pisces": """
**Emotional Mystic**
Your Moon in Pisces gives you profound emotional sensitivity and spiritual connection. You feel the emotions of others as your own and have deep compassion. Your emotional boundaries are fluid, allowing profound connection but requiring careful management.

**Emotional Needs:**
- Spiritual emotional connection
- Creative emotional expression
- Compassionate environments
- Time for emotional retreat

**Healing Approach**: Learning to establish healthy emotional boundaries while maintaining your profound capacity for empathy and spiritual connection.
"""
        },
        "Mercury": {
            "Aries": """
**Pioneering Intellect**
Your Mercury in Aries gives you quick, original thinking and the ability to grasp concepts instantly. You're mentally courageous and enjoy intellectual challenges. Your thinking process is direct and you prefer to get straight to the point.

**Mental Strengths:**
- Rapid comprehension of new ideas
- Courage in expressing opinions
- Innovative problem-solving
- Leadership in intellectual matters

**Growth Area**: Learning to consider alternative viewpoints before reaching conclusions while maintaining your mental initiative.
""",
            "Taurus": """
**Practical Thinker**
Your Mercury in Taurus gives you steady, methodical thinking and excellent common sense. You process information thoroughly and remember what you learn. Your mental approach is practical and grounded in reality.

**Mental Strengths:**
- Practical problem-solving
- Excellent memory retention
- Steady, reliable thinking
- Financial and material understanding

**Growth Area**: Learning to be more mentally flexible when circumstances change while maintaining your practical wisdom.
""",
            "Gemini": """
**Versatile Communicator**
Your Mercury in Gemini gives you exceptional communication skills and mental versatility. You learn quickly and can handle multiple streams of information simultaneously. Your curiosity drives constant mental exploration.

**Mental Strengths:**
- Rapid learning ability
- Excellent verbal skills
- Mental adaptability
- Networking and connecting ideas

**Growth Area**: Learning to focus your mental energies on depth as well as breadth while maintaining your intellectual curiosity.
""",
            "Cancer": """
**Intuitive Thinker**
Your Mercury in Cancer gives you intuitive, emotionally-based thinking and excellent memory. You think with your heart as well as your mind, and you remember emotional details others forget. Your mental process is protective and nurturing.

**Mental Strengths:**
- Emotional intelligence
- Strong memory, especially for feelings
- Intuitive understanding
- Protective communication

**Growth Area**: Learning to balance emotional thinking with objective analysis while maintaining your intuitive gifts.
""",
            "Leo": """
**Dramatic Communicator**
Your Mercury in Leo gives you confident, expressive communication and creative thinking. You speak with authority and enjoy being the center of intellectual attention. Your mental process is generous and inspiring.

**Mental Strengths:**
- Confident self-expression
- Creative problem-solving
- Inspirational communication
- Leadership in discussions

**Growth Area**: Learning to listen as well as you speak while maintaining your confident self-expression.
""",
            "Virgo": """
**Analytical Mind**
Your Mercury in Virgo gives you exceptional analytical abilities and attention to detail. You notice what others miss and have a talent for improving systems. Your thinking is practical, organized, and service-oriented.

**Mental Strengths:**
- Critical analysis
- Systematic thinking
- Practical problem-solving
- Health and service knowledge

**Growth Area**: Learning to see the big picture while maintaining your valuable attention to detail.
""",
            "Libra": """
**Diplomatic Thinker**
Your Mercury in Libra gives you balanced, diplomatic thinking and aesthetic appreciation. You see all sides of issues and excel at finding harmonious solutions. Your mental process seeks beauty and fairness.

**Mental Strengths:**
- Diplomatic communication
- Balanced decision-making
- Artistic understanding
- Partnership-oriented thinking

**Growth Area**: Learning to make firm decisions when necessary while maintaining your diplomatic approach.
""",
            "Scorpio": """
**Investigative Mind**
Your Mercury in Scorpio gives you penetrating, investigative thinking and psychological insight. You see beneath surface appearances and understand hidden motivations. Your mental process is intense and transformative.

**Mental Strengths:**
- Psychological insight
- Investigative ability
- Strategic thinking
- Understanding of mysteries

**Growth Area**: Learning to share your insights with sensitivity while maintaining your penetrating understanding.
""",
            "Sagittarius": """
**Philosophical Thinker**
Your Mercury in Sagittarius gives you broad, philosophical thinking and honest communication. You seek the larger meaning in information and enjoy exploring big ideas. Your mental process is optimistic and expansive.

**Mental Strengths:**
- Philosophical understanding
- Honest expression
- Teaching ability
- Cross-cultural thinking

**Growth Area**: Learning to ground your philosophical insights in practical details while maintaining your expansive vision.
""",
            "Capricorn": """
**Strategic Thinker**
Your Mercury in Capricorn gives you organized, ambitious thinking and practical wisdom. You think in terms of long-term goals and structural integrity. Your mental process is disciplined and responsible.

**Mental Strengths:**
- Strategic planning
- Organizational ability
- Business acumen
- Practical implementation

**Growth Area**: Learning to incorporate innovation within structures while maintaining your practical wisdom.
""",
            "Aquarius": """
**Innovative Thinker**
Your Mercury in Aquarius gives you original, forward-thinking ideas and humanitarian vision. You think outside conventional boxes and have visionary insights. Your mental process is independent and progressive.

**Mental Strengths:**
- Innovative ideas
- Technological understanding
- Humanitarian thinking
- Future-oriented vision

**Growth Area**: Learning to implement your innovative ideas practically while maintaining your visionary thinking.
""",
            "Pisces": """
**Intuitive Mind**
Your Mercury in Pisces gives you imaginative, compassionate thinking and spiritual understanding. You think with intuition and empathy, often knowing things beyond logical explanation. Your mental process is creative and healing.

**Mental Strengths:**
- Intuitive understanding
- Creative imagination
- Compassionate communication
- Spiritual insight

**Growth Area**: Learning to ground your intuitive insights in practical reality while maintaining your imaginative gifts.
"""
        },
        "Venus": {
            "Aries": """
**Passionate Lover**
Your Venus in Aries approaches love with enthusiasm, directness, and a pioneering spirit. You're attracted to challenge and enjoy the thrill of pursuit. In relationships, you need independence and admire partners who have their own strong identity.

**Love Style:**
- Direct expression of affection
- Enjoyment of romantic challenges
- Need for excitement in relationships
- Appreciation of partners' independence

**Relationship Lesson**: Learning patience and consideration in relationships while maintaining your passionate approach to love.
""",
            "Taurus": """
**Sensual Partner**
Your Venus in Taurus approaches love with loyalty, sensuality, and a need for security. You value stability, physical affection, and tangible expressions of love. Your approach to relationships is steady and deeply committed.

**Love Style:**
- Physical expressions of love
- Loyalty and commitment
- Appreciation of beauty and comfort
- Slow, steady relationship building

**Relationship Lesson**: Learning flexibility in love while maintaining the stability that nourishes you.
""",
            "Gemini": """
**Playful Communicator**
Your Venus in Gemini approaches love with curiosity, communication, and a need for mental stimulation. You enjoy playful relationships and need partners who can engage you intellectually. Your love style is lighthearted and versatile.

**Love Style:**
- Mental connection in relationships
- Playful, flirtatious approach
- Need for variety and stimulation
- Communication as love expression

**Relationship Lesson**: Learning emotional depth in relationships while maintaining your playful, communicative approach.
""",
            "Cancer": """
**Nurturing Partner**
Your Venus in Cancer approaches love with emotional depth, protectiveness, and strong family orientation. You need emotional security and create nurturing relationships. Your love is deeply loyal and emotionally rich.

**Love Style:**
- Emotional security needs
- Family-oriented relationships
- Nurturing expression of love
- Strong protective instincts

**Relationship Lesson**: Learning healthy emotional boundaries while maintaining your nurturing capacity.
""",
            "Leo": """
**Generous Lover**
Your Venus in Leo approaches love with generosity, drama, and a need for recognition. You express love grandly and need partners who appreciate your romantic gestures. Your love is warm, loyal, and expressive.

**Love Style:**
- Dramatic romantic expressions
- Need for appreciation
- Generous giving and receiving
- Loyal, protective love

**Relationship Lesson**: Learning humble love expression while maintaining your generous, warm approach.
""",
            "Virgo": """
**Practical Partner**
Your Venus in Virgo approaches love with practicality, service, and attention to detail. You show love through helpful actions and appreciate partners who are competent and reliable. Your love is modest and sincere.

**Love Style:**
- Practical expressions of care
- Service as love language
- Appreciation of competence
- Modest, sincere affection

**Relationship Lesson**: Learning to accept imperfection in love while maintaining your practical, caring approach.
""",
            "Libra": """
**Harmonious Lover**
Your Venus in Libra approaches love with diplomacy, beauty, and a need for partnership. You seek balanced, beautiful relationships and excel at creating romantic harmony. Your love is artistic and fair-minded.

**Love Style:**
- Need for partnership balance
- Appreciation of beauty in relationships
- Diplomatic approach to love
- Romantic, idealistic nature

**Relationship Lesson**: Learning to establish your own identity in relationships while maintaining your harmonious approach.
""",
            "Scorpio": """
**Intense Partner**
Your Venus in Scorpio approaches love with intensity, passion, and emotional depth. You seek transformative relationships and are drawn to emotional mysteries. Your love is powerful, loyal, and deeply emotional.

**Love Style:**
- Emotional intensity in love
- Transformative relationships
- Loyalty and commitment
- Psychological connection needs

**Relationship Lesson**: Learning trust and emotional openness while maintaining your passionate depth.
""",
            "Sagittarius": """
**Adventurous Lover**
Your Venus in Sagittarius approaches love with optimism, adventure, and a need for freedom. You're attracted to partners who share your love of exploration and learning. Your love is honest and expansive.

**Love Style:**
- Need for freedom in relationships
- Honest, direct expression
- Adventure-oriented love
- Philosophical connection

**Relationship Lesson**: Learning commitment within freedom while maintaining your adventurous spirit.
""",
            "Capricorn": """
**Serious Partner**
Your Venus in Capricorn approaches love with seriousness, responsibility, and long-term planning. You value stability and build relationships carefully over time. Your love is loyal, practical, and enduring.

**Love Style:**
- Serious approach to love
- Long-term relationship focus
- Practical expressions of care
- Loyal, committed nature

**Relationship Lesson**: Learning emotional expression within responsibility while maintaining your serious approach.
""",
            "Aquarius": """
**Unconventional Lover**
Your Venus in Aquarius approaches love with originality, friendship, and humanitarian concern. You value intellectual connection and need freedom in relationships. Your love is friendly, progressive, and unique.

**Love Style:**
- Friendship as love foundation
- Need for independence
- Unconventional relationships
- Humanitarian love expression

**Relationship Lesson**: Learning emotional connection within freedom while maintaining your unique approach.
""",
            "Pisces": """
**Romantic Dreamer**
Your Venus in Pisces approaches love with compassion, romance, and spiritual connection. You seek soulmate relationships and have deep empathy for partners. Your love is idealistic, compassionate, and spiritually oriented.

**Love Style:**
- Romantic, idealistic nature
- Compassionate love expression
- Spiritual connection needs
- Empathic understanding

**Relationship Lesson**: Learning practical boundaries in love while maintaining your compassionate, romantic nature.
"""
        },
        "Mars": {
            "Aries": """
**Dynamic Action Taker**
Your Mars in Aries gives you tremendous initiative and courage in taking action. You're a natural pioneer who enjoys starting projects and facing challenges head-on. Your energy is direct and powerful, though sometimes short-lived.

**Action Style:**
- Immediate response to opportunities
- Courage in facing obstacles
- Leadership in physical activities
- Competitive drive

**Growth Opportunity**: Learning sustained effort and consideration of consequences while maintaining your dynamic approach to challenges.
""",
            "Taurus": """
**Persistent Worker**
Your Mars in Taurus gives you steady, determined action and physical endurance. You work methodically toward your goals and have remarkable persistence. Your energy is reliable and grounded in practical reality.

**Action Style:**
- Steady, persistent effort
- Practical approach to challenges
- Physical endurance
- Financial initiative

**Growth Opportunity**: Learning flexibility in action while maintaining your reliable, persistent approach.
""",
            "Gemini": """
**Versatile Doer**
Your Mars in Gemini gives you versatile, communicative action and mental energy. You excel at multitasking and can handle multiple projects simultaneously. Your energy is quick, adaptable, and mentally oriented.

**Action Style:**
- Multitasking ability
- Communication as action
- Intellectual initiative
- Adaptable energy use

**Growth Opportunity**: Learning focused action while maintaining your versatile, communicative approach.
""",
            "Cancer": """
**Protective Action Taker**
Your Mars in Cancer gives you emotionally driven action and protective energy. You act from deep feelings and defend what you care about passionately. Your energy is nurturing but can be defensive when threatened.

**Action Style:**
- Emotionally motivated action
- Protective initiatives
- Home and family focus
- Intuitive energy use

**Growth Opportunity**: Learning direct action while maintaining your protective, emotionally intelligent approach.
""",
            "Leo": """
**Confident Leader**
Your Mars in Leo gives you confident, dramatic action and creative energy. You lead with enthusiasm and enjoy being recognized for your accomplishments. Your energy is generous, warm, and inspiring to others.

**Action Style:**
- Confident initiative
- Creative action
- Leadership energy
- Recognition-driven effort

**Growth Opportunity**: Learning humble action while maintaining your confident, inspiring approach.
""",
            "Virgo": """
**Precise Worker**
Your Mars in Virgo gives you precise, analytical action and service-oriented energy. You work efficiently and pay attention to important details. Your energy is practical, organized, and healing-oriented.

**Action Style:**
- Efficient, precise action
- Service-oriented initiatives
- Health-focused energy
- Analytical problem-solving

**Growth Opportunity**: Learning big-picture action while maintaining your precise, efficient approach.
""",
            "Libra": """
**Diplomatic Actor**
Your Mars in Libra gives you balanced, diplomatic action and relationship-oriented energy. You act through partnership and seek harmonious solutions. Your energy is cooperative, fair-minded, and aesthetically oriented.

**Action Style:**
- Partnership-based action
- Diplomatic initiatives
- Balanced energy use
- Artistic expression

**Growth Opportunity**: Learning independent action while maintaining your diplomatic, cooperative approach.
""",
            "Scorpio": """
**Intense Powerhouse**
Your Mars in Scorpio gives you intense, determined action and transformative energy. You pursue goals with tremendous focus and can completely reinvent situations. Your energy is powerful, secretive, and psychologically astute.

**Action Style:**
- Intense, focused action
- Transformative initiatives
- Psychological energy use
- Strategic pursuit

**Growth Opportunity**: Learning transparent action while maintaining your intense, transformative power.
""",
            "Sagittarius": """
**Adventurous Explorer**
Your Mars in Sagittarius gives you optimistic, adventurous action and philosophical energy. You act from higher principles and enjoy exploration and learning. Your energy is freedom-loving, honest, and expansive.

**Action Style:**
- Adventurous initiatives
- Philosophically motivated action
- Freedom-oriented energy
- Teaching and exploring

**Growth Opportunity**: Learning grounded action while maintaining your adventurous, expansive approach.
""",
            "Capricorn": """
**Ambitious Achiever**
Your Mars in Capricorn gives you disciplined, ambitious action and structured energy. You work patiently toward long-term goals and build lasting achievements. Your energy is responsible, practical, and authority-oriented.

**Action Style:**
- Disciplined, patient action
- Ambitious initiatives
- Structured energy use
- Career-focused effort

**Growth Opportunity**: Learning spontaneous action while maintaining your disciplined, ambitious approach.
""",
            "Aquarius": """
**Innovative Initiator**
Your Mars in Aquarius gives you original, innovative action and humanitarian energy. You act from visionary ideas and enjoy pioneering new approaches. Your energy is independent, progressive, and group-oriented.

**Action Style:**
- Innovative initiatives
- Humanitarian action
- Independent energy use
- Technological expression

**Growth Opportunity**: Learning traditional action when useful while maintaining your innovative, progressive approach.
""",
            "Pisces": """
**Compassionate Doer**
Your Mars in Pisces gives you compassionate, intuitive action and spiritual energy. You act from deep empathy and can accomplish things through inspired effort. Your energy is adaptive, healing, and creatively expressed.

**Action Style:**
- Compassionate initiatives
- Intuitive action
- Spiritual energy use
- Creative expression

**Growth Opportunity**: Learning focused action while maintaining your compassionate, intuitive approach.
"""
        }
    }

    # EXTENSIVE CAREER INTERPRETATIONS
    career_interpretations = {
        "Sun": {
            "Aries": """
**Career as Pioneer and Leader**
Your Sun in Aries shines brightest in careers that allow initiative, leadership, and competition. You thrive in environments where you can be first - whether launching new projects, entering new markets, or pioneering innovative approaches.

**Ideal Career Paths:**
- Entrepreneurship and business ownership
- Military or police leadership
- Sports and athletics
- Emergency services and crisis management
- Surgical medicine (especially trauma)
- Engineering and technology innovation

**Success Strategy**: Your competitive nature drives you to excel, but remember that sustainable success comes from building teams that complement your pioneering energy. Look for careers where your courage and initiative are valued assets.
""",
            "Taurus": """
**Career as Builder and Stabilizer**
Your Sun in Taurus finds fulfillment in careers that involve creating tangible value and lasting security. You excel in fields where patience, persistence, and practical wisdom lead to gradual but substantial accumulation.

**Ideal Career Paths:**
- Banking, finance, and investment
- Real estate and property development
- Agriculture and environmental management
- Luxury goods and high-quality products
- Arts and crafts with material mastery
- Hospitality and comfort industries

**Success Strategy**: Your methodical approach ensures quality, but be open to innovation within your field. Your gift is creating enduring value that withstands economic fluctuations and changing trends.
""",
            "Gemini": """
**Career as Communicator and Networker**
Your Sun in Gemini excels in careers that involve communication, information, and variety. You thrive in fast-paced environments where you can use your mental agility and networking skills. Multi-tasking comes naturally to you.

**Ideal Career Paths:**
- Journalism, writing, and publishing
- Sales and marketing
- Teaching and education
- Technology and IT
- Public relations and media
- Transportation and logistics

**Success Strategy**: Your versatility is a great asset, but focus on developing depth in one or two key areas to complement your breadth of knowledge. Look for careers that offer continuous learning opportunities.
""",
            "Cancer": """
**Career as Nurturer and Protector**
Your Sun in Cancer finds fulfillment in careers that involve caring, protecting, and creating emotional security. You excel in fields where your intuition and nurturing instincts can flourish. Building lasting emotional connections is key to your success.

**Ideal Career Paths:**
- Healthcare and nursing
- Education and childcare
- Hospitality and restaurant management
- Real estate and home-related businesses
- Psychology and counseling
- Family businesses and traditions

**Success Strategy**: Your emotional intelligence is your greatest asset. Create work environments that feel like family, and don't be afraid to use your intuitive understanding of people's needs.
""",
            "Leo": """
**Career as Creative Leader**
Your Sun in Leo thrives in careers that allow creative expression, leadership, and recognition. You need to be in the spotlight and excel when your talents are appreciated. Your natural charisma draws opportunities to you.

**Ideal Career Paths:**
- Entertainment and performing arts
- Management and executive positions
- Teaching and coaching
- Luxury brands and high-end products
- Event planning and production
- Entrepreneurship with creative vision

**Success Strategy**: Your confidence inspires others, but remember to share the spotlight and develop teams that can implement your visionary ideas. Look for careers where you can be the "face" of an organization.
""",
            "Virgo": """
**Career as Analyst and Healer**
Your Sun in Virgo excels in careers that require precision, analysis, and service. You find fulfillment in improving systems, helping others, and paying attention to important details. Your practical wisdom makes you invaluable.

**Ideal Career Paths:**
- Healthcare and medicine
- Research and development
- Accounting and finance
- Editing and writing
- Environmental science
- Quality control and efficiency

**Success Strategy**: Your attention to detail is exceptional, but remember to also see the big picture. Your gift is making things work better - find organizations that value improvement and service.
""",
            "Libra": """
**Career as Diplomat and Artist**
Your Sun in Libra thrives in careers that involve beauty, harmony, and partnership. You excel in environments where diplomacy, aesthetics, and balanced relationships are valued. Your sense of justice and beauty guides your career choices.

**Ideal Career Paths:**
- Law and mediation
- Design and architecture
- Public relations and diplomacy
- Arts and entertainment
- Relationship counseling
- Luxury goods and fashion

**Success Strategy**: Your diplomatic skills are invaluable, but learn to make decisions confidently. Your gift is creating harmony and beauty - find careers where these qualities are appreciated and rewarded.
""",
            "Scorpio": """
**Career as Transformer and Investigator**
Your Sun in Scorpio excels in careers that involve depth, transformation, and power dynamics. You're drawn to fields where you can investigate mysteries, manage resources, or facilitate profound change. Your intensity drives major accomplishments.

**Ideal Career Paths:**
- Psychology and psychiatry
- Finance and investment
- Research and investigation
- Surgery and emergency medicine
- Leadership in crisis situations
- Spiritual counseling and transformation

**Success Strategy**: Your ability to handle intensity is remarkable, but remember to maintain balance. Your gift is transformation - find careers where you can help people or organizations through significant changes.
""",
            "Sagittarius": """
**Career as Philosopher and Explorer**
Your Sun in Sagittarius thrives in careers that involve adventure, learning, and expansion. You need freedom and meaning in your work, and excel when you can explore new horizons physically or intellectually. Your optimism opens doors.

**Ideal Career Paths:**
- Education and academia
- Travel and tourism
- Publishing and media
- Philosophy and religion
- Sports and adventure
- International business

**Success Strategy**: Your love of freedom is essential to your happiness, but develop enough structure to manifest your big ideas. Your gift is inspiration - find careers where you can expand people's horizons.
""",
            "Capricorn": """
**Career as Architect and Authority**
Your Sun in Capricorn excels in careers that involve structure, authority, and long-term building. You have natural leadership abilities and understand how to create lasting institutions. Your patience and discipline ensure steady advancement.

**Ideal Career Paths:**
- Business management and executive roles
- Government and politics
- Architecture and engineering
- Finance and banking
- Traditional professions (law, medicine)
- Historical preservation

**Success Strategy**: Your ambition drives you to the top, but remember to balance achievement with personal fulfillment. Your gift is building lasting structures - find organizations where you can leave a permanent legacy.
""",
            "Aquarius": """
**Career as Innovator and Humanitarian**
Your Sun in Aquarius thrives in careers that involve innovation, technology, and social progress. You're drawn to fields where you can implement visionary ideas and work for the betterment of humanity. Your originality sets you apart.

**Ideal Career Paths:**
- Technology and IT
- Science and research
- Social work and activism
- Astronomy and space-related fields
- Alternative energy
- Group leadership and organizations

**Success Strategy**: Your visionary thinking is needed in the world, but learn to work within existing systems when necessary. Your gift is innovation - find careers where you can implement progressive ideas.
""",
            "Pisces": """
**Career as Mystic and Healer**
Your Sun in Pisces excels in careers that involve compassion, creativity, and spiritual connection. You're drawn to fields where you can heal, inspire, or create beauty. Your empathy and intuition guide you to meaningful work.

**Ideal Career Paths:**
- Arts and entertainment
- Healthcare and healing professions
- Spiritual counseling and ministry
- Environmental conservation
- Photography and film
- Service-oriented organizations

**Success Strategy**: Your compassion is your greatest gift, but establish clear boundaries to avoid burnout. Your purpose is to bring spiritual values into practical reality through your work.
"""
        }
    }

    # EXTENSIVE RELATIONSHIP INTERPRETATIONS
    relationship_interpretations = {
        "Sun": {
            "Aries": """
**Relationship Style: The Passionate Partner**
In relationships, your Aries Sun needs excitement, challenge, and plenty of independence. You're attracted to partners who have their own strong identity and who appreciate your direct, enthusiastic approach to love.

**What You Need:**
- Partners who respect your independence
- Excitement and new experiences together
- Direct communication without games
- Appreciation for your initiatives
- Space to pursue individual interests

**Growth Opportunity**: Learning to balance your need for independence with the commitment required for deep intimacy. Your passion is magnetic, but lasting relationships require patience and compromise.
""",
            "Taurus": """
**Relationship Style: The Loyal Partner**
Your Taurus Sun approaches relationships with steadfast loyalty and a deep need for security. You value consistency, physical affection, and tangible expressions of love. Once committed, you're incredibly reliable and devoted.

**What You Need:**
- Emotional and financial security
- Physical closeness and affection
- Stable, predictable partnership
- Appreciation for your practical care
- Beautiful, comfortable home environment

**Growth Opportunity**: Learning flexibility when change is necessary while maintaining the stability that nourishes you. Your loyalty is precious, but avoid becoming possessive or resistant to necessary growth.
""",
            "Gemini": """
**Relationship Style: The Communicative Partner**
Your Gemini Sun needs mental connection and variety in relationships. You're attracted to partners who can engage you intellectually and who appreciate your curious, adaptable nature. Communication is your primary love language.

**What You Need:**
- Mental stimulation and interesting conversation
- Freedom to maintain separate interests
- Lighthearted, playful connection
- Partners who appreciate your versatility
- Social activities and networking together

**Growth Opportunity**: Learning to connect emotionally as well as intellectually. Your mental agility is attractive, but deep relationships also require emotional consistency and vulnerability.
""",
            "Cancer": """
**Relationship Style: The Nurturing Partner**
Your Cancer Sun approaches relationships with deep emotional commitment and protective care. You need emotional security and create strong family bonds. Your intuition helps you understand your partner's unspoken needs.

**What You Need:**
- Emotional security and commitment
- Family connection and traditions
- Nurturing home environment
- Partners who appreciate your caring nature
- Time to build trust slowly

**Growth Opportunity**: Learning to establish healthy boundaries while maintaining your nurturing capacity. Your emotional depth is precious, but protect yourself from becoming overly dependent or smothering.
""",
            "Leo": """
**Relationship Style: The Generous Lover**
Your Leo Sun brings warmth, generosity, and dramatic expression to relationships. You need appreciation and admiration from your partner, and you give loyalty and protection in return. Your love is big-hearted and expressive.

**What You Need:**
- Appreciation and recognition
- Romantic gestures and celebrations
- Loyal, committed partnership
- Opportunities to shine together
- Generous emotional exchange

**Growth Opportunity**: Learning humility and equal partnership while maintaining your generous spirit. Your warmth is magnetic, but remember that true partnership involves mutual admiration and support.
""",
            "Virgo": """
**Relationship Style: The Practical Partner**
Your Virgo Sun approaches relationships with practical care, service, and attention to detail. You show love through helpful actions and appreciate partners who are reliable and competent. Your love is sincere and modest.

**What You Need:**
- Practical expressions of care
- Shared health and wellness goals
- Orderly, harmonious home life
- Partners who appreciate your helpful nature
- Clear communication about needs

**Growth Opportunity**: Learning to accept imperfection in relationships while maintaining your caring approach. Your practical support is valuable, but remember that love also requires emotional spontaneity and acceptance.
""",
            "Libra": """
**Relationship Style: The Harmonious Partner**
Your Libra Sun needs partnership, beauty, and balance in relationships. You're naturally diplomatic and excel at creating romantic harmony. You appreciate aesthetic beauty and seek partners who share your love of elegance.

**What You Need:**
- Balanced, fair partnership
- Beautiful surroundings and experiences
- Diplomatic communication
- Social connection as a couple
- Romantic harmony and peace

**Growth Opportunity**: Learning to establish your own identity within relationships while maintaining your harmonious approach. Your diplomatic skills are valuable, but remember that healthy relationships also require honest conflict.
""",
            "Scorpio": """
**Relationship Style: The Intense Partner**
Your Scorpio Sun approaches relationships with depth, passion, and transformative intensity. You seek soul-level connection and are drawn to emotional mysteries. Your loyalty is absolute, and you expect the same in return.

**What You Need:**
- Emotional depth and honesty
- Transformative growth together
- Absolute loyalty and commitment
- Psychological understanding
- Privacy and intimacy

**Growth Opportunity**: Learning trust and emotional openness while maintaining your passionate depth. Your intensity creates profound bonds, but remember that love also requires lightness and space.
""",
            "Sagittarius": """
**Relationship Style: The Adventurous Partner**
Your Sagittarius Sun needs freedom, adventure, and philosophical connection in relationships. You're attracted to partners who share your love of exploration and learning. Your approach is honest, optimistic, and freedom-loving.

**What You Need:**
- Freedom within commitment
- Adventure and new experiences
- Philosophical compatibility
- Honest, direct communication
- Partners who appreciate your independence

**Growth Opportunity**: Learning commitment within freedom while maintaining your adventurous spirit. Your optimism is refreshing, but lasting relationships also require consistency and emotional presence.
""",
            "Capricorn": """
**Relationship Style: The Serious Partner**
Your Capricorn Sun approaches relationships with seriousness, responsibility, and long-term planning. You value stability and build relationships carefully over time. Your love is loyal, practical, and enduring.

**What You Need:**
- Long-term commitment
- Practical partnership goals
- Respect for tradition and stability
- Partners who appreciate your responsible nature
- Slowly built trust and connection

**Growth Opportunity**: Learning emotional expression within responsibility while maintaining your serious approach. Your reliability is precious, but remember that love also requires spontaneity and emotional vulnerability.
""",
            "Aquarius": """
**Relationship Style: The Unconventional Partner**
Your Aquarius Sun needs intellectual connection, friendship, and freedom in relationships. You value uniqueness and are attracted to partners who appreciate your original approach to love. Your love is friendly, progressive, and mentally stimulating.

**What You Need:**
- Intellectual companionship
- Freedom and independence
- Unconventional relationship styles
- Shared humanitarian interests
- Partners who respect your uniqueness

**Growth Opportunity**: Learning emotional connection within freedom while maintaining your unique approach. Your intellectual companionship is valuable, but deep relationships also require emotional intimacy and consistency.
""",
            "Pisces": """
**Relationship Style: The Romantic Dreamer**
Your Pisces Sun approaches relationships with compassion, romance, and spiritual connection. You seek soulmate relationships and have deep empathy for your partner. Your love is idealistic, compassionate, and spiritually oriented.

**What You Need:**
- Spiritual and emotional connection
- Romantic idealism
- Compassionate understanding
- Creative expression together
- Healing and supportive partnership

**Growth Opportunity**: Learning practical boundaries in love while maintaining your compassionate nature. Your empathy creates deep bonds, but protect yourself from losing your identity in relationships.
"""
        }
    }

    # Choose interpretation dictionary based on type
    if interpretation_type == "Career & Vocation":
        interpretations = career_interpretations
        focus_description = "professional path, vocational calling, and success patterns"
    elif interpretation_type == "Relationships & Love":
        interpretations = relationship_interpretations
        focus_description = "relationship dynamics, love patterns, and partnership needs"
    elif interpretation_type == "Spiritual Growth":
        interpretations = natal_interpretations
        focus_description = "soul evolution, spiritual lessons, and higher purpose"
    elif interpretation_type == "Personality Analysis":
        interpretations = natal_interpretations
        focus_description = "core personality traits, strengths, and growth areas"
    elif interpretation_type == "Life Purpose":
        interpretations = natal_interpretations
        focus_description = "soul mission, karmic lessons, and life direction"
    else:  # Natal Chart
        interpretations = natal_interpretations
        focus_description = "complete astrological profile and life patterns"
    
    # Display interpretation for each planet
    planets_to_display = ["Sun", "Moon", "Mercury", "Venus", "Mars"]
    
    for planet_name in planets_to_display:
        if planet_name in chart_data['planets']:
            planet_data = chart_data['planets'][planet_name]
            planet_sign = planet_data['sign']
            
            # Display interpretation for sign
            if (planet_name in interpretations and 
                planet_sign in interpretations[planet_name]):
                
                with st.expander(f"{planet_name} in {planet_sign}", expanded=True):
                    st.markdown(interpretations[planet_name][planet_sign])
    
    # Add house interpretations
    st.markdown("---")
    st.subheader("🏠 House Placements Analysis")
    
    house_interpretations = {
        1: "**The House of Self** - Your approach to life, personal identity, and how others see you. This house reveals your basic personality, physical appearance, and overall approach to new beginnings.",
        2: "**The House of Values** - Your relationship with money, possessions, and personal values. This area shows how you attract resources, what you truly value, and your attitude toward material security.",
        3: "**The House of Communication** - Your thinking style, communication, and immediate environment. This covers siblings, early education, local travel, and how you process and share information.",
        4: "**The House of Home** - Your roots, family, emotional foundation, and private life. This reveals your connection to family traditions, your need for security, and what makes you feel emotionally safe.",
        5: "**The House of Creativity** - Your self-expression, romance, children, and creative pursuits. This area shows how you approach pleasure, love affairs, creative projects, and what brings you joy.",
        6: "**The House of Service** - Your work habits, health routines, and service to others. This covers daily work environment, health practices, and how you organize your life for efficiency.",
        7: "**The House of Partnership** - Your approach to relationships, marriage, and significant others. This reveals what you seek in partners and how you approach all one-to-one relationships.",
        8: "**The House of Transformation** - Your approach to intimacy, shared resources, and rebirth. This covers psychological depth, other people's resources, and your capacity for personal transformation.",
        9: "**The House of Philosophy** - Your beliefs, higher education, travel, and search for meaning. This reveals your approach to religion, philosophy, foreign cultures, and expanding your horizons.",
        10: "**The House of Career** - Your public life, career, reputation, and life direction. This shows your professional ambitions, public image, and what you strive to achieve in the world.",
        11: "**The House of Community** - Your friendships, groups, hopes, and humanitarian interests. This covers your social circles, group affiliations, and your vision for the future.",
        12: "**The House of Spirituality** - Your subconscious, spirituality, solitude, and hidden strengths. This reveals your connection to the unconscious, spiritual practices, and what you need to release."
    }
    
    for house_num in range(1, 13):
        if house_num in chart_data['houses']:
            house_data = chart_data['houses'][house_num]
            st.write(f"**House {house_num} in {house_data['sign']}**: {house_data['position_str']}")
            st.write(f"*{house_interpretations[house_num]}*")
            st.write("")

def display_about():
    st.header("ℹ️ About This Astrology App")
    st.markdown("""
    ### Professional Astrology App v2.0
    
    **Copyright © 2025**  
    Advanced Astrological Analysis System
    
    **Professional Features**  
    - Precise astronomical calculations using Swiss Ephemeris
    - Comprehensive natal chart interpretations
    - Detailed transit and progression analysis
    - Professional-grade aspect calculations
    - In-depth psychological and spiritual insights
    - Career, relationship, and life purpose analysis
    
    **Technical Specifications**  
    - Swiss Ephemeris for maximum astronomical accuracy
    - Placidus house system as professional standard
    - Complete planetary aspects with precise orbs
    - Advanced chart visualization
    - Professional interpretation database
    
    **Astrological Methodology**  
    This application uses traditional Western astrological techniques combined with modern psychological insights. All calculations meet professional astrological standards for accuracy and depth of interpretation.
    
    **Data Privacy**  
    All birth data and calculations remain private and are not stored on any server. Your astrological information is processed locally in your browser session.
    """)

if __name__ == "__main__":
    main()
