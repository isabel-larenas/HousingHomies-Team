import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout = 'wide')
SideBarLinks()

if st.session_state.get("draft_saved"):
    st.success("Draft updated successfully!")
    st.session_state["draft_saved"] = False

if st.session_state.get("draft_deleted"):
    st.success("Draft deleted successfully!")
    st.session_state["draft_deleted"] = False

st.title("My Funding Drafts")
st.caption("View, update, or delete your proposed funding plans.")

BASE = "http://web-api:4000/housing"

#Get drafts for the current user
try:
    user_id = st.session_state.get("user_id")
    r = requests.get(f"{BASE}/funding-draft", params = {"user_id": user_id})
    drafts = r.json() if r.status_code == 200 else []
except Exception as e:
    st.error(f"Error fetching drafts: {e}")
    drafts = []

if not drafts:
    st.info("No funding drafts found.")
    if st.button("Create a Funding Draft", type = "primary"):
        st.session_state["scroll_to_draft"] = True
        st.switch_page("pages/11_view_funding.py")

else:
    for draft in drafts:
        with st.container(border = True):
            col1, col2 = st.columns([4, 1])

            with col1:
                st.subheader(draft.get("program", "Unnamed Program"))
                st.caption(f"{draft.get('country_name', '')} — €{float(draft.get('amount', 0)):,.0f}")
                st.write(f"**Indicators:** {draft.get('indicators_targeted', '')}")
                st.write(f"**Demographics:** {draft.get('demographics_targeted', '')}")
                st.write(f"**Description:** {draft.get('description', '')}")

            with col2:
                draft_id = draft.get("draft_id")

                if st.button("Delete", key = f"delete_{draft_id}", type = "secondary"):
                    try:
                        res = requests.delete(f"{BASE}/funding-draft/{draft_id}")
                        if res.status_code == 200:
                            st.session_state["draft_deleted"] = True
                            st.rerun()
                        else:
                            st.error("Failed to delete.")
                    except Exception as e:
                        st.error(f"Error: {e}")

                if st.button("Edit", key = f"edit_{draft_id}"):
                    st.session_state[f"editing_{draft_id}"] = True

            if st.session_state.get(f"editing_{draft_id}"):
                with st.form(key = f"form_{draft_id}"):
                    new_program = st.text_input("Program Name", value = draft.get("program", ""))
                    new_amount = st.number_input("Amount (€)", value = float(draft.get("amount", 0)), min_value = 0.0, step = 1000.0)
                    new_description = st.text_area("Description", value = draft.get("description", ""))
                    new_indicators = st.multiselect(
                        "Indicators Targeted",
                        ["Pollution", "Crime, Violence, and Vandalism",
                        "Poverty", "Overcrowding", "Noise", "House Price Index", "Under-occupied"],
                        default = [i.strip() for i in draft.get("indicators_targeted", "").split(",") if i.strip()]
                    )
                    new_demographics = st.multiselect(
                        "Demographics Targeted",
                        ["Students", "Low Income", "Elderly", "Families"],
                        default = [d.strip() for d in draft.get("demographics_targeted", "").split(",") if d.strip()]
                    )
                    save = st.form_submit_button("Save Changes")
                    cancel = st.form_submit_button("Cancel")

                    if save:
                        try:
                            payload = {
                                "program": new_program,
                                "amount": new_amount,
                                "description": new_description,
                                "indicators_targeted": ", ".join(new_indicators),
                                "demographics_targeted": ", ".join(new_demographics)
                            }
                            res = requests.put(f"{BASE}/funding-draft/{draft_id}", json = payload)
                            if res.status_code == 200:
                                st.session_state[f"editing_{draft_id}"] = False
                                st.session_state["draft_saved"] = True
                                st.rerun()
                            else:
                                st.error("Failed to update.")
                        except Exception as e:
                            st.error(f"Error: {e}")

                    if cancel:
                        st.session_state[f"editing_{draft_id}"] = False
                        st.rerun()