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
            'Conjunction': 0,
            'Sextile': 60,
            'Square': 90,
            'Trine': 120,
            'Opposition': 180
        }
    
    def calculate_planetary_positions(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate planetary positions based on birth data"""
        positions = {}
        
        # Simplified calculation (in a real app, this would use ephemeris)
        julian_day = self._to_julian_day(birth_datetime)
        
        for i, planet in enumerate(self.planets):
            # Simplified position calculation
            base_position = (julian_day % 360 + i * 30) % 360
            sign_index = int(base_position // 30)
            degrees_in_sign = base_position % 30
            
            positions[planet] = {
                'position': round(degrees_in_sign, 2),
                'sign': self.zodiac_signs[sign_index],
                'house': (i % 12) + 1,
                'retrograde': np.random.random() > 0.85,  # 15% chance of retrograde
                'longitude': base_position
            }
        
        return positions
    
    def calculate_houses(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate house cusps"""
        houses = {}
        
        # Simplified house calculation
        base_angle = (longitude % 360)  # Use longitude as base
        
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
                for aspect_name, aspect_angle in self.aspects.items():
                    orb = abs(angle - aspect_angle)
                    if orb <= max_orb:
                        strength = self._get_aspect_strength(orb)
                        aspects_found.append({
                            'planet1': planet1,
                            'planet2': planet2,
                            'aspect': aspect_name,
                            'orb': round(orb, 2),
                            'strength': strength,
                            'exact_angle': aspect_angle
                        })
        
        # Sort by orb (closest first)
        return sorted(aspects_found, key=lambda x: x['orb'])
    
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
        
        jd = (dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045)
        jd += (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400
        
        return jd
    
    def get_zodiac_info(self, sign_name):
        """Get information about a zodiac sign"""
        signs_info = {
            'Aries': {'element': 'Fire', 'modality': 'Cardinal', 'ruler': 'Mars'},
            'Taurus': {'element': 'Earth', 'modality': 'Fixed', 'ruler': 'Venus'},
            'Gemini': {'element': 'Air', 'modality': 'Mutable', 'ruler': 'Mercury'},
            'Cancer': {'element': 'Water', 'modality': 'Cardinal', 'ruler': 'Moon'},
            'Leo': {'element': 'Fire', 'modality': 'Fixed', 'ruler': 'Sun'},
            'Virgo': {'element': 'Earth', 'modality': 'Mutable', 'ruler': 'Mercury'},
            'Libra': {'element': 'Air', 'modality': 'Cardinal', 'ruler': 'Venus'},
            'Scorpio': {'element': 'Water', 'modality': 'Fixed', 'ruler': 'Pluto'},
            'Sagittarius': {'element': 'Fire', 'modality': 'Mutable', 'ruler': 'Jupiter'},
            'Capricorn': {'element': 'Earth', 'modality': 'Cardinal', 'ruler': 'Saturn'},
            'Aquarius': {'element': 'Air', 'modality': 'Fixed', 'ruler': 'Uranus'},
            'Pisces': {'element': 'Water', 'modality': 'Mutable', 'ruler': 'Neptune'}
        }
        return signs_info.get(sign_name, {})
