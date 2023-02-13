import streamlit as st
st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
from main import authenticator, db, credentials

from streamlit_extras.switch_page_button import switch_page
from gen_functions import logged_in, load_css_file, multile_button_inline
from db_functions import check_temporary_token
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")
from st_pages import add_indentation

add_indentation()

if logged_in():
    switch_page("Mi perfil")

# check if page query parameter is given, if not show warning and stop
try:
    search_params = st.experimental_get_query_params()
    page = search_params.get("page")[0]
except:
    st.warning("Página no encontrada.")
    multile_button_inline(["Ir al inicio"],["Mi perfil"])
    st.stop()

# check if page is "reset_pass", if not show warning and stop
if page != "reset_pass":
    st.warning("Página no encontrada. Página especificada no válida.")
    multile_button_inline(["Ir al inicio"],["Mi perfil"])
    st.stop()

# check if token and username query parameters are given, if not show warning and stop
try:
    token = search_params.get("token")[0]
    username = search_params.get("username")[0]
except:
    st.warning("El enlace proporcionado no es válido.")
    multile_button_inline(["Ir al inicio"],["Mi perfil"])
    st.stop()

# check if token is valid, if not show error and stop
try:
    check_temporary_token("password_reset_tokens", token)
except Exception as e:
    st.warning("El enlace proporcionado no es válido.")
    multile_button_inline(["Ir al inicio"],["Mi perfil"])
    st.stop()

# show form to get new password and update it in the database
try:
    # get user id from database
    user_id = db.fetchone("SELECT id from users where username='{}'".format(username))[0]
    if authenticator.forgot_password(username, "Cambiar contraseña"):
        new_pass = credentials["usernames"][username]["password"]
        db.commit("UPDATE users SET pass=%s WHERE id=%s", (new_pass, user_id))
        st.success("Contraseña modificada correctamente")
except Exception as e:
    st.error(e)

multile_button_inline(["Iniciar sesión"],["Mi perfil"])
