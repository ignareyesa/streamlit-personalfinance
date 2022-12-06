from main import logged_in, authenticator, commit_query, credentials, run_query
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page


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
        if authenticator.update_user_details(username, 'Modificar tus datos'):
            new_name = credentials['usernames'][username]['name']
            new_email = credentials['usernames'][username]['email']
            query = f"UPDATE users SET email='{new_email}', name='{new_name}' WHERE id={user_id}"
            commit_query(query)
            st.success('Datos modificados existosamente')
    except Exception as e:
        st.error(e)
signin = st.button("Volver al inicio")
if signin:
    switch_page("Comienza a explorar")


    