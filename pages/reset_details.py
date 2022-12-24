from init_app import credentials, authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

load_css_file("styles/forms.css")

# Check if user is logged in, if not, show warning message and stop execution of code
if not logged_in():
    st.warning("Para poder cambiar tu contraseña tienes que haber iniciado sesión.")
    # Show a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

else:
    authenticator.logout("Cerrar sesión", "sidebar")
    try:
        username = st.session_state["username"]
        query_id = "SELECT id from users where username=%s"
        # Get id from database
        user_id = run_query(query_id, (username,))[0][0]

        # Authenticate user details
        if authenticator.update_user_details(username, "Modificar tus datos"):
            new_name = credentials["usernames"][username]["name"]
            new_email = credentials["usernames"][username]["email"]

            # Update user details in the database
            query = "UPDATE users SET email=%s, name=%s WHERE id=%s"
            commit_query(query, (new_email, new_name, user_id))
            st.success("Datos modificados exitósamente.")
    except Exception as e:
        st.error(e)

    # Show a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])
