import streamlit as st
import numpy as np
import pandas as pd
import datetime
import plotly.express as px
from plots import line_plot_unifiedhover, line_bar_plot_unifiedhover
from streamlit_extras.switch_page_button import switch_page
from gen_functions import  logged_in, df_with_all_dates_given_period, spanish_month_name, spanish_month_num, load_css_file, multile_button_inline
from st_pages import add_indentation
with open('error.txt', 'r') as error_file:
    error_text = error_file.read()
add_indentation()

if not logged_in():
    switch_page("Mi perfil")

try:

    authenticator = st.session_state["authenticator"]
    db = st.session_state["db"]
    load_css_file("styles/sidebar.css")



    authenticator.logout("Salir", "sidebar")
    username = st.session_state["username"]
    query_id = "SELECT id from users where username=%s"
    # Get id from database
    user_id = db.fetchone(query_id, (username,))[0]


    activos = ['Propiedad', 'Cuenta bancaria', 'Inversiones', 'Vehículo', 'Ahorros']
    pasivos = ['Deuda', 'Préstamo', 'Tarjeta de crédito', 'Hipoteca']

    with st.container():
        st.markdown("""<style>
                    .search-button {width: 25px;height: 25px;background-color: transparent;background-repeat: no-repeat;
                    border: none;cursor: pointer;overflow: hidden;outline: none;}
                    .search-button svg {width: 16px;height: 16px;}
                    </style>""", unsafe_allow_html=True)
        col1, col2 = st.columns([1.7,7])
        with col1:
            st.write("""<h1 style='text-align: left;'>Mi patrimonio</h1>""", unsafe_allow_html=True)
        with col2:
            st.markdown("""
                    <button class="search-button" title="La información mostrada es para los meses ya acabados.">
                        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
                    </button>""", unsafe_allow_html=True)

    # Radio button to choose between active or pasive

    tab1, tab2 = st.tabs(["General", "Detalle"])
    
    with tab1:
        with st.container():
            query = """SELECT LAST_DAY(CONCAT(year,"-",month,"-01")) as date, pasive, active, heritage FROM ( 
                SELECT COALESCE(pas.month, act.month) AS month, COALESCE(pas.year, act.year) AS year, COALESCE(pas.pasives, 0) as pasive, COALESCE(act.actives, 0) as active,
                COALESCE(act.actives, 0) - COALESCE(pas.pasives, 0) AS heritage
            FROM
                (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS pasives
                FROM pasives_movements
                WHERE user_id = %s
                GROUP BY month(date), year(date)) AS pas
            LEFT JOIN
                (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS actives
                FROM actives_movements
                WHERE user_id = %s
                GROUP BY month(date), year(date)) AS act
            ON pas.month = act.month AND pas.year = act.year
            UNION
            SELECT COALESCE(pas.month, act.month) AS month, COALESCE(pas.year, act.year) AS year, COALESCE(pas.pasives, 0) as pasive, COALESCE(act.actives, 0) as active,
                COALESCE(act.actives, 0) - COALESCE(pas.pasives, 0) AS heritage
            FROM
                (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS pasives
                FROM pasives_movements
                WHERE user_id = %s
                GROUP BY month(date), year(date)) AS pas
            RIGHT JOIN
                (SELECT month(date) AS month, year(date) AS year, sum(quantity) AS actives
                FROM actives_movements
                WHERE user_id = %s
                GROUP BY month(date), year(date)) AS act
            ON pas.month = act.month AND pas.year = act.year) AS main;"""
            query_results = db.fetchall(query, (user_id, user_id, user_id, user_id))
            
            if query_results == []:
                st.warning("No ha añadido ningún patrimonio.")
                multile_button_inline(["Añadir"], ["Activos y pasivos"])
                st.stop()

            df_heritage = df_with_all_dates_given_period(query_results, ["date"], 15, ["pasive", "active", "heritage"])
            df = df_heritage[["date","heritage"]]
            df["heritage"] = df["heritage"].astype(float)
            df_heritage["heritage"] = df_heritage["heritage"].replace(0,None)
            safes_last = df["heritage"].values[-1]
            safes_previous = df["heritage"].values[-2]
            date_last = df.iloc[-1,0]

            try:
                safes_last_perc = abs((safes_last - safes_previous)/safes_previous)*100
            except:
                safes_last_perc = 0
            safes_last_difference = safes_last - safes_previous
            st.write("<p style='text-align: center; font-size: 20px; font-weight:bold;'>Patrimonio de los últimos 15 meses</p>" , unsafe_allow_html=True)
            if safes_last_difference >= 0:
                st.write(f"""<p style='text-align: center;'>A día {date_last.day}-{spanish_month_name(date_last.month)}-{date_last.year} tu patrimonio neto tiene un valor de: 
                <span style='background-color:#48494b; color:#FFFFFF; font-weight:bold; font-style:italic;' >{round(safes_last,1)}€ </span>. 
                Esto es <span style='color:#538b01;'>+{round(safes_last_perc,1)}% </span> respecto al último mes.""" , unsafe_allow_html=True)
            else: 
                st.write(f"""<p style='text-align: center;'>A día {date_last.day}-{spanish_month_name(date_last.month)}-{date_last.year} tu patrimonio neto tiene un valor de: 
                <span style='background-color:#48494b; color:#FFFFFF; font-weight:bold; font-style:italic;' >{round(safes_last,1)}€ </span>. 
                Esto es <span style='color:#600b01;'>-{round(safes_last_perc,1)}% </span> respecto al último mes.""" , unsafe_allow_html=True)
            df_heritage["pasive"] = -1*df_heritage["pasive"]
            fig = line_bar_plot_unifiedhover(df_heritage, "date", ["pasive","active"], "heritage", "Fecha", ["Pasivo","Activo"],"Patrimonio Neto",
                        ["#9a5833","#0979b0"],'#b5aa8d', y_ticksuffix="€", height=370)  
            fig.update_xaxes(
                tick0="2000-01-31",
                dtick="M1",
                tickformat="%b\n%Y")

            fig.update_layout(
                xaxis=dict(
                    showline=False,
                    ticklen = 0),
                yaxis=dict(
                    showline=False,
                    ticklen = 0,
                    showticklabels=False)
                )
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0.05,
                    font = dict(size=14)
                    )
                )
            fig["data"][0]["connectgaps"] = True



            fig["data"][0]['line']['color'] = "#b5aa8d"
            fig["data"][0]['line']['width'] = 3
            fig["data"][0]['marker']['size'] = 9

            fig["data"][0]["showlegend"] = True
            fig["data"][1]["showlegend"] = True
            fig["data"][2]["showlegend"] = True

            fig["data"][0]['hovertemplate'] = 'Patrimonio: %{y:.1f}€<extra></extra>'
            fig["data"][1]['hovertemplate'] = 'Pasivo: %{y:.1f}€<extra></extra>'
            fig["data"][2]['hovertemplate'] = 'Activo: %{y:.1f}€<extra></extra>'

            last_value = df_heritage["heritage"].fillna(0).iloc[-1]
            annotations = [dict(xref='paper', x=0.95, y=last_value,
                            xanchor='left', yanchor='middle',
                            text=f'{last_value}€',
                            font=dict(family='Arial',
                                    size=16,
                                    color = "#b5aa8d"),
                            showarrow=False)]

            fig.update_layout(annotations=annotations)

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        with st.container():
            col1, col2,col3 = st.columns([5.5,1,0.6])
            with col1:
                option = st.selectbox("Selecciona los datos a consultar",["Activos","Pasivos"])
            if option=="Activos":
                table = "actives_movements"
                selection = activos
            else:
                table = "pasives_movements"
                selection = pasivos

            query = f"""SELECT LAST_DAY(CONCAT(year,"-",month,"-01")), category, quantity FROM (
            SELECT month(date) AS month, year(date) AS year, category, sum(quantity) AS quantity
                FROM {table}
                WHERE user_id = %s
                GROUP BY month(date), year(date), category) AS main"""
            query_results = db.fetchall(query, (user_id, ))
            if query_results == []:
                st.warning(f"No ha añadido ningún {option[:-1].lower()}")
                multile_button_inline(["Añadir"], ["Activos y pasivos"])
                st.stop()

            df = df_with_all_dates_given_period(query_results, ["date"], 15, ["category","quantity"])
            df["category"] = df["category"].replace(0,None)
            df["date"] = pd.to_datetime(df["date"])
            df["quantity"] = df["quantity"].astype(float)
            df["year"] = df["date"].dt.year
            df["month"] = df["date"].dt.month
            df = df.sort_values("date",ascending=False)

            df_pie = df.replace(0,np.nan).dropna()

            df_pie["month"] = df_pie["month"].apply(spanish_month_name, abbreviate=False)
            df_pie["month"] = df_pie["month"].str.capitalize()
            dates = (df_pie["month"] + " " + df_pie["year"].astype(str)).unique()
            mask = df_pie['date']<=datetime.datetime.now()
            most_race_date = df_pie[mask]["month"].values[0] + " " + df_pie[mask]["year"].values[0].astype(str)

            
            with col2:
                month_name, year = st.selectbox("Fecha", dates, index=list(dates).index(most_race_date)).split(" ")
                month = int(spanish_month_num(month_name))
                year = int(year)  

        with st.container():        
            col1, col2 = st.columns([3,1])
            
            with col1:
                fig = line_plot_unifiedhover(df, "date","quantity","Fecha","Valor", y_ticksuffix="€", height=400, series="category", text="category", series_label="Categoría")
                fig.update_traces(mode="markers+lines")
                fig.update_xaxes(
                    tick0="2000-01-31",
                    dtick="M1",
                    tickformat="%b\n%Y")
                fig.update_layout(legend=dict(
                    orientation="h",
                    font = dict(size=14),
                    yanchor="bottom",
                    y=1.02,
                    xanchor="left",
                    x=0.01
                ),
                legend_title_text='Categoría')
                colors = ["#1058ae","#c23c4f","#76138e","#02983e","#f94f6a"]

                for i in fig['data']:
                    index_pic = selection.index(i["legendgroup"]) 
                    i['line']['color'] = colors[index_pic]
                    i['line']['width'] = 3
                    i['marker']['size'] = 9

                annotations = []

                df_max = df[df["date"]==max(df["date"])]
                try:
                    for i in range(len(df_max)):
                        last_category = df_max.iloc[i,1]
                        last_value = df_max.fillna(0).iloc[i,2]

                        annotations.append(dict(xref='paper', x=0.95, y=last_value,
                                            xanchor='left', yanchor='middle',
                                            text=f'{last_value}€',
                                            font=dict(family='Arial',
                                                    size=16,
                                                    color = colors[selection.index(last_category)]),
                                            showarrow=False))
                    fig.update_layout(annotations=annotations)                
                except:
                    pass
                fig.update_traces(connectgaps=False)
                
                fig.update_traces(hovertemplate= 'Categoría: %{text}<br>Valor: %{y:.1f}€<extra></extra>')

                st.plotly_chart(fig, use_container_width=True)   
            
            with col2:
                df_pie_filtered = df_pie[(df_pie["year"]==year) & (df_pie["month"]==month_name)]
                fig = px.pie(df_pie_filtered, values='quantity', names='category',
                            height=350)
                fig.update_traces(textinfo='percent+label', hole=.5, textfont_size=17, marker=dict(colors=colors, 
                line=dict(color='#000000', width=.5)),
                    hovertemplate = "%{label}: <br>Valor: %{value}€ </br>Porcentaje : %{percent}")
                fig.update_layout(margin=dict(t=10, b=30, l=50, r=50))
                fig.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    showlegend = False,
                    title=None
                )
                fig.update_layout(hovermode="x unified", hoverlabel=dict(bgcolor='rgba(255,255,255,0.95)'))
                try:
                    fig["data"][0]["marker"]["colors"] = [colors[activos.index(i)] for i in fig["data"][0]["labels"]]
                except:
                    fig["data"][0]["marker"]["colors"] = [colors[pasivos.index(i)] for i in fig["data"][0]["labels"]]

                fig.update_layout(
                        annotations=[
                            dict(
                                text=f"{month_name.capitalize()} {year}:",
                                x=0.5,
                                y=0.55,
                                font_size=20,
                                showarrow=False,
                            ),
                            dict(
                                text=f'{round(sum(df_pie_filtered["quantity"]),1)}€',
                                x=0.5,
                                y=0.45,
                                font_size=20,
                                showarrow=False,
                            ),
                        ]
                    )
                st.plotly_chart(fig, use_container_width=True)   

except:
    st.write(error_text, unsafe_allow_html=True)
    