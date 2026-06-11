import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import world_bank_data as wb
import folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from streamlit_folium import st_folium
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks
import requests

st.set_page_config(page_title="Housing Satisfaction Predictor", layout="wide")

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
    crime     = st.slider("🔒 How much does crime bother you?",     0, 100, 25, key="crime")
    pollution = st.slider("🌫️ How much does pollution bother you?", 0, 100, 25, key="pollution")
 
with col2:
    noise = st.slider("🔊 How much does noise bother you?",         0, 100, 25, key="noise")
    hpi   = st.slider("🏠 How much do housing costs matter?",       0, 100, 40, key="hpi")

st.subheader("Area type")
 
urb = st.radio(
    "",
    options=["Cities", "Towns & Suburbs", "Rural Areas"],
    horizontal=True,
    label_visibility="collapsed"
)

is_rural = urb == "Rural Areas"
is_towns = urb == "Towns & Suburbs"

# coordinates for heatmap
GEOJSON_URL = "https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson"
 
country_coordinates = {
    'Austria': [47.5162, 14.5501],
    'Belgium': [50.8503, 4.3517],
    'Bulgaria': [42.7339, 25.4858],
    'Croatia': [45.1, 15.2],
    'Cyprus': [35.1264, 33.4299],
    'Czechia': [49.8175, 15.4730],
    'Denmark': [56.2639, 9.5018],
    'Estonia': [58.5953, 25.0136],
    'Finland': [61.9241, 25.7482],
    'France': [46.6034, 1.8883],
    'Germany': [51.1657, 10.4515],
    'Greece': [39.0742, 21.8243],
    'Hungary': [47.1625, 19.5033],
    'Iceland': [64.9631, -19.0208],
    'Ireland': [53.1424, -7.6921],
    'Italy': [41.8719, 12.5674],
    'Latvia': [56.8796, 24.6032],
    'Lithuania': [55.1694, 23.8813],
    'Luxembourg': [49.8153, 6.1296],
    'Malta': [35.9375, 14.3754],
    'Netherlands': [52.1326, 5.2913],
    'Norway': [60.4720, 8.4689],
    'Poland': [51.9194, 19.1451],
    'Portugal': [39.3999, -8.2245],
    'Romania': [45.9432, 24.9668],
    'Slovakia': [48.6690, 19.6990],
    'Slovenia': [46.1512, 14.9955],
    'Spain': [40.4637, -3.7492],
    'Sweden': [60.1282, 18.6435],
    'Switzerland': [46.8182, 8.2275],
    'United Kingdom': [55.3781, -3.4360],
}

# Heatmap
 
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
        response = requests.post(f"http://web-api:4000/housing/student/prediction", json=payload)
        response.raise_for_status()
        data = response.json()
        results = data.get("all_countries", [])
 
        df = pd.DataFrame(results)
 
        st.divider()
 
        # ── Heatmap ──────────────────────────────────────────────────────
        st.subheader("Predicted Life Satisfaction Across Europe")
        st.markdown(
            '''- Darker **green** countries have <u>**higher predicted satisfaction**</u> based on your priorities.
- Darker **red** countries have <u>**lower predicted satisfaction**</u> based on your priorities.''',
            unsafe_allow_html=True
        )
        st.caption("*Scores are normalized to a 1–10 scale. 10 = best match for your preferences.*")
 
        # color mapping: green = high (10), red = low (1)
        cmap = plt.get_cmap('RdYlGn')
        norm = mcolors.Normalize(vmin=1, vmax=10)
 
        def get_color(value):
            return mcolors.to_hex(cmap(norm(value)))
 
        color_map = {
            row["geo"]: get_color(row["predicted_score"])
            for _, row in df.iterrows()
        }
 
        try:
            geo_data = requests.get(GEOJSON_URL).json()
            m = folium.Map(location=[54.5260, 15.2551], zoom_start=4)
 
            def style_function(feature):
                name = feature['properties'].get('NAME', '')
                return {
                    'fillColor': color_map.get(name, '#cccccc'),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }
 
            folium.GeoJson(
                geo_data,
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(fields=['NAME'], aliases=['Country']),
            ).add_to(m)
 
            for _, row in df.iterrows():
                coords = country_coordinates.get(row["geo"])
                if coords:
                    folium.CircleMarker(
                        location=coords,
                        radius=5,
                        color='black',
                        fill=True,
                        fill_color=get_color(row["predicted_score"]),
                        fill_opacity=1,
                        popup=folium.Popup(
                            f"<b>{row['geo']}</b><br>"
                            f"Satisfaction score: {row['predicted_score']} / 10",
                            max_width=220
                        )
                    ).add_to(m)
 
            st_folium(m, width=1250, height=500, returned_objects=[])
            st.caption("Map boundaries: leakyMirror/map-of-europe (GitHub), MIT License.")
 
        except Exception as e:
            st.error(f"Error rendering map: {e}")
 
        # ── Ranked table ─────────────────────────────────────────────────
        st.subheader("Country Rankings")
 
        ranked = df.sort_values("predicted_score", ascending=False).reset_index(drop=True)
        ranked.index += 1
        ranked.index.name = "Rank"
 
        st.dataframe(
            ranked.rename(columns={
                "geo": "Country",
                "predicted_score": "Predicted Satisfaction (1-10)",
            }),
            use_container_width=True,
        )
 
    except requests.exceptions.ConnectionError:
        st.error("Could not connect to the backend.")
    except Exception as e:
        st.error(f"Something went wrong: {e}")