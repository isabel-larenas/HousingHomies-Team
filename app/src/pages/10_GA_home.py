import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Government Agency Home", layout = 'wide')
SideBarLinks()

st.markdown("""
    <style>
    section[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button {
        height: 75px;
        font-size: 25px;
    }
    div[data-testid="stMarkdownContainer"] p {
        text-align: center;
    }
    </style>
""", unsafe_allow_html = True)

st.title(f"Welcome, {st.session_state['name']}.")
st.text("Government Agency Dashboard")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View Funding", use_container_width = True, type = "primary"):
        st.switch_page("pages/11_view_funding.py")
    st.write("Browse EU housing funding programs")

with col2:
    if st.button("Create Funding Draft", use_container_width = True, type = "primary"):
        st.switch_page("pages/15_create_funding_draft.py")
    st.write("Propose a new funding plan")

with col3:
    if st.button("My Funding Drafts", use_container_width = True, type = "primary"):
        st.switch_page("pages/13_funding_drafts.py")
    st.write("View and manage your drafts")

st.divider()

col4, col5 = st.columns(2)

with col4:
    if st.button("Housing Deprivation Predictor", use_container_width = True, type = "primary"):
        st.switch_page("pages/14_government_pred.py")
    st.write("ML-based housing risk predictions")

with col5:
    if st.button("Risk Heatmap", use_container_width = True, type = "primary"):
        st.switch_page("pages/12_risk_heatmap.py")
    st.write("Map social risk by country")