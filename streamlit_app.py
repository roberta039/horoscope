import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
from utils.calculator import HoroscopeCalculator
from utils.design import apply_cosmic_design
from utils.exporter import ExportManager
import base64

# Apply Cosmic Vintage design
apply_cosmic_design()

# Initialize session state
if 'calculator' not in st.session_state:
    st.session_state.calculator = HoroscopeCalculator()
if 'export_manager' not in st.session_state:
    st.session_state.export_manager = ExportManager()

def main():
    st.title("🔮 1.Chart Horoscope v2.42")
    st.markdown("### *Cosmic Vintage Reconstruction*")
    
    # Navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Birth Data", "🪐 Chart", "⭐ Aspects", "⚙️ Settings"])
    
    with tab1:
        render_birth_data_tab()
    
    with tab2:
        render_chart_tab()
    
    with tab3:
        render_aspects_tab()
    
    with tab4:
        render_settings_tab()

def render_birth_data_tab():
    st.header("📊 Enter Birth Information")
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            birth_date = st.date_input("📅 Date of Birth", datetime.now())
            birth_time = st.time_input("⏰ Time of Birth", datetime.now().time())
            birth_place = st.text_input("🌍 Place of Birth", "Zagreb, Croatia")
        
        with col2:
            latitude = st.number_input("📍 Latitude", value=45.8150, format="%.4f")
            longitude = st.number_input("📍 Longitude", value=15.9819, format="%.4f")
            house_system = st.selectbox("🏠 House System", ["Placidus", "Koch", "Equal", "Whole Sign"])
    
    if st.button("🧮 Calculate Chart", type="primary", use_container_width=True):
        calculate_chart(birth_date, birth_time, birth_place, latitude, longitude, house_system)

# Continuă cu următoarele funcții...
def calculate_chart(birth_date, birth_time, birth_place, latitude, longitude, house_system):
    with st.spinner("🔮 Calculating planetary positions..."):
        # Combine date and time
        birth_datetime = datetime.combine(birth_date, birth_time)
        
        # Calculate planetary positions
        planetary_data = st.session_state.calculator.calculate_planetary_positions(
            birth_datetime, latitude, longitude, house_system
        )
        
        # Calculate houses
        houses_data = st.session_state.calculator.calculate_houses(
            birth_datetime, latitude, longitude, house_system
        )
        
        # Store in session state
        st.session_state.planetary_data = planetary_data
        st.session_state.houses_data = houses_data
        st.session_state.birth_info = {
            'date': birth_date,
            'time': birth_time,
            'place': birth_place,
            'latitude': latitude,
            'longitude': longitude
        }
        
        st.success("🎉 Chart calculated successfully!")
        
        # Display quick results
        st.subheader("📋 Quick Results")
        display_quick_results(planetary_data)

def display_quick_results(planetary_data):
    cols = st.columns(3)
    planets_display = list(planetary_data.keys())[:6]  # Show first 6 planets
    
    for i, planet in enumerate(planets_display):
        with cols[i % 3]:
            data = planetary_data[planet]
            emoji = "☉" if planet == "Sun" else "☽" if planet == "Moon" else "☆"
            st.metric(
                label=f"{emoji} {planet}",
                value=f"{data['position']:.1f}°",
                delta=data['sign']
            )

def render_chart_tab():
    st.header("🪐 Natal Chart")
    
    if 'planetary_data' not in st.session_state:
        st.warning("⚠️ Please calculate a chart first in the Birth Data tab.")
        return
    
    # Chart visualization
    st.subheader("🌌 Zodiac Wheel")
    render_zodiac_wheel()
    
    # Planetary positions table
    st.subheader("📊 Detailed Positions")
    render_planetary_table()
    
    # Export options
    st.subheader("📤 Export Chart")
    render_export_options()

def render_zodiac_wheel():
    # Create a simple zodiac wheel visualization
    fig = go.Figure()
    
    # Add zodiac signs in circle
    signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 
             'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']
    
    for i, sign in enumerate(signs):
        angle = i * 30
        x = np.cos(np.radians(angle))
        y = np.sin(np.radians(angle))
        
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='text',
            text=[sign[:3]],
            textfont=dict(size=10, color='white'),
            showlegend=False
        ))
    
    # Style the chart
    fig.update_layout(
        width=400,
        height=400,
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(visible=False, range=[-1.2, 1.2]),
        yaxis=dict(visible=False, range=[-1.2, 1.2]),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)

def render_planetary_table():
    planetary_data = st.session_state.planetary_data
    df_data = []
    
    for planet, data in planetary_data.items():
        df_data.append({
            'Planet': planet,
            'Position': f"{data['position']:.2f}°",
            'Sign': data['sign'],
            'House': data['house'],
            'Retrograde': '✓' if data.get('retrograde', False) else '✗'
        })
    
    df = pd.DataFrame(df_data)
    st.dataframe(df, use_container_width=True)

def render_export_options():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📄 PDF Report"):
            export_pdf_report()
    
    with col2:
        if st.button("📝 Text File"):
            export_text_report()
    
    with col3:
        if st.button("📊 CSV Data"):
            export_csv_data()
    
    with col4:
        if st.button("🔗 Share"):
            show_share_options()

def export_pdf_report():
    # PDF export functionality
    pdf_data = st.session_state.export_manager.generate_pdf(
        st.session_state.planetary_data,
        st.session_state.houses_data,
        st.session_state.birth_info
    )
    
    st.download_button(
        label="⬇️ Download PDF",
        data=pdf_data,
        file_name="horoscope_report.pdf",
        mime="application/pdf"
    )
def render_aspects_tab():
    st.header("⭐ Astrological Aspects")
    
    if 'planetary_data' not in st.session_state:
        st.warning("⚠️ Please calculate a chart first.")
        return
    
    # Calculate aspects
    aspects = st.session_state.calculator.calculate_aspects(st.session_state.planetary_data)
    
    # Display aspects
    st.subheader("🔍 Detected Aspects")
    
    for aspect in aspects:
        with st.container():
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{aspect['planet1']}** {aspect['aspect']} **{aspect['planet2']}**")
            with col2:
                orb_color = "🟢" if aspect['orb'] <= 1 else "🟡" if aspect['orb'] <= 3 else "🔴"
                st.write(f"{orb_color} {aspect['orb']:.2f}° orb")
            with col3:
                st.write(f"*{aspect['strength']}*")

def render_settings_tab():
    st.header("⚙️ Settings & Configuration")
    
    st.subheader("🎨 Appearance")
    theme = st.selectbox("Color Theme", ["Cosmic Vintage", "Dark Mode", "Light Mode"])
    font_size = st.slider("Font Size", 12, 24, 16)
    
    st.subheader("📐 Calculation Settings")
    orb_tight = st.number_input("Tight Orb", value=1.0, step=0.5)
    orb_medium = st.number_input("Medium Orb", value=3.0, step=0.5)
    orb_wide = st.number_input("Wide Orb", value=6.0, step=0.5)
    
    if st.button("💾 Save Settings", type="primary"):
        st.success("Settings saved successfully!")

def show_share_options():
    st.subheader("🔗 Share Your Horoscope")
    
    share_data = {
        'planetary_data': st.session_state.planetary_data,
        'birth_info': st.session_state.birth_info
    }
    
    # Generate shareable link (base64 encoded data)
    encoded_data = base64.b64encode(str(share_data).encode()).decode()
    share_url = f"https://your-app.com/share?data={encoded_data}"
    
    st.text_input("Shareable Link", share_url)
    
    # Social media buttons
    st.write("Share on:")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.button("📧 Email")
    with col2:
        st.button("🐦 Twitter")
    with col3:
        st.button("💬 WhatsApp")

if __name__ == "__main__":
    main()
