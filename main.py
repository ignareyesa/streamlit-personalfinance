import streamlit as st
from init_app import authenticator
from streamlit_extras.badges import badge
from streamlit_extras.mention import mention
from markdownlit import mdlit
from st_pages import Page, show_pages, Section, add_indentation
from gen_functions import logged_in, load_css_file
from streamlit_extras.switch_page_button import switch_page
from PIL import Image

st.experimental_set_query_params()
st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/sidebar.css")
load_css_file("styles/main.css")

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

Esta aplicación forma parte de una serie de proyectos mensuales publicados en la newsletter de Ignacio. Todos [violet]**los proyectos tratan sobre
análitica avanzada de datos y la programación**[/violet]. La aplicación presente se ha realizado únicamente haciendo uso de Python🐍 y, en concreto de la librería
`streamlit`.

Concretamente, este proyecto se ha divido en 4 entregas:

1. @(⚙️)([violet]**Inicio app, configuración BBDD y portal entrada de usuarios**[/violet])(/) <- Estas aquí
2. @(📊)(Recogida de datos por usuario y creación de dashboard)(/)
3. @(🌍)(Despliegue en la web)(/)
4. @(🟢)(Expandir funcionalidades)(/)

Si te gusta lo que lees, [violet]**te animo a probar la app**[/violet], pulsando en el siquiente enlace (no hace falta registro)."""
    )

    start_now = st.button("👉 Comienza ya! ")
    if start_now:
        switch_page("Mi perfil")

    mdlit("""
No te vayas! Si crees que este u otros proyectos te pueden parecer interesantes, te dejo por aquí unos enlaces.

- @(📰)(Newsletter)(/)
- @(🧮)(Entregas newsletter dedicados a este proyecto)(/)
- @(💻)(Código del proyecto)(https://github.com/ignareyesa/streamlit-personalfinance)

    Y... algún enlace más por si quieres ponerte en contacto conmigo. 
    """
    )

with col3:
    image = Image.open('11235941_11124.jpeg')
    st.image(image, use_column_width=True)

col1, col2, col3, col4 = st.columns(4)

foot_mention_1 = mention(
    label="**[violet]Mi Web[/violet]**",
    icon="👨‍💻",
    url="https://ignacioreyesarboledas.tech/",
    write=False,
)
foot_mention_2 = mention(
    label="**[violet]Github[/violet]**",
    icon="github",
    url="https://github.com/ignareyesa/",
    write=False,
)
foot_mention_3 = mention(
    label="**[violet]LinkedIn[/violet]**",
    icon="🟦",
    url="https://www.linkedin.com/in/ignacioreyesarboledas/",
    write=False,
)

with col2:
    mdlit(f"{foot_mention_1}")

with col3:
    mdlit(f"{foot_mention_2}")

with col4:
    mdlit(f"{foot_mention_3}")


