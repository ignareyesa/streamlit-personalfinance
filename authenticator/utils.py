import string
import random
import re

def generate_random_pw(length: int=16) -> str:
    """
    Generates a random password.

    Parameters
    ----------
    length: int
        The length of the returned password.
    Returns
    -------
    str
        The randomly generated password.
    """
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length)).replace(' ','')

def check_email(email: str) -> bool:
    """
    Checks wether the input is a valid email or not

    Parameters
    ----------
    email: str
        Input string
    Returns
    -------
    bool   
        True or False depending on passing the test

    """
    pat = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if re.match(pat,email):
        return True
    else:
        return False