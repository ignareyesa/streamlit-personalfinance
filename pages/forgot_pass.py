from main import logged_in, authenticator
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page




if not logged_in():
    st.warning("You must log-in to see the content of this sensitive page! Head over to the log-in page.")
    signin = st.button("Back to log in")
    if signin:
            switch_page("Home")
    st.stop()  # App won't run anything after this line

try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Forgot password')
        if username_forgot_pw:
            st.success('New password sent securely')
            # Random password to be transferred to user securely
        elif username_forgot_pw == False:
            st.error('Username not found')
except Exception as e:
        st.error(e)