import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide", initial_sidebar_state="auto")

from gen_functions import logged_in, load_css_file
from streamlit_extras.badges import badge
from streamlit_extras.mention import mention
from markdownlit import mdlit
from st_pages import Page, show_pages, Section, add_indentation
from streamlit_extras.switch_page_button import switch_page
from PIL import Image
from init_app import authenticator
from init_exceptions import if_reconnect


load_css_file("styles/sidebar.css")
load_css_file("styles/main.css")
st.experimental_set_query_params()


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
if_reconnect()
authenticator = st.session_state["authenticator"]
db = st.session_state["db"]

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
    
    mdlit(f"""Con esta aplicación podrás [violet]controlar tus ingresos, gastos y tu patrimonio[/violet] de manera rápida e intuitiva gracias a sus [violet]paneles de control interactivos[/violet], los cuales podrás utilizar con tan solo unos simples clics.

[violet]"Finanzas Personales con Streamlit"[/violet] es el primer proyecto de mi nueva iniciativa "Conversaciones sobre Data & Analytics", una newsletter en la que semanalmente publicaré contenido sobre el sector de la analítica y la ciencia de datos. Te animo a echarle un vistazo al primer artículo y conocer de primera mano que cosillas vamos a hacer juntos -> [Presentación Newsletter](https://dataanalyticstalks.substack.com)

La ejecución de este primer proyecto, se presenta a lo largo de 5 artículos en los que explico de forma técnica y no tan técnica los componentes más útiles de Streamlit con el fin de entender el potencial y la usabilidad de esta herramienta. Los artículos son los siguientes:

1. @(⚙️)([violet]**Proceso CRISP-DM y configuración app en Streamlit**[/violet])(https://dataanalyticstalks.substack.com)
2. @(👤)(Portal para usuarios y conexión a BBDD)(https://dataanalyticstalks.substack.com)
3. @(🌍)(Formularios y gráficas y tablas interactivas)(https://dataanalyticstalks.substack.com)
4. @(📊)(Personalización de la app)(https://dataanalyticstalks.substack.com)
5. @(🟢)(Despligue de la app y conclusiones sobre Streamlit)(https://dataanalyticstalks.substack.com)

Además, el código de la aplicación se encuentra en GitHub para su consulta.

@(💻)(Código del proyecto)(https://github.com/ignareyesa/streamlit-personalfinance)

¡¡¡[violet]**Prueba la App**[/violet], pulsando en el siquiente enlace!!!."""
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



