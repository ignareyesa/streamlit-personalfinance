from main import logged_in, authenticator, run_query
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page


if logged_in():
    st.warning("You are already log-in.")
    signin = st.button("Back to log in")
    if signin:
            switch_page("Comienza a explorar")
    st.stop() 

else:
    try:
        username_forgot_username, email_forgot_username = authenticator.forgot_username('Forgot username')
        login = st.button("Volver a iniciar sesión")
        if login:
            switch_page("Comienza a explorar")
        if username_forgot_username:
            query_username = f"SELECT username from users where email='{email_forgot_username}'"
            username = run_query(query_username)[0][0]
            st.success(f'Tu nombre de usuario es: **{username}**. No lo olvides!😜')
            # Username to be transferred to user securely
        elif username_forgot_username == False:
            st.error('El correo eléctronico proporcionado no coincide con ninguno registrado.')
    except Exception as e:
        st.error(e)