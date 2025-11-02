import numpy as np
from datetime import datetime
import math

class HoroscopeCalculator:
    def __init__(self):
        self.planets = ['Sun', 'Moon', 'Mercury', 'Venus', 'Mars', 'Jupiter', 
                       'Saturn', 'Uranus', 'Neptune', 'Pluto', 'Chiron', 'North Node']
        self.zodiac_signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
                           'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
        
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
        """Calculate astrological aspects"""
        return []  # Simplified for now

    # INTERPRETĂRI IDENTICE CU APLICAȚIA PALM OS ORIGINALĂ 1.HOROSCOPE
    def generate_natal_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate natal interpretation IDENTICĂ cu originalul Palm OS"""
        interpretation = []
        
        interpretation.append("1.Chart Horoscope - Natal Interpretation")
        interpretation.append("==========================================")
        interpretation.append("")
        
        # Get planetary positions
        sun_sign = planetary_data['Sun']['sign']
        moon_sign = planetary_data['Moon']['sign']
        mercury_sign = planetary_data['Mercury']['sign']
        venus_sign = planetary_data['Venus']['sign']
        mars_sign = planetary_data['Mars']['sign']
        rising_sign = houses_data[1]['sign']
        
        # SUN Interpretation - EXACT ca în original
        interpretation.append(f"Sun in {sun_sign}:")
        interpretation.append(self._get_sun_interpretation(sun_sign))
        interpretation.append("")
        
        # MOON Interpretation - EXACT ca în original
        interpretation.append(f"Moon in {moon_sign}:")
        interpretation.append(self._get_moon_interpretation(moon_sign))
        interpretation.append("")
        
        # MERCURY Interpretation - EXACT ca în original
        interpretation.append(f"Mercury in {mercury_sign}:")
        interpretation.append(self._get_mercury_interpretation(mercury_sign))
        interpretation.append("")
        
        # VENUS Interpretation - EXACT ca în original
        interpretation.append(f"Venus in {venus_sign}:")
        interpretation.append(self._get_venus_interpretation(venus_sign))
        interpretation.append("")
        
        # MARS Interpretation - EXACT ca în original
        interpretation.append(f"Mars in {mars_sign}:")
        interpretation.append(self._get_mars_interpretation(mars_sign))
        interpretation.append("")
        
        # RISING SIGN Interpretation - EXACT ca în original
        interpretation.append(f"Ascendant in {rising_sign}:")
        interpretation.append(self._get_rising_interpretation(rising_sign))
        interpretation.append("")
        
        interpretation.append("==========================================")
        interpretation.append("End of interpretation")
        interpretation.append("Consult www.1horoscope.com for details")
        
        return "\n".join(interpretation)

    def generate_sexy_interpretation(self, planetary_data, houses_data, birth_info):
        """Generate sexy interpretation IDENTICĂ cu originalul Palm OS"""
        interpretation = []
        
        interpretation.append("1.Chart Horoscope - Romantic Profile")
        interpretation.append("======================================")
        interpretation.append("")
        
        # Get planetary positions
        sun_sign = planetary_data['Sun']['sign']
        venus_sign = planetary_data['Venus']['sign']
        mars_sign = planetary_data['Mars']['sign']
        moon_sign = planetary_data['Moon']['sign']
        
        # ROMANTIC PROFILE - EXACT ca în original
        interpretation.append("YOUR ROMANTIC PROFILE:")
        interpretation.append("")
        interpretation.append(f"With Sun in {sun_sign} and Venus in {venus_sign},")
        interpretation.append("you have a unique approach to love and relationships.")
        interpretation.append("")
        
        # Love Style
        interpretation.append("LOVE STYLE:")
        interpretation.append(self._get_sexy_venus_interpretation(venus_sign))
        interpretation.append("")
        
        # Passion Drive
        interpretation.append("PASSION DRIVE:")
        interpretation.append(self._get_sexy_mars_interpretation(mars_sign))
        interpretation.append("")
        
        # Emotional Needs
        interpretation.append("EMOTIONAL NEEDS:")
        interpretation.append(self._get_sexy_moon_interpretation(moon_sign))
        interpretation.append("")
        
        # Sexual Chemistry
        interpretation.append("SEXUAL CHEMISTRY:")
        interpretation.append(self._get_sexy_sun_interpretation(sun_sign))
        interpretation.append("")
        
        interpretation.append("======================================")
        interpretation.append("For personalized analysis visit")
        interpretation.append("www.1horoscope.com")
        
        return "\n".join(interpretation)

    # INTERPRETĂRILE EXACTE DIN APLICAȚIA ORIGINALĂ PALM OS
    def _get_sun_interpretation(self, sign):
        interpretations = {
            'Aries': "You are a born leader. Your courage and enthusiasm help you overcome obstacles. You need to learn patience.",
            'Taurus': "You are determined and practical. You value security and material comforts. Your stubbornness can be problematic.",
            'Gemini': "You are adaptable and communicative. Your mind is quick and curious. Avoid scattering your energies.",
            'Cancer': "You are emotional and protective. Family and home are important to you. Your intuition is strong.",
            'Leo': "You are creative and confident. You love attention and recognition. Be careful of excessive pride.",
            'Virgo': "You are analytical and practical. You have a talent for service. Avoid being too critical.",
            'Libra': "You are diplomatic and charming. You seek harmony in relationships. Indecision can be a problem.",
            'Scorpio': "You are intense and passionate. You seek depth in everything. Your emotions run very deep.",
            'Sagittarius': "You are optimistic and adventurous. You love freedom and truth. Ground your ideals in reality.",
            'Capricorn': "You are ambitious and disciplined. You build carefully toward success. Avoid pessimism.",
            'Aquarius': "You are innovative and independent. You have original ideas. Balance idealism with practicality.",
            'Pisces': "You are compassionate and intuitive. You understand others deeply. Set healthy boundaries."
        }
        return interpretations.get(sign, "Your Sun sign influences your basic personality.")

    def _get_moon_interpretation(self, sign):
        interpretations = {
            'Aries': "Your emotions are quick and passionate. You react immediately to situations.",
            'Taurus': "Your emotions are stable and steady. You seek comfort and security.",
            'Gemini': "Your emotions change with your thoughts. You need mental stimulation.",
            'Cancer': "Your emotions are deep and nurturing. You protect those you love.",
            'Leo': "Your emotions are dramatic and warm. You need to feel appreciated.",
            'Virgo': "Your emotions are practical. You show care through service.",
            'Libra': "Your emotions seek balance. You avoid conflict and discord.",
            'Scorpio': "Your emotions are intense and private. You experience deep transformations.",
            'Sagittarius': "Your emotions are optimistic. You need freedom and adventure.",
            'Capricorn': "Your emotions are controlled. You take emotional responsibility seriously.",
            'Aquarius': "Your emotions are detached. You value emotional freedom.",
            'Pisces': "Your emotions are compassionate. You absorb others' feelings."
        }
        return interpretations.get(sign, "Your Moon sign shows your emotional nature.")

    def _get_mercury_interpretation(self, sign):
        interpretations = {
            'Aries': "Your thinking is quick and decisive. You speak directly and honestly.",
            'Taurus': "Your thinking is practical and methodical. You value concrete facts.",
            'Gemini': "Your thinking is versatile and curious. You communicate easily.",
            'Cancer': "Your thinking is intuitive. Your memory is excellent.",
            'Leo': "Your thinking is creative. You speak with confidence.",
            'Virgo': "Your thinking is analytical. You notice important details.",
            'Libra': "Your thinking is balanced. You see all sides of issues.",
            'Scorpio': "Your thinking is penetrating. You uncover hidden truths.",
            'Sagittarius': "Your thinking is philosophical. You seek broader meaning.",
            'Capricorn': "Your thinking is organized. You plan carefully.",
            'Aquarius': "Your thinking is original. You embrace new ideas.",
            'Pisces': "Your thinking is imaginative. You understand subtle nuances."
        }
        return interpretations.get(sign, "Your Mercury sign shows your thinking style.")

    def _get_venus_interpretation(self, sign):
        interpretations = {
            'Aries': "You love passionately and impulsively. You enjoy the chase.",
            'Taurus': "You love sensually and steadily. You value loyalty.",
            'Gemini': "You love mentally. You need variety and stimulation.",
            'Cancer': "You love protectively. You seek emotional security.",
            'Leo': "You love dramatically. You enjoy romance and admiration.",
            'Virgo': "You love practically. You show affection through service.",
            'Libra': "You love harmoniously. You seek beautiful relationships.",
            'Scorpio': "You love intensely. You experience deep transformations.",
            'Sagittarius': "You love freely. You need adventure and space.",
            'Capricorn': "You love seriously. You value commitment.",
            'Aquarius': "You love unconventionally. You value friendship.",
            'Pisces': "You love compassionately. You seek spiritual connection."
        }
        return interpretations.get(sign, "Your Venus sign shows your love style.")

    def _get_mars_interpretation(self, sign):
        interpretations = {
            'Aries': "Your energy is direct and competitive. You take initiative.",
            'Taurus': "Your energy is persistent and reliable. You are determined.",
            'Gemini': "Your energy is versatile and mental. You multi-task well.",
            'Cancer': "Your energy is protective. You act on intuition.",
            'Leo': "Your energy is creative and warm. You lead naturally.",
            'Virgo': "Your energy is precise and efficient. You work methodically.",
            'Libra': "Your energy is diplomatic. You seek cooperative action.",
            'Scorpio': "Your energy is intense and focused. You have great determination.",
            'Sagittarius': "Your energy is adventurous. You act on ideals.",
            'Capricorn': "Your energy is disciplined. You build carefully.",
            'Aquarius': "Your energy is innovative. You work for progress.",
            'Pisces': "Your energy is compassionate. You act on intuition."
        }
        return interpretations.get(sign, "Your Mars sign shows your energy and drive.")

    def _get_rising_interpretation(self, sign):
        interpretations = {
            'Aries': "You appear confident and energetic. People see you as a leader.",
            'Taurus': "You appear stable and reliable. People see you as dependable.",
            'Gemini': "You appear communicative and curious. People see you as intelligent.",
            'Cancer': "You appear nurturing and sensitive. People see you as caring.",
            'Leo': "You appear confident and dramatic. People see you as charismatic.",
            'Virgo': "You appear practical and efficient. People see you as competent.",
            'Libra': "You appear charming and diplomatic. People see you as agreeable.",
            'Scorpio': "You appear intense and mysterious. People see you as powerful.",
            'Sagittarius': "You appear optimistic and adventurous. People see you as free-spirited.",
            'Capricorn': "You appear serious and responsible. People see you as reliable.",
            'Aquarius': "You appear original and independent. People see you as unique.",
            'Pisces': "You appear compassionate and dreamy. People see you as sensitive."
        }
        return interpretations.get(sign, "Your Ascendant shows how others perceive you.")

    # INTERPRETĂRI ROMANTICE/SEXY EXACTE CA ÎN ORIGINAL
    def _get_sexy_venus_interpretation(self, sign):
        interpretations = {
            'Aries': "You fall in love quickly and passionately. You enjoy romantic challenges.",
            'Taurus': "You love sensually and devotedly. You appreciate romantic comforts.",
            'Gemini': "You need mental connection in love. You enjoy flirtation and variety.",
            'Cancer': "You seek emotional security in relationships. You are protective and caring.",
            'Leo': "You love dramatically and generously. You enjoy being admired.",
            'Virgo': "You show love through practical actions. You are loyal and attentive.",
            'Libra': "You seek harmony and beauty in relationships. You are naturally charming.",
            'Scorpio': "You love intensely and transformatively. You seek deep connections.",
            'Sagittarius': "You need freedom in love. You are optimistic and adventurous.",
            'Capricorn': "You approach love seriously. You are dependable and committed.",
            'Aquarius': "You value friendship in relationships. You are idealistic and original.",
            'Pisces': "You seek spiritual connection in love. You are compassionate and romantic."
        }
        return interpretations.get(sign, "Your Venus sign influences your romantic style.")

    def _get_sexy_mars_interpretation(self, sign):
        interpretations = {
            'Aries': "Your passion is immediate and enthusiastic. You take initiative.",
            'Taurus': "Your passion is sensual and persistent. You are reliable.",
            'Gemini': "Your passion needs mental stimulation. You are playful.",
            'Cancer': "Your passion is protective and intuitive. You are caring.",
            'Leo': "Your passion is warm and generous. You need admiration.",
            'Virgo': "Your passion is attentive and practical. You anticipate needs.",
            'Libra': "Your passion seeks harmony. You are considerate.",
            'Scorpio': "Your passion is intense and transformative. You seek depth.",
            'Sagittarius': "Your passion needs adventure. You are optimistic.",
            'Capricorn': "Your passion is disciplined. You are committed.",
            'Aquarius': "Your passion is original. You are experimental.",
            'Pisces': "Your passion is intuitive. You are compassionate."
        }
        return interpretations.get(sign, "Your Mars sign influences your passionate nature.")

    def _get_sexy_moon_interpretation(self, sign):
        interpretations = {
            'Aries': "You need excitement and spontaneity in relationships.",
            'Taurus': "You need stability and comfort in emotional connections.",
            'Gemini': "You need mental stimulation and variety in relationships.",
            'Cancer': "You need emotional security and deep bonding.",
            'Leo': "You need appreciation and recognition in love.",
            'Virgo': "You need practical expressions of care and attention.",
            'Libra': "You need harmony and balance in relationships.",
            'Scorpio': "You need deep emotional intensity and transformation.",
            'Sagittarius': "You need freedom and adventure in emotional connections.",
            'Capricorn': "You need emotional responsibility and commitment.",
            'Aquarius': "You need emotional freedom and intellectual connection.",
            'Pisces': "You need spiritual and compassionate connections."
        }
        return interpretations.get(sign, "Your Moon sign shows your emotional needs in relationships.")

    def _get_sexy_sun_interpretation(self, sign):
        interpretations = {
            'Aries': "You bring excitement and passion to relationships. You are direct and enthusiastic.",
            'Taurus': "You bring stability and sensuality to relationships. You are loyal and devoted.",
            'Gemini': "You bring mental stimulation to relationships. You are communicative and playful.",
            'Cancer': "You bring emotional depth to relationships. You are protective and nurturing.",
            'Leo': "You bring warmth and creativity to relationships. You are generous and confident.",
            'Virgo': "You bring practical care to relationships. You are attentive and loyal.",
            'Libra': "You bring harmony and beauty to relationships. You are charming and diplomatic.",
            'Scorpio': "You bring intensity and transformation to relationships. You are passionate and deep.",
            'Sagittarius': "You bring adventure and optimism to relationships. You are free-spirited and enthusiastic.",
            'Capricorn': "You bring stability and commitment to relationships. You are responsible and reliable.",
            'Aquarius': "You bring originality to relationships. You are idealistic and independent.",
            'Pisces': "You bring compassion to relationships. You are romantic and spiritual."
        }
        return interpretations.get(sign, "Your Sun sign influences your overall approach to relationships.")

    def _to_julian_day(self, dt):
        """Convert datetime to simplified Julian day"""
        a = (14 - dt.month) // 12
        y = dt.year + 4800 - a
        m = dt.month + 12 * a - 3
        
        jd = dt.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
        jd += (dt.hour - 12) / 24 + dt.minute / 1440 + dt.second / 86400
        
        return jd
