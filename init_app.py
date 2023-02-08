# import mysql.connector
import json
import streamlit as st
import os
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from dotenv import load_dotenv
from database_connection.database import Database
from smtp_connection.email_client import EmailClient

load_dotenv()

st.set_page_config(page_title="Tus finanzas", page_icon="🐍", layout="wide")

with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

with open("predefined_queries.json") as file:
    json_loads = json.load(file)
    predefine_queries = list(json_loads.values())

# Create an instance of the Database class
db = Database(**st.secrets["mysql-dev"])

# Connect to the database
connection = db.connect()

# Commit predefined queries
for query in predefine_queries:
    try:
        db.commit(query)
    except Exception as e:
        raise ValueError(
            "Something went wrong during first connection to database: ", e)

users = db.fetchall("SELECT * from users;")
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


# smtp_server = os.getenv("SMTP_SERVER")
# smtp_port = os.getenv("SMTP_PORT")
# smtp_username = os.getenv("SMTP_API_NAME")
# smtp_password = os.getenv("SMTP_API_KEY")
# smtp_from_addr = os.getenv("SMTP_FROM_ADDRESS")
# smtp_from_name = os.getenv("SMTP_FROM_NAME")

# email_client = EmailClient(
#     smtp_server=smtp_server,
#     smtp_port=smtp_port,
#     username=smtp_username,
#     password=smtp_password,
#     from_addr=smtp_from_addr,
#     from_name=smtp_from_name,
# )