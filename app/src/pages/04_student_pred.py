import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks
import requests

try:
    if 'model_trained' not in st.session_state:
        requests.post("http://web-api:4000/housing/student/train")
        st.session_state['model_trained'] = True
except:
    st.warning("Backend not ready yet — try refreshing in a moment.")

st.title("Housing Satisfaction Predictor")
SideBarLinks()
st.write("Set your comfortability levels with these housing conditions to see your predicted life satisfaction score in different countries across Europe.")
st.divider()


RAW_RANGES = {
    'crime_rate':     (0.0,  37.3),
    'noise_rate':     (3.2,  55.9),
    'pollution_rate': (1.6,  43.1),
    'hpi_weight':     (-9.1, 14.3),
}

def pct_to_raw(pct, col):
    low, high = RAW_RANGES[col]
    return low + (pct / 100) * (high - low)

def raw_to_pct(val, col):
    low, high = RAW_RANGES[col]
    return int(max(0, min(100, ((val - low) / (high - low)) * 100)))

st.subheader("Environmental conditions")

col1, col2 = st.columns(2)

with col1:
    crime     = st.slider("🔒 Crime Levels",  0, 100, 25, key="crime")
    pollution = st.slider("🌫️ Pollution Levels",  0, 100, 25, key="pollution")

with col2:
    noise = st.slider("🔊 Noise Levels",          0, 100, 25, key="noise")
    hpi   = st.slider("🏠 Housing Price Growth",  0, 100, 40, key="hpi")

st.subheader("Area type")
 
urb = st.radio(
    "",
    options=["Cities", "Towns & Suburbs", "Rural Areas"],
    horizontal=True,
    label_visibility="collapsed"
)

is_rural = urb == "Rural Areas"
is_towns = urb == "Towns & Suburbs"


RAW_RANGES = {
    'crime_rate':     (0.0,  37.3),
    'noise_rate':     (3.2,  55.9),
    'pollution_rate': (1.6,  43.1),
    'hpi_weight':     (-9.1, 14.3),
}

def pct_to_raw(pct, col):
    low, high = RAW_RANGES[col]
    return low + (pct / 100) * (high - low)


if st.button("Predict for all countries", type="primary", use_container_width=True):
    payload = {
        "crime":     pct_to_raw(crime,     'crime_rate'),
        "noise":     pct_to_raw(noise,     'noise_rate'),
        "pollution": pct_to_raw(pollution, 'pollution_rate'),
        "hpi":       pct_to_raw(hpi,       'hpi_weight'),
        "is_rural":  is_rural,
        "is_towns":  is_towns,
    }

    try:
        response = requests.post("http://web-api:4000/housing/student/prediction", json=payload)
        response.raise_for_status()
        data = response.json()
        results = data.get("all_countries", [])

        st.divider()
        st.subheader("Predicted Life Satisfaction by Country")
        st.write("See your predicted life satisfaction score under your chosen conditions in each country, between 0 - 10 with 0 being least satisfied and 10 being most satisfied.")

        df_results = pd.DataFrame(results)
        df_results.index = df_results.index + 1
        df_results.index.name = "Rank"
        df_results.columns = ["Country", "Predicted Satisfaction Rating (0-10)"]
        st.dataframe(df_results, use_container_width=True)

    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")