import streamlit as st
import pandas as pd
import datetime
import secrets
from time import sleep
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

def verify_column_values(df: pd.DataFrame, column:str, predefined_values:list):
    """
    Verify if all values in a column in a pandas dataframe belong to a predefined list.
    
    Args:
    df (pandas.DataFrame): The dataframe to verify
    column (str): The name of the column to verify
    predefined_list (list): The list of values that the column values should belong to
    
    Raises:
    ValueError: If any value in the column is not in the predefined list

    """
    if not df[column].isin(predefined_values).all():
        raise ValueError("Values in column '{}' are not in the predefined list".format(column))

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


def abbreviate_number(number, decimals_small_numbers=2, small_number=50000):
    """Abbreviate a number according to its size.

    Parameters:
    number (float): The number to abbreviate.
    decimals_small_numbers (int, optional): The number of decimal places to show for numbers less than 50000 (default is 2).

    Returns:
    str: The abbreviated number as a string.
    """
    # If the number is less than small_number, return it as is
    if number < small_number:
        return f"{number:,.{decimals_small_numbers}f}".replace(".","*").replace(",",".").replace("*",",")

    # If the number is less than 1 million
    elif number < 1000000:
        # Divide the number by 1000 and round to 2 decimal places
        abbreviated = round(number/1000, 2)
        # Convert the number to a string and add "k" at the end
        return f"{abbreviated:,.2f}k".replace(".","*").replace(",",".").replace("*",",")

    # If the number is less than 1 billion
    elif number < 1000000000:
        # Divide the number by 1 million and round to 2 decimal places
        abbreviated = round(number/1000000, 2)
        # Convert the number to a string and add "m" at the end
        return f"{abbreviated:,.2f}m".replace(".","*").replace(",",".").replace("*",",")

    # If the number is more than 1 billion
    else:
        # Divide the number by 1 billion and round to 2 decimal places
        abbreviated = round(number/1000000000, 2)
        # Convert the number to a string and add "b" at the end
        return f"{abbreviated:,.2f}b".replace(".","*").replace(",",".").replace("*",",")

def df_with_all_dates_given_period(query_result, date_column=["date"], periods=12, other_columns = [], include_actual = False):
    dates = pd.date_range(end=pd.datetime.today(), periods=periods, freq="M")
    if include_actual:
        dates = dates.shift(1, freq="M")
        dates = dates.date
    else:
        dates = dates.date
    df_period = pd.DataFrame(dates, columns=date_column)
    df = pd.DataFrame(query_result, columns=date_column+other_columns)
    df["date"] = pd.to_datetime(df["date"], format = "%Y-%m-%d")
    df_period["date"] = pd.to_datetime(df_period["date"], format = "%Y-%m-%d")
    df_period = df_period.merge(df, on="date",how="left").fillna(0)
    return df_period

def spanish_month_num(month_name):
    months = {"enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6, "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12
    }
    return months.get(month_name.lower())

def spanish_month_name(month_number, abbreviate=False):
    full_months = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                  7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                 }
    abr_months = {1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
                  7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"
                 }
    if abbreviate:
        return abr_months.get(month_number)
    else:
        return full_months.get(month_number)

def prev_date(month, year, abbreviate = False):
    if month == 1:
        month = 12
        year = year-1
    else:
        month = month-1
        year = year
    return spanish_month_name(month_number=month, abbreviate=abbreviate).capitalize() + " " + str(year)


def progressbar():
    my_bar = st.progress(0)
    for percent_complete in range(100):
        sleep(0.01)
        my_bar.progress(percent_complete + 1)