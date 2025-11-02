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
        
        # NATAL INTERPRETATIONS (Comprehensive)
        self.natal_interpretations = {
            'Sun': {
                'Aries': 'PIONEERING SPIRIT. Natural leader with strong initiative. Your courage drives you forward. Need to learn patience.',
                'Taurus': 'STEADFAST BUILDER. Great determination and practical wisdom. Value security and comforts. Can be stubborn.',
                'Gemini': 'VERSATILE COMMUNICATOR. Quick and adaptable mind. Thrive on mental stimulation. Avoid scattering energies.',
                'Cancer': 'NURTURING SOUL. Deeply emotional and protective. Strong connection to home and family. Intuition guides you.',
                'Leo': 'RADIANT CENTER. Natural charisma and creative expression. Seek recognition and enjoy spotlight. Generous heart.',
                'Virgo': 'ANALYTICAL PERFECTIONIST. Service-oriented with sharp mind. Remarkable attention to detail. Avoid excessive criticism.',
                'Libra': 'DIPLOMATIC PEACEMAKER. Strong sense of justice and harmony. Excel in partnerships. Indecision can challenge you.',
                'Scorpio': 'INTENSE TRANSFORMER. Powerful emotions and penetrating insight. Seek depth in experiences. Intensity can overwhelm.',
                'Sagittarius': 'PHILOSOPHICAL EXPLORER. Love freedom and truth-seeking. Optimistic and adventurous. Ground your ideals.',
                'Capricorn': 'AMBITIONS BUILDER. Strong responsibility and discipline. Climb steadily toward goals. Can be too serious.',
                'Aquarius': 'INNOVATIVE THINKER. Progressive ideas and humanitarian values. March to your own drummer. Balance idealism.',
                'Pisces': 'COMPASSIONATE DREAMER. Deeply intuitive and spiritually connected. Empathy knows no bounds. Set healthy boundaries.'
            },
            'Moon': {
                'Aries': 'EMOTIONAL PIONEER. Feelings are spontaneous and passionate. Quick to react emotionally. Develop emotional patience.',
                'Taurus': 'STEADY EMOTIONS. Seek emotional security and comfort. Feelings are stable and enduring. Resist emotional change.',
                'Gemini': 'VERSATILE FEELINGS. Emotions change with mental stimulation. Need to communicate feelings. Can be emotionally scattered.',
                'Cancer': 'DEEP NURTURER. Strong emotional intuition and memory. Protect those you love. Sensitive to environment.',
                'Leo': 'DRAMATIC HEART. Emotions are warm and generous. Need for emotional recognition. Pride affects feelings.',
                'Virgo': 'ANALYTICAL EMOTIONS. Analyze feelings carefully. Service brings satisfaction. Can worry excessively.',
                'Libra': 'HARMONIOUS FEELINGS. Seek emotional balance and partnership. Dislike conflict. Can be indecisive emotionally.',
                'Scorpio': 'INTENSE EMOTIONS. Feelings run deep and powerful. Emotional transformations frequent. Share deep feelings.',
                'Sagittarius': 'OPTIMISTIC HEART. Emotions are enthusiastic and free. Need emotional adventure. Can be tactlessly honest.',
                'Capricorn': 'RESERVED FEELINGS. Control emotions carefully. Emotional responsibility important. Emotionally cautious.',
                'Aquarius': 'DETACHED EMOTIONS. Feelings are idealistic and unconventional. Need emotional freedom. Can seem aloof.',
                'Pisces': 'COMPASSIONATE SOUL. Emotions are empathetic and spiritual. Strong psychic sensitivity. Protect emotional boundaries.'
            }
        }
        
        # SEXY INTERPRETATIONS (Romantic/Sexual)
        self.sexy_interpretations = {
            'Sun': {
                'Aries': '🔥 PASSIONATE LOVER. You pursue romance with fiery enthusiasm. Direct and adventurous in intimacy. Need spontaneous excitement.',
                'Taurus': '💎 SENSUAL SEDUCER. You appreciate physical beauty and slow, sensual lovemaking. Very tactile and devoted lover.',
                'Gemini': '💋 PLAYFUL CHARMER. You enjoy mental stimulation and variety in relationships. Flirtatious and communicative partner.',
                'Cancer': '🌙 NURTURING INTIMATE. You seek emotional security and deep bonding. Protective and sensitive in relationships.',
                'Leo': '👑 DRAMATIC ROMANTIC. You love grand gestures and passionate displays. Generous and warm-hearted lover.',
                'Virgo': '🎯 PERFECTIONIST PARTNER. You show love through attentive service. Analytical but deeply loyal in intimacy.',
                'Libra': '💝 HARMONIOUS LOVER. You seek beauty and balance in relationships. Natural charm and romantic idealism.',
                'Scorpio': '⚡ INTENSE CONNECTOR. You crave deep, transformative intimacy. Passionate and mysterious sexual energy.',
                'Sagittarius': '🏹 ADVENTUROUS FREE-SPIRIT. You need freedom and excitement in love. Optimistic and enthusiastic partner.',
                'Capricorn': '🏔️ SERIOUS SEDUCER. You approach relationships with commitment and responsibility. Slow but deep connections.',
                'Aquarius': '🌌 UNCONVENTIONAL LOVER. You value intellectual connection and freedom. Experimental and open-minded.',
                'Pisces': '🌊 ROMANTIC DREAMER. You seek spiritual and emotional merging in love. Compassionate and imaginative lover.'
            },
            'Venus': {
                'Aries': '💘 IMPULSIVE ATTRACTION. You fall in love quickly and passionately. Need excitement and chase in romance.',
                'Taurus': '🌹 SENSUAL PLEASURE. You value physical touch and romantic comforts. Very loyal and devoted in love.',
                'Gemini': '💌 MENTAL CONNECTION. You're attracted to intelligence and wit. Need variety and mental stimulation.',
                'Cancer': '🏡 EMOTIONAL BONDING. You seek security and nurturing in relationships. Very protective and caring.',
                'Leo': '🎭 DRAMATIC ROMANCE. You love being adored and admired. Generous with grand romantic gestures.',
                'Virgo': '📝 PRACTICAL LOVE. You show affection through service and attention. Very loyal and helpful partner.',
                'Libra': '💑 HARMONIOUS PARTNER. You seek balance and beauty in relationships. Natural charm and diplomacy.',
                'Scorpio': '💞 INTENSE PASSION. You crave deep, transformative love. Very passionate and intensely loyal.',
                'Sagittarius': '🎯 ADVENTUROUS SPIRIT. You need freedom and exploration in love. Optimistic and enthusiastic.',
                'Capricorn': '💍 SERIOUS COMMITMENT. You approach love with responsibility and loyalty. Very dependable partner.',
                'Aquarius': '🌟 UNCONVENTIONAL BOND. You value friendship and intellectual connection. Very idealistic in love.',
                'Pisces': '🌙 ROMANTIC DREAM. You seek spiritual and emotional merging. Compassionate and unconditionally loving.'
            },
            'Mars': {
                'Aries': '⚡ DIRECT PASSION. Your sexual energy is immediate and enthusiastic. Natural confidence and initiative.',
                'Taurus': '🎯 STEADY DESIRE. Your passion is persistent and sensual. Very reliable and physically expressive.',
                'Gemini': '💫 MENTAL STIMULATION. Your drive needs variety and communication. Playful and experimental approach.',
                'Cancer': '🌊 EMOTIONAL INTIMACY. Your passion is protective and nurturing. Strong intuitive connection.',
                'Leo': '🔥 DRAMATIC EXPRESSION. Your energy is warm and generous. Need for admiration and recognition.',
                'Virgo': '🎯 PRECISE ATTENTION. Your drive is methodical and attentive. Excellent at anticipating needs.',
                'Libra': '💝 HARMONIOUS APPROACH. Your passion seeks balance and beauty. Cooperative and considerate lover.',
                'Scorpio': '💥 INTENSE ENERGY. Your drive is powerful and transformative. Deep psychological connection.',
                'Sagittarius': '🏹 ADVENTUROUS SPIRIT. Your passion needs freedom and exploration. Enthusiastic and optimistic.',
                'Capricorn': '🏔️ AMBITIOUS DRIVE. Your energy is disciplined and responsible. Strong sense of commitment.',
                'Aquarius': '🌌 INNOVATIVE APPROACH. Your passion is original and unconventional. Experimental and open-minded.',
                'Pisces': '🌊 COMPASSIONATE ENERGY. Your drive is intuitive and spiritual. Deep emotional and psychic connection.'
            }
        }
    
    def calculate_planetary_positions(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate planetary positions based on birth data"""
        positions = {}
        
        julian_day = self._to_julian_day(birth_datetime)
        
        for i, planet in enumerate(self.planets):
            base_position = (julian_day * 0.9856 + i * 30) % 360
            sign_index = int(base_position // 30)
            degrees_in_sign = base_position % 30
            
            house = ((i * 2) % 12) + 1
            
            positions[planet] = {
                'position': round(degrees_in_sign, 2),
                'sign': self.zodiac_signs[sign_index],
                'house': house,
                'retrograde': np.random.random() > 0.85,
                'longitude': base_position
            }
        
        return positions
    
    def calculate_houses(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate house cusps"""
        houses = {}
        
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
                
                angle = abs(pos1 - pos2)
                angle = min(angle, 360 - angle)
                
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
        
        return sorted(aspects_found, key=lambda x: x['orb'])
    
    def _get_aspect_interpretation(self, planet1, planet2, aspect):
        """Get interpretation for specific aspect"""
        aspect_interpretations = {
            'Conjunction': f"FUSION OF ENERGIES. {planet1} and {planet2} work together as one. Powerful focus in your chart.",
            'Sextile': f"HARMONIOUS OPPORTUNITY. {planet1} and {planet2} support each other naturally. Easy opportunities and talents.",
            'Square': f"DYNAMIC TENSION. {planet1} and {planet2} create internal conflict. Drives growth through challenges.",
            'Trine': f"FLOWING HARMONY. {planet1} and {planet2} work together effortlessly. Natural talent aspect.",
            'Opposition': f"BALANCING POLARITIES. {planet1} and {planet2} face each other. Creates awareness through relationships."
        }
        return aspect_interpretations.get(aspect, f"Interaction between {planet1} and {planet2}.")
    
    # NATAL INTERPRETATION METHODS
    def get_natal_interpretation(self, planet, sign):
        """Get natal interpretation for planet in sign"""
        planet_interpretations = self.natal_interpretations.get(planet, {})
        return planet_interpretations.get(sign, f"{planet} in {sign} expresses uniquely.")
    
    def generate_natal_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate complete natal interpretation"""
        interpretation = []
        
        interpretation.append("🌌 1.CHART HOROSCOPE - NATAL INTERPRETATION")
        interpretation.append("=" * 60)
        interpretation.append(f"Birth: {birth_info['date']} {birth_info['time']}")
        interpretation.append(f"Location: {birth_info['place']}")
        interpretation.append("=" * 60)
        interpretation.append("")
        
        # Core Identity
        sun_sign = planetary_data['Sun']['sign']
        moon_sign = planetary_data['Moon']['sign']
        
        interpretation.append("🌟 CORE IDENTITY")
        interpretation.append("-" * 40)
        interpretation.append(f"SUN in {sun_sign}:")
        interpretation.append(self.get_natal_interpretation('Sun', sun_sign))
        interpretation.append("")
        interpretation.append(f"MOON in {moon_sign}:")
        interpretation.append(self.get_natal_interpretation('Moon', moon_sign))
        interpretation.append("")
        
        # Personal Planets
        interpretation.append("🪐 PERSONAL INFLUENCES")
        interpretation.append("-" * 40)
        for planet in ['Mercury', 'Venus', 'Mars']:
            if planet in planetary_data:
                data = planetary_data[planet]
                interpretation.append(f"{planet.upper()} in {data['sign']}:")
                interpretation.append(self.get_natal_interpretation(planet, data['sign']))
                interpretation.append("")
        
        interpretation.append("=" * 60)
        interpretation.append("End of Natal Interpretation")
        
        return "\n".join(interpretation)
    
    # SEXY INTERPRETATION METHODS
    def get_sexy_interpretation(self, planet, sign):
        """Get sexy/romantic interpretation for planet in sign"""
        planet_interpretations = self.sexy_interpretations.get(planet, {})
        return planet_interpretations.get(sign, f"{planet} in {sign} expresses romantically.")
    
    def generate_sexy_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate sexy/romantic interpretation"""
        interpretation = []
        
        interpretation.append("💖 1.CHART HOROSCOPE - ROMANTIC PROFILE")
        interpretation.append("=" * 60)
        interpretation.append(f"Birth: {birth_info['date']} {birth_info['time']}")
        interpretation.append("=" * 60)
        interpretation.append("")
        
        # Romantic Style
        venus_sign = planetary_data['Venus']['sign']
        mars_sign = planetary_data['Mars']['sign']
        moon_sign = planetary_data['Moon']['sign']
        
        interpretation.append("💘 ROMANTIC NATURE")
        interpretation.append("-" * 40)
        interpretation.append(f"VENUS in {venus_sign} (How You Love):")
        interpretation.append(self.get_sexy_interpretation('Venus', venus_sign))
        interpretation.append("")
        interpretation.append(f"MARS in {mars_sign} (Passionate Drive):")
        interpretation.append(self.get_sexy_interpretation('Mars', mars_sign))
        interpretation.append("")
        interpretation.append(f"MOON in {moon_sign} (Emotional Needs):")
        interpretation.append(self.get_sexy_interpretation('Moon', moon_sign))
        interpretation.append("")
        
        # Sexual Chemistry
        interpretation.append("🔥 SEXUAL ENERGY")
        interpretation.append("-" * 40)
        sun_sign = planetary_data['Sun']['sign']
        interpretation.append(f"SUN in {sun_sign} (Core Expression):")
        interpretation.append(self.get_sexy_interpretation('Sun', sun_sign))
        interpretation.append("")
        
        # Relationship House
        seventh_house = houses_data[7]['sign']
        interpretation.append(f"7th HOUSE in {seventh_house}:")
        interpretation.append(f"You attract partners with {seventh_house} qualities and seek {seventh_house}-style relationships.")
        interpretation.append("")
        
        interpretation.append("=" * 60)
        interpretation.append("Explore your romantic potential at www.1horoscope.com")
        
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
