import streamlit as st
import pandas as pd
import datetime
import random
from datetime import datetime, timedelta

# Configurare pagină
st.set_page_config(
    page_title="Horoscop Palm OS Classic",
    page_icon="♈",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Stil CSS pentru a recrea aspectul Palm OS
st.markdown("""
<style>
    .main {
        background-color: #C0C0C0;
        font-family: "Courier New", monospace;
    }
    .palm-header {
        background-color: #000080;
        color: white;
        padding: 10px;
        font-weight: bold;
        text-align: center;
        border: 2px outset #C0C0C0;
    }
    .palm-button {
        background-color: #C0C0C0;
        border: 2px outset #C0C0C0;
        padding: 5px 15px;
        font-family: "Courier New", monospace;
        font-size: 14px;
    }
    .horoscope-text {
        background-color: white;
        border: 2px inset #C0C0C0;
        padding: 15px;
        margin: 10px 0;
        min-height: 150px;
        font-size: 14px;
        line-height: 1.4;
    }
    .zodiac-selector {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }
    .zodiac-option {
        text-align: center;
        cursor: pointer;
        padding: 10px;
        border: 2px outset #C0C0C0;
        background-color: #C0C0C0;
    }
    .zodiac-option:hover {
        border: 2px inset #C0C0C0;
    }
    .selected-zodiac {
        border: 2px inset #C0C0C0;
        background-color: #000080;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# Date pentru zodiile românești
ZODIAC_DATA = {
    "Berbec": {"date": "Mar 21 - Apr 19", "element": "Foc", "planet": "Marte"},
    "Taur": {"date": "Apr 20 - May 20", "element": "Pământ", "planet": "Venus"},
    "Gemeni": {"date": "May 21 - Jun 20", "element": "Aer", "planet": "Mercur"},
    "Rac": {"date": "Jun 21 - Jul 22", "element": "Apă", "planet": "Lună"},
    "Leu": {"date": "Jul 23 - Aug 22", "element": "Foc", "planet": "Soare"},
    "Fecioara": {"date": "Aug 23 - Sep 22", "element": "Pământ", "planet": "Mercur"},
    "Balanta": {"date": "Sep 23 - Oct 22", "element": "Aer", "planet": "Venus"},
    "Scorpion": {"date": "Oct 23 - Nov 21", "element": "Apă", "planet": "Pluto"},
    "Sagetator": {"date": "Nov 22 - Dec 21", "element": "Foc", "planet": "Jupiter"},
    "Capricorn": {"date": "Dec 22 - Jan 19", "element": "Pământ", "planet": "Saturn"},
    "Varsator": {"date": "Jan 20 - Feb 18", "element": "Aer", "planet": "Uranus"},
    "Pesti": {"date": "Feb 19 - Mar 20", "element": "Apă", "planet": "Neptun"}
}

# Previziuni pentru fiecare zodiac
HOROSCOPE_TEXTS = {
    "Berbec": [
        "Energia ta este la maxim azi. Profită de această zi pentru a începe proiecte noi.",
        "Marte îți oferă curaj. Nu ezita să îți exprimi părerea în fața superiorilor.",
        "Atenție la impulsivitate. Gândește-te de două ori înainte de a acționa."
    ],
    "Taur": [
        "Venus aduce armonie în relații. Este momentul potrivit pentru reconciliere.",
        "Stabilitatea financiară este accentuată. O investiție mică ar putea aduce profit.",
        "Rămâi deschis la schimbări, chiar dacă îți plac rutinele."
    ],
    "Gemeni": [
        "Mercur stimulează comunicarea. O conversație importantă așteaptă să fie avută.",
        "Curiozitatea ta intelectuală este stimulată. Citește ceva nou sau învață o abilitate.",
        "Evită să fii prea dispersat. Concentrează-te pe un singur lucru la un moment dat."
    ],
    "Rac": [
        "Luna influențează emoțiile. Ascultă-ți intuiția în deciziile de azi.",
        "Familia este importantă. Petrece timp cu cei dragi.",
        "Protejează-ți spațiul personal. Nu permite altora să îți tulbure liniștea."
    ],
    "Leu": [
        "Soarele îți aduce încredere. Ești în centrul atenției - profită de moment!",
        "Creativitatea este la cote maxime. Exprimă-te artistic sau profesional.",
        "Atenție la mândrie excesivă. Recunoaște și contribuția altora."
    ],
    "Fecioara": [
        "Mercur îți ascuțește mintea. Detaliile nu îți vor scăpa astăzi.",
        "Organizarea este cheia succesului. Fă-ți o listă de sarcini și respect-o.",
        "Nu fi prea critic cu tine însuți. Acceptă-ți imperfecțiunile."
    ],
    "Balanta": [
        "Venus aduce echilibru. Este momentul pentru compromisuri în relații.",
        "Frumusețea și arta te atrag. Vizitează un muzeu sau o expoziție.",
        "Evită amânarea deciziilor importante. Ascultă-ți rațiunea, nu doar inima."
    ],
    "Scorpion": [
        "Pluto aduce transformare. Ceva veche se termină pentru ca ceva nou să înceapă.",
        "Intuiția ta este puternică. Oamenii nu te pot păcăli cu ușurință.",
        "Transformă-ți pasiunea în acțiune constructivă."
    ],
    "Sagetator": [
        "Jupiter îți extinde orizonturile. Planifică o călătorie sau învață ceva nou.",
        "Optimismul tău este contagios. Inspiră-i pe cei din jurul tău.",
        "Caută adevărul mai profund în orice situație."
    ],
    "Capricorn": [
        "Saturn îți oferă disciplină. Obiectivele pe termen lung sunt în centru.",
        "Responsabilitățile tale sunt multe, dar le poți gestiona.",
        "Nu uita să te bucuri de micile victorii de-a lungul drumului."
    ],
    "Varsator": [
        "Uranus aduce schimbări neașteptate. Fii deschis la idei revoluționare.",
        "Originalitatea ta este remarcată. Adu-ți contribuția unică în grup.",
        "Prieteniile sunt importante astăzi. Conexiuni noi ar putea apărea."
    ],
    "Pesti": [
        "Neptun îți intensifică visurile. Notează-ți visele - ar putea fi revelatoare.",
        "Compașiunea ta este necesară cuiva apropiat. Oferă sprijin fără să judeci.",
        "Protejează-ți energia. Evită situațiile prea haotice sau negative."
    ]
}

def get_daily_horoscope(zodiac):
    """Generează un horoscop zilnic pentru zodiacul selectat"""
    today = datetime.now().date()
    random.seed(f"{zodiac}_{today}")
    prediction = random.choice(HOROSCOPE_TEXTS[zodiac])
    
    return prediction

def get_zodiac_from_date(birth_date):
    """Determină zodiacul pe baza datei de naștere"""
    month = birth_date.month
    day = birth_date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "Berbec"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "Taur"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "Gemeni"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "Rac"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "Leu"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "Fecioara"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "Balanta"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "Scorpion"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "Sagetator"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "Capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "Varsator"
    else:
        return "Pesti"

def main():
    # Header Palm OS style
    st.markdown('<div class="palm-header">♉ HOROSCOP Palm OS v1.0 ♉</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Selectare zodiac
    st.subheader("Alege-ți zodiacul:")
    
    # Afișare zodiile ca butoane
    cols = st.columns(4)
    zodiac_names = list(ZODIAC_DATA.keys())
    
    selected_zodiac = st.session_state.get('selected_zodiac', 'Berbec')
    
    for i, zodiac in enumerate(zodiac_names):
        with cols[i % 4]:
            if st.button(zodiac, key=zodiac, use_container_width=True):
                selected_zodiac = zodiac
                st.session_state.selected_zodiac = zodiac
    
    # Sau determinare automată din data nașterii
    st.markdown("---")
    st.subheader("Sau introdu data nașterii:")
    
    col1, col2 = st.columns(2)
    with col1:
        birth_date = st.date_input(
            "Data nașterii",
            value=datetime.now() - timedelta(days=365*25),
            max_value=datetime.now()
        )
    
    with col2:
        if st.button("Determină zodiacul", use_container_width=True):
            calculated_zodiac = get_zodiac_from_date(birth_date)
            selected_zodiac = calculated_zodiac
            st.session_state.selected_zodiac = calculated_zodiac
            st.success(f"Zodiul tău este: {calculated_zodiac}")
    
    st.markdown("---")
    
    # Afișare horoscop
    if selected_zodiac:
        st.subheader(f"Horoscop pentru {selected_zodiac}")
        
        # Informații despre zodiac
        zodiac_info = ZODIAC_DATA[selected_zodiac]
        st.write(f"**Perioadă:** {zodiac_info['date']} | "
                f"**Element:** {zodiac_info['element']} | "
                f"**Planetă:** {zodiac_info['planet']}")
        
        # Buton pentru generare horoscop
        if st.button("🔮 Vezi horoscopul zilnic", use_container_width=True):
            with st.spinner("Consultăm stelele..."):
                horoscope = get_daily_horoscope(selected_zodiac)
                
                # Afișare horoscop în casetă Palm OS style
                st.markdown(f'<div class="horoscope-text">{horoscope}</div>', 
                           unsafe_allow_html=True)
                
                # Data curentă
                st.caption(f"Horoscop pentru {datetime.now().strftime('%d %B %Y')}")
        
        # Afișează ultimul horoscop generat dacă există
        if 'last_horoscope' in st.session_state and st.session_state.get('last_zodiac') == selected_zodiac:
            st.markdown(f'<div class="horoscope-text">{st.session_state.last_horoscope}</div>', 
                       unsafe_allow_html=True)
            st.caption(f"Horoscop pentru {st.session_state.get('last_date', 'astăzi')}")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-size: 12px;'>"
        "Palm OS Horoscope © 1998-2001 | Recreated for Streamlit 2024"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
