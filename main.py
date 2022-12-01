import pandas as pd  
import streamlit as st  
import mysql.connector
import streamlit_authenticator as stauth  
import yaml
from streamlit_extras.switch_page_button import switch_page
from st_pages import Page, show_pages
from yaml import CLoader as Loader




# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="streamlit Dashboard", page_icon=":bar_chart:", layout="wide")
# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

# Perform query.
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        all = cur.fetchall()
        cur.close()
        return all
        
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
def commit_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()
        cur.close()

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
try:
    from pages.sign_up import credentials
    credentials = credentials
except:
    users = run_query("SELECT * from users;")
    credentials = {"usernames": {i[2]:{"email":i[1],"name":i[3],"password":i[4]} for i in users}}
authenticator = stauth.Authenticate(
    credentials,
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


name, authentication_status, username = authenticator.login('Welcome!', 'main')

print(credentials)
if st.session_state["authentication_status"]:
    
    authenticator.logout('Logout', 'sidebar')
    st.write(f'Welcome *{st.session_state["name"]}*')
    st.title('Some content')
    rows = run_query("SELECT * from users;")
    print(rows)

    # Print results.
    for row in rows:
        st.write(f"{row[0]} has a :{row[1]}:")
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')
    forgot_pass = st.button("Forgot password?")
    signup = st.button("New user? Sign up")
    if forgot_pass:
        switch_page("")
    if signup:
        switch_page("   ")
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