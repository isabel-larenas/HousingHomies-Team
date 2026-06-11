import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
import folium
import plotly.express as px
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from streamlit_folium import st_folium
from modules.nav import SideBarLinks

st.set_page_config(page_title="Risk Heatmap", layout = 'wide')
SideBarLinks()

st.markdown("""
    <style>
    thead tr th { color: white !important; }
    </style>
""", unsafe_allow_html = True)

st.title("Risk Heatmap")
st.caption("Visualize social indicator risk levels across EU countries.")

GEOJSON_URL = "https://raw.githubusercontent.com/leakyMirror/map-of-europe/master/GeoJSON/europe.geojson"

INDICATOR_UNITS = {
    "Pollution": "% of population",
    "Crime, Violence, and Vandalism": "% of population",
    "Poverty": "% of population",
    "Overcrowding": "% of population",
    "Noise": "% of population",
    "House Price Index": "Index (2015=100)",
}

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
    'Netherlands': [52.1326, 5.2913],
    'Poland': [51.9194, 19.1451],
    'Portugal': [39.3999, -8.2245],
    'Romania': [45.9432, 24.9668],
    'Slovakia': [48.6690, 19.6990],
    'Slovenia': [46.1512, 14.9955],
    'Spain': [40.4637, -3.7492],
    'Sweden': [60.1282, 18.6435],
    'Norway': [60.4720, 8.4689],
    'Iceland': [64.9631, -19.0208],
    'Switzerland': [46.8182, 8.2275],
    'United Kingdom': [55.3781, -3.4360],
    'Albania': [41.1533, 20.1683],
    'Montenegro': [42.7087, 19.3744],
    'North Macedonia': [41.6086, 21.7453],
    'Serbia': [44.0165, 21.0059],
    'Turkiye': [38.9637, 35.2433],
    'Kosovo': [42.6026, 20.9030],
}

# Sync data on first page load
if "synced" not in st.session_state:
    st.session_state.synced = False

if not st.session_state.synced:
    with st.spinner("Syncing..."):
        for ep in ["pollution", "crime", "poverty", "overcrowding", "noise", "hpi"]:
            requests.post(f"http://web-api:4000/housing/social-indicator-stats/{ep}")
    st.session_state.synced = True
    st.rerun()

# Filters
col1, col2 = st.columns(2)

with col1:
    indicators = list(INDICATOR_UNITS.keys())
    indicator_type = st.selectbox(
        "Shade Map By Indicator",
        indicators,
        index = indicators.index("Poverty")
    )

with col2:
    try:
        r = requests.get(
            "http://web-api:4000/housing/social-indicator-stats",
            params = {"social_indicator_type": indicator_type}
        )
        if r.status_code == 200 and r.json():
            available_years = sorted(list(set(str(row["year"]) for row in r.json())), reverse = True)
        else:
            available_years = [str(y) for y in range(2010, 2026)]
    except:
        available_years = [str(y) for y in range(2010, 2026)]

    selected_year = st.selectbox(
        "Year",
        available_years,
        index = 0
    )

st.divider()

# Map and Rankings 
map_col, chart_col = st.columns([1, 1])

with map_col:
    st.subheader(f"{indicator_type} Risk Map ({selected_year})")

    try:
        response = requests.get(
            "http://web-api:4000/housing/social-indicator-stats",
            params = {"social_indicator_type": indicator_type, "year": selected_year}
        )

        if response.status_code == 200 and response.json():
            data = response.json()
            df = pd.DataFrame(data)[["country_name", "value"]]
            df["value"] = pd.to_numeric(df["value"], errors = "coerce")
            df = df.dropna()

            if indicator_type == "House Price Index":
                cmap = plt.get_cmap('YlOrRd')
                norm = mcolors.Normalize(vmin = 80, vmax = 200)
            else:
                cmap = plt.get_cmap('RdYlGn_r')
                norm = mcolors.Normalize(vmin = df["value"].min(), vmax = df["value"].max())

            def get_color(value):
                return mcolors.to_hex(cmap(norm(value)))

            color_map = {row["country_name"]: get_color(row["value"]) for _, row in df.iterrows()}

            geo_data = requests.get(GEOJSON_URL).json()
            m = folium.Map(location = [54.5260, 15.2551], zoom_start = 3.5)
            

            NAME_MAP = {"Czech Republic": "Czechia",
                        "Turkey": "Turkiye",
                        "The former Yugoslav Republic of Macedonia": "North Macedonia",
                        }

            def style_function(feature):
                raw_name = feature['properties'].get('NAME', '')
                name = NAME_MAP.get(raw_name, raw_name)
                return {
                    'fillColor': color_map.get(name, '#cccccc'),
                    'color': 'black',
                    'weight': 1,
                    'fillOpacity': 0.7,
                }

            folium.GeoJson(
                geo_data,
                style_function = style_function,
                tooltip = folium.GeoJsonTooltip(fields = ['NAME'], aliases = ['Country']),
            ).add_to(m)

            for _, row in df.iterrows():
                coords = country_coordinates.get(row["country_name"])
                if coords:
                    folium.CircleMarker(
                        location = coords,
                        radius = 6,
                        color = 'black',
                        fill = True,
                        fill_color = get_color(row["value"]),
                        fill_opacity = 1,
                        popup = folium.Popup(
                            f"<b>{row['country_name']}</b><br>{indicator_type}: {row['value']}%",
                            max_width = 200
                        )
                    ).add_to(m)

            st_folium(m, use_container_width = True, height = 900, returned_objects = [])
            st.caption("Map boundaries: leakyMirror/map-of-europe (GitHub), MIT License.")
            map_html = m._repr_html_()
            st.download_button(
                label = "Download Map as HTML",
                data = m._repr_html_(),
                file_name = f"{indicator_type}_{selected_year}_map.html",
                mime = "text/html"
            )

        else:
            st.info("No data — try selecting a different year.")

    except Exception as e:
        st.error(f"Error: {e}")

with chart_col:
    st.subheader(f"{indicator_type} Rankings ({selected_year})")

    if indicator_type == "House Price Index":
        st.caption("% change in house prices relative to the 2015 baseline. Positive = prices risen, negative = prices fallen.")
    else:
        st.caption("Countries ranked highest to lowest by percentage of population impacted.")

    try:
        r = requests.get(
            "http://web-api:4000/housing/social-indicator-stats",
            params = {"social_indicator_type": indicator_type, "year": selected_year}
        )

        if r.status_code == 200 and r.json():
            unit = INDICATOR_UNITS.get(indicator_type, "value")
            df_rank = pd.DataFrame(r.json())[["country_name", "value"]]
            df_rank["value"] = pd.to_numeric(df_rank["value"], errors = "coerce")
            df_rank = df_rank.dropna().sort_values("value", ascending = False).reset_index(drop = True)
            df_rank.columns = ["Country", f"Value ({unit})"]

            if indicator_type == "House Price Index":
                unit = "% change from 2015 baseline"
                df_rank["Value (Index (2015=100))"] = df_rank["Value (Index (2015=100))"] - 100
                df_rank.columns = ["Country", f"Value ({unit})"]

            x_label = "% Change from 2015 Baseline" if indicator_type == "House Price Index" else "% of Population Impacted"
            color_scale = "ylorrd" if indicator_type == "House Price Index" else "RdYlGn_r"
            range_color = [-50, 150] if indicator_type == "House Price Index" else None

            fig = px.bar(
                df_rank,
                x = f"Value ({unit})",
                y = "Country",
                orientation = 'h',
                color = f"Value ({unit})",
                color_continuous_scale = color_scale,
                range_color = range_color,
                title = f"{indicator_type} by Country ({selected_year})",
                labels = {f"Value ({unit})": x_label}
            )

            if indicator_type == "House Price Index":
                fig.update_layout(
                    xaxis = dict(range = [-50, 150]),
                    yaxis = dict(autorange = "reversed", tickfont = dict(size = 14)),
                    height = 900,
                    showlegend = False,
                    coloraxis_showscale = False
                )

                fig.update_traces(
                    hovertemplate = "<b>%{y}</b><br>%{x:.1f} " + x_label.lower() + "<extra></extra>"
                )
                
            else:
                fig.update_layout(
                    yaxis = dict(autorange = "reversed", tickfont = dict(size = 14)),
                    height = 900,
                    showlegend = False,
                    coloraxis_showscale = False
                )

                fig.update_traces(
                    hovertemplate = "<b>%{y}</b><br>%{x:.1f} " + x_label.lower() + "<extra></extra>"
                )
            st.plotly_chart(fig, use_container_width = True)

            csv = df_rank.to_csv(index = False)
            st.download_button(
                label = "Download Rankings as CSV",
                data = csv,
                file_name = f"{indicator_type}_{selected_year}_rankings.csv",
                mime = "text/csv"
            )

        else:
            st.info("No data — try selecting a different year.")

    except Exception as e:
        st.error(f"Error loading rankings: {e}")