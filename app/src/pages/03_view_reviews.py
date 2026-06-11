import logging
logger = logging.getLogger(__name__)
import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(page_title="View Reviews", layout='wide')

listing_id = st.session_state.get("listing_id")
listing_title = st.session_state.get("title")

SideBarLinks()

st.header(f'Reviews on \'{listing_title}\'')

reviews = requests.get(
    f'http://web-api:4000/housing/reviews?listing_id={listing_id}').json()

rated = [r for r in reviews if r['rating'] is not None]
unrated = [r for r in reviews if r['rating'] is None]

if rated:
    total = sum(int(r['rating']) for r in rated)
    avg = round(total / len(rated), 2)
    stars = "⭐" * round(avg)

    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        st.metric("Average Rating", f"{avg} / 5")
    with col2:
        st.metric("Total Reviews", len(reviews))

    st.divider()

if not reviews:
    st.info("No reviews found for this listing.")
    st.stop()

if st.button('Return to listings'):
    if st.session_state["role"] == "Real Estate Agent":
        st.switch_page('pages/07_view_listings_rea.py')
    if st.session_state["role"] == "Student":
        st.switch_page('pages/01_view_listings_student.py')


for review in reviews:
    with st.container(border=True):
        if review['rating'] is not None:
            stars = "⭐" * int(review['rating'])
            col1, col2 = st.columns([5, 1])
            with col1:
                st.write(review['comment'])
            with col2:
                st.write(f"{review['rating']} / 5", stars)
        else:
            st.caption(review['comment'])