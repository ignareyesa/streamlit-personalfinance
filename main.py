import streamlit as st
from streamlit_extras.badges import badge
from streamlit_extras.mention import mention
from markdownlit import mdlit
from st_pages import Page, show_pages, Section, add_indentation
from gen_functions import logged_in, load_css_file
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
import json
import yaml
from yaml import CLoader as Loader
import authenticator as stauth
from database_connection.database import Database
from smtp_connection.email_client import EmailClient

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
st.experimental_set_query_params()
load_css_file("styles/sidebar.css")
load_css_file("styles/main.css")

with open("config.yaml") as file:
    config = yaml.load(file, Loader=Loader)

show_pages(
    [
        Page("main.py", "Inicio", ":house:"),
        Page("pages/login.py", "Mi perfil", ":bust_in_silhouette:"),
        Page("pages/forgot_pass.py", "", ""),
        Page("pages/forgot_user.py", " ", ""),
        Page("pages/sign_up.py", "  ", ""),
        Page("pages/reset_pass.py", "    ", ""),
        Section("Gastos e Ingresos", ":coin:"),
            Page("pages/dashboard_movements.py", "Seguimiento", ":bar_chart:"),
            Page("pages/consult_movements.py","Movimientos",":currency_exchange:"),
            Page("pages/dashboard_safes.py", "Ahorros", "💹"),
        Section("Patrimonio", ":bank:"),
            Page("pages/dashboard_heritage.py","Seguimiento patrimonio",":bar_chart:"),
            Page("pages/consult_heritage.py","Activos y pasivos",":currency_exchange:"),
        Section("Administración", ":card_file_box:"),
            Page("pages/profile_settings.py", "Configuración", ":gear:"),
    ]
)

add_indentation()

with open("predefined_queries.json") as file:
    json_loads = json.load(file)
    predefine_queries = list(json_loads.values())

db = Database(**st.secrets["mysql-dev"])
connection = db.connect()

# Commit predefined queries
for query in predefine_queries:
    try:
        db.commit(query)
    except Exception as e:
        raise ValueError(
            "Something went wrong during first connection to database: ", e)

users = db.fetchall("SELECT * from users;")
credentials = {
    "usernames": {i[2]: {"email": i[1], "name": i[3], "password": i[4]} for i in users}
}


authenticator = stauth.Authenticate(
    credentials,
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

smtp_connection = st.secrets["smtp_connection"]

smtp_server = smtp_connection["SMTP_SERVER"]
smtp_port = smtp_connection["SMTP_PORT"]
smtp_username = smtp_connection["SMTP_API_NAME"]
smtp_password = smtp_connection["SMTP_API_KEY"]
smtp_from_addr = smtp_connection["SMTP_FROM_ADDRESS"]
smtp_from_name = smtp_connection["SMTP_FROM_NAME"]

email_client = EmailClient(
    smtp_server=smtp_server,
    smtp_port=smtp_port,
    username=smtp_username,
    password=smtp_password,
    from_addr=smtp_from_addr,
    from_name=smtp_from_name,
)

if logged_in():
    authenticator.logout("Salir", "sidebar")

col1, col2, col3 = st.columns([1,0.2,0.9])
with col1:

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

Esta aplicación forma parte de una serie de proyectos publicados en mi newsletter, donde, semanalmente publico artículos prácticos que profundizan en proyectos relacionados con la analítica y la ciencia de datos. Si quieres conocer más a fondo la newsletter, aquí tienes el árticulo de presentación. -> [Enlace](https://dataanalyticstalks.substack.com)

[violet]**Finanzas Personales con Streamlit**[/violet] se trata del primer proyecto presentado, el cual se desarrolla a lo largo de 5 entregas, en las que se desarrolla esta aplicación haciendo uso del *framework* Streamlit de *Python*, herramienta que posteriormente utilizaremos para disponibilizar modelos de predicción y análisis al usuario.

Las cinco entregas de las que consta el proyecto son:

1. @(⚙️)([violet]**Inicio app y configuración Base de Datos**[/violet])(https://dataanalyticstalks.substack.com)
2. @(👤)(Portal para usuarios y creación de formularios)(https://dataanalyticstalks.substack.com)
3. @(🌍)(Tablas interactivas y personalización de la app)(https://dataanalyticstalks.substack.com)
4. @(📊)(Creación de Dashboards interactivos)(https://dataanalyticstalks.substack.com)
5. @(🟢)(Despligue de la app y conclusiones sobre Streamlit)(https://dataanalyticstalks.substack.com)


Puedes encontrar todo el código en GitHub, a lo largo de las entregas iremos explicando las diferentes partes del código.

@(💻)(Código del proyecto)(https://github.com/ignareyesa/streamlit-personalfinance)

[violet]**Prueba la App**[/violet], pulsando en el siquiente enlace (no hace falta registro)."""
    )

    start_now = st.button("👉 Comienza ya! ")
    if start_now:
        switch_page("Mi perfil")

mdlit("""
Para no perderte ningún proyecto, subscribete a la newsletter de forma gratuita. 

@(📰)(Mi newsletter)(https://dataanalyticstalks.substack.com/)

@(🧮)(Presentación newsletter e introducción este proyecto)(/)
    """
    )

with col3:
    image = Image.open('images/main_vector.jpeg')
    st.image(image, use_column_width=True)
    st.write(
            """<hr style='border-top: 3px solid #bbb; border-radius: 1px;'>""",
            unsafe_allow_html=True,
        )
    st.info('**[Web personal](https://ignacioreyesarboledas.tech/)**', icon="👨‍💻")
    st.info('**[LinkedIn](https://www.linkedin.com/in/ignacioreyesarboledas/)**', icon="🟦",)
    st.info('**[GitHub](https://github.com/ignareyesa/)**', icon="💼")



