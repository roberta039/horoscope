# app.py
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import math
import ephem
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px

class AstroCalculator:
    def __init__(self):
        self.planets = {
            'Sun': ephem.Sun(),
            'Moon': ephem.Moon(),
            'Mercury': ephem.Mercury(),
            'Venus': ephem.Venus(),
            'Mars': ephem.Mars(),
            'Jupiter': ephem.Jupiter(),
            'Saturn': ephem.Saturn(),
            'Uranus': ephem.Uranus(),
            'Neptune': ephem.Neptune(),
            'Pluto': ephem.Pluto(),
            'Chiron': None,  # Va fi calculat separat
            'North Node': None  # Nodul Nord (calculat)
        }
        
        self.signs = [
            'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
            'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
        ]
        
        self.aspects = {
            'Conjunction': (0, 8),
            'Sextile': (60, 6),
            'Square': (90, 8),
            'Trine': (120, 8),
            'Opposition': (180, 8),
            'Semi-Sextile': (30, 3),
            'Semi-Square': (45, 3),
            'Sesqui-Square': (135, 3),
            'Quincunx': (150, 3),
            'Quintile': (72, 2),
            'Decile': (36, 2),
            'Biquintile': (144, 2)
        }

    def calculate_planet_positions(self, date: datetime, lat: float, lon: float) -> Dict:
        """Calculează pozițiile planetare pentru o dată și locație dată"""
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = date
        
        positions = {}
        
        for planet_name, planet in self.planets.items():
            if planet is not None:
                try:
                    planet.compute(observer)
                    positions[planet_name] = {
                        'longitude': math.degrees(planet.ra),
                        'latitude': math.degrees(planet.dec),
                        'sign': self.get_sign(math.degrees(planet.ra)),
                        'house': self.calculate_house(math.degrees(planet.ra), date, lat, lon)
                    }
                except Exception as e:
                    positions[planet_name] = {
                        'longitude': 0,
                        'latitude': 0,
                        'sign': 'Aries',
                        'house': 1
                    }
        
        # Calcul Nod Nord (simplificat)
        positions['North Node'] = self.calculate_north_node(date)
        positions['Chiron'] = self.calculate_chiron(date)
        
        return positions

    def get_sign(self, longitude: float) -> str:
        """Determină semnul zodiacal pentru o longitudine dată"""
        sign_index = int(longitude / 30) % 12
        return self.signs[sign_index]

    def calculate_house(self, longitude: float, date: datetime, lat: float, lon: float) -> int:
        """Calculează casa pentru o longitudine dată (sistem Placidus)"""
        # Calcul simplificat - în implementarea reală s-ar folosi calculul caseleor
        ascendant = self.calculate_ascendant(date, lat, lon)
        house_size = 30  # 360/12
        house_num = int((longitude - ascendant) / house_size) % 12 + 1
        return house_num if house_num > 0 else 12

    def calculate_ascendant(self, date: datetime, lat: float, lon: float) -> float:
        """Calculează ascendentul"""
        # Calcul simplificat - în implementarea reală s-ar folosi formule precise
        observer = ephem.Observer()
        observer.lat = str(lat)
        observer.lon = str(lon)
        observer.date = date
        
        sun = ephem.Sun()
        sun.compute(observer)
        
        # Formula simplificată pentru ascendent
        ascendant = (math.degrees(sun.ra) + 90) % 360
        return ascendant

    def calculate_north_node(self, date: datetime) -> Dict:
        """Calculează Nodul Nord (simplificat)"""
        # Calcul bazat pe ciclul de 18.6 ani al Nodurilor Lunare
        cycle_days = 6798  # 18.6 ani în zile
        days_since_epoch = (date - datetime(2000, 1, 1)).days
        node_longitude = (days_since_epoch / cycle_days * 360) % 360
        
        return {
            'longitude': node_longitude,
            'latitude': 0,
            'sign': self.get_sign(node_longitude),
            'house': 1  # Va fi calculat corect mai târziu
        }

    def calculate_chiron(self, date: datetime) -> Dict:
        """Calculează Chiron (simplificat)"""
        # Orbită aproximativă a lui Chiron - 50.7 ani
        cycle_days = 18500  # 50.7 ani în zile
        days_since_epoch = (date - datetime(2000, 1, 1)).days
        chiron_longitude = (days_since_epoch / cycle_days * 360) % 360
        
        return {
            'longitude': chiron_longitude,
            'latitude': 0,
            'sign': self.get_sign(chiron_longitude),
            'house': 1  # Va fi calculat corect mai târziu
        }

    def calculate_aspects(self, positions: Dict) -> List[Dict]:
        """Calculează aspectele dintre planete"""
        aspects_found = []
        planets_list = list(positions.keys())
        
        for i in range(len(planets_list)):
            for j in range(i + 1, len(planets_list)):
                planet1 = planets_list[i]
                planet2 = planets_list[j]
                
                if planet1 in positions and planet2 in positions:
                    lon1 = positions[planet1]['longitude']
                    lon2 = positions[planet2]['longitude']
                    
                    # Diferența de longitudine
                    diff = abs(lon1 - lon2)
                    if diff > 180:
                        diff = 360 - diff
                    
                    # Verifică fiecare aspect
                    for aspect_name, (angle, orb) in self.aspects.items():
                        if abs(diff - angle) <= orb:
                            aspects_found.append({
                                'planet1': planet1,
                                'planet2': planet2,
                                'aspect': aspect_name,
                                'angle': angle,
                                'exact_diff': diff,
                                'orb': abs(diff - angle)
                            })
        
        return aspects_found
      # app.py (continuare)
def main():
    st.set_page_config(
        page_title="1.Chart Horoscope v2.42",
        page_icon="♐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # CSS personalizat
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #4B0082;
        text-align: center;
        margin-bottom: 2rem;
    }
    .planet-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #4B0082;
    }
    .aspect-card {
        background-color: #fff;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 5px;
        border-left: 3px solid #FF6B6B;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="main-header">♐ 1.Chart Horoscope v2.42</div>', unsafe_allow_html=True)
    
    # Inițializare calculator
    if 'calculator' not in st.session_state:
        st.session_state.calculator = AstroCalculator()
    
    if 'chart_data' not in st.session_state:
        st.session_state.chart_data = None
    
    if 'aspects_data' not in st.session_state:
        st.session_state.aspects_data = None
    
    # Sidebar pentru input
    with st.sidebar:
        st.header("📅 Birth Data")
        
        col1, col2 = st.columns(2)
        with col1:
            birth_date = st.date_input("Birth Date", datetime(1990, 1, 1))
        with col2:
            birth_time = st.time_input("Birth Time", datetime(1990, 1, 1, 12, 0))
        
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        col3, col4 = st.columns(2)
        with col3:
            latitude = st.number_input("Latitude", value=45.81, format="%.6f")
        with col4:
            longitude = st.number_input("Longitude", value=15.98, format="%.6f")
        
        timezone = st.selectbox("Time Zone", [
            "GMT-12", "GMT-11", "GMT-10", "GMT-9", "GMT-8", "GMT-7", 
            "GMT-6", "GMT-5", "GMT-4", "GMT-3", "GMT-2", "GMT-1", 
            "GMT", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", 
            "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12"
        ])
        
        house_system = st.selectbox("House System", ["Placidus", "Koch", "Equal", "Whole Sign"])
        
        if st.button("🔄 Calculate Chart", type="primary"):
            with st.spinner("Calculating planetary positions..."):
                st.session_state.chart_data = st.session_state.calculator.calculate_planet_positions(
                    birth_datetime, latitude, longitude
                )
                st.session_state.aspects_data = st.session_state.calculator.calculate_aspects(
                    st.session_state.chart_data
                )
            st.success("Chart calculated successfully!")
    
    # Tab-uri principale
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏠 Chart", "🔗 Aspects", "📊 Positions", "📖 Interpretation", "⚙️ Options"
    ])
    
    with tab1:
        display_chart_tab()
    
    with tab2:
        display_aspects_tab()
    
    with tab3:
        display_positions_tab()
    
    with tab4:
        display_interpretation_tab()
    
    with tab5:
        display_options_tab()

def display_chart_tab():
    st.header("Natal Chart")
    
    if st.session_state.chart_data:
        # Afișare roată astrologică simplificată
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Chart Wheel")
            create_chart_wheel(st.session_state.chart_data)
        
        with col2:
            st.subheader("Chart Data")
            display_chart_summary(st.session_state.chart_data)
    else:
        st.info("Please enter birth data and click 'Calculate Chart'")

def display_aspects_tab():
    st.header("Aspects")
    
    if st.session_state.aspects_data:
        # Filtre pentru aspecte
        col1, col2, col3 = st.columns(3)
        with col1:
            min_orb = st.slider("Minimum Orb", 0.0, 5.0, 0.0, 0.1)
        with col2:
            selected_aspects = st.multiselect(
                "Aspect Types",
                list(st.session_state.calculator.aspects.keys()),
                default=list(st.session_state.calculator.aspects.keys())
            )
        
        # Afișare aspecte filtrate
        filtered_aspects = [
            aspect for aspect in st.session_state.aspects_data 
            if aspect['aspect'] in selected_aspects and aspect['orb'] >= min_orb
        ]
        
        if filtered_aspects:
            for aspect in filtered_aspects:
                with st.container():
                    st.markdown(f"""
                    <div class="aspect-card">
                    <strong>{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}</strong><br>
                    Angle: {aspect['angle']}° | Exact: {aspect['exact_diff']:.2f}° | Orb: {aspect['orb']:.2f}°
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("No aspects found with the selected filters")
    else:
        st.info("Calculate a chart to see aspects")

def display_positions_tab():
    st.header("Planetary Positions")
    
    if st.session_state.chart_data:
        # Tabel cu pozițiile planetare
        positions_data = []
        for planet, data in st.session_state.chart_data.items():
            positions_data.append({
                'Planet': planet,
                'Longitude': f"{data['longitude']:.2f}°",
                'Sign': data['sign'],
                'House': data['house']
            })
        
        df = pd.DataFrame(positions_data)
        st.dataframe(df, use_container_width=True)
        
        # Grafic cu pozițiile
        fig = go.Figure()
        
        signs = [data['sign'] for data in st.session_state.chart_data.values()]
        houses = [data['house'] for data in st.session_state.chart_data.values()]
        planets = list(st.session_state.chart_data.keys())
        
        fig.add_trace(go.Scatterpolar(
            r=houses,
            theta=signs,
            text=planets,
            mode='markers+text',
            marker=dict(size=15, color='blue'),
            textposition="middle center"
        ))
        
        fig.update_layout(
            polar=dict(
                angularaxis=dict(
                    direction="clockwise",
                    period=12
                ),
                radialaxis=dict(
                    visible=True,
                    range=[0, 13]
                )
            ),
            showlegend=False,
            title="Planetary Positions in Houses"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Calculate a chart to see planetary positions")

def display_interpretation_tab():
    st.header("Chart Interpretation")
    
    if st.session_state.chart_data:
        # Interpretări de bază
        st.subheader("Sun Sign Interpretation")
        sun_sign = st.session_state.chart_data['Sun']['sign']
        st.write(f"Your Sun is in {sun_sign}. {get_sun_interpretation(sun_sign)}")
        
        st.subheader("Moon Sign Interpretation")
        moon_sign = st.session_state.chart_data['Moon']['sign']
        st.write(f"Your Moon is in {moon_sign}. {get_moon_interpretation(moon_sign)}")
        
        st.subheader("Ascendant Analysis")
        # Aici s-ar calcula ascendentul real
        st.info("Ascendant calculation requires precise house system implementation")
        
        st.subheader("Key Aspects")
        if st.session_state.aspects_data:
            major_aspects = [a for a in st.session_state.aspects_data if a['orb'] <= 3]
            for aspect in major_aspects[:5]:  # Primele 5 aspecte majore
                st.write(f"**{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}**")
                st.write(f"  - Influence: {get_aspect_interpretation(aspect)}")
    else:
        st.info("Calculate a chart to see interpretations")

def display_options_tab():
    st.header("Settings & Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Calculation Settings")
        st.checkbox("Use True Node", value=True)
        st.checkbox("Include Asteroids", value=False)
        st.checkbox("Show Declinations", value=False)
        
        st.selectbox("Default House System", ["Placidus", "Koch", "Equal", "Whole Sign"])
    
    with col2:
        st.subheader("Display Settings")
        st.checkbox("Show Glyphs", value=True)
        st.checkbox("Colorize Aspects", value=True)
        st.checkbox("Animate Chart", value=False)
        
        st.slider("Chart Size", 1, 10, 5)
    
    st.subheader("About")
    st.markdown("""
    **1.Chart Horoscope v2.42**
    - Original Palm OS version: 1998-2001
    - Reconstructed for modern web
    - Using PyEphem for astronomical calculations
    """)

# Funcții helper pentru interpretări
def get_sun_interpretation(sign):
    interpretations = {
        'Aries': "Energetic, pioneering, and courageous. You have a strong will and natural leadership abilities.",
        'Taurus': "Practical, reliable, and sensual. You value stability and have a strong connection to the material world.",
        'Gemini': "Communicative, curious, and adaptable. You have a quick mind and enjoy intellectual stimulation.",
        # ... adaugă pentru toate semnele
    }
    return interpretations.get(sign, "Basic interpretation not available.")

def get_moon_interpretation(sign):
    interpretations = {
        'Aries': "Your emotional nature is impulsive and enthusiastic.",
        'Taurus': "You seek emotional security through stability and comfort.",
        'Gemini': "Your emotions are changeable and you process feelings through communication.",
        # ... adaugă pentru toate semnele
    }
    return interpretations.get(sign, "Basic interpretation not available.")

def get_aspect_interpretation(aspect):
    return f"This {aspect['aspect']} creates a dynamic relationship between {aspect['planet1']} and {aspect['planet2']}."

def create_chart_wheel(chart_data):
    """Creează o reprezentare vizuală simplă a horoscopului"""
    fig = go.Figure()
    
    # Cercul exterior cu semnele
    angles = np.linspace(0, 2*np.pi, 13, endpoint=True)
    signs = st.session_state.calculator.signs
    
    for i, (angle, sign) in enumerate(zip(angles, signs)):
        x = 1.1 * np.cos(angle)
        y = 1.1 * np.sin(angle)
        fig.add_annotation(x=x, y=y, text=sign, showarrow=False, font=dict(size=10))
    
    # Planetele pe cerc
    for planet, data in chart_data.items():
        planet_angle = (data['longitude'] % 30) * np.pi / 15  # Convert to radians
        x = 0.8 * np.cos(planet_angle)
        y = 0.8 * np.sin(planet_angle)
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(size=12, color='red'),
            text=[planet[:3]],  # Abreviere
            textposition="middle center",
            name=planet
        ))
    
    fig.update_layout(
        xaxis=dict(visible=False, range=[-1.2, 1.2]),
        yaxis=dict(visible=False, range=[-1.2, 1.2]),
        showlegend=False,
        width=400,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_chart_summary(chart_data):
    """Afișează un rezumat al horoscopului"""
    st.metric("Sun Sign", chart_data['Sun']['sign'])
    st.metric("Moon Sign", chart_data['Moon']['sign'])
    st.metric("Ascendant", "Calculating...")  # S-ar calcula separat
    
    st.subheader("Planets in Signs")
    for planet in ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars']:
        if planet in chart_data:
            st.write(f"**{planet}**: {chart_data[planet]['sign']} (House {chart_data[planet]['house']})")

if __name__ == "__main__":
    main()
