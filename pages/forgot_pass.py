from gen_functions import load_css_file
import streamlit as st
st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")


from gen_functions import logged_in, multile_button_inline
from db_functions import create_temporary_token
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

authenticator = st.session_state["authenticator"]
db = st.session_state["db"]
email_client = st.session_state["email_client"]

add_indentation()

# The body of the email to be sent to the user
email_body = """
<html>
  <head>
    <title>Recuperación de contraseña</title>
  </head>
  <body>
    <p>Hola,</p>
    <p>Recibimos una solicitud para recuperar tu contraseña. Si no fuiste tú quien lo solicitó, por favor ignora este mensaje.</p>
    <p>Para recuperar tu contraseña, haz clic en el siguiente botón:</p>
    <p><a href="https://finanzaspersonales.streamlit.app/Configuración?page=reset_pass&token={token}&username={username}"><button style="background-color:rgba(128, 61, 245);border:none;color:white;padding:14px 23px;text-align:center;text-decoration:none;display:inline-block;font-size:15px;margin:3px 1px;cursor:pointer;">Recuperar contraseña</button></a></p>    <p>Si tienes problemas para acceder al enlace, copia y pega la siguiente dirección en tu navegador:</p>
    <p>https://finanzaspersonales.streamlit.app/Configuración?page=reset_pass&token={token}&username={username}</p>
    <p>Un saludo,</p>
    <p>El equipo de Finanzas Personales</p>
  </body>
</html>
"""

# The subject of the email to be sent to the user
email_subject = "Recuperación de contraseña"

# Check if user is logged in, if is, show warning message and stop execution of code
if logged_in():
    switch_page("Mi perfil")

else:
    try:
        # Show the form to enter the username
        username = authenticator.username_form("Recuperar contraseña")
        if username:
            # If the user entered a username, generate a temporary token
            token = create_temporary_token(table="password_reset_tokens")

            # Query the database to get the user's ID
            user_id = db.fetchone("SELECT id from users where username=%s", (username,))[0]

            # Query the database to get the user's email and name
            email, name = db.fetchone(
                "SELECT email, name from users where id=%s", (user_id,))

            # Use the email client to send the password reset email
            email_client.send_email(
                email,
                name,
                email_subject,
                email_body.format(token=token, username=username),
            )

            # Show a success message
            st.success(
                "Se le ha enviado un enlace a la dirección de correo electrónico asociada a la cuenta (revise la carpeta Promociones o Spam)"
            )
    except Exception as e:
        # If there was an error, show it
        st.error(e)

    # Show a button to go back to the login page
    multile_button_inline(["Iniciar sesión"],["Mi perfil"])
