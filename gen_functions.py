import streamlit as st
import pandas as pd
import datetime
import secrets
from st_click_detector import click_detector
from streamlit_extras.switch_page_button import switch_page
from init_app import db


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


def multile_button_inline(
    labels: list,
    object_ids: list,
    ids_as_links: bool = True,
    html_class: str = "css-1x8cf1d edgvbvh10",
    css: str = "styles/default_buttons.css",
):
    """
    Generates a string of HTML code containing single or multiple inline buttons with the specified labels.
    Depending on the value of the `ids_as_links` argument, the function behaves differently when a button is clicked:
        - If `ids_as_links` is `True` (default), the user will be redirected to the link assigned to that button.
        - If `ids_as_links` is `False`, the function will return the ID of the button that was clicked.

    Args:
        labels (list): A list of strings to be used as the labels for the buttons.
        object_ids (list): A list of object IDs for the buttons. If provided, the length of this list must be equal to the length of the `labels` list. If `ids_as_links` is `True`, these IDs will be passed as arguments to the `switch_page` function when a button is clicked. If `ids_as_links` is `False`, the object IDs will be used as the IDs for the buttons.
        ids_as_links (bool, optional): A flag indicating whether the `switch_page` function should be used to switch pages when a button is clicked. Defaults to `True`.
        html_class (str, optional): The CSS class to be used for the buttons. Defaults to "css-1x8cf1d edgvbvh10".
        css (str): The path to the CSS file to be used for styling the buttons.

    Raises:
        Exception: If the `labels` and `object_ids` lists have different lengths.

    Returns:
        str: The ID of the button that was clicked, or an empty string if no button was clicked (if `ids_as_links` is `False`).
    """
    if ids_as_links:
        if len(labels) == len(object_ids):
            content = load_css_file(css, as_markdown=False)
            for i, label in enumerate(labels):
                temp_content = (
                    f"""<a href="" id="link_{i}" class="{html_class}">{label}</a> """
                )
                content += temp_content
            clicked = click_detector(content)
            for i, object_id in enumerate(object_ids):
                if clicked == f"link_{i}":
                    switch_page(object_id)
        else:
            raise Exception("labels and object_ids length must have the same lenght")
    else:
        if len(labels) == len(object_ids):
            content = load_css_file(css, as_markdown=False)
            for i, label in enumerate(labels):
                temp_content = f"""<a href="" id="{object_ids[i]}" class="{html_class}">{label}</a> """
                content += temp_content
            clicked = click_detector(content)
            return clicked
        else:
            raise Exception("labels and object_ids length must have the same lenght")

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
    db.commit(query, (token, expiration_date))
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
    results = db.fetchone(query, (token, now))
    if results:
        return True
    else:
        raise Exception("El enlace proporcionado no es válido")


def check_columns(df : pd.DataFrame, expected_columns : list):
    """Check if a DataFrame has the expected columns.
    
    Args:
        df: The DataFrame to check.
        expected_columns: A list of the expected column names.
    
    Raises:
        ValueError: If any of the expected columns are missing from the DataFrame.
    """
    missing_columns = set(expected_columns) - set(df.columns)
    if missing_columns:
        raise ValueError(f"""Al archivo le faltan los siguientes campos : {', '.join(missing_columns)}""")
        #raise ValueError(f"""The dataframe is missing the followings columns : {', '.join(missing_columns)}""")

def check_data_types(df : pd.DataFrame, expected_columns : list, expected_types : list):
    """Check if the data types of the columns in a DataFrame are as expected.
    
    Args:
        df: The DataFrame to check.
        expected_columns: A list of the column names.
        expected_types: A list of the expected data types for the columns.
    
    Raises:
        ValueError: If any of the columns have the wrong data type.
    """
    # Check if expected_columns and expected_types have the same length
    if len(expected_columns) != len(expected_types):
        raise ValueError(f"expected_columns and expected_types should have the same length")
    
    # Check if the data types of the columns are correct
    for column, dtype in zip(expected_columns, expected_types):
        if df[column].dtype != dtype:
            raise ValueError(f"Column '{column}' should have data type {dtype}, but has data type {df[column].dtype}")

def check_schema(df : pd.DataFrame, expected_columns : list, expected_types : list):
    """Check if a DataFrame has the expected columns and data types.
    
    Args:
        df: The DataFrame to check.
        expected_columns: A list of the expected column names.
        expected_types: A list of the expected data types for the columns.
    
    Raises:
        ValueError: If any of the expected columns are missing from the DataFrame, or if any of the columns have the wrong data type.
    """
    check_columns(df, expected_columns)
    check_data_types(df, expected_columns, expected_types)