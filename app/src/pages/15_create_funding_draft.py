import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')
SideBarLinks()

st.title("Create Funding Draft")
st.caption("Propose a new funding plan targeting social indicators in EU countries.")

with st.container(border = True):
    program = st.text_input("Program Name")

    countries_res = requests.get("http://web-api:4000/housing/country")
    country_list = countries_res.json() if countries_res.status_code == 200 else []
    country_options = {c["country_name"]: c["country_id"] for c in country_list}
    selected_plan_country = st.selectbox("Country", list(country_options.keys()), key = "plan_country")

    amount = st.number_input("Amount (€)", min_value = 0, step = 1000)

    indicators_targeted = st.multiselect(
        "Indicators Targeted",
        ["Pollution", "Crime, Violence, and Vandalism",
         "Poverty", "Overcrowding", "Noise", "House Price Index", "Under-occupied"],
        default = []
    )
    demographics_targeted = st.multiselect(
        "Demographics Targeted",
        ["Students", "Low Income", "Elderly", "Families"],
        default = []
    )

    description = st.text_area("Description")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Submit Draft", type = "primary", use_container_width = True):
            if not program or not description:
                st.warning("Please fill in Program Name and Description.")
            else:
                try:
                    payload = {
                        "user_id": st.session_state.get("user_id", 1),
                        "country_id": country_options[selected_plan_country],
                        "program": program,
                        "amount": amount,
                        "indicators_targeted": ", ".join(indicators_targeted),
                        "demographics_targeted": ", ".join(demographics_targeted),
                        "description": description
                    }
                    response = requests.post("http://web-api:4000/housing/funding-draft", json = payload)
                    if response.status_code == 201:
                        st.success("Draft saved successfully!")
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")
    with col2:
        if st.button("View My Drafts", type = "secondary", use_container_width = True):
            st.switch_page("pages/13_funding_drafts.py")