import streamlit as st  
from streamlit_extras.switch_page_button import switch_page
from main import authenticator
from st_btn_select import st_btn_select


section1 = "Modifica tu perfil"
section1_but1 = "Cambiar contraseña"
section1_link1 = "    "
section1_but2 = "Cambiar nombre de usuario"
section1_link2 = "     "
section1_but3 = "Modificar tus datos"
section1_link3 = "   "
section1_but4='Solo soy un botón'

sections = [{section1:{"buttons":[section1_but1,section1_but2, section1_but3,section1_but4],
                       "links":[section1_link1, section1_link2, section1_link3]}}]

selection = None

name, authentication_status, username = authenticator.login('Bienvenido!', 'main')
if st.session_state["authentication_status"]:    
    authenticator.logout('Cerrar sesión', 'sidebar')
    st.title(f'Nos encanta verte otra vez por aquí')
    for section in sections:
        st.subheader(list(section.keys())[0])
        selection = st_btn_select(list(section.values())[0]["buttons"], index = -1)
        for i,but in enumerate(list(section.values())[0]["buttons"]):
            if selection == section1_but4:
                break
            elif selection==but and selection!=section1_but4:
                switch_page(list(section.values())[0]["links"][i])
            else:
                continue

elif st.session_state["authentication_status"] == False:
    st.error('La combinación usuario/contraseña no coinciden.')
    forgot_pass = st.button("¿Has olvidado tu contraseña?")
    forgot_user = st.button("¿Has olvidado tu nombre de usuario?")
    signup = st.button("¿Eres nuevo? Registrate")
    if forgot_pass:
        switch_page("")
    if forgot_user:
        switch_page(" ")
    if signup:
        switch_page("  ")
elif st.session_state["authentication_status"] == None:
    forgot_pass = st.button("¿Has olvidado tu contraseña?")
    forgot_user = st.button("¿Has olvidado tu nombre de usuario?")
    signup = st.button("¿Eres nuevo? Registrate")
    if forgot_pass:
        switch_page("")
    if forgot_user:
        switch_page(" ")
    if signup:
        switch_page("  ")