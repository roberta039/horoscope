import numpy as np
from datetime import datetime
import math

class HoroscopeCalculator:
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North Node']
        self.zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                           'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        self.aspects = {
            'Conjunction': {'angle': 0, 'orb': 8, 'symbol': '☌'},
            'Sextile': {'angle': 60, 'orb': 6, 'symbol': '⚹'},
            'Square': {'angle': 90, 'orb': 8, 'symbol': '□'},
            'Trine': {'angle': 120, 'orb': 8, 'symbol': '△'},
            'Opposition': {'angle': 180, 'orb': 8, 'symbol': '☍'}
        }
        
        # Interpretations database
        self.interpretations = {
            'Sun': {
                'Aries': 'Energetic, pioneering, and assertive leader.',
                'Taurus': 'Stable, determined, and sensual nature.',
                'Gemini': 'Communicative, curious, and adaptable personality.',
                'Cancer': 'Nurturing, emotional, and protective character.',
                'Leo': 'Creative, confident, and charismatic individual.',
                'Virgo': 'Analytical, practical, and service-oriented.',
                'Libra': 'Diplomatic, harmonious, and relationship-focused.',
                'Scorpio': 'Intense, transformative, and deeply passionate.',
                'Sagittarius': 'Adventurous, philosophical, and freedom-loving.',
                'Capricorn': 'Ambitious, disciplined, and responsible.',
                'Aquarius': 'Innovative, humanitarian, and independent thinker.',
                'Pisces': 'Compassionate, intuitive, and spiritually connected.'
            },
            'Moon': {
                'Aries': 'Emotionally impulsive and enthusiastic.',
                'Taurus': 'Emotionally stable and comfort-seeking.',
                'Gemini': 'Emotionally communicative and changeable.',
                'Cancer': 'Emotionally nurturing and sensitive.',
                'Leo': 'Emotionally dramatic and proud.',
                'Virgo': 'Emotionally analytical and practical.',
                'Libra': 'Emotionally diplomatic and peace-loving.',
                'Scorpio': 'Emotionally intense and secretive.',
                'Sagittarius': 'Emotionally optimistic and freedom-loving.',
                'Capricorn': 'Emotionally reserved and responsible.',
                'Aquarius': 'Emotionally detached and unconventional.',
                'Pisces': 'Emotionally compassionate and dreamy.'
            }
        }
    
    def calculate_planetary_positions(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate planetary positions based on birth data"""
        positions = {}
        
        # More realistic calculation based on birth datetime
        julian_day = self._to_julian_day(birth_datetime)
        
        for i, planet in enumerate(self.planets):
            # More varied positions based on actual date
            base_position = (julian_day * 0.9856 + i * 30) % 360  # Simulate planetary motion
            sign_index = int(base_position // 30)
            degrees_in_sign = base_position % 30
            
            # More realistic house distribution
            house = ((i * 2) % 12) + 1
            
            positions[planet] = {
                'position': round(degrees_in_sign, 2),
                'sign': self.zodiac_signs[sign_index],
                'house': house,
                'retrograde': np.random.random() > 0.85,  # 15% chance of retrograde
                'longitude': base_position
            }
        
        return positions
    
    def calculate_houses(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate house cusps"""
        houses = {}
        
        # More realistic house calculation based on time and location
        base_angle = (longitude + (birth_datetime.hour * 15)) % 360
        
        for house in range(1, 13):
            house_angle = (base_angle + (house - 1) * 30) % 360
            sign_index = int(house_angle // 30)
            
            houses[house] = {
                'angle': house_angle,
                'sign': self.zodiac_signs[sign_index],
                'degrees': house_angle % 30
            }
        
        return houses
    
    def calculate_aspects(self, planetary_data, max_orb=8):
        """Calculate astrological aspects between planets"""
        aspects_found = []
        planets = list(planetary_data.keys())
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                planet1 = planets[i]
                planet2 = planets[j]
                
                pos1 = planetary_data[planet1]['longitude']
                pos2 = planetary_data[planet2]['longitude']
                
                # Calculate the angle between planets
                angle = abs(pos1 - pos2)
                angle = min(angle, 360 - angle)  # Get smallest angle
                
                # Check for aspects
                for aspect_name, aspect_info in self.aspects.items():
                    orb = abs(angle - aspect_info['angle'])
                    if orb <= aspect_info['orb']:
                        strength = self._get_aspect_strength(orb)
                        interpretation = self._get_aspect_interpretation(planet1, planet2, aspect_name)
                        
                        aspects_found.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_name,
                            'symbol': aspect_info['symbol'],
                            'orb': round(orb, 2),
                            'strength': strength,
                            'exact_angle': aspect_info['angle'],
                            'interpretation': interpretation
                        })
        
        # Sort by orb (closest first)
        return sorted(aspects_found, key=lambda x: x['orb'])
    
    def _get_aspect_interpretation(self, planet1, planet2, aspect):
        """Get interpretation for specific aspect"""
        interpretations = {
            'Conjunction': f"Blending of {planet1} and {planet2} energies. Unified expression.",
            'Sextile': f"Opportunity between {planet1} and {planet2}. Harmonious cooperation.",
            'Square': f"Tension between {planet1} and {planet2}. Challenge and growth.",
            'Trine': f"Natural flow between {planet1} and {planet2}. Easy expression.",
            'Opposition': f"Polarity between {planet1} and {planet2}. Balance needed."
        }
        return interpretations.get(aspect, f"Interaction between {planet1} and {planet2}.")
    
    def get_planet_interpretation(self, planet, sign):
        """Get detailed interpretation for planet in sign"""
        planet_interpretations = self.interpretations.get(planet, {})
        return planet_interpretations.get(sign, f"{planet} in {sign} expresses uniquely.")
    
    def get_house_interpretation(self, house, sign):
        """Get interpretation for house placement"""
        house_interpretations = {
            1: f"Self-expression and identity through {sign} qualities.",
            2: f"Values and resources expressed in {sign} manner.",
            3: f"Communication and learning with {sign} approach.",
            4: f"Home and foundation influenced by {sign} energy.",
            5: f"Creativity and romance expressed {sign}-style.",
            6: f"Work and health approached with {sign} diligence.",
            7: f"Relationships and partnerships reflect {sign} traits.",
            8: f"Transformation and intimacy through {sign} intensity.",
            9: f"Philosophy and expansion with {sign} perspective.",
            10: f"Career and public image shaped by {sign} ambitions.",
            11: f"Friendships and goals influenced by {sign} ideals.",
            12: f"Spirituality and subconscious through {sign} sensitivity."
        }
        return house_interpretations.get(house, f"House {house} expresses {sign} energy.")
    
    def generate_full_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate complete horoscope interpretation"""
        interpretation = []
        
        interpretation.append("🌌 PERSONAL HOROSCOPE ANALYSIS")
        interpretation.append("=" * 50)
        
        # Sun and Moon analysis
        sun_sign = planetary_data['Sun']['sign']
        moon_sign = planetary_data['Moon']['sign']
        rising_sign = houses_data[1]['sign']
        
        interpretation.append(f"🌟 CORE IDENTITY")
        interpretation.append(f"Sun in {sun_sign}: {self.get_planet_interpretation('Sun', sun_sign)}")
        interpretation.append(f"Moon in {moon_sign}: {self.get_planet_interpretation('Moon', moon_sign)}")
        interpretation.append(f"Rising Sign ({rising_sign}): Your outward personality and first impressions")
        interpretation.append("")
        
        # Key planetary placements
        interpretation.append("🪐 KEY PLANETARY PLACEMENTS")
        for planet in ['Mercury', 'Venus', 'Mars']:
            if planet in planetary_data:
                data = planetary_data[planet]
                interpretation.append(f"{planet} in {data['sign']}: {self.get_planet_interpretation(planet, data['sign'])}")
        interpretation.append("")
        
        # House emphasis
        interpretation.append("🏠 HOUSE EMPHASIS")
        for house in [1, 4, 7, 10]:  # Angular houses
            if house in houses_data:
                data = houses_data[house]
                interpretation.append(f"House {house} ({data['sign']}): {self.get_house_interpretation(house, data['sign'])}")
        
        return "\n".join(interpretation)
    
    def _get_aspect_strength(self, orb):
        """Determine aspect strength based on orb"""
        if orb <= 1:
            return 'Strong'
        elif orb <= 3:
            return 'Medium'
        else:
            return 'Weak'
    
    def _to_julian_day(self, dt):
        """Convert datetime to simplified Julian day for calculations"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd += (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400
        
        return jd
