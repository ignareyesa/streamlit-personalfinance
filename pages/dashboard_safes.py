from gen_functions import multile_button_inline, logged_in, df_with_all_dates_given_period, spanish_month_name, spanish_month_num, load_css_file
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")

from streamlit_toggle import st_toggle_switch
import numpy as np
from streamlit_extras.stoggle import stoggle
from init_app import db, authenticator
import pandas as pd
import plotly.express as px
import datetime
from plots import bar_plot_unifiedhover
from streamlit_extras.switch_page_button import switch_page
from st_pages import add_indentation

add_indentation()
load_css_file("styles/sidebar.css")


if not logged_in():
    switch_page("Mi perfil")

authenticator.logout("Salir", "sidebar")

# Get the user's ID from the database
username = st.session_state["username"]
query_id = "SELECT id from users where username=%s"
user_id = db.fetchone(query_id, (username,))[0]

with st.container():
    st.markdown("""<style>
                .search-button {width: 25px;height: 25px;background-color: transparent;background-repeat: no-repeat;
                border: none;cursor: pointer;overflow: hidden;outline: none;}
                .search-button svg {width: 16px;height: 16px;}
                </style>""", unsafe_allow_html=True)
    col1, col2 = st.columns([1.5,7])
    with col1:
        st.write("""<h1 style='text-align: left;'>Mis ahorros</h1>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
                <button class="search-button" title="La información mostrada es para los meses ya terminados.">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                </button>""", unsafe_allow_html=True)

with st.container():
    query = """SELECT LAST_DAY(CONCAT(year,"-",month,"-01")) as date, safes FROM ( 
        SELECT COALESCE(exp.month, inc.month) AS month, COALESCE(exp.year, inc.year) AS year, exp.expenses, inc.incomes,
        COALESCE(inc.incomes, 0) - COALESCE(exp.expenses, 0) AS safes
    FROM
        (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS expenses
        FROM expenses_movements
        WHERE user_id = %s
        GROUP BY month(date), year(date)) AS exp
    LEFT JOIN
        (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS incomes
        FROM incomes_movements
        WHERE user_id = %s
        GROUP BY month(date), year(date)) AS inc
    ON exp.month = inc.month AND exp.year = inc.year
    UNION
    SELECT COALESCE(exp.month, inc.month) AS month, COALESCE(exp.year, inc.year) AS year, exp.expenses, inc.incomes,
        COALESCE(inc.incomes, 0) - COALESCE(exp.expenses, 0) AS safes
    FROM
        (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS expenses
        FROM expenses_movements
        WHERE user_id = %s
        GROUP BY month(date), year(date)) AS exp
    RIGHT JOIN
        (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS incomes
        FROM incomes_movements
        WHERE user_id = %s
        GROUP BY month(date), year(date)) AS inc
    ON exp.month = inc.month AND exp.year = inc.year) AS main;"""
    query_results = db.fetchall(query, (user_id, user_id, user_id, user_id))

    if query_results == []:
        st.warning("No ha añadido ningún movimiento")
        multile_button_inline(["Añadir movimiento"], ["Movimientos"])
        st.stop()

    df_24 = df_with_all_dates_given_period(query_results, ["date"], 24, ["safes"])
    df_24["safes"] = df_24["safes"].astype(float)
    safes_12_mean = np.mean(df_24["safes"].values[12:])
    safes_last = df_24["safes"].values[-1]
    safes_last_difference = safes_last - safes_12_mean
    
    st.write("<p style='text-align: center; font-size: 20px; font-weight:bold;'>Ahorro de los últimos 24 meses</p>" , unsafe_allow_html=True)
    if safes_last_difference >= 0:
        st.write(f"""<p style='text-align: center;'>El último mes has ahorrado un total de 
        <span style='background-color:#48494b; color:#FFFFFF; font-weight:bold; font-style:italic;' >{round(safes_last,1)}€ </span>. 
        Esto es <span style='color:#538b01;'>+{abs(round(safes_last_difference,1))}€ </span> respecto a la media del último año.""" , unsafe_allow_html=True)
    else: 
        st.write(f"""<p style='text-align: center;'>El último mes has ahorrado un total de 
        <span style='background-color:#48494b; color:#FFFFFF; font-weight:bold; font-style:italic;' >{round(safes_last,1)}€ </span>. 
        Esto es <span style='color:#600b01;'>-{abs(round(safes_last_difference,1))}€ </span> respecto a la media del último año.""" , unsafe_allow_html=True)
    
    fig = bar_plot_unifiedhover(df_24, "date", "safes","Fecha","Ahorro", y_ticksuffix="€", height=370, text_auto=True)   
    fig.update_traces(marker_color = "#b5aa8d")
    fig.update_layout(
        xaxis=dict(
            showline=False,
            ticklen = 0),
        yaxis=dict(
            showline=False,
            ticklen = 0,
            showticklabels=False)
        )
    fig.update_xaxes(
        tick0="2000-01-31",
        dtick="M1",
        tickformat="%b\n%Y") 
    fig.update_traces(textfont_size=13, textangle=0, texttemplate = '%{y:.0f}€', textposition="inside", cliponaxis=False,)
    fig.update_traces(hovertemplate= 'Ahorros: %{y:.1f}€<extra></extra>')

    st.plotly_chart(fig, use_container_width=True)
    
with st.container():
    col1, col2 = st.columns([1,1])
    with col1:
        st.write("#### Distribuye el reparto de los ahorros")
        st.write("Selecciona el mes que quieres configurar")
    df_aux = pd.DataFrame(query_results, columns=["date","safes"])
    df_aux["date"] = pd.to_datetime(df_aux["date"])
    df_aux["year"] = df_aux["date"].dt.year
    df_aux["month"] = df_aux["date"].dt.month
    df_aux = df_aux.sort_values("date",ascending=False)
    df_aux["month"] = df_aux["month"].apply(spanish_month_name, abbreviate=False)
    df_aux["month"] = df_aux["month"].str.capitalize()

    dates = (df_aux["month"] + " " + df_aux["year"].astype(str)).unique()
    mask = df_aux['date']<=datetime.datetime.now()
    try:
        most_race_date = df_aux[mask]["month"].values[0] + " " + df_aux[mask]["year"].values[0].astype(str)
    except:
        most_race_date = df_aux["month"].values[0] + " " + df_aux["year"].values[0].astype(str)
    with col2:
        month_name, year = st.selectbox("Fecha", dates, index=list(dates).index(most_race_date)).split(" ")
        month = int(spanish_month_num(month_name))
        year = int(year)

    

with st.container():
    col1, col2 = st.columns([1,1])
    query = "select sum(quantity) from {} where user_id=%s and month(date)=%s and year(date)=%s"
    incomes = db.fetchone(query.format("incomes_movements"), (user_id, month, year))[0]
    
    # Check if current month
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month

    if not incomes: 
        incomes = 0
    query = "select sum(quantity) from {} where user_id=%s and month(date)=%s and YEAR(date)=%s"
    expenses = db.fetchone(query.format("expenses_movements"), (user_id, month, year))[0]
    if not expenses:
        expenses = 0
    safes = float(incomes - expenses)
    if safes<=0 or (year>=current_year and month >= current_month):
        with col1:
            pass
        if (year>=current_year and month >= current_month):
            with col2:
                st.info("El mes seleccionado todavía no ha finalizado, por lo que todavía no se pueden distribuir los ahorros.")
        else:
            with col2:
                st.info("En el mes seleccionado los gastos superan a los ingresos, no hay ahorros para distribuir.")
    else:
        with col1:
            st.write(f"<p style='text-align: center; font-size:18px;'>Distribución ahorros: {spanish_month_name(month).capitalize()}-{year}</p>", unsafe_allow_html=True)
        with col2:
            st.info(f"En el mes seleccionado tienes un total de {round(safes,1)}€ ahorrados para distribuir.")


with st.container():
    col1, col2 = st.columns([1,1])
    
    if safes<=0 or (year>=current_year and month >= current_month):
        with col1:
            pass

        with col2:
            cash = 0
            donate = 0
            investment = 0
            cash_toggle = st_toggle_switch(
                label="Efectivo",
                key="switch_1",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#b9b9b9",
                track_color="#f9f9f9",
            )
            
            investment_toggle = st_toggle_switch(
                label="Inversión",
                key="switch_2",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#b9b9b9",
                track_color="#f9f9f9",
            )

            donate_toggle = st_toggle_switch(
                label="Donación",
                key="switch_3",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#b9b9b9",
                track_color="#f9f9f9",
                )

            but = st.button("Actualizar", disabled = True)
        
    
    else:
        with col1:
            labels = ['Efectivo', 'Inversión', 'Donación']
            colors = ['mediumturquoise', 'darkorange', 'lightgreen']
            query = "select cash, investment, donation from safes_distribution where user_id=%s and month=%s and year=%s"
            safes_percentages = db.fetchall(query, (user_id, month, year))
            if safes_percentages != []:
                safes_percentages_df = pd.DataFrame(safes_percentages, columns=labels).T
                safes_percentages = list(safes_percentages_df.replace(0, np.nan).dropna().T.iloc[0].astype(float).values)
                labels =  list(safes_percentages_df.replace(0, np.nan).dropna().T.columns)
            else:
                safes_percentages = [1]
                labels = ["Efectivo"]
            sizes = [safes*perc for perc in safes_percentages]
            df = pd.DataFrame([labels,sizes], index=["safes_cat","values"]).T
            fig = px.pie(df, values='values', names='safes_cat',
                        height=350)
            fig.update_traces(textinfo='percent+label', hole=.3, textfont_size=17, marker=dict(colors=colors, line=dict(color='#000000', width=.5)),
                hovertemplate = "%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}")
            fig.update_layout(margin=dict(t=10, b=30, l=50, r=50))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                showlegend = False,
                title=None
            )
            fig.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.95)'))
            st.plotly_chart(fig, use_container_width=True) 

        with col2:
            cash = 0
            donate = 0
            investment = 0
            cash_toggle = st_toggle_switch(
                label="Efectivo",
                key="switch_1",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#009385",
                track_color="#b2dfdb"
            )
            if cash_toggle:
                cash = st.slider('', 0, 100, 100, key = "slider_1")/100
            
            investment_toggle = st_toggle_switch(
                label="Inversión",
                key="switch_2",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#009385",
                track_color="#b2dfdb"
            )
            if investment_toggle:
                investment = st.slider('', 0, 100, 0, key = "slider_2")/100

            donate_toggle = st_toggle_switch(
                label="Donación",
                key="switch_3",
                default_value=False,
                label_after=False,
                inactive_color="#b9b9b9",
                active_color="#009385",
                track_color="#b2dfdb"
            )
            if donate_toggle:
                donate = st.slider('', 0, 100, 0,  key = "slider_3")/100           
            
            stoggle(
                "Mostrar reparto",
                f"""

- Efectivo: {round(safes*cash,1)} €
- Inversión: {round(safes*investment,1)} €
- Donación: {round(safes*donate,1)} €
                """,
            )
            st.info(f"Total: {round(safes*(donate + investment + cash),1)}/{round(safes,1)}€")
            if (cash + investment + donate) != 1:
                st.button("Actualizar", disabled = True)
            else:
                if st.button("Actualizar"):
                    query = "SELECT id from safes_distribution WHERE user_id =%s and month=%s and year=%s"
                    safes_id = db.fetchone(query, (user_id, month, year))
                    if safes_id:
                        query = """UPDATE safes_distribution SET cash = %s, investment=%s, donation=%s WHERE ID=%s"""
                        db.commit(query, (cash, investment, donate, safes_id[0]))
                        st.experimental_rerun()
                    else:
                        query = """INSERT INTO safes_distribution (user_id, month, year, cash, investment, donation) VALUES (%s, %s, %s, %s, %s, %s);"""
                        db.commit(query, (user_id, month, year, cash, investment, donate))
                        st.experimental_rerun()