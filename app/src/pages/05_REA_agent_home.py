import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')
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
st.text("Real Estate Agent Dashboard")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("View Market Dashboard", use_container_width = True, type = "primary"):
        st.switch_page("pages/06_market_dashboard.py")
    st.write("Explore EU housing market trends")

with col2:
    if st.button("View Listings", use_container_width = True, type = "primary"):
        st.switch_page("pages/07_view_listings_rea.py")
    st.write("Browse and manage your listings")

with col3:
    if st.button("Create Listing", use_container_width = True, type = "primary"):
        st.switch_page("pages/08_add_listing.py")
    st.write("Add a new property listing")