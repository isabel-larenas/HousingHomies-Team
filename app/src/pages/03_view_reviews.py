import logging
logger = logging.getLogger(__name__)
import pandas as pd
import streamlit as st
import world_bank_data as wb
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

listing_id = st.session_state.get("listing_id")
listing_title = st.session_state.get("title")

# Call the SideBarLinks from the nav module in the modules directory
SideBarLinks()

# set the header of the page
st.header(f'Reviews on \'{listing_title}\'')

# You can access the session state to make a more customized/personalized app experience
# get a list of all countries
reviews = requests.get(
    f'http://web-api:4000/housing/reviews?listing_id={listing_id}').json()

if st.button('Return to listings'):
    if st.session_state["role"] == "Real Estate Agent":
        st.switch_page('pages/07_view_listings_rea.py')
    if st.session_state["role"] == "Student":
        st.switch_page('pages/01_view_listings_student.py')


for review in reviews:
    
    if review['rating'] is None:
        with st.container(border=True):
            st.write(f"'{review['comment']}'")
    else:
        with st.container(border=True):
            col1, col2, col3 = st.columns([15, 2,2])

            with col1:
                st.write(f"'{review['comment']}'")
            with col2:
                if review['rating'] == 1:
                    st.write("⭐")
                elif review['rating'] == 2:
                    st.write("⭐⭐")
                elif review['rating'] == 3:
                    st.write("⭐⭐⭐")
                elif review['rating'] == 4:
                    st.write("⭐⭐⭐⭐")
                elif review['rating'] == 5:
                    st.write("⭐⭐⭐⭐⭐")
            with col3:
                st.write(f"{review['rating']} / 5")
        


    st.write("")
