from init_db import authenticator, run_query, credentials
from gen_functions import logged_in,load_css_file
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

if logged_in():
    st.warning("Sesión ya iniciada")
    signin = st.button("Volver al inicio")
    if signin:
            switch_page("Comienza a explorar")
    st.stop() 

else:
    try:
        username_forgot_pw, email_forgot_password, random_password = authenticator.forgot_password('Generar nueva contraseña')
        if username_forgot_pw:
            query_id = f"SELECT id from users where username='{username_forgot_pw}'"
            user_id = run_query(query_id)[0][0]
            new_pass = credentials['usernames'][username_forgot_pw]['password']
            query_pass = f"UPDATE users SET pass='{new_pass}' WHERE id={user_id}"
            st.success(f'Tu nueva contraseña es: **{random_password}**. La puedes modificar cuando inicies sesión.')
        elif username_forgot_pw == False:
            st.error('Usuario no encontrado.')
    except Exception as e:
        print(e)
        st.error(e)
    login = st.button("Volver a iniciar sesión")
    if login:
        switch_page("Comienza a explorar")

