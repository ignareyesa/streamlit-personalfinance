import streamlit as st
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from init_app import run_predefined_queries, set_connection, set_smtp_connection, fetchall



with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

db = set_connection(retry=True)
st.session_state["db"] = db


run_predefined_queries(retry=True)

users = fetchall("SELECT * from users;", retry=True)
credentials = {
    "usernames": {i[2]: {"email": i[1], "name": i[3], "password": i[4]} for i in users}
}
st.session_state["credentials"] = credentials 

authenticator = stauth.Authenticate(
    credentials,
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)
st.session_state["authenticator"] = authenticator

email_client = set_smtp_connection()
st.session_state["email_client"] = email_client 
