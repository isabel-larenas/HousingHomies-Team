import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(page_title="Real Estate Agent Home", layout = 'wide')
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
st.text("This is your Real Estate Agent Dashboard. What would you like to do today?")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True, height=320):
        st.subheader("📈 Market Dashboard")
        st.write("Explore European housing market trends.")
        if st.button("View Market Dashboard", use_container_width=True, type="primary"):
            st.switch_page("pages/06_market_dashboard.py")

with col2:
    with st.container(border=True, height=320):
        st.subheader("🏘️ View Listings")
        st.write("View and manage your listings.")
        if st.button("View Listings", use_container_width=True, type="primary"):
            st.switch_page("pages/07_view_listings_rea.py")

with col3:
    with st.container(border=True, height=320):
        st.subheader("📄 Create Listing")
        st.write("Add a new property listing.")
        if st.button("Create a New Listing", use_container_width=True, type="primary"):
            st.switch_page("pages/08_add_listing.py")
