from init_db import credentials, authenticator, commit_query
from gen_functions import logged_in, load_css_file
import streamlit as st  
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

if logged_in():
    st.warning("Sesión ya iniciada")
    st.stop()  # App won't run anything after this line
try:
    if authenticator.register_user('¡Únete!', preauthorization=False):
        key = list(credentials["usernames"])[-1]
        form_input = credentials["usernames"][key]
        query = f"""INSERT INTO users (email, username, name, pass) VALUES
                {form_input["email"],key,form_input["name"], form_input["password"]}
                """
        commit_query(query)
        st.success(f'⬇️ Usuario registrado correctamente.')
except Exception as e:
    if "1062 (23000)" in str(e):
        st.error("Ya existe un usuario con el correo eléctronico proporcionado.")
    else:
        st.error(e)
signin = st.button("¿Ya estás registrado? Inicia sesión")
if signin:
    switch_page("Comienza a explorar")
    