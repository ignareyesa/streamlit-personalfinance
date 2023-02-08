from gen_functions import load_css_file
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")


from init_app import authenticator, email_client, db
from gen_functions import logged_in, create_temporary_token, multile_button_inline
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

add_indentation()

# The body of the email to be sent to the user
email_body = """
Hola,

Recibimos una solicitud para recuperar tu contraseña. Si no fuiste tú quien lo solicitó, por favor ignora este mensaje.

Para recuperar tu contraseña, haz clic en el siguiente enlace:

http://localhost:8501/Configuración?page=reset_pass&token={token}&username={username}

Si tienes problemas para acceder al enlace, copia y pega la siguiente dirección en tu navegador:

http://localhost:8501/Configuración?page=reset_pass&token={token}&username={username}

Un saludo,

El equipo de Finanzas Personales
"""

# The subject of the email to be sent to the user
email_subject = "Recuperación de Contraseña"

# Check if user is logged in, if is, show warning message and stop execution of code
if logged_in():
    st.warning("Sesión ya iniciada")
    multile_button_inline(["Volver a tu perfil"],["Comienza a explorar"])

    st.stop()

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
                "Se le ha enviado un enlace a la dirección de correo electrónico asociada a la cuenta"
            )
    except Exception as e:
        # If there was an error, show it
        st.error(e)

    # Show a button to go back to the login page
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"])
