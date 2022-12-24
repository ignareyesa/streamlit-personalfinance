from init_app import authenticator, db
from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

load_css_file("styles/forms.css")

# Check if user is logged in, if is, show warning message and stop execution of code
if logged_in():
    st.warning("Sesión ya iniciada")
    # Add a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])

    st.stop()

else:
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
                "El correo eléctronico propor proporcionado no coincide con ninguno registrado."
            )
    except Exception as e:
        st.error(e)
    # Show a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])
