from init_db import credentials, authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file, switch_page_button
import streamlit as st

load_css_file("styles/forms.css")

if not logged_in():
    st.warning("Para poder cambiar tu contraseña tienes que haber iniciado sesión.")
    # Show a button to go back to the login page
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])

    st.stop()


else:
    authenticator.logout("Cerrar sesión", "sidebar")
    try:
        username = st.session_state["username"]
        print(username)
        query_id = "SELECT id from users where username=%s"
        print(query_id)
        # Get id from database
        user_id = run_query(query_id, (username,))[0][0]
        # If the user entered a new password, commit the change to the database
        if authenticator.reset_password(username, "Cambiar contraseña"):
            new_pass = credentials["usernames"][st.session_state["username"]][
                "password"
            ]
            query_pass = "UPDATE users SET pass=%s WHERE id=%s"
            commit_query(query_pass, (new_pass, user_id))
            st.success("Contraseña modificada correctamente")
    except Exception as e:
        st.error(e)
    # Show a button to go back to the login page
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
