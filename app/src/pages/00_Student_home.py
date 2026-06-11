import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Student Home", layout = 'wide')
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
st.text("Student Dashboard")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View Listings", use_container_width = True, type = "primary"):
        st.switch_page("pages/01_view_listings_student.py")
    st.write("Browse available EU housing listings")

with col2:
    if st.button("View Saved Listings", use_container_width = True, type = "primary"):
        st.switch_page("pages/02_view_saved_listings.py")
    st.write("View your saved housing listings")

with col3:
    if st.button("Housing Satisfaction Predictor", use_container_width = True, type = "primary"):
        st.switch_page("pages/04_student_pred.py")
    st.write("Predict your housing satisfaction score")