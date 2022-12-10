from init_db import authenticator, email_client, run_query
from gen_functions import logged_in,load_css_file, create_temporary_token
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

email_body ="""
Hola,

Recibimos una solicitud para recuperar tu contraseña. Si no fuiste tú quien lo solicitó, por favor ignora este mensaje.

Para recuperar tu contraseña, haz clic en el siguiente enlace:

http://localhost:8501/Configuración?page=reset_pass&token={token}&username={username}

Si tienes problemas para acceder al enlace, copia y pega la siguiente dirección en tu navegador:

http://localhost:8501/Configuración?page=reset_pass&token={token}&username={username}

Un saludo,

El equipo de Finanzas Personales
"""
email_subject = "Recuperación de Contraseña"

if logged_in():
    st.warning("Sesión ya iniciada")
    signin = st.button("Volver al inicio")
    if signin:
            switch_page("Comienza a explorar")
    st.stop() 

else:
    try:
        username = authenticator.username_form("Recuperar contraseña")        
        if username:
            token = create_temporary_token(table="password_reset_tokens")
            query_id = f"SELECT id from users where username='{username}'"
            user_id = run_query(query_id)[0][0]
            query_info = f"SELECT email,name from users where id='{user_id}'"
            email, name = run_query(query_info)[0]
            email_client.send_email(email,name,email_subject,email_body.format(token=token, username=username))
            st.success("Se le ha enviado un enlace a la dirección de correo electrónico asociada a la cuenta")
    except Exception as e:
        st.error(e)
    login = st.button("Volver a iniciar sesión")
    if login:
        switch_page("Comienza a explorar")

