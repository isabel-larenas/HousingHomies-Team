import streamlit as st
from modules.nav import SideBarLinks
from pathlib import Path
from PIL import Image



st.set_page_config(layout='wide')

SideBarLinks(show_home = True)

st.write("# About EuroHome")

st.markdown(
    """
    EuroHome is a data platform helping students, real estate agents, 
    and government agencies navigate EU housing markets. Students can 
    research listings and plan their budget, real estate agents can find 
    properties and post listings, and government agencies/project managers
    can explore funding projects with Eurostat data to help propose 
    funding plan drafts. 
    """
)

st.write("# About the team")
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True, height = 850):
        img_path = Path(__file__).parent.parent / "assets" / "geo-headshot.jpg"
        st.image(str(img_path))
        st.write("##### Geo Thatch")

        st.write('Geo is an incoming sophomore at Northeastern University studying ' \
        'Computer Science and Mathematics. Currently taking CS 3200 and CS 4973.')
    
    with st.container(border=True, height = 850):
        img_path = Path(__file__).parent.parent / "assets" / "isabel-headshot.jpeg"
        st.image(str(img_path))
        st.write("##### Isabel Larenas")
        st.write('Isabel is an incoming junior at Northeastern University majoring in ' \
        'Computer Science with a minor in Spanish. Currently taking DS 3000 and CS 4973.')

with col2:
    with st.container(border=True, height = 850):
        img_path = Path(__file__).parent.parent / "assets" / "maira-headshot.png"
        st.image(str(img_path))
        st.write("##### Maira Padani")
        st.write('Maira is an incoming senior at Northeastern University majoring in ' \
        'Business Administration with a minor in Data Science. Currently taking CS 3200 and CS 4973.')

    with st.container(border=True, height = 850):
        img_path = Path(__file__).parent.parent / "assets" / "laasya-headshot.jpeg"
        st.image(str(img_path))
        st.write("##### Laasya Gattu")
        st.write('Laasya is an incoming sophomore at Northeastern University majoring in ' \
        'Data Science and Business Administration with a minor in Public Health. Currently taking DS 3000 and CS 4973.')
