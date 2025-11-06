import streamlit as st
import swisseph as swe
from datetime import datetime, timedelta
import pytz
import math

# Configurare pagină
st.set_page_config(page_title="Astrology App", page_icon="🌟", layout="wide")

# Dicționar cu capitalele lumii
capitale_lumii = {
    "Selectează o capitală": {"lat": 0, "lon": 0},
    "Bucharest": {"lat": 44.4268, "lon": 26.1025},
    "Paris": {"lat": 48.8566, "lon": 2.3522},
    "London": {"lat": 51.5074, "lon": -0.1278},
    "Berlin": {"lat": 52.5200, "lon": 13.4050},
    "Rome": {"lat": 41.9028, "lon": 12.4964},
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Lisbon": {"lat": 38.7223, "lon": -9.1393},
    "Amsterdam": {"lat": 52.3676, "lon": 4.9041},
    "Brussels": {"lat": 50.8503, "lon": 4.3517},
    "Vienna": {"lat": 48.2082, "lon": 16.3738},
    "Prague": {"lat": 50.0755, "lon": 14.4378},
    "Warsaw": {"lat": 52.2297, "lon": 21.0122},
    "Budapest": {"lat": 47.4979, "lon": 19.0402},
    "Athens": {"lat": 37.9838, "lon": 23.7275},
    "Stockholm": {"lat": 59.3293, "lon": 18.0686},
    "Oslo": {"lat": 59.9139, "lon": 10.7522},
    "Copenhagen": {"lat": 55.6761, "lon": 12.5683},
    "Helsinki": {"lat": 60.1699, "lon": 24.9384},
    "Dublin": {"lat": 53.3498, "lon": -6.2603},
    "Moscow": {"lat": 55.7558, "lon": 37.6173},
    "Kyiv": {"lat": 50.4501, "lon": 30.5234},
    "Minsk": {"lat": 53.9045, "lon": 27.5615},
    "Sofia": {"lat": 42.6977, "lon": 23.3219},
    "Zagreb": {"lat": 45.8150, "lon": 15.9819},
    "Belgrade": {"lat": 44.7866, "lon": 20.4489},
    "Bratislava": {"lat": 48.1486, "lon": 17.1077},
    "Ljubljana": {"lat": 46.0569, "lon": 14.5058},
    "Vilnius": {"lat": 54.6872, "lon": 25.2797},
    "Riga": {"lat": 56.9496, "lon": 24.1052},
    "Tallinn": {"lat": 59.4370, "lon": 24.7536},
    "Istanbul": {"lat": 41.0082, "lon": 28.9784},
    "Ankara": {"lat": 39.9334, "lon": 32.8597},
    "Beijing": {"lat": 39.9042, "lon": 116.4074},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
    "New Delhi": {"lat": 28.6139, "lon": 77.2090},
    "Washington D.C.": {"lat": 38.9072, "lon": -77.0369},
    "Ottawa": {"lat": 45.4215, "lon": -75.6972},
    "Canberra": {"lat": -35.2809, "lon": 149.1300},
    "Wellington": {"lat": -41.2865, "lon": 174.7762},
    "Brasilia": {"lat": -15.7975, "lon": -47.8919},
    "Buenos Aires": {"lat": -34.6037, "lon": -58.3816},
    "Mexico City": {"lat": 19.4326, "lon": -99.1332},
    "Cairo": {"lat": 30.0444, "lon": 31.2357},
    "Pretoria": {"lat": -25.7479, "lon": 28.2293},
    "Nairobi": {"lat": -1.2921, "lon": 36.8219},
    "Bangkok": {"lat": 13.7563, "lon": 100.5018},
    "Jakarta": {"lat": -6.2088, "lon": 106.8456},
    "Seoul": {"lat": 37.5665, "lon": 126.9780},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Dubai": {"lat": 25.2048, "lon": 55.2708},
    "Riyadh": {"lat": 24.7136, "lon": 46.6753},
    "Jerusalem": {"lat": 31.7683, "lon": 35.2137},
    "Tehran": {"lat": 35.6892, "lon": 51.3890},
    "Baghdad": {"lat": 33.3152, "lon": 44.3661},
    "Kabul": {"lat": 34.5553, "lon": 69.2075},
    "Islamabad": {"lat": 33.6844, "lon": 73.0479},
    "Dhaka": {"lat": 23.8103, "lon": 90.4125},
    "Hanoi": {"lat": 21.0278, "lon": 105.8342},
    "Manila": {"lat": 14.5995, "lon": 120.9842},
    "Kuala Lumpur": {"lat": 3.1390, "lon": 101.6869},
    "Colombo": {"lat": 6.9271, "lon": 79.8612},
    "Kathmandu": {"lat": 27.7172, "lon": 85.3240},
    "Ulaanbaatar": {"lat": 47.8864, "lon": 106.9057},
    "Pyongyang": {"lat": 39.0392, "lon": 125.7625},
    "Taipei": {"lat": 25.0330, "lon": 121.5654},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694},
    "Macau": {"lat": 22.1987, "lon": 113.5439},
    "Abu Dhabi": {"lat": 24.4539, "lon": 54.3773},
    "Doha": {"lat": 25.2854, "lon": 51.5310},
    "Muscat": {"lat": 23.5880, "lon": 58.3829},
    "Sana'a": {"lat": 15.3694, "lon": 44.1910},
    "Amman": {"lat": 31.9539, "lon": 35.9106},
    "Damascus": {"lat": 33.5138, "lon": 36.2765},
    "Beirut": {"lat": 33.8938, "lon": 35.5018},
    "Tbilisi": {"lat": 41.7151, "lon": 44.8271},
    "Yerevan": {"lat": 40.1792, "lon": 44.4991},
    "Baku": {"lat": 40.4093, "lon": 49.8671},
    "Ashgabat": {"lat": 37.9601, "lon": 58.3261},
    "Tashkent": {"lat": 41.2995, "lon": 69.2401},
    "Astana": {"lat": 51.1605, "lon": 71.4704},
    "Bishkek": {"lat": 42.8746, "lon": 74.5698},
    "Dushanbe": {"lat": 38.5598, "lon": 68.7870},
    "Almaty": {"lat": 43.2220, "lon": 76.8512}
}

# Funcție pentru conversia grade-minute în grade zecimale
def convert_dms_to_decimal(degrees, minutes=0, seconds=0, direction=''):
    decimal = degrees + minutes/60 + seconds/3600
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal

# Funcție pentru parsarea inputului de longitudine
def parse_longitude_input(lon_input):
    try:
        # Încercă să parseze ca float direct
        return float(lon_input)
    except ValueError:
        # Încercă să parseze formatul grade-minute
        parts = str(lon_input).replace('°', ' ').replace("'", ' ').replace('"', ' ').split()
        if len(parts) >= 2:
            degrees = float(parts[0])
            minutes = float(parts[1])
            direction = parts[2] if len(parts) > 2 else 'E'
            return convert_dms_to_decimal(degrees, minutes, 0, direction)
        else:
            raise ValueError("Format longitudine invalid")

# Inițializare Swiss Ephemeris
swe.set_ephe_path('./ephe')

# Dicționare pentru planete și semne
planets = {
    swe.SUN: "Soare",
    swe.MOON: "Lună",
    swe.MERCURY: "Mercur",
    swe.VENUS: "Venus",
    swe.MARS: "Marte",
    swe.JUPITER: "Jupiter",
    swe.SATURN: "Saturn",
    swe.URANUS: "Uranus",
    swe.NEPTUNE: "Neptun",
    swe.PLUTO: "Pluto",
    swe.TRUE_NODE: "Nod Lunar"
}

signs = [
    "Berbec", "Taur", "Gemeni", "Rac", "Leu", "Fecioară",
    "Balanță", "Scorpion", "Săgetător", "Capricorn", "Vărsător", "Pești"
]

houses = [
    "House 1", "House 2", "House 3", "House 4", "House 5", "House 6",
    "House 7", "House 8", "House 9", "House 10", "House 11", "House 12"
]

aspects = {
    0: "Conjuncție",
    60: "Sextil",
    90: "Pătrat",
    120: "Trigon",
    180: "Opoziție"
}

# Titlul aplicației
st.title("🌌 Aplicație de Astrologie")
st.markdown("---")

# Sidebar pentru input utilizator
with st.sidebar:
    st.header("📅 Date de Naștere")
    
    # Data și ora nașterii
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input("Data nașterii", value=datetime(1990, 1, 1))
    with col2:
        birth_time = st.time_input("Ora nașterii", value=datetime(1990, 1, 1, 12, 0))
    
    # Locație - Dropdown pentru capitale
    st.header("📍 Locație")
    
    selected_capital = st.selectbox("Capitală", list(capitale_lumii.keys()))
    
    if selected_capital != "Selectează o capitală":
        capital_data = capitale_lumii[selected_capital]
        st.info(f"📍 {selected_capital}: Lat {capital_data['lat']:.4f}°, Lon {capital_data['lon']:.4f}°")
    
    # Câmpuri pentru coordonate manuale
    st.subheader("Sau introdu coordonate manual:")
    
    col_lat, col_lon = st.columns(2)
    with col_lat:
        latitude = st.number_input("Latitude", value=44.4268, format="%.6f")
    with col_lon:
        lon_input = st.text_input("Longitude", value="26.1025")
    
    # Buton pentru calcul
    calculate_button = st.button("🎯 Calculează Horoscop", type="primary")

# Funcție pentru calculul pozițiilor planetare
def calculate_planet_positions(julian_day):
    positions = {}
    for planet in planets.keys():
        if planet == swe.TRUE_NODE:
            # Calcul special pentru Nodul Lunar
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        else:
            flags = swe.FLG_SWIEPH | swe.FLG_SPEED
        
        planet_data = swe.calc_ut(julian_day, planet, flags=flags)
        longitude = planet_data[0][0]
        
        # Calcul semn și grad
        sign_index = int(longitude / 30)
        sign_degrees = longitude % 30
        
        positions[planet] = {
            'longitude': longitude,
            'sign': signs[sign_index],
            'degrees': sign_degrees,
            'speed': planet_data[0][3]
        }
    
    return positions

# Funcție pentru calculul caselor
def calculate_houses(julian_day, lat, lon):
    house_cusps, ascmc = swe.houses(julian_day, lat, lon, b'P')
    return house_cusps, ascmc

# Funcție pentru aspecte
def calculate_aspects(positions):
    aspect_list = []
    planets_list = list(positions.keys())
    
    for i in range(len(planets_list)):
        for j in range(i + 1, len(planets_list)):
            planet1 = planets_list[i]
            planet2 = planets_list[j]
            
            lon1 = positions[planet1]['longitude']
            lon2 = positions[planet2]['longitude']
            
            # Calcul diferență unghiulară
            diff = abs(lon1 - lon2)
            if diff > 180:
                diff = 360 - diff
            
            # Verifică aspecte majore
            for aspect_angle in aspects.keys():
                orb = 8 if aspect_angle in [0, 180] else 3  # Orb mai larg pentru conjuncție/opoziție
                if abs(diff - aspect_angle) <= orb:
                    aspect_list.append({
                        'planet1': planets[planet1],
                        'planet2': planets[planet2],
                        'aspect': aspects[aspect_angle],
                        'angle': diff,
                        'orb': abs(diff - aspect_angle)
                    })
    
    return aspect_list

# Main app logic
if calculate_button:
    try:
        # Procesare longitudine
        try:
            if selected_capital != "Selectează o capitală":
                longitude = capitale_lumii[selected_capital]['lon']
                latitude = capitale_lumii[selected_capital]['lat']
            else:
                longitude = parse_longitude_input(lon_input)
        except ValueError as e:
            st.error(f"Eroare la parsarea longitudinii: {e}")
            st.stop()
        
        # Creare datetime pentru naștere
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        # Convertire la Julian Day
        julian_day = swe.julday(birth_datetime.year, birth_datetime.month, birth_datetime.day, 
                               birth_datetime.hour + birth_datetime.minute/60.0)
        
        # Calcul poziții planetare
        with st.spinner("🔮 Calculez pozițiile planetare..."):
            positions = calculate_planet_positions(julian_day)
            houses_cusps, ascmc = calculate_houses(julian_day, latitude, longitude)
            aspect_list = calculate_aspects(positions)
        
        # Afișare rezultate
        st.success("✨ Calcul complet!")
        
        # Layout cu coloane
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🪐 Poziții Planetare")
            for planet, data in positions.items():
                planet_name = planets[planet]
                st.write(f"**{planet_name}**: {data['sign']} {data['degrees']:.1f}°")
        
        with col2:
            st.subheader("🏠 Case Astrologice")
            for i, cusp in enumerate(houses_cusps[:12]):
                sign_index = int(cusp / 30)
                degrees = cusp % 30
                st.write(f"**{houses[i]}**: {signs[sign_index]} {degrees:.1f}°")
        
        # Aspecte
        st.subheader("🔗 Aspecte Astrologice")
        if aspect_list:
            for aspect in aspect_list:
                st.write(f"**{aspect['planet1']}** {aspect['aspect']} **{aspect['planet2']}** "
                        f"({aspect['angle']:.1f}°, orb: {aspect['orb']:.1f}°)")
        else:
            st.write("Nu s-au găsit aspecte majore în orbul specificat")
        
        # Informații Ascendent
        ascendant_sign_index = int(ascmc[0] / 30)
        ascendant_degrees = ascmc[0] % 30
        st.info(f"**Ascendent**: {signs[ascendant_sign_index]} {ascendant_degrees:.1f}°")
        
    except Exception as e:
        st.error(f"Eroare la calcul: {e}")

# Secțiune informații
with st.expander("ℹ️ Instrucțiuni de utilizare"):
    st.markdown("""
    1. **Selectează data și ora nașterii**
    2. **Alege o capitală** din dropdown sau introdu coordonate manual
    3. **Formate acceptate pentru longitudine**:
       - Grade zecimale: `26.1025`
       - Grade-minute: `26°6'` sau `26 6`
    4. **Apasă butonul 'Calculează Horoscop'**
    
    ⚠️ **Notă**: Asigură-te că fișierele efemeride sunt în folderul `./ephe/`
    """)

# Footer
st.markdown("---")
st.markdown("*Aplicație dezvoltată cu Swiss Ephemeris și Streamlit*")
