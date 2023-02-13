import json
import streamlit as st
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from database_connection.database import Database
from smtp_connection.email_client import EmailClient

with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

with open("predefined_queries.json") as file:
    json_loads = json.load(file)
    predefine_queries = list(json_loads.values())

# Create an instance of the Database class
db = Database(**st.secrets["mysql-dev"])

#Connect to the database
@st.cache_resource
def set_connection():
    db.connect()
    return db

db = set_connection()
st.session_state["db"] = db

# Commit predefined queries
@st.cache_data
def run_predefined_queries():
    for query in predefine_queries:
        try:
            db.commit(query)
        except Exception as e:
            raise ValueError(
                "Something went wrong during first connection to database: ", e)

run_predefined_queries()


@st.cache_data
def fetchall(query, params=None):
    return db.fetchall(query, params)

users = fetchall("SELECT * from users;")
credentials = {
    "usernames": {i[2]: {"email": i[1], "name": i[3], "password": i[4]} for i in users}
}
authenticator = stauth.Authenticate(
    credentials,
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)
st.session_state["authenticator"] = authenticator

smtp_connection = st.secrets["smtp_connection"]
smtp_server = smtp_connection["SMTP_SERVER"]
smtp_port = smtp_connection["SMTP_PORT"]
smtp_username = smtp_connection["SMTP_API_NAME"]
smtp_password = smtp_connection["SMTP_API_KEY"]
smtp_from_addr = smtp_connection["SMTP_FROM_ADDRESS"]
smtp_from_name = smtp_connection["SMTP_FROM_NAME"]

@st.cache_resource
def set_smtp_connection():
    return EmailClient(
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        username=smtp_username,
        password=smtp_password,
        from_addr=smtp_from_addr,
        from_name=smtp_from_name,
    )

email_client = set_smtp_connection()
st.session_state["email_client"] = email_client 

