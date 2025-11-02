# app.py
import streamlit as st
import datetime
from datetime import date
import random

def get_zodiac_en(birth_date):
    """
    Calculate zodiac sign in English based on birth date
    Adapted from original C logic
    """
    day = birth_date.day
    month = birth_date.month
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Aquarius"
    else:  # (month == 2 and day >= 19) or (month == 3 and day <= 20)
        return "Pisces"

def get_zodiac_element(zodiac_sign):
    """Return the element of the zodiac sign"""
    elements = {
        "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
        "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
        "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
        "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water"
    }
    return elements.get(zodiac_sign, "Unknown")

def get_daily_horoscope(zodiac_sign):
    """
    Return detailed daily horoscope for zodiac sign
    With realistic predictions in English
    """
    horoscope_data = {
        "Aries": {
            "prediction": "🌟 High energy today! It's time to start new projects and take initiative. Your natural leadership will shine.",
            "love": "❤️ Passionate encounters are possible. Be open to new connections.",
            "career": "💼 Good day for negotiations and presenting your ideas.",
            "lucky_number": random.randint(1, 9),
            "compatibility": "Leo, Sagittarius"
        },
        "Taurus": {
            "prediction": "💪 Stability and patience are your strengths today. Focus on long-term goals.",
            "love": "🌹 Romantic moments with someone special. Quality time matters.",
            "career": "📈 Financial decisions should be carefully considered.",
            "lucky_number": random.randint(2, 6),
            "compatibility": "Virgo, Capricorn"
        },
        "Gemini": {
            "prediction": "💬 Communication is key today. Social interactions will bring opportunities.",
            "love": "💕 Interesting conversations could lead to romantic connections.",
            "career": "📝 Excellent day for writing, teaching, or networking.",
            "lucky_number": random.randint(3, 7),
            "compatibility": "Libra, Aquarius"
        },
        "Cancer": {
            "prediction": "🏠 Emotional day. Focus on home and family matters for comfort.",
            "love": "💞 Your sensitivity attracts others. Share your feelings openly.",
            "career": "🤝 Teamwork brings better results than working alone.",
            "lucky_number": random.randint(4, 8),
            "compatibility": "Scorpio, Pisces"
        },
        "Leo": {
            "prediction": "👑 The spotlight is on you! Confidence will help you achieve your goals.",
            "love": "🔥 Passionate and dramatic encounters possible. Enjoy the attention.",
            "career": "🎯 Perfect day for leadership roles and creative projects.",
            "lucky_number": random.randint(1, 5),
            "compatibility": "Aries, Sagittarius"
        },
        "Virgo": {
            "prediction": "📚 Focus on organization and details. Your analytical skills are sharp.",
            "love": "💝 Practical gestures speak louder than words today.",
            "career": "✅ Complete pending tasks for satisfaction and progress.",
            "lucky_number": random.randint(6, 9),
            "compatibility": "Taurus, Capricorn"
        },
        "Libra": {
            "prediction": "⚖️ Balance and harmony are important. Seek beauty in everything.",
            "love": "💑 Social events could bring romantic opportunities.",
            "career": "🎨 Creative solutions solve work challenges effectively.",
            "lucky_number": random.randint(2, 7),
            "compatibility": "Gemini, Aquarius"
        },
        "Scorpio": {
            "prediction": "🔮 Intuition is strong today. Trust your inner guidance.",
            "love": "💘 Deep emotional connections possible. Be vulnerable.",
            "career": "🕵️ Research and investigation yield valuable insights.",
            "lucky_number": random.randint(3, 8),
            "compatibility": "Cancer, Pisces"
        },
        "Sagittarius": {
            "prediction": "🧭 Adventure calls! Be open to new experiences and learning.",
            "love": "💃 Social gatherings bring exciting encounters.",
            "career": "🌍 International or educational opportunities may arise.",
            "lucky_number": random.randint(5, 9),
            "compatibility": "Aries, Leo"
        },
        "Capricorn": {
            "prediction": "🏔️ Hard work pays off. Your determination is impressive.",
            "love": "💒 Serious conversations about commitment are favorable.",
            "career": "📊 Strategic planning leads to long-term success.",
            "lucky_number": random.randint(4, 8),
            "compatibility": "Taurus, Virgo"
        },
        "Aquarius": {
            "prediction": "💡 Innovative ideas flow. Share your unique perspective.",
            "love": "🤝 Friendship could turn into something more meaningful.",
            "career": "🚀 Technology and innovation bring opportunities.",
            "lucky_number": random.randint(1, 7),
            "compatibility": "Gemini, Libra"
        },
        "Pisces": {
            "prediction": "🎨 Creativity and intuition are heightened. Dream big!",
            "love": "💝 Romantic and compassionate encounters likely.",
            "career": "🎭 Creative fields and helping professions favored.",
            "lucky_number": random.randint(2, 6),
            "compatibility": "Cancer, Scorpio"
        }
    }
    return horoscope_data.get(zodiac_sign, {
        "prediction": "Horoscope not available for this sign.",
        "love": "",
        "career": "",
        "lucky_number": 0,
        "compatibility": ""
    })

def main():
    st.set_page_config(
        page_title="Daily Horoscope App",
        page_icon="🔮",
        layout="centered"
    )
    
    # Header
    st.title("🔮 Daily Horoscope")
    st.markdown("Discover your zodiac sign and today's horoscope prediction!")
    st.markdown("---")
    
    # Sidebar for additional features
    with st.sidebar:
        st.header("About")
        st.info("This app calculates your zodiac sign based on your birth date and provides daily horoscope predictions.")
        
        st.header("Zodiac Elements")
        elements_info = """
        **Fire Signs**: Aries, Leo, Sagittarius - Passionate & Energetic  
        **Earth Signs**: Taurus, Virgo, Capricorn - Practical & Grounded  
        **Air Signs**: Gemini, Libra, Aquarius - Intellectual & Social  
        **Water Signs**: Cancer, Scorpio, Pisces - Emotional & Intuitive
        """
        st.markdown(elements_info)
    
    # Main content
    option = st.radio("Choose an option:", 
                     ["🔍 Find My Zodiac Sign", "📅 Daily Horoscope Prediction"])
    
    if option == "🔍 Find My Zodiac Sign":
        st.subheader("Discover Your Zodiac Sign")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            birth_date = st.date_input(
                "Select your birth date:",
                min_value=datetime.date(1900, 1, 1),
                max_value=datetime.date.today()
            )
        
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Find My Sign", type="primary"):
                zodiac = get_zodiac_en(birth_date)
                element = get_zodiac_element(zodiac)
                
                st.success(f"**Your Zodiac Sign:** {zodiac}")
                st.info(f"**Element:** {element}")
                
                # Zodiac date ranges
                date_ranges = {
                    "Aries": "March 21 - April 19",
                    "Taurus": "April 20 - May 20",
                    "Gemini": "May 21 - June 20",
                    "Cancer": "June 21 - July 22",
                    "Leo": "July 23 - August 22",
                    "Virgo": "August 23 - September 22",
                    "Libra": "September 23 - October 22",
                    "Scorpio": "October 23 - November 21",
                    "Sagittarius": "November 22 - December 21",
                    "Capricorn": "December 22 - January 19",
                    "Aquarius": "January 20 - February 18",
                    "Pisces": "February 19 - March 20"
                }
                
                st.write(f"**Date Range:** {date_ranges.get(zodiac, 'Unknown')}")
    
    else:  # Daily Horoscope
        st.subheader("Today's Horoscope")
        
        zodiac_choice = st.selectbox(
            "Select your zodiac sign:",
            ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        )
        
        if st.button("Get Today's Horoscope", type="primary"):
            horoscope = get_daily_horoscope(zodiac_choice)
            element = get_zodiac_element(zodiac_choice)
            
            # Display results in a nice layout
            st.success(f"🌟 **Horoscope for {zodiac_choice} ({element})**")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Prediction:** {horoscope['prediction']}")
                if horoscope['love']:
                    st.write(f"**Love & Relationships:** {horoscope['love']}")
                if horoscope['career']:
                    st.write(f"**Career & Finance:** {horoscope['career']}")
                if horoscope['compatibility']:
                    st.write(f"**Best Matches:** {horoscope['compatibility']}")
            
            with col2:
                st.metric("Lucky Number", horoscope['lucky_number'])
            
            # Additional info
            with st.expander("💫 Today's Advice"):
                advice = [
                    "Trust your intuition today",
                    "Embrace new opportunities",
                    "Practice gratitude",
                    "Stay true to yourself",
                    "Connect with loved ones",
                    "Follow your passions"
                ]
                st.write(f"**{random.choice(advice)}**")
    
    # Footer
    st.markdown("---")
    st.caption("Made with Streamlit • Horoscope predictions for entertainment purposes")

if __name__ == "__main__":
    main()
