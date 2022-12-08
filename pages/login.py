import streamlit as st  
from init_db import authenticator
from gen_functions import logged_in, multiple_buttons, load_css_file

load_css_file("styles/forms.css")

section1 = "Modifica tu perfil"
section1_but1 = "Cambiar contraseña"
section1_link1 = "    "
section1_but2 = "Cambiar nombre de usuario"
section1_link2 = "     "
section1_but3 = "Modificar tus datos"
section1_link3 = "   "

sections = [{section1:{"buttons":[section1_but1,section1_but2, section1_but3],
                       "links":[section1_link1, section1_link2, section1_link3]}}]


labels_forgot = ["¿Has olvidado tu contraseña?","¿Has olvidado tu nombre de usuario?"]
links_forgot =  [""," "]
labels_sign = ["¿Eres nuevo? Registrate"]
links_sign = ["  "]
css_style = "styles/buttons.css"

if not logged_in():
    pass



name, authentication_status, username = authenticator.login('Bienvenido!', 'main')
if st.session_state["authentication_status"]:    
    authenticator.logout('Cerrar sesión', 'sidebar')
    st.title(f'Nos encanta verte otra vez por aquí')
    for section in sections:
        st.subheader(list(section.keys())[0])
        labels_login = list(section.values())[0]["buttons"]
        links_login = list(section.values())[0]["links"]
        multiple_buttons(labels_login,links_login)
elif st.session_state["authentication_status"] == False:
    st.error('La combinación usuario/contraseña no coinciden.')
    multiple_buttons(labels_forgot, links_forgot,css=css_style)
    multiple_buttons(labels_sign,links_sign,css=css_style)
    st.session_state["authentication_status"] = None

elif (st.session_state["authentication_status"] == None) or (not "authentication_status" in st.session_state):
    multiple_buttons(labels_forgot, links_forgot,css=css_style)
    multiple_buttons(labels_sign,links_sign,css=css_style)

