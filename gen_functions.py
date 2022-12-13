import streamlit as st
import datetime
import secrets
from st_click_detector import click_detector
from streamlit_extras.switch_page_button import switch_page
from init_db import commit_query, run_query


def load_css_file(css_file_path, as_markdown=True):
    """
    Loads the CSS file from the specified path.
    If the `as_markdown` argument is set to `True`, the function
    returns the CSS code as Markdown. Otherwise, it returns the
    CSS code as a string.

    Args:
        css_file_path (str): The path to the CSS file to be loaded.
        as_markdown (bool): Whether to return the CSS code as Markdown or as a string.

    Returns:
        str: The CSS code from the specified file.
    """
    with open(css_file_path) as f:
        if as_markdown:
            return st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
        else:
            return f"<style>{f.read()}</style>"


# determine is user is logged_in or nor
def logged_in(session_state=st.session_state):
    """
    Checks whether the user is logged in or not by checking the
    `authentication_status` field in the `st.session_state` object.
    If the `authentication_status` field is not present in the
    `st.session_state` object, the function sets the default
    values for several fields in the `st.session_state` object.

    Args:
        session_state (State): The `st.session_state` object to check.

    Returns:
        bool: Whether the user is logged in or not.
    """
    try:
        if session_state["authentication_status"]:
            return True
    except KeyError:
        st.session_state["authentication_status"] = None
        st.session_state["username"] = ""
        st.session_state["logout"] = None
        st.session_state["name"] = None
        st.session_state["init"] = None


def switch_page_button(
    labels: list,
    links,
    html_class: str = "css-1x8cf1d edgvbvh10",
    css: str = "styles/default_buttons.css",
):
    """
    Generates a string of HTML code containing single or multiple buttons
    with the specified labels and links. When a button is clicked,
    the function uses the `switch_page` function from the
    `streamlit_extras` library to switch to the corresponding page.

    Args:
        labels (list): A list of labels for the buttons.
        links (list): A list of links for the buttons.
        html_class (str): The CSS class to be used for the buttons.
        css (str): The path to the CSS file to be used for styling the buttons.

    Raises:
        Exception: If the `labels` and `links` lists have different lengths.

    Returns:
        str: The HTML code for the buttons
    """
    if len(labels) == len(links):
        content = load_css_file(css, as_markdown=False)
        for i, label in enumerate(labels):
            temp_content = (
                f"""<a href="" id="link_{i}" class="{html_class}">{label}</a> """
            )
            content += temp_content
        clicked = click_detector(content)
        for i, link in enumerate(links):
            if clicked == f"link_{i}":
                switch_page(link)
        return content
    else:
        raise Exception("labels and links length must have the same lenght")



def create_temporary_token(table: str):
    """Generates a random token and inserts it into the specified table
    along with the current date and time plus one hour.
    Returns the generated token.

    Args:
        table (str): The name of the table to insert the token into.

    Returns:
        str: The generated token.
    """
    token = secrets.token_hex(16)
    now = datetime.datetime.now()
    expiration_date = now + datetime.timedelta(hours=1)

    # Use parameterized queries to prevent SQL injection
    query = f"INSERT INTO {table} (token, expiration_date) VALUES (%s, %s)"
    commit_query(query, (token, expiration_date))
    return token


def check_temporary_token(table: str, token: str):
    """Checks whether the provided token is present in the specified table
    and whether its expiration date is in the future. If the token is valid,
    the function returns `True`. Otherwise, it raises an exception.

    Args:
        table (str): The name of the table to check the token in.
        token (str): The token to check.

    Raises:
        Exception: If the token is not present in the table or if its expiration date has passed.

    Returns:
        bool: Whether the token is valid or not.
    """
    now = datetime.datetime.now()

    # Use parameterized queries to prevent SQL injection
    query = f"SELECT * FROM {table} WHERE token = %s AND expiration_date > %s"
    results = run_query(query, (token, now))
    if results:
        return True
    else:
        raise Exception("El enlace proporcionado no es válido")
