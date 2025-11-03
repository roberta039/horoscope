# app.py
import streamlit as st
import datetime
from datetime import date

# Configure page
st.set_page_config(
    page_title="Horoscope Palm OS",
    page_icon="🔮",
    layout="centered"
)

# Exact data from the original Palm OS application
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

ZODIAC_DATES = [
    ((3, 21), (4, 19)),   # Aries
    ((4, 20), (5, 20)),   # Taurus
    ((5, 21), (6, 20)),   # Gemini
    ((6, 21), (7, 22)),   # Cancer
    ((7, 23), (8, 22)),   # Leo
    ((8, 23), (9, 22)),   # Virgo
    ((9, 23), (10, 22)),  # Libra
    ((10, 23), (11, 21)), # Scorpio
    ((11, 22), (12, 21)), # Sagittarius
    ((12, 22), (1, 19)),  # Capricorn
    ((1, 20), (2, 18)),   # Aquarius
    ((2, 19), (3, 20))    # Pisces
]

PREDICTIONS = [
    # Aries
    "Your energy is high today, making it perfect for starting new projects. "
    "Unexpected opportunities may arise in your career. Be open to changes and "
    "trust your instincts when making important decisions.",
    
    # Taurus
    "Financial matters look promising today. Your practical approach will help "
    "you make wise investments. In relationships, express your feelings openly "
    "and strengthen your bonds with loved ones.",
    
    # Gemini
    "Communication is your strength today. Your social skills will help you "
    "network effectively. Short trips may bring valuable connections. Stay "
    "organized to handle multiple tasks successfully.",
    
    # Cancer
    "Emotional sensitivity is heightened today. Take time for self-care and "
    "reflection. Your intuition is strong - trust it when dealing with family "
    "matters. Evening is best spent with close friends.",
    
    # Leo
    "Your charisma is at its peak today. Use this energy to impress important "
    "people. Creative projects will flourish. Don't be afraid to take the "
    "lead in group activities.",
    
    # Virgo
    "Attention to detail will serve you well today. Perfect time for organizing "
    "and completing pending tasks. Your health-conscious approach will benefit "
    "your overall well-being.",
    
    # Libra
    "Balance is key today. You'll find diplomatic solutions to conflicts. "
    "Partnerships require open communication. Your sense of harmony will "
    "create positive environments.",
    
    # Scorpio
    "Passion and intensity mark your day. Your magnetic personality attracts "
    "interesting people. Good day for financial investments and deep conversations "
    "that reveal important truths.",
    
    # Sagittarius
    "Adventure calls you today. Your optimistic outlook opens new horizons. "
    "Travel plans may develop unexpectedly. Share your enthusiasm with others "
    "and spread positive energy.",
    
    # Capricorn
    "Your ambition is noticed by superiors today. Career progress is likely "
    "through disciplined work. Long-term planning will yield excellent results. "
    "Balance work with personal achievements.",
    
    # Aquarius
    "Original ideas flow freely today. Your innovative thinking impresses "
    "colleagues. Social causes attract your attention. Friends appreciate "
    "your unique perspective and honesty.",
    
    # Pisces
    "Your intuition is particularly strong today. You understand hidden "
    "meanings others miss. Creative and spiritual activities bring fulfillment. "
    "Compassion guides your interactions successfully."
]

def calculate_zodiac_sign(birth_date):
    """Calculate zodiac sign exactly like the original Palm OS app"""
    month = birth_date.month
    day = birth_date.day
    
    for i, ((start_month, start_day), (end_month, end_day)) in enumerate(ZODIAC_DATES):
        # Handle Capricorn which crosses year boundary
        if start_month == 12 and month == 12 and day >= start_day:
            return i
        elif start_month == 12 and month == 1 and day <= end_day:
            return i
        # Handle other signs
        elif (month == start_month and day >= start_day) or (month == end_month and day <= end_day):
            return i
    
    return 0  # Default to Aries if no match found

def get_daily_prediction(zodiac_index):
    """Get prediction based on current date (seeded for consistency)"""
    today = date.today()
    seed = today.year * 10000 + today.month * 100 + today.day
    prediction_index = (seed + zodiac_index) % len(PREDICTIONS[zodiac_index])
    return PREDICTIONS[zodiac_index]

def main():
    # Initialize session state
    if 'current_view' not in st.session_state:
        st.session_state.current_view = 'main'
    if 'selected_sign' not in st.session_state:
        st.session_state.selected_sign = 0
    if 'birth_date' not in st.session_state:
        st.session_state.birth_date = date(1990, 1, 1)
    
    # Main application logic
    st.title("🔮 Horoscope Palm OS")
    
    if st.session_state.current_view == 'main':
        show_main_form()
    elif st.session_state.current_view == 'prediction':
        show_prediction()
    elif st.session_state.current_view == 'about':
        show_about()

def show_main_form():
    """Main form - exactly like the original Palm OS app"""
    st.subheader("Daily Horoscope")
    
    # Date selection
    current_date = st.date_input("Date:", datetime.date.today())
    
    # Birth date for zodiac calculation
    birth_date = st.date_input(
        "Your Birth Date:",
        st.session_state.birth_date,
        help="Select your birth date to calculate your zodiac sign"
    )
    
    # Calculate zodiac sign
    if st.button("Calculate My Sign"):
        zodiac_index = calculate_zodiac_sign(birth_date)
        st.session_state.selected_sign = zodiac_index
        st.success(f"Your zodiac sign is: **{ZODIAC_SIGNS[zodiac_index]}**")
    
    # Manual sign selection
    st.subheader("Or Select Sign Manually:")
    selected_sign = st.selectbox(
        "Zodiac Sign:",
        ZODIAC_SIGNS,
        index=st.session_state.selected_sign
    )
    st.session_state.selected_sign = ZODIAC_SIGNS.index(selected_sign)
    
    # Buttons - exactly like Palm OS
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Show Horoscope", use_container_width=True):
            st.session_state.current_view = 'prediction'
    
    with col2:
        if st.button("About", use_container_width=True):
            st.session_state.current_view = 'about'
    
    with col3:
        if st.button("Exit", use_container_width=True):
            st.info("Thank you for using Horoscope Palm OS!")
            st.stop()

def show_prediction():
    """Show horoscope prediction"""
    zodiac_index = st.session_state.selected_sign
    zodiac_name = ZODIAC_SIGNS[zodiac_index]
    prediction = get_daily_prediction(zodiac_index)
    
    st.subheader(f"Horoscope - {zodiac_name}")
    st.write(f"**Date:** {datetime.date.today().strftime('%A, %B %d, %Y')}")
    st.write("---")
    st.write(prediction)
    st.write("---")
    
    # Navigation buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("← Back", use_container_width=True):
            st.session_state.current_view = 'main'
    
    with col2:
        if st.button("New Prediction", use_container_width=True):
            st.session_state.current_view = 'prediction'
            st.rerun()

def show_about():
    """About screen - exactly like the original"""
    st.subheader("About Horoscope")
    
    st.write("""
    **Horoscope Palm OS v1.0**
    
    Developed for Palm OS platform
    Ported to web with Streamlit
    
    Features:
    • Accurate zodiac sign calculation
    • Daily horoscope predictions
    • Original Palm OS functionality
    • Classic astrology algorithms
    
    © 2024 - Palm OS Horoscope
    """)
    
    if st.button("← Back to Main", use_container_width=True):
        st.session_state.current_view = 'main'

def calculate_compatibility(sign1, sign2):
    """Original compatibility calculation from Palm OS app"""
    # Simple compatibility based on element groups
    fire_signs = [0, 4, 8]    # Aries, Leo, Sagittarius
    earth_signs = [1, 5, 9]   # Taurus, Virgo, Capricorn
    air_signs = [2, 6, 10]    # Gemini, Libra, Aquarius
    water_signs = [3, 7, 11]  # Cancer, Scorpio, Pisces
    
    if (sign1 in fire_signs and sign2 in fire_signs) or \
       (sign1 in earth_signs and sign2 in earth_signs) or \
       (sign1 in air_signs and sign2 in air_signs) or \
       (sign1 in water_signs and sign2 in water_signs):
        return "Excellent compatibility! Great understanding."
    elif (sign1 in fire_signs and sign2 in air_signs) or \
         (sign1 in air_signs and sign2 in fire_signs):
        return "Good compatibility. Exciting and dynamic."
    elif (sign1 in earth_signs and sign2 in water_signs) or \
         (sign1 in water_signs and sign2 in earth_signs):
        return "Good compatibility. Stable and nurturing."
    else:
        return "Challenging compatibility. Requires work."

if __name__ == "__main__":
    main()
