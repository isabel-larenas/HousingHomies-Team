import logging
logger = logging.getLogger(__name__)
import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(page_title="View Saved Listings", layout='wide')
SideBarLinks()

st.header('Saved Listings')

user_id = st.session_state.get('user_id')
if not user_id:
    st.warning("Please log in to view your saved listings.")
    st.stop()

favorites = requests.get('http://web-api:4000/listing/favorites', 
                         params={"user_id": user_id})

if not favorites:
    st.info("You haven't saved any listings yet.")
    st.stop()

for listing in favorites:
    
    reviews = requests.get('http://web-api:4000/listing/reviews',
                           params={"listing_id": listing['listing_id']}).json()
    total, num = 0, 0
    for review in reviews:
        if review['rating'] is not None:
            total += int(review['rating'])
            num += 1
    avg = round(total / num, 2) if num > 0 else None

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(listing['title'])
        with col2:
            if avg:
                st.subheader(f'⭐ {avg}/5.0')

        col1, col2, col3 = st.columns([3, 3, 2])

        with col1:
            st.write(f"📍 {listing['city_name']}, {listing['country_name']}")
            st.write(f"🏠 {listing['property_type']}")
            if listing.get('university_name'):
                st.write(f"🎓 {listing['university_name']}")

        with col2:
            st.subheader(f"€{int(listing['price']):,} / month")

        with col3:
            if st.button("View reviews", key=f"reviews_{listing['listing_id']}"):
                st.session_state['listing_id'] = listing['listing_id']
                st.session_state['title'] = listing['title']
                st.switch_page('pages/03_view_reviews.py')

            if st.button("🗑 Remove", key=f"remove_{listing['listing_id']}"):
                requests.delete('http://web-api:4000/listing/favorites', json={
                    "listing_id": listing['listing_id'],
                    "user_id": user_id
                })
                st.rerun()

    st.write("")