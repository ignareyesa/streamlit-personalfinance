from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")


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
    credentials = st.session_state["credentials"]
except:
    st.write(error_text, unsafe_allow_html=True)
    st.stop()

try:
    if authenticator.register_user("¡Únete!", preauthorization=False):
        key = list(credentials["usernames"])[
            -1
        ]  # Get the newly registered user's username
        form_input = credentials["usernames"][
            key
        ]  # Get the user's information from the form
        # Create the INSERT query
        db.commit(
            "INSERT INTO users (email, username, name, pass) VALUES (%s,%s,%s,%s)",(
            form_input["email"],
            key,
            form_input["name"],
            form_input["password"])
        )
        # Execute the query and commit the changes to the database
        st.success(f"⬇️ Usuario registrado correctamente.")
    # Show a button to go back to the login page
except Exception as e:
    if "1062 (23000)" in str(e):
        st.error("Ya existe un usuario con el correo eléctronico proporcionado.")
    else:
        st.error(e)
 
multile_button_inline(["Iniciar sesión"],["Mi perfil"])

