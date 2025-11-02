import streamlit as st

def apply_cosmic_design():
    """Apply Cosmic Vintage design to Streamlit app"""
    st.markdown("""
    <style>
    :root {
        --cosmic-deep: #0f0c29;
        --cosmic-mid: #302b63;
        --cosmic-light: #24243e;
        --gold-primary: #f1c40f;
        --gold-glow: rgba(241, 196, 15, 0.3);
        --starlight: #3498db;
        --nebula-purple: #8e44ad;
    }
    
    .stApp {
        background: radial-gradient(circle at 20% 80%, var(--cosmic-mid), var(--cosmic-deep));
        color: white;
        font-family: 'Georgia', serif;
    }
    
    .main .block-container {
        padding-top: 2rem;
    }
    
    h1, h2, h3 {
        color: var(--gold-primary) !important;
        text-shadow: 0 0 10px var(--gold-glow);
        font-weight: bold;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, var(--gold-primary), #e67e22);
        color: var(--cosmic-deep);
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        font-family: 'Georgia', serif;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px var(--gold-glow);
    }
    
    .stTextInput>div>div>input, .stNumberInput>div>div>input, 
    .stDateInput>div>div>input, .stTimeInput>div>div>input,
    .stSelectbox>div>div>select {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--gold-glow);
        color: white;
        border-radius: 8px;
    }
    
    .stDataFrame {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--gold-glow);
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px 8px 0px 0px;
        padding: 1rem 2rem;
        color: white;
        font-weight: bold;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--gold-primary), #e67e22) !important;
        color: var(--cosmic-deep) !important;
    }
    
    /* Custom cards */
    .cosmic-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid var(--gold-glow);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(31, 38, 135, 0.3);
    }
    
    /* Success/warning messages */
    .stAlert {
        border-radius: 8px;
        border: 1px solid var(--gold-glow);
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid var(--gold-glow);
        border-radius: 8px;
        padding: 1rem;
    }
    
    </style>
    """, unsafe_allow_html=True)
