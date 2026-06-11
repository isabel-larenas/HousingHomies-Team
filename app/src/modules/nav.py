# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: student ------------------------------------------------
def student_home_nav():
    st.sidebar.page_link(
        "pages/00_Student_home.py", label="Student Home", icon="🧑‍🎓"
    )

def view_listings_nav():
    st.sidebar.page_link(
        "pages/01_view_listings_student.py", label="View Listings", icon="🏘️"
    )

def view_saved_listings_nav():
    st.sidebar.page_link(
        "pages/02_view_saved_listings.py", label="View Saved Listings", icon="❤️")

def housing_satisfaction_pred_nav():
    st.sidebar.page_link("pages/04_student_pred.py", label="Housing Satisfaction Predictor", icon="😌")


# ---- Role: Government Agency -----------------------------------------------------

def government_agency_home_nav():
    st.sidebar.page_link(
        "pages/10_GA_home.py", label="Government Agency Home", icon="🇪🇺"
    )

def view_funding_nav():
    st.sidebar.page_link("pages/11_view_funding.py", label="View Funding", icon="💶")

def funding_drafts_nav():
    st.sidebar.page_link("pages/13_funding_drafts.py", label="My Funding Drafts", icon="📝")

def funding_draft_create_nav():
    st.sidebar.page_link("pages/15_create_funding_draft.py", label="Create Funding Draft", icon="✍️")

def risk_heatmap_nav():
    st.sidebar.page_link("pages/12_risk_heatmap.py", label="Risk Heatmap", icon="🗺️")

def housing_deprivation_pred_nav():
    st.sidebar.page_link("pages/14_government_pred.py", label="Housing Deprivation Predictor", icon="🏚️")


# ---- Role: real estate agent ----------------------------------------------------

def real_estate_agent_home_nav():
    st.sidebar.page_link("pages/05_REA_agent_home.py", label="Real Estate Agent Home", icon="🏠")


def market_dashboard_nav():
    st.sidebar.page_link(
        "pages/06_market_dashboard.py", label="Market Dashboard", icon="📈"
    )

def view_listings_rea_nav():
    st.sidebar.page_link(
        "pages/07_view_listings_rea.py", label="View Listings", icon="🏘️"
    )

def add_listings_rea_nav():
    st.sidebar.page_link(
        "pages/08_add_listing.py", label="Create or Edit Listing", icon="📄"
    )

# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/LogoNew.png", width=300)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    if show_home:
        home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "Student":
            student_home_nav()
            view_listings_nav()
            view_saved_listings_nav()
            housing_satisfaction_pred_nav()

        if st.session_state["role"] == "Real Estate Agent":
            real_estate_agent_home_nav()
            market_dashboard_nav()
            view_listings_rea_nav()
            add_listings_rea_nav()

        if st.session_state["role"] == "Government Agency":
            government_agency_home_nav()
            view_funding_nav()
            funding_drafts_nav()
            funding_draft_create_nav()
            risk_heatmap_nav()
            housing_deprivation_pred_nav()
            

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
