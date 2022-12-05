from main import logged_in, authenticator, commit_query, credentials, run_query
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
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Generar nueva contraseña')
        login = st.button("Volver a iniciar sesión")
        if login:
            switch_page("Comienza a explorar")
        if username_forgot_pw:
            query_id = f"SELECT id from users where username='{username_forgot_pw}'"
            user_id = run_query(query_id)[0][0]
            new_pass = credentials['usernames'][st.session_state['username']]['password']
            query_pass = f"UPDATE users SET pass='{new_pass}' WHERE id={user_id}"
            commit_query(query_pass)
            st.success(f'Tu nueva contraseña es: **{random_password}**')
        elif username_forgot_pw == False:
            st.error('Usuario no encontrado')
    except Exception as e:
        st.error(e)

