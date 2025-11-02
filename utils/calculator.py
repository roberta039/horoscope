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
        
        # EXTENSIVE INTERPRETATIONS LIKE ORIGINAL PALM OS APP
        self.interpretations = {
            'Sun': {
                'Aries': 'PIONEERING SPIRIT. You are a natural leader with strong initiative. Your courage and enthusiasm drive you forward. Need to learn patience and consideration for others.',
                'Taurus': 'STEADFAST BUILDER. You possess great determination and practical wisdom. Value security and material comforts. Your stubbornness can be both strength and weakness.',
                'Gemini': 'VERSATILE COMMUNICATOR. Your mind is quick and adaptable. You thrive on mental stimulation and social interaction. Need to avoid scattering your energies.',
                'Cancer': 'NURTURING SOUL. Deeply emotional and protective. Strong connection to home and family. Your intuition guides you well in personal matters.',
                'Leo': 'RADIANT CENTER. Natural charisma and creative expression. You seek recognition and enjoy being in spotlight. Generous heart but can be overly proud.',
                'Virgo': 'ANALYTICAL PERFECTIONIST. Service-oriented with sharp analytical mind. Your attention to detail is remarkable. Need to avoid excessive criticism.',
                'Libra': 'DIPLOMATIC PEACEMAKER. Strong sense of justice and harmony. You excel in partnerships and social situations. Indecision can be your challenge.',
                'Scorpio': 'INTENSE TRANSFORMER. Powerful emotions and penetrating insight. You seek depth in all experiences. Your intensity can be overwhelming to others.',
                'Sagittarius': 'PHILOSOPHICAL EXPLORER. Love for freedom and truth-seeking. Optimistic and adventurous spirit. Need to ground your lofty ideals.',
                'Capricorn': 'AMBITIONS BUILDER. Strong sense of responsibility and discipline. You climb steadily toward your goals. Can be too serious or pessimistic.',
                'Aquarius': 'INNOVATIVE THINKER. Progressive ideas and humanitarian values. You march to your own drummer. Need to balance idealism with practicality.',
                'Pisces': 'COMPASSIONATE DREAMER. Deeply intuitive and spiritually connected. Your empathy knows no bounds. Must learn to set healthy boundaries.'
            },
            'Moon': {
                'Aries': 'EMOTIONAL PIONEER. Your feelings are spontaneous and passionate. Quick to react emotionally. Need to develop emotional patience.',
                'Taurus': 'STEADY EMOTIONS. You seek emotional security and comfort. Your feelings are stable and enduring. Resistant to emotional change.',
                'Gemini': 'VERSATILE FEELINGS. Your emotions change with mental stimulation. Need to communicate your feelings. Can be emotionally scattered.',
                'Cancer': 'DEEP NURTURER. Strong emotional intuition and memory. You protect those you love. Very sensitive to environment and moods.',
                'Leo': 'DRAMATIC HEART. Your emotions are warm and generous. Need for emotional recognition. Pride plays big role in feelings.',
                'Virgo': 'ANALYTICAL EMOTIONS. You analyze your feelings carefully. Service brings emotional satisfaction. Can worry excessively.',
                'Libra': 'HARMONIOUS FEELINGS. You seek emotional balance and partnership. Dislike conflict and discord. Can be indecisive emotionally.',
                'Scorpio': 'INTENSE EMOTIONS. Your feelings run deep and powerful. Emotional transformations are frequent. Need to share deep feelings.',
                'Sagittarius': 'OPTIMISTIC HEART. Your emotions are enthusiastic and free. Need for emotional adventure. Can be tactlessly honest.',
                'Capricorn': 'RESERVED FEELINGS. You control emotions carefully. Emotional responsibility is important. Can be emotionally cautious.',
                'Aquarius': 'DETACHED EMOTIONS. Your feelings are idealistic and unconventional. Need for emotional freedom. Can seem emotionally aloof.',
                'Pisces': 'COMPASSIONATE SOUL. Your emotions are empathetic and spiritual. Strong psychic sensitivity. Need to protect emotional boundaries.'
            },
            'Mercury': {
                'Aries': 'QUICK-THINKING. Your mind is sharp and decisive. You think and speak directly. Impatient with slow thinkers.',
                'Taurus': 'PRACTICAL MIND. Your thinking is methodical and grounded. You value concrete facts. Resistant to new ideas.',
                'Gemini': 'VERSATILE INTELLECT. Your mind is quick and adaptable. Excellent communication skills. Can be mentally scattered.',
                'Cancer': 'INTUITIVE THINKING. Your mind is influenced by emotions. Strong memory and imagination. Thinking is subjective.',
                'Leo': 'CREATIVE MIND. Your thinking is dramatic and expressive. You speak with authority. Can be opinionated.',
                'Virgo': 'ANALYTICAL THINKER. Your mind is precise and detail-oriented. Excellent at critical analysis. Can be overly critical.',
                'Libra': 'DIPLOMATIC MIND. Your thinking is balanced and fair. You see all sides of issues. Can be indecisive.',
                'Scorpio': 'PENETRATING INTELLECT. Your mind is investigative and deep. You uncover hidden truths. Can be suspicious.',
                'Sagittarius': 'PHILOSOPHICAL MIND. Your thinking is broad and expansive. You seek higher meaning. Can overlook details.',
                'Capricorn': 'ORGANIZED THINKER. Your mind is structured and ambitious. You think in practical terms. Can be pessimistic.',
                'Aquarius': 'INNOVATIVE INTELLECT. Your thinking is original and progressive. You embrace new ideas. Can be fixed in opinions.',
                'Pisces': 'IMAGINATIVE MIND. Your thinking is intuitive and creative. You understand subtle nuances. Can be confusing.'
            },
            'Venus': {
                'Aries': 'PASSIONATE IN LOVE. You pursue relationships enthusiastically. Need for excitement in love. Can be impatient in relationships.',
                'Taurus': 'SENSUAL LOVER. You value stability and beauty in relationships. Very loyal and devoted. Can be possessive.',
                'Gemini': 'SOCIAL CHARMER. You enjoy mental connection in relationships. Need for variety and stimulation. Can be flirtatious.',
                'Cancer': 'NURTURING PARTNER. You seek emotional security in love. Very protective and caring. Can be overly sensitive.',
                'Leo': 'GENEROUS LOVER. You express love dramatically and warmly. Need for admiration in relationships. Can be proud.',
                'Virgo': 'PRACTICAL IN LOVE. You show love through service and attention. Very loyal and helpful. Can be critical.',
                'Libra': 'HARMONIOUS PARTNER. You seek balance and beauty in relationships. Natural charm and diplomacy. Can be indecisive.',
                'Scorpio': 'INTENSE LOVER. You seek deep transformation in relationships. Very passionate and loyal. Can be jealous.',
                'Sagittarius': 'FREE-SPIRITED. You need freedom and adventure in love. Optimistic and enthusiastic. Can commit reluctantly.',
                'Capricorn': 'RESPONSIBLE PARTNER. You approach love seriously and practically. Very loyal and dependable. Can be reserved.',
                'Aquarius': 'UNCONVENTIONAL LOVER. You value friendship and freedom in relationships. Very idealistic. Can be emotionally detached.',
                'Pisces': 'ROMANTIC DREAMER. You seek spiritual connection in love. Very compassionate and giving. Can be unrealistic.'
            },
            'Mars': {
                'Aries': 'DYNAMIC ENERGY. Your drive is direct and competitive. Natural leadership ability. Can be impulsive and aggressive.',
                'Taurus': 'STEADY DRIVE. Your energy is persistent and determined. Very reliable and practical. Can be stubborn.',
                'Gemini': 'VERSATILE ENERGY. Your drive is mental and adaptable. Multi-tasking comes naturally. Can lack follow-through.',
                'Cancer': 'EMOTIONAL DRIVE. Your energy is protective and nurturing. Strong intuitive action. Can be moody.',
                'Leo': 'CREATIVE ENERGY. Your drive is dramatic and enthusiastic. Natural charisma in action. Can be arrogant.',
                'Virgo': 'PRECISE ACTION. Your energy is methodical and efficient. Excellent at detailed work. Can be critical.',
                'Libra': 'DIPLOMATIC ACTION. Your drive seeks balance and partnership. Cooperative approach. Can avoid confrontation.',
                'Scorpio': 'INTENSE ENERGY. Your drive is powerful and transformative. Great determination and focus. Can be obsessive.',
                'Sagittarius': 'ADVENTUROUS DRIVE. Your energy seeks freedom and expansion. Enthusiastic and optimistic. Can be reckless.',
                'Capricorn': 'AMBITIOUS ENERGY. Your drive is disciplined and responsible. Strong organizational skills. Can be cold.',
                'Aquarius': 'INNOVATIVE ACTION. Your drive is original and progressive. Works well with groups. Can be rebellious.',
                'Pisces': 'COMPASSIONATE ENERGY. Your drive is intuitive and spiritual. Adaptable and sympathetic. Can lack direction.'
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
        """Get interpretation for specific aspect - LIKE ORIGINAL APP"""
        aspect_interpretations = {
            'Conjunction': f"FUSION OF ENERGIES. {planet1} and {planet2} work together as one. This creates a powerful focus in your chart. The combined energy dominates the areas of life these planets rule.",
            'Sextile': f"HARMONIOUS OPPORTUNITY. {planet1} and {planet2} support each other naturally. This aspect brings easy opportunities and talents. You can make things happen with minimal effort.",
            'Square': f"DYNAMIC TENSION. {planet1} and {planet2} create internal conflict. This aspect drives growth through challenges. You must learn to balance these competing energies.",
            'Trine': f"FLOWING HARMONY. {planet1} and {planet2} work together effortlessly. This is a natural talent aspect. The energy flows smoothly but may be taken for granted.",
            'Opposition': f"BALANCING POLARITIES. {planet1} and {planet2} face each other across the chart. This creates awareness through relationships. You must learn to integrate these opposites."
        }
        return aspect_interpretations.get(aspect, f"Interaction between {planet1} and {planet2}.")
    
    def get_planet_interpretation(self, planet, sign):
        """Get detailed interpretation for planet in sign - LIKE ORIGINAL"""
        planet_interpretations = self.interpretations.get(planet, {})
        return planet_interpretations.get(sign, f"{planet} in {sign} expresses uniquely.")
    
    def get_house_interpretation(self, house, sign):
        """Get interpretation for house placement - LIKE ORIGINAL"""
        house_interpretations = {
            1: f"HOUSE OF SELF. Your identity and approach to life are colored by {sign} qualities. How you present yourself to the world.",
            2: f"HOUSE OF POSSESSIONS. Your values, resources, and self-worth expressed through {sign} energy. What you consider valuable.",
            3: f"HOUSE OF COMMUNICATION. Your thinking, learning, and local environment influenced by {sign}. How you process information.",
            4: f"HOUSE OF HOME. Your roots, family, and private life carry {sign} characteristics. Your emotional foundation.",
            5: f"HOUSE OF CREATION. Your creativity, romance, and self-expression show {sign} flair. What brings you joy.",
            6: f"HOUSE OF SERVICE. Your work, health, and daily routines organized by {sign} principles. Your approach to duty.",
            7: f"HOUSE OF PARTNERSHIP. Your relationships and collaborations reflect {sign} dynamics. What you seek in others.",
            8: f"HOUSE OF TRANSFORMATION. Your approach to intimacy, shared resources, and rebirth through {sign} intensity. Deep psychological patterns.",
            9: f"HOUSE OF EXPANSION. Your philosophy, travel, and higher learning colored by {sign} outlook. Your search for meaning.",
            10: f"HOUSE OF CAREER. Your public life, reputation, and ambitions shaped by {sign} drive. Your life purpose.",
            11: f"HOUSE OF COMMUNITY. Your friendships, groups, and aspirations influenced by {sign} ideals. Your hopes for humanity.",
            12: f"HOUSE OF SPIRIT. Your subconscious, spirituality, and hidden strengths through {sign} sensitivity. Your connection to the collective."
        }
        return house_interpretations.get(house, f"House {house} expresses {sign} energy.")
    
    def generate_full_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate complete horoscope interpretation - LIKE ORIGINAL PALM OS"""
        interpretation = []
        
        interpretation.append("🌌 1.CHART HOROSCOPE - PERSONAL ANALYSIS")
        interpretation.append("=" * 60)
        interpretation.append(f"Generated for birth: {birth_info['date']} {birth_info['time']}")
        interpretation.append(f"Location: {birth_info['place']}")
        interpretation.append("=" * 60)
        interpretation.append("")
        
        # Core Identity Analysis
        sun_sign = planetary_data['Sun']['sign']
        moon_sign = planetary_data['Moon']['sign']
        rising_sign = houses_data[1]['sign']
        
        interpretation.append("🌟 CORE IDENTITY ANALYSIS")
        interpretation.append("-" * 40)
        interpretation.append(f"SUN in {sun_sign}:")
        interpretation.append(self.get_planet_interpretation('Sun', sun_sign))
        interpretation.append("")
        interpretation.append(f"MOON in {moon_sign}:")
        interpretation.append(self.get_planet_interpretation('Moon', moon_sign))
        interpretation.append("")
        interpretation.append(f"ASCENDANT in {rising_sign}:")
        interpretation.append(f"Your outward personality and first impressions are colored by {rising_sign} qualities. This is the mask you wear when meeting new people.")
        interpretation.append("")
        
        # Key Planetary Placements
        interpretation.append("🪐 KEY PLANETARY INFLUENCES")
        interpretation.append("-" * 40)
        for planet in ['Mercury', 'Venus', 'Mars']:
            if planet in planetary_data:
                data = planetary_data[planet]
                interpretation.append(f"{planet.upper()} in {data['sign']}:")
                interpretation.append(self.get_planet_interpretation(planet, data['sign']))
                interpretation.append("")
        
        # House Emphasis
        interpretation.append("🏠 LIFE AREA EMPHASIS")
        interpretation.append("-" * 40)
        # Focus on angular houses (1,4,7,10) as most important
        angular_houses = [1, 4, 7, 10]
        for house in angular_houses:
            if house in houses_data:
                data = houses_data[house]
                interpretation.append(f"HOUSE {house} - {data['sign'].upper()}:")
                interpretation.append(self.get_house_interpretation(house, data['sign']))
                interpretation.append("")
        
        # Special Aspects Analysis
        interpretation.append("⭐ NOTABLE ASPECT PATTERNS")
        interpretation.append("-" * 40)
        aspects = self.calculate_aspects(planetary_data)
        strong_aspects = [a for a in aspects if a['strength'] == 'Strong']
        
        if strong_aspects:
            for aspect in strong_aspects[:3]:  # Show top 3 strongest aspects
                interpretation.append(f"{aspect['symbol']} {aspect['planet1']} {aspect['aspect']} {aspect['planet2']}:")
                interpretation.append(aspect['interpretation'])
                interpretation.append("")
        else:
            interpretation.append("No strong aspects within 1° orb detected.")
            interpretation.append("")
        
        # Life Theme Summary
        interpretation.append("🎯 LIFE THEME SUMMARY")
        interpretation.append("-" * 40)
        interpretation.append(self._generate_life_theme(planetary_data, houses_data))
        interpretation.append("")
        
        interpretation.append("=" * 60)
        interpretation.append("End of 1.Chart Horoscope Analysis")
        interpretation.append("For detailed chart calculation, visit www.1horoscope.com")
        
        return "\n".join(interpretation)
    
    def _generate_life_theme(self, planetary_data, houses_data):
        """Generate overall life theme based on chart patterns"""
        sun_sign = planetary_data['Sun']['sign']
        moon_sign = planetary_data['Moon']['sign']
        ascendant = houses_data[1]['sign']
        
        themes = {
            'Aries': "Pioneering and leadership define your path.",
            'Taurus': "Building security and appreciating beauty guide you.",
            'Gemini': "Communication and learning are your life themes.",
            'Cancer': "Nurturing and emotional security drive you.",
            'Leo': "Creative expression and recognition motivate you.",
            'Virgo': "Service and perfection are your guiding principles.",
            'Libra': "Harmony and relationships shape your journey.",
            'Scorpio': "Transformation and depth characterize your path.",
            'Sagittarius': "Exploration and truth-seeking define you.",
            'Capricorn': "Achievement and responsibility guide your way.",
            'Aquarius': "Innovation and humanitarian ideals inspire you.",
            'Pisces': "Compassion and spiritual connection are your themes."
        }
        
        sun_theme = themes.get(sun_sign, "")
        moon_theme = themes.get(moon_sign, "")
        rising_theme = themes.get(ascendant, "")
        
        return f"Your life combines {sun_theme.lower()} emotionally, you seek {moon_theme.lower()} and you present yourself as {rising_theme.lower()}"
    
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
