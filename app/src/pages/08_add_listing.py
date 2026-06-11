import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks
import plotly.express as px

st.set_page_config(page_title="Create or Edit Listing", layout="wide")

SideBarLinks()


BASE = "http://web-api:4000/housing"

st.title('Add listing')
with st.container(border=True):
    title = st.text_input("Listing Title*")
    city = st.text_input('City*')

    countries_res2 = requests.get("http://web-api:4000/housing/country")
    country_list = countries_res2.json() if countries_res2.status_code == 200 else []
    country_options = {c["country_name"]: c["country_id"] for c in country_list}
    selected_country = st.selectbox("Country*", list(country_options.keys()),index=None,
                                placeholder="Select a country",
                                key="listing_country")

    uni_res2 = requests.get("http://web-api:4000/housing/university", params={"limit":1000})
    uni_list = uni_res2.json() if uni_res2.status_code == 200 else []
    uni_options = {c["university_name"]: c["university_id"] for c in uni_list}
    selected_uni = st.selectbox("University (optional)", ["None"] + list(uni_options.keys()),index = 0, key="associated_uni")

    price = st.slider("Price/Month (€)", min_value=0, max_value=3000, value=1500, step=50)

    property_type = st.selectbox('Property type*', ['Townhouse', 'Studio Apartment', 'Apartment', 'House'],
                                index=None,
                                placeholder="Select property type")

    if st.button("Submit Listing", type="primary"):
        if not(title and price and property_type and city):
            st.warning("Please fill in all required fields.")
        else:
            try:
                payload = {
                    "user_id": st.session_state.get("user_id", 1),
                    "title": title,
                    "country_id": country_options[selected_country],
                    "price": price,
                    "associated_university_id": uni_options.get(selected_uni) if selected_uni != "None" else None,
                    "property_type": property_type,
                    "city_name": city
                }
                response = requests.post("http://web-api:4000/housing/listing", json=payload)
                if response.status_code == 201:
                    st.success("Listing posted successfully!")
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Error: {e}")


#Get listings for the current user
st.subheader('My listings')
try:
    user_id = st.session_state.get("user_id")
    r = requests.get(f"{BASE}/listing", params = {"user_id": user_id})
    my_listings = r.json() if r.status_code == 200 else []
except Exception as e:
    st.error(f"Error fetching drafts: {e}")
    my_listings = []

if not my_listings:
    st.info("No listings found.")

for listing in reversed(my_listings):
    listing['price'] = int(listing['price'])
    listing_id = listing.get("listing_id")


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
            avg = 0
            for review in reviews:
                if review['rating'] is not None:
                    total += int(review['rating'])
                    num +=1
            if num > 0:
                avg = total/num
            avg = round(avg, 2)
            if avg > 0:
                st.subheader(f'{avg}/5.0')

        if listing['university_name']:
            with st.container(border=False):
                col1, col2, col3= st.columns([3, 3, 2])

            with col1:
                st.write(f"📍 {listing['city_name']}, {listing['country_name']}")
                st.write(f"🏠 {listing['property_type']}")
                st.write(f"🏫 Associated with {listing['university_name']}")

            with col2:
                st.subheader(f"€{listing['price']} / month")

            with col3:
                if st.button("View reviews", key=f"listing_{listing['listing_id']}"):
                    st.session_state['listing_id'] = listing['listing_id']
                    st.session_state['title'] = listing['title']
                    st.switch_page('pages/03_view_reviews.py')

            col11, col22 = st.columns([4, 1])

            #Delete button
            with col22:
                if st.button("Delete", key = f"delete_{listing_id}", type = "secondary"):
                    try:
                        res = requests.delete(f"{BASE}/listing/{listing_id}")
                        if res.status_code == 200:
                            st.success("Draft deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    except Exception as e:
                        st.error(f"Error: {e}")



            #Edit button
            with col11:
                if st.button("Edit", key = f"edit_{listing_id}"):
                    st.session_state[f"editing_{listing_id}"] = True

                if st.session_state.get(f"editing_{listing_id}"):
                    with st.form(key = f"form_{listing_id}"):
                        title = st.text_input("Listing Title", value=listing["title"])
                        city = st.text_input('City', value=listing["city_name"])


                        
                        countries_res2 = requests.get("http://web-api:4000/housing/country")
                        country_list = countries_res2.json() if countries_res2.status_code == 200 else []
                        country_options = {c["country_name"]: c["country_id"] for c in country_list}

                        country_keys = list(country_options.keys())
                        country_index = country_keys.index(listing["country_name"]) if listing["country_name"] in country_keys else 0

                        selected_country = st.selectbox("Country", list(country_options.keys()), index=country_index,
                                                                                                key=f"plan_country_{listing_id}")

                        uni_res2 = requests.get("http://web-api:4000/housing/university", params={"limit":1000})
                        uni_list = uni_res2.json() if uni_res2.status_code == 200 else []
                        uni_options = {c["university_name"]: c["university_id"] for c in uni_list}
                        uni_keys = ["None"] + list(uni_options.keys())
                        current_uni = listing.get("university_name")
                        uni_index = uni_keys.index(current_uni) if current_uni and current_uni in uni_keys else 0
                        selected_uni = st.selectbox("University", uni_keys, index=uni_index, key=f"associated_uni_{listing_id}")
                            

                        price = st.slider("Price/Month (€)", min_value=0, max_value=3000, value=listing["price"], step=50, key=f"price_{listing_id}")


                        property_options = ['Townhouse', 'Studio Apartment', 'Apartment', 'House']
                        property_index = property_options.index(listing["property_type"]) if listing["property_type"] in property_options else 0
                        property_type = st.selectbox('Property type', ['Townhouse', 'Studio Apartment', 'Apartment', 'House'], 
                                                    index=property_index, key=f"property_type_{listing_id}")


                        save = st.form_submit_button("Save Changes")
                        cancel = st.form_submit_button("Cancel")

                    if save:
                        try:
                            payload = {
                                "user_id": st.session_state.get("user_id", 1),
                                "title": title,
                                "country_id": country_options[selected_country],
                                "price": price,
                                "associated_university_id": uni_options[selected_uni],
                                "property_type": property_type,
                                "city_name": city
                            }

                            res = requests.put(f"{BASE}/listing/{listing_id}", json = payload)
                            if res.status_code == 200:
                                st.success("Listing updated.")
                                st.session_state[f"editing_{listing_id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to update.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    if cancel:
                        st.session_state[f"editing_{listing_id}"] = False
                        st.rerun()


            st.write("")


        else:
            with st.container(border=False):
                col1, col2, col3 = st.columns([3, 3, 2])

                with col1:
                    st.write(f"📍 {listing['city_name']}, {listing['country_name']}")
                    st.write(f"🏠 {listing['property_type']}")

                with col2:
                    st.subheader(f"€{listing['price']} / month")
                
                with col3:
                    if st.button("View reviews", key=f"listing_{listing['listing_id']}"):
                        st.session_state['listing_id'] = listing['listing_id']
                        st.session_state['title'] = listing['title']
                        st.switch_page('pages/03_view_reviews.py')
            
            st.divider()
            col11, col22 = st.columns([4, 1])

            #Delete button
            with col22:
                if st.button("Delete", key = f"delete_{listing_id}", type = "secondary"):
                    try:
                        res = requests.delete(f"{BASE}/listing/{listing_id}")
                        if res.status_code == 200:
                            st.success("Draft deleted.")
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    except Exception as e:
                        st.error(f"Error: {e}")



            #Edit button
            with col11:
                if st.button("Edit", key = f"edit_{listing_id}"):
                    st.session_state[f"editing_{listing_id}"] = True

                if st.session_state.get(f"editing_{listing_id}"):
                    with st.form(key = f"form_{listing_id}"):
                        title = st.text_input("Listing Title", value=listing["title"])
                        city = st.text_input('City', value=listing["city_name"])
                        
                        countries_res2 = requests.get("http://web-api:4000/housing/country")
                        country_list = countries_res2.json() if countries_res2.status_code == 200 else []
                        country_options = {c["country_name"]: c["country_id"] for c in country_list}

                        country_keys = list(country_options.keys())
                        country_index = country_keys.index(listing["country_name"]) if listing["country_name"] in country_keys else 0

                        selected_country = st.selectbox("Country", list(country_options.keys()), index=country_index,
                                                                                                key=f"plan_country_{listing_id}")

                        uni_res2 = requests.get("http://web-api:4000/housing/university", params={"limit":1000})
                        uni_list = uni_res2.json() if uni_res2.status_code == 200 else []
                        uni_options = {c["university_name"]: c["university_id"] for c in uni_list}
                        uni_keys = ["None"] + list(uni_options.keys())
                        current_uni = listing.get("university_name")
                        uni_index = uni_keys.index(current_uni) if current_uni and current_uni in uni_keys else 0
                        selected_uni = st.selectbox("University", uni_keys, index=uni_index, key=f"associated_uni_{listing_id}")

                        price = st.slider("Price/Month (€)", min_value=0, max_value=3000, value=listing["price"], step=50, key=f"price_{listing_id}")

                        property_options = ['Townhouse', 'Studio Apartment', 'Apartment', 'House']
                        property_index = property_options.index(listing["property_type"]) if listing["property_type"] in property_options else 0
                        property_type = st.selectbox('Property type', ['Townhouse', 'Studio Apartment', 'Apartment', 'House'], 
                                                    index=property_index, key=f"property_type_{listing_id}")


                        save = st.form_submit_button("Save Changes")
                        cancel = st.form_submit_button("Cancel")

                    if save:
                        try:
                            payload = {
                                "user_id": st.session_state.get("user_id", 1),
                                "title": title,
                                "country_id": country_options[selected_country],
                                "price": price,
                                "associated_university_id": uni_options.get(selected_uni) if selected_uni != "None" else None,
                                "property_type": property_type,
                                "city_name": city
                            }

                            res = requests.put(f"{BASE}/listing/{listing_id}", json = payload)
                            if res.status_code == 200:
                                st.success("Listing updated.")
                                st.session_state[f"editing_{listing_id}"] = False
                                st.rerun()
                            else:
                                st.error("Failed to update.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    if cancel:
                        st.session_state[f"editing_{listing_id}"] = False
                        st.rerun()


            st.write("")


