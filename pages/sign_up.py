from init_db import credentials, authenticator, commit_query
from gen_functions import logged_in, load_css_file, switch_page_button
import streamlit as st

load_css_file("styles/forms.css")

# If the user is already logged in, show a warning message and stop the app
if logged_in():
    st.warning("Sesión ya iniciada")
    st.stop()  # App won't run anything after this line

# Register the user if they haven't already done so
else:
    try:
        if authenticator.register_user("¡Únete!", preauthorization=False):
            key = list(credentials["usernames"])[
                -1
            ]  # Get the newly registered user's username
            form_input = credentials["usernames"][
                key
            ]  # Get the user's information from the form
            print(key)
            print(form_input)
            # Create the INSERT query
            commit_query(
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
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])