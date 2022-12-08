from init_db import authenticator, commit_query, run_query, credentials
from gen_functions import logged_in, load_css_file
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

if not logged_in():
    st.warning("Para poder cambiar tu nombre de usuario tienes que haber iniciado sesión.")
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
        new_username = authenticator.reset_username('Cambiar nombre de usuario')
        if new_username:
            query_pass = f"UPDATE users SET username='{new_username}' WHERE id={user_id}"
            commit_query(query_pass)
            print(credentials)
            st.success(f'Su nuevo nombre de usuario es: **{new_username}**')
    except Exception as e:
        st.error(e)
signin = st.button("Volver al inicio")
if signin:
    switch_page("Comienza a explorar")


    