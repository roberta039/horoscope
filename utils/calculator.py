import numpy as np
from datetime import datetime
import math

class HoroscopeCalculator:
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North Node']
        self.zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                           'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
        # EXTENSIVE INTERPRETATIONS LIKE ORIGINAL PALM OS 1.HOROSCOPE
        self.interpretations = {
            'natal': self._get_natal_interpretations(),
            'sexy': self._get_sexy_interpretations()
        }
    
    def _get_natal_interpretations(self):
        """Natal interpretations like original Palm OS app - LONG AND DETAILED"""
        return {
            'Sun_Aries': """
SUN IN ARIES - THE PIONEER

You are a natural born leader with an incredible drive to initiate and pioneer new endeavors. 
Your courage and enthusiasm are your greatest assets, propelling you forward even when others hesitate.

KEY TRAITS:
• Assertive and direct in approach
• Highly competitive spirit  
• Impulsive but passionate
• Natural confidence in abilities
• Need for constant challenge

LIFE PURPOSE: To lead, initiate, and courageously face new challenges. Your path involves learning patience and considering others' perspectives while maintaining your pioneering spirit.

You thrive in situations requiring quick decisions and immediate action. Your challenge is to balance your strong initiative with thoughtful consideration of consequences.
""",

            'Sun_Taurus': """
SUN IN TAURUS - THE BUILDER

You possess remarkable determination and practical wisdom, making you excellent at building stable foundations in all areas of life. Your appreciation for beauty and comfort drives you to create security.

KEY TRAITS:
• Extremely persistent and reliable
• Strong connection to physical senses
• Practical and grounded approach
• Appreciation for quality and beauty
• Resistance to sudden change

LIFE PURPOSE: To build lasting security and appreciate life's sensual pleasures. Your journey involves learning flexibility while maintaining your steadfast nature.

Your methodical approach ensures lasting results, though you must guard against stubbornness when new opportunities arise that require adaptation.
""",

            'Moon_Aries': """
MOON IN ARIES - EMOTIONAL PIONEER

Your emotional nature is spontaneous, passionate, and immediate. You feel things intensely and react quickly, often before fully processing the emotional landscape.

EMOTIONAL PATTERNS:
• Quick emotional reactions
• Passionate but short-lived feelings
• Need for emotional independence
• Impatience with emotional complexity
• Courage in facing emotional challenges

Your emotional well-being requires activities that allow spontaneous expression and challenge. You need to develop patience with slower emotional processes in others.
""",

            'Moon_Taurus': """
MOON IN TAURUS - STEADY EMOTIONS

You seek emotional security through stability, comfort, and predictable routines. Your feelings are deep, enduring, and closely tied to physical comfort and sensory experiences.

EMOTIONAL PATTERNS:
• Slow to emotional change
• Strong need for security
• Emotional connection to possessions
• Consistent and reliable feelings
• Resistance to emotional upheaval

Your emotional health thrives in stable, comfortable environments. You must learn to embrace necessary emotional changes while maintaining your core stability.
""",

            'Venus_Aries': """
VENUS IN ARIES - PASSIONATE LOVER

In relationships, you're direct, enthusiastic, and love the thrill of pursuit. You're attracted to challenge and excitement, often falling in love quickly and passionately.

RELATIONSHIP STYLE:
• Immediate attraction and pursuit
• Love as adventure and conquest
• Need for constant excitement
• Direct expression of affection
• Impatience with relationship routines

You bring excitement and spontaneity to relationships but need to develop consistency and patience for lasting connections.
""",

            'Venus_Taurus': """
VENUS IN TAURUS - SENSUAL PARTNER

You approach love with stability, sensuality, and deep devotion. Physical touch, comfort, and reliability are essential to your experience of love and relationship.

RELATIONSHIP STYLE:
• Slow to commit but deeply loyal
• Strong emphasis on physical affection
• Appreciation for romantic comforts
• Practical expressions of love
• Resistance to relationship changes

You create secure, comfortable partnerships but must remain open to necessary growth and change within relationships.
"""
        }
    
    def _get_sexy_interpretations(self):
        """Sexy/Romantic interpretations like original app"""
        return {
            'Sun_Aries': """
🔥 SEXY ARIES SUN

Your sexual energy is immediate, enthusiastic, and adventurous. You approach intimacy with confidence and love spontaneous, exciting encounters.

SEXUAL STYLE:
• Direct and confident approach
• Love for sexual adventure
• Quick arousal and passionate expression
• Need for variety and challenge
• Competitive in sexual situations

You're most compatible with partners who match your energy and enthusiasm, and who appreciate your direct, passionate approach to intimacy.
""",

            'Venus_Aries': """
💘 ROMANTIC VENUS IN ARIES

You fall in love quickly and passionately, enjoying the thrill of pursuit and conquest. Your romantic style is direct, enthusiastic, and full of spontaneous gestures.

LOVE PATTERNS:
• Immediate crushes and attractions
• Love as exciting adventure
• Generous but impulsive romantic gestures
• Need for constant relationship excitement
• Quick to commit but may need variety

You bring excitement and passion to romance but need partners who understand your need for independence and adventure.
""",

            'Mars_Aries': """
⚡ PASSIONATE MARS IN ARIES

Your sexual drive is immediate, powerful, and direct. You have strong initiative in intimate situations and enjoy taking the lead.

PASSION PROFILE:
• Strong, immediate sexual energy
• Confident and direct approach
• Enjoyment of sexual challenge
• Need for spontaneous encounters
• Competitive sexual nature

Your passionate nature requires partners who appreciate directness and can match your energetic approach to intimacy.
"""
        }

    def calculate_planetary_positions(self, birth_datetime, latitude, longitude, house_system='Placidus'):
        """Calculate planetary positions"""
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
        """Calculate astrological aspects"""
        return []  # Simplified for now

    # NATAL INTERPRETATION METHODS
    def generate_natal_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate complete natal interpretation LIKE ORIGINAL"""
        interpretation = []
        
        interpretation.append("1.CHART HOROSCOPE - NATAL INTERPRETATION")
        interpretation.append("=" * 70)
        interpretation.append(f"Birth Date: {birth_info['date']}")
        interpretation.append(f"Birth Time: {birth_info['time']}")
        interpretation.append(f"Birth Place: {birth_info['place']}")
        interpretation.append("=" * 70)
        interpretation.append("")
        
        # Sun Sign Interpretation (Main Focus like original)
        sun_sign = planetary_data['Sun']['sign']
        sun_key = f"Sun_{sun_sign}"
        if sun_key in self.interpretations['natal']:
            interpretation.append(self.interpretations['natal'][sun_key])
            interpretation.append("")
        
        # Moon Sign Interpretation
        moon_sign = planetary_data['Moon']['sign']
        moon_key = f"Moon_{moon_sign}"
        if moon_key in self.interpretations['natal']:
            interpretation.append(self.interpretations['natal'][moon_key])
            interpretation.append("")
        
        # Venus Sign Interpretation
        venus_sign = planetary_data['Venus']['sign']
        venus_key = f"Venus_{venus_sign}"
        if venus_key in self.interpretations['natal']:
            interpretation.append(self.interpretations['natal'][venus_key])
            interpretation.append("")
        
        interpretation.append("=" * 70)
        interpretation.append("End of Natal Interpretation")
        interpretation.append("For more detailed analysis visit: www.1horoscope.com")
        
        return "\n".join(interpretation)

    # SEXY INTERPRETATION METHODS
    def generate_sexy_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate sexy/romantic interpretation LIKE ORIGINAL"""
        interpretation = []
        
        interpretation.append("1.CHART HOROSCOPE - ROMANTIC PROFILE")
        interpretation.append("=" * 70)
        interpretation.append(f"Birth Date: {birth_info['date']}")
        interpretation.append("=" * 70)
        interpretation.append("")
        
        # Sun Sign Romantic Profile
        sun_sign = planetary_data['Sun']['sign']
        sun_key = f"Sun_{sun_sign}"
        if sun_key in self.interpretations['sexy']:
            interpretation.append(self.interpretations['sexy'][sun_key])
            interpretation.append("")
        
        # Venus Sign Love Style
        venus_sign = planetary_data['Venus']['sign']
        venus_key = f"Venus_{venus_sign}"
        if venus_key in self.interpretations['sexy']:
            interpretation.append(self.interpretations['sexy'][venus_key])
            interpretation.append("")
        
        # Mars Sign Passion Profile
        mars_sign = planetary_data['Mars']['sign']
        mars_key = f"Mars_{mars_sign}"
        if mars_key in self.interpretations['sexy']:
            interpretation.append(self.interpretations['sexy'][mars_key])
            interpretation.append("")
        
        # Relationship House
        seventh_house = houses_data[7]['sign']
        interpretation.append(f"RELATIONSHIP HOUSE (7th) in {seventh_house.upper()}")
        interpretation.append(f"You attract partners who embody {seventh_house} qualities:")
        interpretation.append(self._get_relationship_house_interpretation(seventh_house))
        interpretation.append("")
        
        interpretation.append("=" * 70)
        interpretation.append("Discover your romantic potential at: www.1horoscope.com")
        
        return "\n".join(interpretation)

    def _get_relationship_house_interpretation(self, sign):
        """Get relationship house interpretation"""
        interpretations = {
            'Aries': "Dynamic, independent partners who challenge you and bring excitement to your life.",
            'Taurus': "Stable, reliable partners who provide security and appreciate life's comforts with you.",
            'Gemini': "Communicative, intellectual partners who stimulate your mind and keep things interesting.",
            'Cancer': "Nurturing, emotional partners who create deep emotional bonds and family connections.",
            'Leo': "Confident, generous partners who appreciate romance and bring creativity to your relationship.",
            'Virgo': "Practical, attentive partners who show love through service and thoughtful actions.",
            'Libra': "Harmonious, diplomatic partners who value balance and create beautiful relationships.",
            'Scorpio': "Intense, passionate partners who seek deep transformation and profound connections.",
            'Sagittarius': "Adventurous, philosophical partners who value freedom and expand your horizons.",
            'Capricorn': "Responsible, ambitious partners who build lasting structures and provide stability.",
            'Aquarius': "Unconventional, idealistic partners who value friendship and intellectual connection.",
            'Pisces': "Compassionate, spiritual partners who seek soul-level merging and unconditional love."
        }
        return interpretations.get(sign, f"Partners with {sign} qualities who complement your relationship needs.")

    def _to_julian_day(self, dt):
        """Convert datetime to simplified Julian day"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd += (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400
        
        return jd
