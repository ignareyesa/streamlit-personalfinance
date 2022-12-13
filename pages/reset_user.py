from init_db import authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file, switch_page_button
import streamlit as st

load_css_file("styles/forms.css")

# Check if user is logged in, if is, show warning message and stop execution of code
if not logged_in():
    st.warning(
        "Para poder cambiar tu nombre de usuario tienes que haber iniciado sesión."
    )
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])

    st.stop()

else:
    # Show logout option in sidebar
    authenticator.logout("Cerrar sesión", "sidebar")
    try:
        # Get username from session state
        username = st.session_state["username"]
        # Get id from database
        user_id = run_query("SELECT id from users where username=%s", (username,))[0][0]
        # Show form to change username
        new_username = authenticator.reset_username("Cambiar nombre de usuario")
        # If the user entered a new username, commit the change to the database
        if new_username:
            commit_query(
                "UPDATE users SET username=%s WHERE id=%s", (new_username, user_id)
            )
            st.success(f"Su nuevo nombre de usuario es: **{new_username}**")
    except Exception as e:
        st.error(e)

    # Show a button to go back to the login page
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
