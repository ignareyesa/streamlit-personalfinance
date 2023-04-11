from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")



import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

with open('error.txt', 'r') as error_file:
    error_text = error_file.read()
add_indentation()

if logged_in():
    switch_page("Mi perfil")

try:

    authenticator = st.session_state["authenticator"]
    db = st.session_state["db"]
except:
    st.write(error_text, unsafe_allow_html=True)
    st.stop()

try:
    username_forgot_username, email_forgot_username = authenticator.forgot_username(
        "Forgot username"
    )
    # If the user entered an email address, query the database to get the corresponding username
    if username_forgot_username:
        query_username = "SELECT username from users where email=%s"
        username = db.fetchone(query_username, (email_forgot_username,))[0]
        st.success(f"Tu nombre de usuario es: **{username}**. No lo olvides!😜")

    # If the user didn't enter an email address, show an error message
    elif username_forgot_username == False:
        st.error(
            "El correo eléctronico proporcionado no coincide con ninguno registrado."
        )

except Exception as e:
        st.error(e)
# Show a button to go back to the login page
multile_button_inline(["Iniciar sesión"],["Mi perfil"])