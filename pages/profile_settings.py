from init_db import credentials, authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file, check_temporary_token
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

try:
    search_params = st.experimental_get_query_params()
    token = search_params.get('token')[0]
    username = search_params.get('username')[0]
    page = search_params.get("page")[0]
except:
    if not logged_in():
        st.warning("Para poder ver tu perfil tiene que haber iniciado sesión.")
        signin = st.button("Volver al inicio")
        if signin:
                switch_page("Comienza a explorar")
        st.stop() 

if page == "reset_pass":
    try:
        check_temporary_token("password_reset_tokens", token)
        print(st.session_state)
        print(credentials)
        query_id = f"SELECT id from users where username='{username}'"
        user_id = run_query(query_id)[0][0]
        if authenticator.forgot_password(username, "Cambiar contraseña"):
            new_pass = credentials['usernames'][username]['password']
            query_pass = f"UPDATE users SET pass='{new_pass}' WHERE id={user_id}"
            commit_query(query_pass)
            st.success('Contraseña modificada correctamente')
    except Exception as e:
        st.error(e)
    login = st.button("Volver a iniciar sesión")
    if login:
        switch_page("Comienza a explorar")
    
