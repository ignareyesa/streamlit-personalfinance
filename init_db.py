import mysql.connector
import json
import streamlit as st
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
import os
from dotenv import load_dotenv
from smtp_connection.email_client import EmailClient

load_dotenv()

st.set_page_config(page_title="Tus finanzas", page_icon="🐍", layout="wide")

with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

with open("predefined_queries.json") as file:
    json_loads = json.load(file)
    predefine_queries = list(json_loads.values())

# Initialize connection.
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])


# Run Query
def run_query(query: str, params=None) -> list:
    """
    Takes a SQL query as input and executes it using the `cur` cursor.
    If the query contains placeholders for parameters, the `params` argument
    should be provided to supply the values for the placeholders.
    Returns all the results of the query.

    Args:
        query (str): The query to be executed.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.

    Returns:
        list: The results of the query.
    """
    with conn.cursor() as cur:
        cur.execute(query, params)
        all = cur.fetchall()
        cur.close()
        return all


def commit_query(query: str, params=None):
    """
    Executes the provided query and commits the changes to the database.
    If the query contains placeholders for parameters, the `params` argument
    should be provided to supply the values for the placeholders.

    Args:
        query (str): The query to be executed.
        params (Optional[tuple]): A tuple containing the values for the placeholders in the query.
    """
    with conn.cursor() as cur:
        cur.execute(query, params)
        conn.commit()
        cur.close()


def commit_predefine_queries(queries: list) -> None:
    """
    Takes a list of SQL queries as input and iterates through them,
    executing each query using the `commit_query` function.
    Raises an error if any of the queries fail to execute, and returns
    the result of calling `init_connection` if all queries are executed successfully.
    """
    for query in queries:
        try:
            commit_query(query)
        except Exception as e:
            raise ValueError(
                "Something went wrong during first connection to database: ", e
            )
    return init_connection()


conn = init_connection()
conn = commit_predefine_queries(predefine_queries)


users = run_query("SELECT * from users;")
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


smtp_server = os.getenv("SMTP_SERVER")
smtp_port = os.getenv("SMTP_PORT")
smtp_username = os.getenv("SMTP_API_NAME")
smtp_password = os.getenv("SMTP_API_KEY")
smtp_from_addr = os.getenv("SMTP_FROM_ADDRESS")
smtp_from_name = os.getenv("SMTP_FROM_NAME")

email_client = EmailClient(
    smtp_server=smtp_server,
    smtp_port=smtp_port,
    username=smtp_username,
    password=smtp_password,
    from_addr=smtp_from_addr,
    from_name=smtp_from_name,
)
