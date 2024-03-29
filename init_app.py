import json
import streamlit as st
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from database_connection.database import Database

with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

with open("predefined_queries.json") as file:
    json_loads = json.load(file)
    predefine_queries = list(json_loads.values())

# Create an instance of the Database class
db = Database(**st.secrets["mysql-digitalocean"])

#Connect to the database
@st.cache_resource
def set_connection(retry=False):
    db.connect()
    return db

db = set_connection()
st.session_state["db"] = db

@st.cache_data
def kill_slept_connections(retry=False):
    resultados = db.fetchall("SELECT CONCAT('KILL ', id, ';') FROM INFORMATION_SCHEMA.PROCESSLIST WHERE COMMAND = 'Sleep'")
    for resultado in resultados:
        try:
            db.commit(resultado[0])
        except Exception as e:
            raise ValueError(
                "Something went wrong while killing connections: ", e)

kill_slept_connections()

# Commit predefined queries
@st.cache_data
def run_predefined_queries(retry=False):
    for query in predefine_queries:
        try:
            db.commit(query)
        except Exception as e:
            raise ValueError(
                "Something went wrong during first connection to database: ", e)

run_predefined_queries()


@st.cache_data
def fetchall(query, params=None, retry=False):
    return db.fetchall(query, params)

users = fetchall("SELECT * from users;")
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
