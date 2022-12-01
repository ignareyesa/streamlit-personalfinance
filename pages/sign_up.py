from main import logged_in, authenticator, credentials, commit_query, run_query
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

if logged_in():
    st.warning("You are already log-in")
    st.stop()  # App won't run anything after this line

try:
    if authenticator.register_user('Register user', preauthorization=False):
        key = list(credentials["usernames"])[-1]
        form_input = credentials["usernames"][key]
        query = f"""INSERT INTO users (email, username, name, pass) VALUES
                {form_input["email"],key,form_input["name"], form_input["password"]}
                """
        results = commit_query(query)
        st.success('User registered successfully')
        users = run_query("SELECT * from users")
        credentials = {"usernames": {i[2]:{"email":i[1],"name":i[3],"password":i[4]} for i in users}}
        print(credentials)       
except Exception as e:
    if "1062 (23000)" in str(e):
        st.error("Email already taken")
    else:
        st.error(e)

signin = st.button("Already register? Sign in")
if signin:
    switch_page("Home")
    