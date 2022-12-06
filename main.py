import pandas as pd  
import streamlit as st  
import mysql.connector
import authenticator as stauth  
import yaml
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.badges import badge
from streamlit_extras.mention import mention
from markdownlit import mdlit
from st_pages import Page, show_pages
from yaml import CLoader as Loader


st.set_page_config(page_title="Tus finanzas", page_icon="🐍", layout="wide")

# Initialize connection.
def init_connection():
    return mysql.connector.connect(**st.secrets["mysql"])

conn = init_connection()

show_pages(
    [
        Page("main.py", "Inicio", ""),
        Page("pages/login.py","Comienza a explorar",""),  
        Page("pages/forgot_pass.py", "", ""),
        Page("pages/forgot_user.py", " ", ""),
        Page("pages/sign_up.py", "  ", ""),    
        Page("pages/reset_details.py","   ",""),
        Page("pages/reset_pass.py", "    ", ""),    
        Page("pages/reset_user.py", "     ", ""), 
    ]
)

# determine is user is logged_in or nor
def logged_in(session_state = st.session_state):
    if session_state["authentication_status"]:
        return True

# Perform query.
def run_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        all = cur.fetchall()
        cur.close()
        return all
        
def commit_query(query):
    with conn.cursor() as cur:
        cur.execute(query)
        conn.commit()
        cur.close()

with open('config.yaml') as file:
    config = yaml.load(file, Loader=Loader)
   
users = run_query("SELECT * from users;")
credentials = {"usernames": {i[2]:{"email":i[1],"name":i[3],"password":i[4]} for i in users}}
authenticator = stauth.Authenticate(
    credentials,
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
     config['preauthorized']
)

if logged_in():
    authenticator.logout('Cerrar sesión', 'sidebar')

ig_mention = mention(
    label="[violet]por Ignacio Reyes Arboledas[/violet] 👨‍💻",
    icon="",
    url="https://ignacioreyesarboledas.tech/",
    write=False,
)
stream_mention = mention(
    label="`streamlit`",
    icon="streamlit",  # Twitter is also featured!
    url="https://www.twitter.com/streamlit",
    write=False,
)

st.title("Finanzas Personales con Streamlit")

mdlit(f"{ig_mention}")

badge(type="github", name="ignareyesa/streamlit-personalfinance")

mdlit(f"""Esta app te permite [violet]**controlar tu ingresos, gastos e inversiones**[/violet] de una forma rápida e intuitiva mediante el uso de [violet]**dashboards interactivos**[/violet] con unos simples clicks.

Esta aplicación forma parte de una serie de proyectos mensuales publicados en la newsletter de Ignacio. Todos [violet]**los proyectos tratan sobre
análitica avanzada de datos y la programación**[/violet]. La aplicación presente se ha realizado únicamente haciendo uso de Python🐍 y, en concreto de la librería
`streamlit`.

Concretamente, este proyecto se ha divido en 4 entregas:

1. @(⚙️)([violet]**Inicio app, configuración BBDD y portal entrada de usuarios**[/violet])(/) <- Estas aquí
2. @(📊)(Recogida de datos por usuario y creación de dashboard)(/)
3. @(🌍)(Despliegue en la web)(/)
4. @(🟢)(Expandir funcionalidades)(/)

Si te gusta lo que lees, [violet]**te animo a probar la app**[/violet], pulsando en el siquiente enlace (no hace falta registro).""")

login = st.button("Comienza ya!")
if login:
    switch_page("Comienza a explorar")

mdlit(f"""No te vayas! Si crees que este u otros proyectos te pueden parecer interesantes, te dejo por aquí unos enlaces.

- @(📰)(Newsletter)(/)
- @(🧮)(Entregas newsletter dedicados a este proyecto)(/)
- @(💻)(Código del proyecto)(https://github.com/ignareyesa/streamlit-personalfinance)

Y... algún enlace más por si quieres ponerte en contacto conmigo. 
""")

col1, col2, col3 = st.columns(3)

foot_mention_1 = mention(
    label="**[violet]Mi Web[/violet]**",
    icon="👨‍💻",
    url="https://ignacioreyesarboledas.tech/",
    write=False)
foot_mention_2 = mention(
    label="**[violet]Github[/violet]**",
    icon="github",
    url="https://github.com/ignareyesa/",
    write=False)
foot_mention_3 = mention(
    label="**[violet]LinkedIn[/violet]**",
    icon="🟦",
    url="https://www.linkedin.com/in/ignacioreyesarboledas/",
    write=False)

with col1:
    mdlit(f"{foot_mention_1}")

with col2:
   mdlit(f"{foot_mention_2}")

with col3:
    mdlit(f"{foot_mention_3}")
