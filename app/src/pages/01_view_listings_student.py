import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(page_title="View Listings", layout='wide')
SideBarLinks()

st.header('Available Listings')

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    country_filter = st.selectbox("Country", 
                                options=["All"] + [c['country_name'] for c in 
                                        requests.get('http://web-api:4000/housing/country').json()])
with col2:
    property_filter = st.selectbox("Property Type", 
                                options=["All", "House", "Apartment", "Studio Apartment", "Townhouse"])
with col3:
    price_filter = st.number_input("Max Price (€)", 
                                   min_value=0, max_value=4000, value=4000, step=100)
with col4:
    university_filter = st.selectbox("Associated Uni", 
                                options=["All"] + [u['university_name'] for u 
                                in requests.get('http://web-api:4000/housing/university').json()])
with col5:
    city_filter = st.selectbox("City", options=["All"] + [c['city_name'] for c
                                in requests.get('http://web-api:4000/housing/listing/cities').json()])

params = {}
if country_filter != "All":
    params["country"] = country_filter
if property_filter != "All":
    params["property_type"] = property_filter
if price_filter < 3000:
    params["price"] = price_filter
if city_filter != "All":
    params["city_name"] = city_filter
if university_filter != "All":
    params["university"] = university_filter

listings = requests.get('http://web-api:4000/housing/listing', params=params).json()

if not listings:
    st.info("No listings found.")
else:
    for listing in listings:
        listing['price'] = int(listing['price'])

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])

            with col1:
                st.subheader(listing['title'])

            with col2:
                reviews = requests.get(
                    f"http://web-api:4000/housing/reviews",
                    params={"listing_id": listing['listing_id']}
                ).json()
                total = 0
                num = 0
                for review in reviews:
                    if review['rating'] is not None:
                        total += int(review['rating'])
                        num += 1
                avg = round(total / num, 2) if num > 0 else 0
                if avg > 0:
                    st.subheader(f'{avg}/5.0')
                    stars = "⭐" * round(avg)
                    st.write(stars)

            col1, col2, col3 = st.columns([3, 3, 2])

            with col1:
                st.write(f"📍 {listing['city_name']}, {listing['country_name']}")
                st.write(f"🏠 {listing['property_type']}")
                if listing['university_name']:
                    st.write(f"🏫 Associated with {listing['university_name']}")

            with col2:
                st.subheader(f"€{listing['price']} / month")

            with col3:
                if st.button("View reviews", key=f"listing_{listing['listing_id']}"):
                    st.session_state['listing_id'] = listing['listing_id']
                    st.session_state['title'] = listing['title']
                    st.switch_page('pages/03_view_reviews.py')

                if st.button("Save Listing ❤️", key=f"save_{listing['listing_id']}"):
                    requests.post('http://web-api:4000/housing/favorites', json={
                        "listing_id": listing['listing_id'],
                        "user_id": st.session_state.get('user_id')
                    })
                    st.switch_page('pages/02_view_saved_listings.py')
