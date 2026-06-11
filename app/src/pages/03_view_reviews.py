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
BASE = "http://web-api:4000/housing"

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
        st.metric("Average Rating", f"{avg} /5.0")
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
    if st.session_state['user_id'] != review['user_id']:
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

st.subheader('My reviews')
my_reviews = 0
for review in reviews:
    if st.session_state['user_id'] == review['user_id']:
        my_reviews += 1
        review_id = review['review_id']
        with st.container(border=True):
            col_main, col_actions = st.columns([5, 1])

            with col_main:
                if review['rating'] is not None:
                    stars = "⭐" * int(review['rating'])
                    st.caption(f"{stars} {review['rating']}/5")
                st.write(review['comment'])

            with col_actions:
                if st.button("✏️", key=f"edit_{review_id}", help="Edit"):
                    st.session_state[f"editing_{review_id}"] = not st.session_state.get(f"editing_{review_id}", False)
                if st.button("🗑️", key=f"delete_{review_id}", help="Delete"):
                    try:
                        res = requests.delete(f"{BASE}/reviews/{review_id}")
                        if res.status_code == 200:
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    except Exception as e:
                        st.error(f"Error: {e}")

            if st.session_state.get(f"editing_{review_id}"):
                include_rating = st.checkbox("Include Rating", key=f"include_{review_id}")
                rating = None
                if include_rating:
                    rating = st.slider("Rating", min_value=1, max_value=5, step=1, key=f"rating_{review_id}")

                with st.form(key=f"form_{review_id}"):
                    comment = st.text_input('Comment', value=review['comment'])
                    save = st.form_submit_button("Save")
                    cancel = st.form_submit_button("Cancel")

                if save:
                    try:
                        res = requests.put(f"{BASE}/reviews/{review_id}", json={"comment": comment, "rating": rating})
                        if res.status_code == 200:
                            st.session_state[f"editing_{review_id}"] = False
                            st.rerun()
                        else:
                            st.error("Failed to update.")
                    except Exception as e:
                        st.error(f"Error: {e}")

                if cancel:
                    st.session_state[f"editing_{review_id}"] = False
                    st.rerun()
            


if my_reviews == 0:
    st.info('You have not reviewed this listing yet')

                


#Add review
st.subheader('Add review')
listing_id = st.session_state["listing_id"]
comment = st.text_input('Comment')
user_id = st.session_state["user_id"]

include_rating = st.checkbox("Include Rating",key='add')
rating = None
if include_rating:
    rating = st.slider("Rating", min_value=1, max_value=5, step=1)


if st.button("Submit Review", type="primary"):
    if not(comment):
        st.warning("Please add a comment.")
    else:
        try:
            payload = {
                "listing_id": listing_id,
                "user_id": user_id,
                "comment": comment,
                "rating": rating
            }
            response = requests.post("http://web-api:4000/housing/reviews", json=payload)
            
            if response.status_code == 201:
                st.success("Listing posted successfully!")
                st.rerun()
            else:
                st.error(f"Error: {response.text}")
        except Exception as e:
            st.error(f"Error: {e}")




st.write("")