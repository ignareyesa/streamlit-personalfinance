from init_app import authenticator, db
from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

load_css_file("styles/forms.css")

# Check if user is logged in, if is, show warning message and stop execution of code
if not logged_in():
    st.warning(
        "Para poder cambiar tu nombre de usuario tienes que haber iniciado sesión."
    )
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])

    st.stop()

else:
    # Show logout option in sidebar
    authenticator.logout("Cerrar sesión", "sidebar")
    try:
        # Get username from session state
        username = st.session_state["username"]
        # Get id from database
        user_id = db.fetchone("SELECT id from users where username=%s", (username,))[0]
        # Show form to change username
        new_username = authenticator.reset_username("Cambiar nombre de usuario")
        # If the user entered a new username, commit the change to the database
        if new_username:
            db.commit(
                "UPDATE users SET username=%s WHERE id=%s", (new_username, user_id)
            )
            st.success(f"Su nuevo nombre de usuario es: **{new_username}**")
    except Exception as e:
        st.error(e)

    # Show a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])
