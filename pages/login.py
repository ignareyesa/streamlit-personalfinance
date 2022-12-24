import streamlit as st
from init_app import authenticator
from gen_functions import logged_in, multile_button_inline, load_css_file

st.experimental_set_query_params()
load_css_file("styles/forms.css")
css_style = "styles/buttons.css"

# define section and buttons for the navigation menu
section1 = "¿Qué quieres hacer?"
section1_buttons = [
    "Añadir movimientos",
    "Consultar o modificar movimientos",
    "Consultar dashboards"]
section1_links = ["Añadir movimientos", "Consultar movimientos", "   "]


section2 = "Modifica tu perfil"
section2_buttons = [
    "Cambiar contraseña",
    "Cambiar nombre de usuario",
    "Modificar tus datos",
]
section2_links = ["    ", "     ", "   "]


sections = [
    {
        section1:{"buttons":section1_buttons, "links":section1_links},
        section2: {"buttons": section2_buttons, "links": section2_links}
    }
    ]

# define labels and links for the buttons at the bottom of the page
labels_forgot = ["¿Has olvidado tu contraseña?", "¿Has olvidado tu nombre de usuario?"]
links_forgot = ["", " "]
labels_sign = ["¿Eres nuevo? Registrate"]
links_sign = ["  "]

# check if user is logged in
if not logged_in():
    pass

# show login form and handle authentication
name, authentication_status, username = authenticator.login("Bienvenido!", "main")
if st.session_state["authentication_status"]:
    # show logout button and welcome message
    authenticator.logout("Cerrar sesión", "sidebar")
    st.title(f"Nos encanta verte otra vez por aquí")
    # show navigation menu
    for section in sections:
        st.subheader(list(section.keys())[0])
        labels_login = list(section.values())[0]["buttons"]
        links_login = list(section.values())[0]["links"]
        multile_button_inline(labels_login, links_login)
elif st.session_state["authentication_status"] == False:
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
