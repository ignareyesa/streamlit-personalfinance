from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")


from main import credentials, authenticator, db
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

add_indentation()

if logged_in():
    switch_page("Mi perfil")

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
except Exception as e:
    if "1062 (23000)" in str(e):
        st.error("Ya existe un usuario con el correo eléctronico proporcionado.")
    else:
        st.error(e)

# Show a button to go back to the login page
multile_button_inline(["Iniciar sesión"],["Mi perfil"])