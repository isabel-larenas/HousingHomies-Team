##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
import requests
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(page_title="Home", layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************

logger.info("Loading the Home page of the app")

#st.title('EuroHome')



st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700&display=swap');
        @keyframes dropIn {
            from { transform: translateY(-150px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        @keyframes slideLeft {
            from { transform: translateX(-150px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideRight {
            from { transform: translateX(150px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes bounceIn {
            0% { transform: translateY(-80px); opacity: 0; }
            60% { transform: translateY(15px); opacity: 1; }
            80% { transform: translateY(-8px); }
            100% { transform: translateY(0); opacity: 1; }
        }
        .title-container { display: flex; justify-content: center; align-items: center; margin: 2rem 0; }
        .title-container span { font-family: 'Cinzel', serif; font-size: 4rem; font-weight: 700; color: #1D3461; opacity: 0; display: inline-block; }
        .ur  { animation: slideLeft  1s ease 1.2s   forwards; }
        .hm  { animation: slideRight 1s ease 1.2s   forwards; }
        .e   { animation: dropIn    1.2s ease 1.8s   forwards; }
        .o   { animation: dropIn    1.2s ease 1.8s   forwards; }
        .ico { animation: bounceIn  0.8s ease 3.2s forwards; margin-left: 16px; }
    </style>
    <div class="title-container">
        <span class="e">E</span>
        <span class="ur">ur</span>
        <span class="o">o</span>
        <span class="hm">Home</span>
        <span class="ico">
            <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" viewBox="0 0 24 24" fill="#1D3461">
                <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
            </svg>
        </span>
    </div>
""", unsafe_allow_html = True)



st.write('###### Welcome to EuroHome! Eurohome is a web-app designed to help ' \
'students, real estate agents, and government agencies ' \
'with all aspects of the housing market in the EU. Users can view available listings, manage their budgets,'
' and predict housing satisfaction based on their preferences. ' \
    'Our goal is to make the housing market more transparent and accessible for everyone.')
st.write('#### Select a user to log in as')


# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.

col1, col2, col3 = st.columns(3)

#retrieve full list of students
response_students = requests.get('http://web-api:4000/housing/user', params={'role': 'Student'})
students = response_students.json()

#dropdown menu
with col1:
    with st.container(border=True, height=350):
        st.subheader('Student 🧑‍🎓')
        st.write('')
        st.write('')
        st.write('')
        st.write('')

        student_options = {f"{s['name']}": s for s in sorted(students, key=lambda s: s['name'].split()[-1])}
        selected_name_student = st.selectbox('Select a user', options=list(student_options.keys()),index=None,
                                    placeholder="Select user", label_visibility='collapsed')
        student_login = st.button("Login", type='primary', use_container_width=True, key='student')



if student_login:
    if selected_name_student is None:
        st.error('Please select a user')

    else:
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'Student'
        st.session_state['name'] = student_options[selected_name_student]['name']
        st.session_state['user_id'] = student_options[selected_name_student]['user_id']
        logger.info("Logging in as Student Persona")
        st.switch_page('pages/00_Student_home.py')
    st.write("")


#retrieve full list of real estate agents
response_agents_re = requests.get('http://web-api:4000/housing/user', 
                                  params={'role': 'Real Estate Agent'})
re_agents = response_agents_re.json()

#dropdown menu
with col2:
    with st.container(border=True, height=350):
        st.subheader('Real Estate Agent 🏠')
        st.write('')
        st.write('')

        agent_options_re = {f"{s['name']}": s for s in sorted(re_agents, key=lambda s: s['name'].split()[-1])}
        selected_name_agent_re = st.selectbox('Select a user', options=list(agent_options_re.keys()),index=None,
                                    placeholder="Select user", label_visibility='collapsed')
        rea_login = st.button('Login', type='primary', use_container_width=True,key='rea')


if rea_login:
    if selected_name_agent_re is None:
        st.error('Please select a user')
    else:
        #first_name = response from dropdown menu
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'Real Estate Agent'
        st.session_state['name'] = agent_options_re[selected_name_agent_re]['name']
        st.session_state['user_id'] = agent_options_re[selected_name_agent_re]['user_id']
        st.switch_page('pages/05_REA_agent_home.py')

    st.write("")


#retrieve full list of real estate agents
response_ga = requests.get('http://web-api:4000/housing/user', params={'role': 'Government Agency'})
agents_ga = response_ga.json()

# #dropdown menu
with col3:
    with st.container(border=True, height = 350):
        st.subheader('Government Agency Manager 🇪🇺')
        agent_options_ga = {f"{s['name']}": s for s in sorted(agents_ga, key=lambda s: s['name'].split()[-1])}
        selected_name_ga = st.selectbox('Select a user', options=list(agent_options_ga.keys()),index=None,
                                    placeholder="Select user", label_visibility='collapsed')
        ga_login = st.button('Login', type='primary', use_container_width=True, key= 'ga')


if ga_login:
    if selected_name_ga is None:
        st.error('Please select a user')
    else:
        #first_name = response from dropdown menu
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'Government Agency'
        st.session_state['name'] = agent_options_ga[selected_name_ga]['name']
        st.session_state['user_id'] = agent_options_ga[selected_name_ga]['user_id']
        st.switch_page('pages/10_GA_home.py')

response_students = requests.get('http://web-api:4000/housing/user', params={'role': 'Student'})
logger.info(f"STATUS: {response_students.status_code}, BODY: {response_students.text}")

if response_students.status_code == 200:
    students = response_students.json()
else:
    students = []
    st.error(f"Failed to load students: {response_students.text}")
