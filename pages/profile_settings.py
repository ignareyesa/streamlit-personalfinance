from init_db import credentials, authenticator, commit_query, run_query
from gen_functions import logged_in, load_css_file, check_temporary_token, switch_page_button
import streamlit as st
from streamlit_extras.switch_page_button import switch_page

load_css_file("styles/forms.css")

# check if user is logged in, if not show warning and stop
if not logged_in():
    st.warning("Para poder ver tu perfil tiene que haber iniciado sesión.")
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

# check if page query parameter is given, if not show warning and stop
try:
    search_params = st.experimental_get_query_params()
    page = search_params.get("page")[0]
except:
    st.warning("Página no encontrada. No se han especificado parámetros de búsqueda.")
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

# check if page is "reset_pass", if not show warning and stop
if page != "reset_pass":
    st.warning("Página no encontrada. Página especificada no válida.")
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

# check if token and username query parameters are given, if not show warning and stop
try:
    token = search_params.get("token")[0]
    username = search_params.get("username")[0]
except:
    st.warning("El enlace proporcionado no es válido.")
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

# check if token is valid, if not show error and stop
try:
    check_temporary_token("password_reset_tokens", token)
except Exception as e:
    st.warning("El enlace proporcionado no es válido.")
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()


# show form to get new password and update it in the database
try:
    # get user id from database
    user_id = run_query("SELECT id from users where username=%s", (username))[0][0]
    if authenticator.forgot_password(username, "Cambiar contraseña"):
        new_pass = credentials["usernames"][username]["password"]
        commit_query("UPDATE users SET pass=%s WHERE id=%s", (new_pass, user_id))
        st.success("Contraseña modificada correctamente")
except Exception as e:
    st.error(e)

switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
