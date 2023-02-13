from gen_functions import logged_in, load_css_file, multile_button_inline
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/forms.css")
load_css_file("styles/sidebar.css")


from main import credentials, authenticator, db
import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

add_indentation()

if not logged_in():
    switch_page("Mi perfil")

authenticator.logout("Salir", "sidebar")
try:
    username = st.session_state["username"]
    query_id = "SELECT id from users where username=%s"
    # Get id from database
    user_id = db.fetchone(query_id, (username,))[0]
    # If the user entered a new password, commit the change to the database
    if authenticator.reset_password(username, "Cambiar contraseña"):
        new_pass = credentials["usernames"][st.session_state["username"]][
            "password"
        ]
        query_pass = "UPDATE users SET pass=%s WHERE id=%s"
        db.commit(query_pass, (new_pass, user_id))
        st.success("Contraseña modificada correctamente")
except Exception as e:
    st.error(e)
# Show a button to go back to the login page
multile_button_inline(["Volver"],["Mi perfil"])
