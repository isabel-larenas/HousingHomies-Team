import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Student Home", layout = 'wide')
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
st.write("This is your Student Dashboard. What would you like to do today?")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True, height=320):
        st.subheader("🏘️ View Listings")
        st.write("Browse available EU housing listings filtered by country, city, price, and more.")
        if st.button("View Listings", use_container_width=True, type="primary"):
            st.switch_page("pages/01_view_listings_student.py")

with col2:
    with st.container(border=True, height=320):
        st.subheader("❤️ My Listings")
        st.write("View and manage the housing listings you've saved.")
        if st.button("View Saved Listings", use_container_width=True, type="primary"):
            st.switch_page("pages/02_view_saved_listings.py")

with col3:
    with st.container(border=True, height=320):
        st.subheader("😌 Predict")
        st.write("Predict your housing satisfaction score based on location factors.")
        if st.button("Housing Satisfaction Predictor", use_container_width=True, type="primary"):
            st.switch_page("pages/04_student_pred.py")