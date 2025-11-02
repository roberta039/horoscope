# app_enhanced.py
import streamlit as st
import math
from datetime import datetime
from advanced_calculations import AdvancedAstroCalculator

class PalmOSApp:
    def __init__(self):
        self.calculator = AdvancedAstroCalculator()
        self.current_screen = 'main'
        self.chart_data = None
        self.settings = {
            'house_system': 'Placidus',
            'wheel_type': 'Graphic',
            'glyphs_system': 'Graphic',
            'zodiac_type': 'Tropical'
        }
        
    def show_main_form(self):
        """Formularul principal exact ca în Palm OS"""
        st.markdown("""
        <style>
        .main-container {
            background: #C0C0C0;
            border: 3px outset #FFFFFF;
            padding: 15px;
            margin: 10px;
        }
        .palm-button {
            background: #C0C0C0;
            border: 2px outset #FFFFFF;
            padding: 8px 16px;
            margin: 4px;
            font-family: Arial;
            font-size: 14px;
            width: 100%;
        }
        .palm-title {
            background: #000080;
            color: white;
            padding: 10px;
            text-align: center;
            font-weight: bold;
            margin: -15px -15px 15px -15px;
        }
        .here-now {
            background: white;
            border: 2px inset #C0C0C0;
            padding: 10px;
            margin: 10px 0;
            font-family: Arial;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        st.markdown('<div class="palm-title">1.Chart</div>', unsafe_allow_html=True)
        
        # Butoanele principale
        cols = st.columns(2)
        
        with cols[0]:
            if st.button('📊 Charts', key='btn_charts', use_container_width=True):
                self.current_screen = 'charts'
                
            if st.button('🕐 Time', key='btn_time', use_container_width=True):
                self.current_screen = 'time'
                
            if st.button('🧮 Calc', key='btn_calc', use_container_width=True):
                self.current_screen = 'calc'
        
        with cols[1]:
            if st.button('📍 Places', key='btn_places', use_container_width=True):
                self.current_screen = 'places'
                
            if st.button('🔗 Aspects', key='btn_aspects', use_container_width=True):
                self.current_screen = 'aspects'
                
            if st.button('⚙️ Options', key='btn_options', use_container_width=True):
                self.current_screen = 'options'
        
        # Here & Now
        st.markdown('<div class="here-now">', unsafe_allow_html=True)
        st.write("**Here&Now**")
        now = datetime.now()
        st.write(f"Date: {now.strftime('%d %b %Y')}")
        st.write(f"Time: {now.strftime('%H:%M')}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def show_time_form(self):
        """Formularul de timp ca în original"""
        st.markdown('<div class="palm-title">Set Time</div>', unsafe_allow_html=True)
        
        with st.form("time_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Time of Birth")
                birth_time = st.time_input("", datetime.now().time(), label_visibility="collapsed")
                
                st.subheader("Time Zone")
                timezone = st.selectbox("", 
                    ["GMT-12", "GMT-11", "GMT-10", "GMT-9", "GMT-8", "GMT-7", 
                     "GMT-6", "GMT-5", "GMT-4", "GMT-3", "GMT-2", "GMT-1", 
                     "GMT", "GMT+1", "GMT+2", "GMT+3", "GMT+4", "GMT+5", 
                     "GMT+6", "GMT+7", "GMT+8", "GMT+9", "GMT+10", "GMT+11", "GMT+12"],
                    index=12, label_visibility="collapsed")
            
            with col2:
                st.subheader("Date")
                birth_date = st.date_input("", datetime.now(), label_visibility="collapsed")
            
            # Butoane
            col_ok, col_cancel, col_now = st.columns([2, 2, 1])
            
            with col_ok:
                submit_ok = st.form_submit_button("OK", use_container_width=True)
            
            with col_cancel:
                submit_cancel = st.form_submit_button("Cancel", use_container_width=True)
            
            with col_now:
                submit_now = st.form_submit_button("Now", use_container_width=True)
            
            if submit_ok:
                self.current_screen = 'main'
                st.rerun()
            elif submit_cancel:
                self.current_screen = 'main'
                st.rerun()
            elif submit_now:
                st.rerun()
    
    def show_calc_form(self):
        """Formularul de calcul complet"""
        st.markdown('<div class="palm-title">Calc</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Data")
            if st.button("Input Data", use_container_width=True):
                self.current_screen = 'time'
                st.rerun()
        
        with col2:
            st.subheader("Chart Type")
            chart_type = st.radio("", ["Natal", "Transit", "Progressed"], index=0, label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Checkbox-uri pentru calcul
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        st.subheader("Calculate")
        
        cols = st.columns(5)
        with cols[0]:
            calc_chart = st.checkbox("Ch", value=True)
        with cols[1]:
            calc_pos = st.checkbox("Pos", value=True)
        with cols[2]:
            calc_asp = st.checkbox("Asp", value=True)
        with cols[3]:
            calc_int = st.checkbox("Int", value=False)
        with cols[4]:
            calc_trn = st.checkbox("Trn", value=False)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Buton Calculate
        if st.button("CALCULATE", use_container_width=True, type="primary"):
            with st.spinner("Calculating planetary positions..."):
                # Exemplu de calcul
                sample_date = datetime(1990, 6, 15, 12, 0)
                positions, houses = self.calculator.calculate_all_positions(
                    sample_date, 45.81, 15.98, self.settings['house_system']
                )
                
                self.chart_data = {
                    'positions': positions,
                    'houses': houses,
                    'birth_data': {
                        'date': sample_date,
                        'latitude': 45.81,
                        'longitude': 15.98
                    }
                }
            st.success("Calculation complete!")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
    
    def show_aspects_form(self):
        """Formularul de aspecte detaliat"""
        st.markdown('<div class="palm-title">Aspects</div>', unsafe_allow_html=True)
        
        if not self.chart_data:
            st.warning("No chart data available. Please calculate a chart first.")
            if st.button("Back", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
            return
        
        # Calcul aspecte
        aspects = self.calculate_aspects_from_positions(self.chart_data['positions'])
        
        st.markdown('<div style="background: white; padding: 10px; margin: 10px 0; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
        
        if aspects:
            for aspect in aspects:
                st.write(f"**{aspect['planet1']} {aspect['aspect']} {aspect['planet2']}**")
                st.write(f"Angle: {aspect['angle']}° | Exact: {aspect['exact_diff']:.2f}° | Orb: {aspect['orb']:.2f}°")
                st.divider()
        else:
            st.info("No aspects found within orb limits")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        if st.button("Done", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
    
    def show_options_form(self):
        """Formularul de opțiuni complet"""
        st.markdown('<div class="palm-title">Options</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div style="background: white; padding: 10px; margin: 5px; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
            
            st.subheader("House System")
            self.settings['house_system'] = st.radio(
                "",
                ["Placidus", "Koch", "Equal"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.subheader("Wheel Type")
            self.settings['wheel_type'] = st.radio(
                "",
                ["Graphic", "Text"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div style="background: white; padding: 10px; margin: 5px; border: 1px inset #C0C0C0;">', unsafe_allow_html=True)
            
            st.subheader("Glyphs System")
            self.settings['glyphs_system'] = st.radio(
                "",
                ["Graphic", "Text"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.subheader("Zodiac")
            self.settings['zodiac_type'] = st.radio(
                "",
                ["Tropical", "Sidereal"],
                index=0,
                label_visibility="collapsed"
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Butoane OK și Cancel
        col_ok, col_cancel = st.columns(2)
        
        with col_ok:
            if st.button("OK", use_container_width=True):
                st.success("Options saved!")
                self.current_screen = 'main'
                st.rerun()
        
        with col_cancel:
            if st.button("Cancel", use_container_width=True):
                self.current_screen = 'main'
                st.rerun()
    
    def show_charts_form(self):
        """Formularul de charts"""
        st.markdown('<div class="palm-title">Charts</div>', unsafe_allow_html=True)
        
        st.info("Charts database functionality - To be implemented")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
    
    def show_places_form(self):
        """Formularul de places"""
        st.markdown('<div class="palm-title">Places</div>', unsafe_allow_html=True)
        
        st.info("Places database functionality - To be implemented")
        
        if st.button("Back", use_container_width=True):
            self.current_screen = 'main'
            st.rerun()
    
    def calculate_aspects_from_positions(self, positions):
        """Calculează aspectele din pozițiile planetare"""
        aspects = []
        planets = [p for p in positions.keys() if p != 'Ascendant']
        
        for i in range(len(planets)):
            for j in range(i + 1, len(planets)):
                p1 = planets[i]
                p2 = planets[j]
                lon1 = positions[p1]['longitude']
                lon2 = positions[p2]['longitude']
                
                diff = abs(lon1 - lon2)
                if diff > 180:
                    diff = 360 - diff
                
                # Verifică aspecte majore
                aspect_orb = {
                    'Conjunction': 8,
                    'Sextile': 6,
                    'Square': 8,
                    'Trine': 8,
                    'Opposition': 8
                }
                
                for aspect, orb in aspect_orb.items():
                    angle = {
                        'Conjunction': 0,
                        'Sextile': 60,
                        'Square': 90,
                        'Trine': 120,
                        'Opposition': 180
                    }[aspect]
                    
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            'planet1': p1,
                            'planet2': p2,
                            'aspect': aspect,
                            'angle': angle,
                            'exact_diff': diff,
                            'orb': abs(diff - angle)
                        })
                        break
        
        return aspects

def main():
    st.set_page_config(
        page_title="1.Chart Horoscope v2.42 - Exact Replica",
        page_icon="♐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Inițializare aplicație
    if 'palm_app' not in st.session_state:
        st.session_state.palm_app = PalmOSApp()
    
    app = st.session_state.palm_app
    
    # Navigare între ecrane
    if app.current_screen == 'main':
        app.show_main_form()
    elif app.current_screen == 'time':
        app.show_time_form()
    elif app.current_screen == 'calc':
        app.show_calc_form()
    elif app.current_screen == 'aspects':
        app.show_aspects_form()
    elif app.current_screen == 'options':
        app.show_options_form()
    elif app.current_screen == 'charts':
        app.show_charts_form()
    elif app.current_screen == 'places':
        app.show_places_form()

if __name__ == "__main__":
    main()
