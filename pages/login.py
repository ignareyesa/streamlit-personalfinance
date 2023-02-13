import streamlit as st

from gen_functions import logged_in, multile_button_inline, load_css_file, switch_page, progressbar
from streamlit_extras.add_vertical_space import add_vertical_space
from authenticator.utils import check_email

from st_pages import add_indentation
from PIL import Image

st.markdown("<style>div[class='row-widget stButton']{margin-top:7px; margin-bottom:34px}</style>", unsafe_allow_html=True)
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")

st.experimental_set_query_params()
add_indentation()

authenticator = st.session_state["authenticator"]
db = st.session_state["db"]

css_style = "styles/buttons.css"

def stateful_button(*args, key=None, **kwargs):
    if key is None:
        raise ValueError("Must pass key")

    if key not in st.session_state:
        st.session_state[key] = False

    if st.button(*args, **kwargs):
        st.session_state[key] = not st.session_state[key]

    return st.session_state[key]

# define labels and links for the buttons at the bottom of the page
labels_forgot = ["¿Has olvidado tu contraseña?", "¿Has olvidado tu nombre de usuario?"]
links_forgot = ["", " "]
labels_sign = ["¿Eres nuevo? Registrate"]
links_sign = ["  "]

# check if user is logged in
if not logged_in():
    pass

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
        image = Image.open('images/login_vector.jpeg')
        st.image(image, use_column_width=True)
    elif (st.session_state["authentication_status"] == None) or (
        not "authentication_status" in st.session_state
    ):
        image = Image.open('images/login_vector.jpeg')
        st.image(image, use_column_width=True)

if st.session_state["authentication_status"]:
    authenticator.logout("Salir", "sidebar")
    username = st.session_state["username"]
    query_id = "SELECT id, name, username, email from users where username=%s"
    user_id, current_name, current_username, current_email  = db.fetchone(query_id, (username,))

    with st.container():
        col1, col2, col3 = st.columns([1,0.3,0.9])
        with col2:
            add_vertical_space(19)

            username_but = stateful_button("Modificar", False, key = "username_but")
            add_vertical_space(1)
            mail_but = stateful_button("Modificar", key="email_but")
            add_vertical_space(1)
            pass_but = st.button("Modificar", key="password_but")
            if pass_but:
                switch_page("    ")

        with col1:
            st.write("### Mi perfil")
            st.write("Usuario desde Oct-2022.")
            st.write("### Mis datos")
            new_name = st.text_input("Nombre", current_name)
            add_vertical_space(1)
            new_username = st.text_input("Nombre de usuario", current_username, disabled = not username_but)
            add_vertical_space(1)
            new_email = st.text_input("Correo electrónico", "ignareyesa@gmail.com", disabled = not mail_but)
            add_vertical_space(1)
            password = st.text_input("Contraseña", "**********", disabled = True)
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
                    st.error("El correo electrónico introducido no es vaĺido")
        with col3:
            add_vertical_space(8)
            st.write("TUTORIAL")
        

