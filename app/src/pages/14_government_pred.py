import logging
logger = logging.getLogger(__name__)

import pandas as pd
import streamlit as st
import requests
import folium
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from streamlit_folium import st_folium

from modules.nav import SideBarLinks

API_BASE = "http://web-api:4000/housing"

st.set_page_config(layout="wide")
SideBarLinks()

st.title("🏚️ Housing Deprivation Predictor")
st.write(
    """
This model predicts each European country's **housing deprivation rate** which is the percent of people living in overcrowded housing or poor living conditions based on socioeconomic indicators:

- **Immigration**: total number of people that immigrated to the country in a given year
- **Housing-cost overburden**: percent of the population spending more than 40% of their 
  disposable income on housing costs like rent, utilities, and maintenance
- **GDP per capita**: the total economic output of a country divided by its population, 
  used as a measure of a country's overall wealth and standard of living
- **Population density**: the number of people living per square kilometer in a country
- **Unemployment rate**: percent of the working-age population that is actively looking 
  for work but does not have a job
"""
)

# Ensure the model is trained so prediction endpoints have parameters to use.
# Cached so we only hit the train endpoint once per session.
@st.cache_data(show_spinner="Training the deprivation model…")
def ensure_model_trained():
    resp = requests.post(f"{API_BASE}/government/train")
    resp.raise_for_status()
    return resp.json()


@st.cache_data(show_spinner="Predicting deprivation across Europe…")
def fetch_deprivation_map():
    resp = requests.get(f"{API_BASE}/government/deprivation-map")
    resp.raise_for_status()
    return resp.json()


try:
    metrics = ensure_model_trained()
    rows = fetch_deprivation_map()
except requests.exceptions.ConnectionError:
    st.error("Could not connect to the backend. Make sure the Flask API is running on port 4000.")
    st.stop()
except Exception as e:
    st.error(f"Could not load the deprivation model: {e}")
    st.stop()

df = pd.DataFrame(rows)

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
    'Ireland': [53.1424, -7.6921],
    'Italy': [41.8719, 12.5674],
    'Latvia': [56.8796, 24.6032],
    'Lithuania': [55.1694, 23.8813],
    'Luxembourg': [49.8153, 6.1296],
    'Malta': [35.9375, 14.3754],
    'Netherlands': [52.1326, 5.2913],
    'Poland': [51.9194, 19.1451],
    'Portugal': [39.3999, -8.2245],
    'Romania': [45.9432, 24.9668],
    'Slovakia': [48.6690, 19.6990],
    'Slovenia': [46.1512, 14.9955],
    'Spain': [40.4637, -3.7492],
    'Sweden': [60.1282, 18.6435],
}

st.divider()

# Europe heatmap ────────────────────────────────────────────────────────────
st.subheader("Predicted Housing Deprivation Across Europe")
st.markdown('''- Darker red countries on the map have <u>**higher predicted deprivation**</u> and a <u>**stronger need for housing funding.**</u>
- Darker green countries on the map have <u>**lower predicted deprivation**</u> and a <u>**lower need for housing funding.**</u>''', unsafe_allow_html=True)
st.caption("*Predictions use each country's most recent year of data.*")

cmap = plt.get_cmap('RdYlGn_r')
norm = mcolors.Normalize(vmin=df["predicted_deprivation"].min(), vmax=df["predicted_deprivation"].max())

def get_color(value):
    return mcolors.to_hex(cmap(norm(value)))

color_map = {row["geo"]: get_color(row["predicted_deprivation"]) for _, row in df.iterrows()}

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
                fill_color=get_color(row["predicted_deprivation"]),
                fill_opacity=1,
                popup=folium.Popup(
                    f"<b>{row['geo']}</b><br>"
                    f"Predicted deprivation: {row['predicted_deprivation']}%<br>"
                    f"Latest measured ({row['year']}): {row['deprivation_rate']}%",
                    max_width=220
                )
            ).add_to(m)

    st_folium(m, width=1250, height=500, returned_objects=[])
    st.caption("Map boundaries: leakyMirror/map-of-europe (GitHub), MIT License.")

except Exception as e:
    st.error(f"Error rendering map: {e}")

# Where funding is most needed ───────────────────────────────────────────────
st.subheader("Countries Most In Need of Housing Funding")

ranked = df.sort_values("predicted_deprivation", ascending=False).reset_index(drop=True)
ranked.index += 1

st.dataframe(
    ranked.drop(columns=["deprivation_rate"]).rename(columns={
        "geo": "Country",
        "predicted_deprivation": "Predicted Housing Deprivation",
        "year": "Data Year",
    }),
    use_container_width=True,
    column_config={
        "Predicted Housing Deprivation": st.column_config.NumberColumn(format="%.2f%%"),
    },
)