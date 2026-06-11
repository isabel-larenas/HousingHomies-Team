import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(page_title="View Funding", layout = 'wide')
SideBarLinks()

st.title("Explore Funding Programs")

st.subheader("Funding Index")
st.caption("Explore existing housing and social funding programs across EU countries.")

try:
    response = requests.get("http://web-api:4000/housing/funding")
    if response.status_code == 200:
        data = response.json()
        if data:
            col1, col2 = st.columns(2)

            with col1:
                countries = ["All"] + sorted(list(set(f["country_name"] for f in data if "country_name" in f)))
                selected_country = st.selectbox("Filter by Country", countries, key = "funding_country")

            with col2:
                agencies = ["All"] + sorted(list(set(f["agency"] for f in data if "agency" in f)))
                selected_agency = st.selectbox("Filter by Agency", agencies, key = "funding_agency")

            df = pd.DataFrame(data)[["country_name", "agency", "program", "amount", "year"]]
            df.columns = ["Country", "Agency", "Program", "Amount (€)", "Year"]

            if selected_country != "All":
                df = df[df["Country"] == selected_country]
            if selected_agency != "All":
                df = df[df["Agency"] == selected_agency]

            st.dataframe(
                df,
                column_config = {
                    "Amount (€)": st.column_config.NumberColumn(
                        "Amount (€)",
                        format = "€ %,.2f",
                    ),
                    "Year": st.column_config.NumberColumn(
                        "Year",
                        format = "%d",
                    ),
                },
                use_container_width = True,
                hide_index = True
            )
        else:
            st.info("No funding data.")
    else:
        st.error("Could not load funding data.")
except Exception as e:
    st.error(f"Error: {e}")