from init_db import credentials, authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

if not logged_in():
    st.warning("Para poder cambiar tu contraseña tienes que haber iniciado sesión.")
    signin = st.button("Volver al inicio")
    if signin:
            switch_page("Comienza a explorar")
    st.stop() 


else:
    authenticator.logout('Cerrar sesión', 'sidebar')
    try:
        username = st.session_state['username']
        query_id = f"SELECT id from users where username='{username}'"
        user_id = run_query(query_id)[0][0]
        if authenticator.reset_password(username, 'Cambiar contraseña'):
            new_pass = credentials['usernames'][st.session_state['username']]['password']
            query_pass = f"UPDATE users SET pass='{new_pass}' WHERE id={user_id}"
            commit_query(query_pass)
            st.success('Contraseña modificada correctamente')
    except Exception as e:
        st.error(e)
signin = st.button("Volver al inicio")
if signin:
    switch_page("Comienza a explorar")


    