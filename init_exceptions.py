import streamlit as st
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from init_app import set_connection, fetchall, kill_slept_connections


with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

db = set_connection(retry=True)
kill_slept_connections(retry=True)
users = fetchall("SELECT * from users;", retry=True)
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
# email_client = set_smtp_connection(retry=True)


def if_reconnect():
    """
    Checks whether the page is working properly
    If the not field is not present in the
    `st.session_state` object, the function sets the default
    values for several fields in the `st.session_state` object.

    Args:
        session_state (State): The `st.session_state` object to check.

    Returns:
        bool: Whether the user is logged in or not.
    """
    try:
        if st.session_state["authenticator"]:
            return
    except KeyError:
        st.session_state["authenticator"] = authenticator
        st.session_state["db"] = db
        # st.session_state["email_client"] = email_client
        st.session_state["credentials"] =  credentials

