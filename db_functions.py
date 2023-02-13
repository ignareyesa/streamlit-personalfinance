from main import db
import datetime
import secrets

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