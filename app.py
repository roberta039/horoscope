import streamlit as st
import ephem
from datetime import datetime
import math
import pytz
import pandas as pd

# Configurare pagină
st.set_page_config(
    page_title="Astrology App - Horoscope Calculator",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Stiluri CSS personalizate
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #6a0dad;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.8rem !important;
        color: #8a2be2;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .planet-info {
        font-size: 1.2rem !important;
        padding: 10px;
        margin: 5px 0;
    }
    .interpretation-box {
        background-color: #f0f8ff;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6a0dad;
        margin: 10px 0;
        font-size: 1.1rem !important;
    }
    .stSelectbox label, .stTextInput label, .stDateInput label {
        font-size: 1.2rem !important;
        font-weight: bold !important;
    }
    .stButton button {
        font-size: 1.3rem !important;
        padding: 10px 25px !important;
        background-color: #6a0dad !important;
        color: white !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Dicționar capitalelor lumii
WORLD_CAPITALS = {
    "București, România": {"lat": "44.4268", "lon": "26.1025"},
    "Londra, Marea Britanie": {"lat": "51.5074", "lon": "-0.1278"},
    "Paris, Franța": {"lat": "48.8566", "lon": "2.3522"},
    "Berlin, Germania": {"lat": "52.5200", "lon": "13.4050"},
    "Roma, Italia": {"lat": "41.9028", "lon": "12.4964"},
    "Madrid, Spania": {"lat": "40.4168", "lon": "-3.7038"},
    "Moscova, Rusia": {"lat": "55.7558", "lon": "37.6173"},
    "Beijing, China": {"lat": "39.9042", "lon": "116.4074"},
    "Tokyo, Japonia": {"lat": "35.6762", "lon": "139.6503"},
    "New Delhi, India": {"lat": "28.6139", "lon": "77.2090"},
    "Washington D.C., SUA": {"lat": "38.9072", "lon": "-77.0369"},
    "Ottawa, Canada": {"lat": "45.4215", "lon": "-75.6972"},
    "Canberra, Australia": {"lat": "-35.2809", "lon": "149.1300"},
    "Buenos Aires, Argentina": {"lat": "-34.6037", "lon": "-58.3816"},
    "Cairo, Egipt": {"lat": "30.0444", "lon": "31.2357"},
    "Nairobi, Kenya": {"lat": "-1.2921", "lon": "36.8219"},
    "Pretoria, Africa de Sud": {"lat": "-25.7479", "lon": "28.2293"},
    "Brasília, Brazilia": {"lat": "-15.7975", "lon": "-47.8919"},
    "Mexico City, Mexic": {"lat": "19.4326", "lon": "-99.1332"},
    "Lisabona, Portugalia": {"lat": "38.7223", "lon": "-9.1393"}
}

# Semne zodiacale cu grade
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_zodiac_sign(degree):
    """Determină semnul zodiacal pentru un grad dat"""
    sign_index = int(degree / 30)
    return ZODIAC_SIGNS[sign_index]

def get_planet_position(planet_name, date, observer):
    """Calculează poziția unei planete"""
    try:
        if planet_name.lower() == 'sun':
            planet = ephem.Sun()
        elif planet_name.lower() == 'moon':
            planet = ephem.Moon()
        elif planet_name.lower() == 'mercury':
            planet = ephem.Mercury()
        elif planet_name.lower() == 'venus':
            planet = ephem.Venus()
        elif planet_name.lower() == 'mars':
            planet = ephem.Mars()
        elif planet_name.lower() == 'jupiter':
            planet = ephem.Jupiter()
        elif planet_name.lower() == 'saturn':
            planet = ephem.Saturn()
        elif planet_name.lower() == 'uranus':
            planet = ephem.Uranus()
        elif planet_name.lower() == 'neptune':
            planet = ephem.Neptune()
        elif planet_name.lower() == 'pluto':
            planet = ephem.Pluto()
        else:
            return None
        
        planet.compute(observer)
        return ephem.degrees(planet.ra)
    except Exception as e:
        st.error(f"Eroare la calcularea poziției pentru {planet_name}: {str(e)}")
        return None

def convert_degrees(degrees):
    """Converteste grade în format grade, minute, secunde"""
    deg = int(degrees)
    min_dec = (degrees - deg) * 60
    minutes = int(min_dec)
    seconds = (min_dec - minutes) * 60
    return f"{deg}° {minutes}' {seconds:.2f}\""

def parse_dms_to_degrees(dms_str):
    """Converteste string DMS (grade, minute, secunde) în grade zecimale"""
    try:
        # Înlătură spațiile și separă componentele
        dms_str = dms_str.replace('°', ' ').replace("'", ' ').replace('"', ' ')
        parts = dms_str.split()
        
        degrees = float(parts[0])
        minutes = float(parts[1]) if len(parts) > 1 else 0
        seconds = float(parts[2]) if len(parts) > 2 else 0
        
        decimal_degrees = degrees + minutes/60 + seconds/3600
        return decimal_degrees
    except:
        return None

def generate_career_interpretation(planets_data, houses_data):
    """Interpretare specifică pentru carieră"""
    tenth_house = houses_data.get(10, {})
    saturn_data = planets_data.get('Saturn', {})
    sun_data = planets_data.get('Sun', {})
    
    interpretations = []
    
    if tenth_house.get('sign') == 'Capricorn':
        interpretations.append("Cariera ta este marcată de ambiție și structură. Ai potențialul de a ajunge în poziții de leadership.")
    elif tenth_house.get('sign') == 'Leo':
        interpretations.append("Cariera ta implică creativitate și vizibilitate. Poți excela în domenii care cer exprimare artistică.")
    else:
        interpretations.append("Cariera ta se bazează pe muncă asiduă și dezvoltare constantă.")
    
    if saturn_data.get('sign') == 'Taurus':
        interpretations.append("Stabilitatea financiară este importantă în cariera ta. Încerci să construiești ceva durabil.")
    
    if sun_data.get('house') == 10:
        interpretations.append("Soarele în casa a 10-a indică un puternic potențial de succes profesional și recunoaștere.")
    
    return " ".join(interpretations) if interpretations else "Cariera ta va fi una de evoluție constantă, cu oportunități care apar prin muncă dedicată."

def generate_relationships_interpretation(planets_data, houses_data):
    """Interpretare specifică pentru relații"""
    seventh_house = houses_data.get(7, {})
    venus_data = planets_data.get('Venus', {})
    mars_data = planets_data.get('Mars', {})
    
    interpretations = []
    
    if seventh_house.get('sign') == 'Libra':
        interpretations.append("Relațiile tale sunt marcate de armonie și echilibru. Cauți parteneriate bazate pe respect reciproc.")
    elif seventh_house.get('sign') == 'Scorpio':
        interpretations.append("Relațiile tale sunt intense și transformatoare. Cauți conexiuni profunde și autentice.")
    else:
        interpretations.append("Relațiile tale se bazează pe comunicare și înțelegere reciprocă.")
    
    if venus_data.get('sign') == 'Pisces':
        interpretations.append("Venera în Pești aduce sensibilitate și compasiune în relațiile tale.")
    elif venus_data.get('sign') == 'Aries':
        interpretations.append("Venera în Berbec aduce pasiune și spontaneitate în dragoste.")
    
    if mars_data.get('house') == 7:
        interpretations.append("Marte în casa a 7-a indică energie și inițiativă în parteneriate.")
    
    return " ".join(interpretations) if interpretations else "Relațiile tale vor fi diverse și învățătoare, aducând lecții importante despre iubire și conexiune."

def generate_spiritual_interpretation(planets_data, houses_data):
    """Interpretare specifică pentru dezvoltare spirituală"""
    twelfth_house = houses_data.get(12, {})
    neptune_data = planets_data.get('Neptune', {})
    moon_data = planets_data.get('Moon', {})
    
    interpretations = []
    
    if twelfth_house.get('sign') == 'Pisces':
        interpretations.append("Călătoria ta spirituală este profundă și intuitivă. Ai o conexiune puternică cu universul.")
    elif twelfth_house.get('sign') == 'Sagittarius':
        interpretations.append("Spiritualitatea ta este exploratoare și filozofică. Cauți înțelepciune și perspective mai largi.")
    else:
        interpretations.append("Drumul tău spiritual este unic și personal, ducând la descoperiri interioare importante.")
    
    if neptune_data.get('house') == 12:
        interpretations.append("Neptun în casa a 12-a amplifică intuiția și conexiunea cu planurile superioare.")
    
    if moon_data.get('sign') == 'Cancer':
        interpretations.append("Luna în Rac aduce sensibilitate și empatie profundă în călătoria ta spirituală.")
    
    return " ".join(interpretations) if interpretations else "Drumul tău spiritual va fi unul de descoperire graduală, cu momente de iluminare și creștere interioară."

def create_simple_chart(planets_data, houses_data):
    """Creează o reprezentare simplă a chart-ului"""
    st.markdown("### 🔮 Chart Astrologic Simplificat")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🌌 Planete")
        for planet, data in planets_data.items():
            if data:
                st.markdown(f"""
                <div class="planet-info">
                <b>{planet}:</b> {data.get('sign', 'Necunoscut')} în Casa {data.get('house', 'Necunoscută')}<br>
                <small>Grad: {data.get('degree_formatted', 'Necunoscut')}</small>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🏠 Case")
        for house_num in range(1, 13):
            house_data = houses_data.get(house_num, {})
            if house_data:
                st.markdown(f"""
                <div class="planet-info">
                <b>Casa {house_num}:</b> {house_data.get('sign', 'Necunoscut')}<br>
                <small>Grad: {house_data.get('degree_formatted', 'Necunoscut')}</small>
                </div>
                """, unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">✨ Calculator Horoscop - Astrologie Avansată</h1>', unsafe_allow_html=True)
    
    # Sidebar pentru input
    with st.sidebar:
        st.markdown("## 📅 Date Naștere")
        
        birth_date = st.date_input(
            "Data nașterii",
            value=datetime(1990, 1, 1),
            min_value=datetime(1900, 1, 1),
            max_value=datetime.now()
        )
        
        birth_time = st.time_input("Ora nașterii", value=datetime.strptime("12:00", "%H:%M").time())
        
        # Selectare capitală sau input manual
        birth_place_option = st.selectbox(
            "Locul nașterii:",
            ["Alege o capitală..."] + list(WORLD_CAPITALS.keys()) + ["Alt loc..."]
        )
        
        if birth_place_option == "Alt loc...":
            birth_city = st.text_input("Oraș", "București")
            birth_country = st.text_input("Țară", "România")
            lat_input = st.text_input("Latitude (ex: 44.4268 sau 44°25'36.5\")", "44.4268")
            lon_input = st.text_input("Longitude (ex: 26.1025 sau 26°6'9.0\")", "26.1025")
        elif birth_place_option != "Alege o capitală...":
            # Extrage coordonatele pentru capitala selectată
            coords = WORLD_CAPITALS[birth_place_option]
            lat_input = coords["lat"]
            lon_input = coords["lon"]
            birth_city = birth_place_option.split(",")[0]
            birth_country = birth_place_option.split(",")[1].strip()
        else:
            lat_input = "44.4268"
            lon_input = "26.1025"
            birth_city = "București"
            birth_country = "România"
        
        # Converteste DMS în grade dacă este necesar
        try:
            if '°' in lat_input:
                latitude = parse_dms_to_degrees(lat_input)
            else:
                latitude = float(lat_input)
                
            if '°' in lon_input:
                longitude = parse_dms_to_degrees(lon_input)
            else:
                longitude = float(lon_input)
        except:
            st.error("Format invalid pentru coordonate. Folosește fie grade zecimale (44.4268) fie DMS (44°25'36.5\")")
            latitude = 44.4268
            longitude = 26.1025
    
    # Buton de calcul
    if st.button("🔮 Calculează Horoscopul", use_container_width=True):
        calculate_horoscope(birth_date, birth_time, latitude, longitude, birth_city, birth_country)

def calculate_horoscope(birth_date, birth_time, latitude, longitude, birth_city, birth_country):
    """Calculează horoscopul complet"""
    
    # Creează observer pentru ephem
    observer = ephem.Observer()
    observer.lat = str(latitude)
    observer.lon = str(longitude)
    
    # Combina data și ora
    birth_datetime = datetime.combine(birth_date, birth_time)
    observer.date = birth_datetime.strftime('%Y/%m/%d %H:%M:%S')
    
    # Planete de calculat
    planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
               'Saturn', 'Uranus', 'Neptune', 'Pluto']
    
    planets_data = {}
    houses_data = {}
    
    # Calculează pozițiile planetelor
    for planet in planets:
        position = get_planet_position(planet, birth_datetime, observer)
        if position:
            degrees = math.degrees(float(position))
            sign = get_zodiac_sign(degrees)
            house = (int(degrees / 30) % 12) + 1
            degree_in_sign = degrees % 30
            
            planets_data[planet] = {
                'degrees': degrees,
                'degree_formatted': convert_degrees(degree_in_sign),
                'sign': sign,
                'house': house
            }
    
    # Calculează casele (simplificat)
    for house_num in range(1, 13):
        house_degree = (house_num - 1) * 30
        house_sign = get_zodiac_sign(house_degree)
        
        houses_data[house_num] = {
            'degrees': house_degree,
            'degree_formatted': convert_degrees(house_degree % 30),
            'sign': house_sign
        }
    
    # Afișează rezultatele
    st.markdown(f'<h2 class="section-header">📊 Rezultate Horoscop pentru {birth_city}, {birth_country}</h2>', unsafe_allow_html=True)
    
    # Informații despre naștere
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Data nașterii", birth_datetime.strftime('%d %B %Y'))
    with col2:
        st.metric("Ora nașterii", birth_datetime.strftime('%H:%M'))
    with col3:
        st.metric("Coordonate", f"Lat: {latitude}, Lon: {longitude}")
    
    # Chart simplificat
    create_simple_chart(planets_data, houses_data)
    
    # Interpretări
    st.markdown('<h2 class="section-header">📖 Interpretări</h2>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💼 Career")
        career_text = generate_career_interpretation(planets_data, houses_data)
        st.markdown(f'<div class="interpretation-box">{career_text}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 💖 Relationships")
        relationships_text = generate_relationships_interpretation(planets_data, houses_data)
        st.markdown(f'<div class="interpretation-box">{relationships_text}</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### 🌟 Spiritual")
        spiritual_text = generate_spiritual_interpretation(planets_data, houses_data)
        st.markdown(f'<div class="interpretation-box">{spiritual_text}</div>', unsafe_allow_html=True)
    
    # Detalii tehnice
    with st.expander("🔍 Detalii Tehnice Complete"):
        st.write("**Planete:**", planets_data)
        st.write("**Case:**", houses_data)

if __name__ == "__main__":
    main()
