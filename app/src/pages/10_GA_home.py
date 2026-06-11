import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Government Agency Home", layout = 'wide')
SideBarLinks()

st.markdown("""
    <style>
    section[data-testid="stMainBlockContainer"] div[data-testid="stButton"] button {
        height: 90px;
        font-size: 20px;
        font-weight: 600;
        border-radius: 12px;
    }
    </style>
""", unsafe_allow_html=True)

st.title(f"Welcome, {st.session_state['name']}.")
st.write("This is your Government Agency Dashboard. What would you like to do today?")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True, height=300):
        st.markdown("<h3 style='text-align: center; font-size: 28px;'>💶 View Funding</h3>", unsafe_allow_html=True)
        st.write("Browse existing European housing funding programs.")
        if st.button("View Funding", use_container_width=True, type="primary"):
            st.switch_page("pages/11_view_funding.py")

with col2:
    with st.container(border=True, height=300):
        st.markdown("<h3 style='text-align: center; font-size: 28px;'>✍️ Create Funding Draft</h3>", unsafe_allow_html=True)
        st.write("Propose a new funding program draft.")
        if st.button("Create Funding Draft", use_container_width=True, type="primary"):
            st.switch_page("pages/15_create_funding_draft.py")

with col3:
    with st.container(border=True, height=300):
        st.markdown("<h3 style='text-align: center; font-size: 28px;'>📝 My Funding Drafts</h3>", unsafe_allow_html=True)
        st.write("View and manage your funding drafts.")
        if st.button("My Funding Drafts", use_container_width=True, type="primary"):
            st.switch_page("pages/13_funding_drafts.py")



col4, col5 = st.columns(2)

with col4:
     with st.container(border=True, height=260):
        st.markdown("<h3 style='text-align: center; font-size: 28px;'>🗺️ Risk Heatmap</h3>", unsafe_allow_html=True)
        st.write("View social indicator risk maps and compare countries.")
        if st.button("Risk Heatmap", use_container_width = True, type = "primary"):
            st.switch_page("pages/12_risk_heatmap.py")

with col5:
    with st.container(border=True, height=260):
        st.markdown("<h3 style='text-align: center; font-size: 28px;'>🏚️ Deprivation Predictor</h3>", unsafe_allow_html=True)
        st.write("View ML-based predictions on housing deprivation risk.")
        if st.button("Housing Deprivation Predictor", use_container_width = True, type = "primary"):
            st.switch_page("pages/14_government_pred.py")