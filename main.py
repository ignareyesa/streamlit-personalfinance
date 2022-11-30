import pandas as pd  
import streamlit as st  
import streamlit_authenticator as stauth  
import yaml
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, add_page_title, show_pages


try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="streamlit Dashboard", page_icon=":bar_chart:", layout="wide")


show_pages(
    [
        Page("main.py", "Home", ""),
        Page("pages/forgot_pass.py", "", ""),
        Page("pages/sign_up.py", "   ", ""),        
    ]
)

# hashed_passwords = stauth.Hasher(['123', '456']).generate()
# print(hashed_passwords)

with open('config.yaml') as file:
    config = yaml.load(file, Loader=Loader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('Welcome!', 'main')


if st.session_state["authentication_status"]:
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
    forgot_pass = None
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] == None:
    forgot_pass = st.button("Forgot password?")
    signup = st.button("New user? Sign up")
    if forgot_pass:
        switch_page("")
    if signup:
        switch_page("   ")




def logged_in(session_state = st.session_state):
    if session_state["authentication_status"]:
        return True