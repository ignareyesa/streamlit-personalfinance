import streamlit as st

from gen_functions import multile_button_inline, load_css_file, switch_page, progressbar, stateful_button
from authenticator.utils import check_email

from st_pages import add_indentation
from PIL import Image

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")
with open('error.txt', 'r') as error_file:
    error_text = error_file.read()

st.experimental_set_query_params()
add_indentation()

try:
    authentication_status = st.session_state["authentication_status"]
    authenticator = st.session_state["authenticator"]
    db = st.session_state["db"]
    credentials = st.session_state["credentials"]
except:
    st.markdown("La web ha sido desactivada para ahorrar recursos, por favor, pulse en el siguiente enlace para reactivarla.")
    multile_button_inline(["Volver a conectar"],["Inicio"])
    st.stop()


css_style = "styles/buttons.css"



# define labels and links for the buttons at the bottom of the page
labels_forgot = ["¿Has olvidado tu contraseña?", "¿Has olvidado tu nombre de usuario?"]
links_forgot = ["", " "]
labels_sign = ["¿Eres nuevo? Registrate"]
links_sign = ["  "]
labels_main = ["Panel de Control", "Añadir Movimientos", "Mis ahorros", "Mi patrimonio"]
links_main = ["seguimiento", "movimientos", "ahorros", "seguimiento patrimonio"]


#show login form and handle authentication
col1, col2, col3 = st.columns([1,0.25,0.77])
with col1:
    name, authentication_status, username = authenticator.login("Bienvenido!", "main")

    if st.session_state["authentication_status"] == False:
        # show error message if login failed
        st.error("La combinación usuario/contraseña no coinciden.")
        # show buttons for forgot password and sign up
        multile_button_inline(labels_forgot, links_forgot, css=css_style)
        multile_button_inline(labels_sign, links_sign, css=css_style)
        st.session_state["authentication_status"] = None

    elif (st.session_state["authentication_status"] == None) or (
        not "authentication_status" in st.session_state
    ):
        # show buttons for forgot password and sign up if user is not logged in and has not tried to login
        multile_button_inline(labels_forgot, links_forgot, css=css_style)
        multile_button_inline(labels_sign, links_sign, css=css_style)

with col3:
    if st.session_state["authentication_status"] == False:
        st.write("TUTORIAL")

    elif (st.session_state["authentication_status"] == None) or (
        not "authentication_status" in st.session_state
    ):

        st.write("TUTORIAL")

if authentication_status:
    st.write(credentials)
    st.write(st.session_state["credentials"])
    authenticator.logout("Salir", "sidebar")
    username = st.session_state["username"]
    query_id = "SELECT id, name, username, email from users where username=%s"
    try:
        user_id, current_name, current_username, current_email  = db.fetchone(query_id, (username,))
    except:
        st.write(error_text, unsafe_allow_html=True)
        st.stop()
    
    with st.container():
        col1, col2, col3 = st.columns([1,0.25,0.77])
        with col1:
            st.write("### Principales enlaces")
            multile_button_inline(labels_main, links_main, css=css_style)
            image = Image.open('images/login_vector.jpeg')
            st.image(image, use_column_width=True)


        with col3:
            st.write("### Mis datos")
            edit_but = stateful_button("Habilitar edición datos", False, key = "edit_but")
            new_name = st.text_input("Nombre", current_name, disabled = not edit_but)
            new_username = st.text_input("Nombre de usuario", current_username, disabled = not edit_but)
            new_email = st.text_input("Correo electrónico", current_email, disabled = not edit_but)
            password = st.text_input("Contraseña", "**********", disabled = True)
            pass_but = st.button("Modificar contraseña", key="password_but")
            if pass_but:
                switch_page("    ")

            if new_username != current_username or new_name != current_name or new_email != current_email:
                final_but_dis = False
            else: 
                final_but_dis = True    
            safe_changes = st.button("Guardar cambios", disabled = final_but_dis)
            
            if safe_changes:
                if check_email(new_email):
                    try:
                        query = "UPDATE users SET email=%s, name=%s, username=%s WHERE id=%s"
                        db.commit(query, (new_email, new_name, new_username, user_id))
                        users = db.fetchall("SELECT * from users;")
                        credentials = {
                            "usernames": {i[2]: {"email": i[1], "name": i[3], "password": i[4]} for i in users}
                        }
                        st.session_state["credentials"] = credentials 
                        st.success("Datos modificados exitósamente, la página se recargará en un instante.")
                        progressbar()
                        st.experimental_rerun()
                    except Exception as e:
                        error = str(e).split(" ")
                        if '1062' in error and '(23000):' in error:
                            if error[-1] == "'email'":
                                st.error(f"El email '{new_email}' ya está en uso, utilize otro")
                            if error[-1] == "'username'":
                                st.error(f"El nombre de usuario '{new_username}' ya está en uso, utilize otro")
                else:
                    st.error("El correo electrónico introducido no es válido")

    