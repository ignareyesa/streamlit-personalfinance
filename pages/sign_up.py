from main import logged_in, authenticator
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

if logged_in():
    st.warning("You are already log-in")
    st.stop()  # App won't run anything after this line

try:
    if authenticator.register_user('Register user', preauthorization=False):
        st.success('User registered successfully')
except Exception as e:
    st.error(e)

signin = st.button("Already register? Sign in")
if signin:
    switch_page("Home")
    