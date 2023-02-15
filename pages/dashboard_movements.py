from gen_functions import load_css_file
import streamlit as st

st.set_page_config(page_title="Finanzas Personales", page_icon="🐍", layout="wide")
load_css_file("styles/sidebar.css")

import pandas as pd
import datetime

from gen_functions import (
    logged_in,
    multile_button_inline,
    df_with_all_dates_given_period,
    spanish_month_num,
    spanish_month_name,
    prev_date,
    calculate_monthly_data,
    calculate_ytd_data
)
import plotly.express as px
import numpy as np
from plots import (
    kpi_single_indicator_comparison,
    bar_plot_horizontal_indicator,
    sankey_movements_plot,
    bar_plot_unifiedhover,
    kpi_double_indicator_comparison,
    line_plot_unifiedhover,
)
from mappers import expenses_subcategories_colors, income_subcategories_colors
from streamlit_option_menu import option_menu
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.mandatory_date_range import date_range_picker
from st_pages import add_indentation

st.experimental_set_query_params()
add_indentation()

if not logged_in():
    switch_page("Mi perfil")

authenticator = st.session_state["authenticator"]
db = st.session_state["db"]



authenticator.logout("Salir", "sidebar")

# Get the user's ID from the database
username = st.session_state["username"]
query_id = "SELECT id from users where username=%s"
user_id = db.fetchone(query_id, (username,))[0]

with st.container():
    st.write(
        "<h1 style='text-align: left;'>Seguimiento General</h1>", unsafe_allow_html=True
    )

# Get the user's income movements from the database
query_expenses = """SELECT date, category, subcategory, quantity, concept
            FROM expenses_movements
            WHERE user_id=%s
            ORDER BY date DESC;
        """
query_incomes = """SELECT date, category, subcategory, quantity, concept
            FROM incomes_movements
            WHERE user_id=%s
            ORDER BY date DESC;
        """

data_expenses = db.fetchall(query_expenses, (user_id,))
columns_expenses = db.get_columns(query_expenses, (user_id,))
data_incomes = db.fetchall(query_incomes, (user_id,))
columns_incomes = db.get_columns(query_incomes, (user_id,))

# Convert the data to a pandas DataFrame
df_expenses = pd.DataFrame(data=data_expenses, columns=columns_expenses)
df_expenses["date"] = pd.to_datetime(df_expenses["date"])
df_expenses["quantity"] = df_expenses["quantity"].astype(float)
df_expenses["year"] = df_expenses["date"].dt.year
df_expenses["month"] = df_expenses["date"].dt.month


# Convert the data to a pandas DataFrame
df_incomes = pd.DataFrame(data=data_incomes, columns=columns_incomes)
df_incomes["date"] = pd.to_datetime(df_incomes["date"])
df_incomes["quantity"] = df_incomes["quantity"].astype(float)
df_incomes["year"] = df_incomes["date"].dt.year
df_incomes["month"] = df_incomes["date"].dt.month

df_all = pd.concat([df_incomes, df_expenses])

if len(df_all)==0:
    st.warning("No ha añadido ningún movimiento")
    multile_button_inline(["Añadir movimiento"], ["Movimientos"])
    st.stop()

tab1, tab2, tab3 = st.tabs(["General", "Detalle", "Extra: Flujo de gastos e ingresos"])

with tab1:
    df_all["month"] = df_all["month"].apply(spanish_month_name, abbreviate=False)
    df_all["month"] = df_all["month"].str.capitalize()
    df_all = df_all.sort_values("date", ascending = False)
    dates = (df_all["month"] + " " + df_all["year"].astype(str)).unique()
    mask = df_all['date']<=datetime.datetime.now()
    most_race_date = df_all[mask]["month"].values[0] + " " + df_all[mask]["year"].values[0].astype(str)
    
    
    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        month_name, year = st.selectbox("Fecha", dates, index=list(dates).index(most_race_date)).split(" ")
        month = int(spanish_month_num(month_name))
        year = int(year)

    with st.container():
        (
            cont1_col1,
            cont1_col2,
            cont1_col3,
            cont1_col4,
            cont1_col5,
            cont1_col6,
        ) = st.columns([1.15, 1.15, 1, 3, 1.5, 1.5])
        with cont1_col4:
            st.write(f"## Datos a {month_name} {year}")

        with cont1_col1:
            multile_button_inline(
                ["Mi patrimonio"],
                ["Seguimiento patrimonio"],
                html_class="patrimony",
                css="styles/text_link.css",
            )

        with cont1_col2:
            multile_button_inline(
                ["Mis ahorros"],
                ["Ahorros"],
                html_class="safes",
                css="styles/text_link.css",
            )

    ytd_expenses, ytd_last_expenses = calculate_ytd_data(df_expenses, year=year, month=month)
    mtd_expenses, mtd_last_expenses, mtd_yoy_expenses = calculate_monthly_data(
        df_expenses, year=year, month=month
    )
    ytd_incomes, ytd_last_incomes = calculate_ytd_data(df_incomes, year=year, month=month)
    mtd_incomes, mtd_last_incomes, mtd_yoy_incomes = calculate_monthly_data(
        df_incomes, year=year, month=month
    )

    with st.container():
        cont2_col1, cont2_col2, cont2_col3, cont2_col4, cont2_col5 = st.columns(
            [3.1, 1.6, 1.6, 3.1, 3.1]
        )

        with cont2_col3:
            st.write(
                "<h3 style='text-align: left; vertical-align: center'>Anual<span style='font-size: 1rem;font-weight: 400;'>(acumulado)</span> </h3>",
                unsafe_allow_html=True,
            )

        with cont2_col4:
            fig = kpi_single_indicator_comparison(
                ytd_expenses,
                ytd_last_expenses,
                f"{year} YTD",
                f"{year-1} YTD",
                "Gastos",
                False,
                "percent",
                True,
            )
            st.pyplot(fig)

        with cont2_col5:
            fig = kpi_single_indicator_comparison(
                ytd_incomes,
                ytd_last_incomes,
                f"{year} YTD",
                f"{year-1} YTD",
                "Ingresos",
                True,
                "percent",
                True,
            )
            st.pyplot(fig)

        with cont2_col1:
            query = """SELECT LAST_DAY(CONCAT(year,"-",month,"-01")) as date, heritage FROM ( 
                SELECT COALESCE(pas.month, act.month) AS month, COALESCE(pas.year, act.year) AS year, pas.pasives, act.actives,
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
            SELECT COALESCE(pas.month, act.month) AS month, COALESCE(pas.year, act.year) AS year, pas.pasives, act.actives,
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

            query_results = db.fetchall(query, (user_id, user_id, user_id, user_id))
            heritage_last_15 = df_with_all_dates_given_period(
                query_results, ["date"], 15, ["heritage"]
            )
            heritage_last_12 = heritage_last_15.iloc[2:]
            heritage_last_12["heritage"] = heritage_last_12["heritage"].astype(float)
            heritage_last_12["heritage"] = heritage_last_12["heritage"].replace(0, None)

            heritage_last = heritage_last_12["heritage"].values[-1]
            heritage_previous = heritage_last_12["heritage"].values[-2]
            heritage_yoy = heritage_last_12["heritage"].values[0]

            heritage_date = spanish_month_name(heritage_last_12["date"].dt.month.values[-1]) + " " + str(heritage_last_12["date"].dt.year.values[-1])


            fig = kpi_double_indicator_comparison(
                heritage_last,
                heritage_previous,
                heritage_yoy,
                heritage_date.capitalize(),
                "Mes, Año anterior",
                "Patrimonio",
                True,
                True,
                background_color="#FFB888",
            )
            st.pyplot(fig)

    with st.container():
        cont2_col1, cont2_col2, cont2_col3, cont2_col4, cont2_col5 = st.columns(
            [3.1, 1.6, 1.6, 3.1, 3.1]
        )

        with cont2_col3:
            st.write(
                "<h3 style='text-align: left; vertical-align: center'>Mensual</h3>",
                unsafe_allow_html=True,
            )
        
        with cont2_col4:
            fig = bar_plot_horizontal_indicator(
                3,
                [mtd_yoy_expenses, mtd_last_expenses, mtd_expenses],
                [f"{month_name[:3]} {year-1}", f"{prev_date(month, year, True)}", "Mes sel."],
                "#9a5833",
            )
            st.pyplot(fig)

        with cont2_col5:
            fig = bar_plot_horizontal_indicator(
                3,
                [mtd_yoy_incomes, mtd_last_incomes, mtd_incomes],
                [f"{month_name[:3]} {year-1}", f"{prev_date(month, year, True)}", "Mes sel."],
                "#0979b0",True,
            )
            st.pyplot(fig)

        with cont2_col1:
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
            safes_last_12 = df_with_all_dates_given_period(
                query_results, ["date"], 12, ["safes"]
            )
            safes_last_12["safes"] = safes_last_12["safes"].astype(float)
            safes_last_12["safes"] = safes_last_12["safes"].replace(0, None)
            safes_last = safes_last_12["safes"].values[-1]
            safes_previous = safes_last_12["safes"].values[-2]
            safes_yoy = safes_last_12["safes"].values[0]
            safes_date = spanish_month_name(safes_last_12["date"].dt.month.values[-1]) + " " + str(safes_last_12["date"].dt.year.values[-1])
            
            fig = kpi_double_indicator_comparison(
                safes_last,
                safes_previous,
                safes_yoy,
                safes_date.capitalize(),
                "Mes, Año anterior",
                "Ahorros",
                True,
                True,
                background_color="#b1d4e0",
            )
            st.pyplot(fig)

    with st.container():
        st.write(
            """<hr style='border-top: 6px solid #bbb; border-radius: 3px;'>""",
            unsafe_allow_html=True,
        )

            
    with st.container():
        cont4_col1, cont4_col2, cont4_col3 = st.columns([4.5, 5.3, 5.3])

        query_inc = """SELECT LAST_DAY(CONCAT(year(date),"-",month(date),"-01")) AS date, sum(quantity) AS incomes
        FROM incomes_movements
        WHERE user_id = %s AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
        GROUP BY month(date), year(date)"""
        query_results = db.fetchall(query_inc, (user_id,))
        # Generate a list of dates representing all of the months within the last 24 months
        df_bars_incomes = df_with_all_dates_given_period(
            query_results, ["date"], 15, ["incomes"], include_actual=True
        )

        query_exp = """SELECT LAST_DAY(CONCAT(year(date),"-",month(date),"-01")) AS date, sum(quantity) AS expenses
        FROM expenses_movements
        WHERE user_id = %s AND date >= DATE_SUB(CURRENT_DATE(), INTERVAL 2 YEAR)
        GROUP BY month(date), year(date)"""
        query_results = db.fetchall(query_exp, (user_id,))
        df_bars_expenses = df_with_all_dates_given_period(
            query_results, ["date"], 15, ["expenses"], include_actual=True
        )

        with cont4_col1:
            fig = line_plot_unifiedhover(
                heritage_last_12,
                "date",
                "heritage",
                "Fecha",
                "Patrimonio Neto",
                y_ticksuffix="€",
                height=340,
            )
            fig["data"][0]["line"]["color"] = "#FFB888"
            fig["data"][0]["line"]["width"] = 3
            fig["data"][0]["marker"]["size"] = 9
            fig.update_xaxes(tick0="2000-01-31", dtick="M1", tickformat="%b\n%Y")
            fig.update_traces(connectgaps=True)
            fig.update_traces(hovertemplate="Patrimonio: %{y:.1f}€<extra></extra>")

            st.write(
                "<h4 style='text-align: center; font-weight: 400; color: rgb(49, 51, 63); padding: 0px; margin: 0px; line-height: 0.5; font-size: 1.3rem;'>Evolución patrimonio </h4>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        with cont4_col2:
            fig = bar_plot_unifiedhover(
                df_bars_expenses,
                x="date",
                y="expenses",
                x_label="Fecha",
                y_label="Gastos",
                y_ticksuffix="€",
                height=340,
                text_auto=True,
            )
            fig.update_traces(marker_color="#9a5833")
            fig.update_xaxes(tick0="2000-01-31", dtick="M1", tickformat="%b\n%Y")
            fig.update_yaxes(
                range=[
                    0,
                    max(
                        [
                            max(df_bars_incomes["incomes"]),
                            max(df_bars_expenses["expenses"]),
                        ]
                    ),
                ]
            )
            fig.update_traces(
                textfont_size=13,
                textangle=0,
                texttemplate="%{y:.0f}€",
                textposition="outside",
                cliponaxis=False,
            )
            fig.update_traces(hovertemplate="Gastos: %{y:.1f}€<extra></extra>")
            st.write(
                "<h4 style='text-align: center; font-weight: 400; color: rgb(49, 51, 63); padding: 0px; margin: 0px; line-height: 0.5; font-size: 1.3rem;'>Evolución gastos</h4>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig, use_container_width=True)

        with cont4_col3:
            fig = bar_plot_unifiedhover(
                df_bars_incomes,
                x="date",
                y="incomes",
                x_label="Fecha",
                y_label="Ingresos",
                y_ticksuffix="€",
                height=340,
                text_auto=True,
            )
            fig.update_traces(marker_color="#0979b0")
            fig.update_xaxes(tick0="2000-01-31", dtick="M1", tickformat="%b\n%Y")
            fig.update_yaxes(
                range=[
                    0,
                    max(
                        [
                            max(df_bars_incomes["incomes"]),
                            max(df_bars_expenses["expenses"]),
                        ]
                    ),
                ]
            )
            fig.update_traces(
                textfont_size=13,
                textangle=0,
                texttemplate="%{y:.0f}€",
                textposition="outside",
                cliponaxis=False,
            )
            fig.update_traces(hovertemplate="Ingresos: %{y:.1f}€<extra></extra>")
            st.write(
                "<h4 style='text-align: center; font-weight: 400; color: rgb(49, 51, 63); padding: 0px; margin: 0px; line-height: 0.5; font-size: 1.3rem;'>Evolución ingresos</h4>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    dates = (df_all["month"] + " " + df_all["year"].astype(str)).unique()

    col1, col2, col3, col4, col5, col6, col7 = st.columns(7)
    with col1:
        month_name, year = st.selectbox("Fecha", dates, index=list(dates).index(most_race_date), key = "tab2main").split(" ")
        month_det_main = int(spanish_month_num(month_name))
        year_det_main = int(year)

    incomes_last = round(
        sum(
            df_incomes[(df_incomes["year"] == year_det_main) & (df_incomes["month"] == month_det_main)][
                "quantity"
            ]
        ),
        1,
    )
    expenses_last = round(
        sum(
            df_expenses[
                (df_expenses["year"] == year_det_main) & (df_expenses["month"] == month_det_main)
            ]["quantity"]
        ),
        1,
    )

    selected = option_menu(None, [f"Ingresos: {incomes_last} €", f"Gastos: {expenses_last} €"],
        icons=['piggy-bank', 'wallet2'], 
        menu_icon="cast", default_index=0, orientation="horizontal",
        styles={
        "container": {"width":"40%"},
        "nav": {"margin-left": "1rem", "margin-right": "1rem"}})

    if selected == f"Ingresos: {incomes_last} €":
        selection = "incomes"
        df_incomes_grouped = (
            df_incomes.groupby(["month", "year", "category"])
            .sum()["quantity"]
            .reset_index()
        )
        # Main
        with st.container():
            col1, col2 = st.columns([1.3, 1])

            # Main pie
            with col1:
                df_incomes_last = df_incomes_grouped[
                    (df_incomes_grouped["year"] == year_det_main)
                    & (df_incomes_grouped["month"] == month_det_main)
                ]
                fig = px.pie(
                    df_incomes_last, values="quantity", names="category", color="category", height=430, color_discrete_map=income_subcategories_colors
                )
                fig.update_traces(
                    textinfo="percent+label",
                    hole=0.00,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                # fig.update_layout(margin=dict(t=10, b=30, l=50, r=50))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                st.plotly_chart(fig, use_container_width=True)

            # Top table
            with col2:
                df_table = df_incomes[
                    (df_incomes["year"] == year_det_main)
                    & (df_incomes["month"] == month_det_main)
                ].sort_values("quantity", ascending=False)
                df_table = df_table[
                    ["date", "category", "subcategory", "concept", "quantity"]
                ]
                df_table["quantity"] = df_table["quantity"].astype(str) + " €"
                df_table.columns = [
                    "Fecha",
                    "Categoría",
                    "Subcategoría",
                    "Concepto",
                    "Cantidad",
                ]
                st.write("#### Principales ingresos")
                table = df_table.to_html(index=False, classes="zui-table")
                style = """.zui-table {
                    border: solid 1px #DDEEEE;
                    border-collapse: collapse;
                    border-spacing: 0;
                    font: normal 13px Arial, sans-serif;
                    }
                    .zui-table thead th {
                    background-color: #DDEFEF;
                    border: solid 1px #DDEEEE;
                    color: #336B6B;
                    padding: 10px;
                    text-align: left;
                    text-shadow: 1px 1px 1px #fff;
                    }
                    .zui-table tbody td {
                    border: solid 1px #DDEEEE;
                    color: #333;
                    padding: 10px;
                    text-shadow: 1px 1px 1px #fff;"""
                st.components.v1.html(
                    """<html><style>{}</style><body>{}</body></html>""".format(
                        style, table
                    )
                )

        with st.expander("Evolución ingresos"):
            col1, col2 = st.columns([2, 5])
            with col1:
                how_sel = st.selectbox(
                    "¿Como quieres mostrar el gráfico?",
                    ["Por años", "Por categorías"],
                    key="how_incomes",
                    help="Por años: Cada línea representará la evolución por año; Por categorías: Cada línea representará la evolución por categoría"
                )
                if how_sel == "Por años":
                    categories_sel = st.selectbox(
                        "Categoría",
                        ["Todas"] + list(df_incomes_grouped["category"].unique()),
                        index=0,
                        key="cat_sel_incomes",
                        help = "Seleccione la categoría para filtrar."
                    )
                    try:
                        years_sel = st.multiselect(
                            "Año(s)",
                            sorted(df_incomes_grouped["year"].unique(), reverse=True),
                            default=[year_det_main],
                            key="year_mulsel_expenses",
                            help = "Seleccione los años a mostrar."
                        )
                    except:
                        years_sel = st.multiselect(
                            "Año(s)",
                            sorted(df_incomes_grouped["year"].unique(), reverse=True),
                            key="year_mulsel_expenses",
                            help = "Seleccione los años a mostrar."
                        )
                    if categories_sel == "Todas":
                        df_incomes_selected = df_incomes_grouped[
                            (df_incomes_grouped["year"].isin(years_sel))
                        ]
                    else:
                        df_incomes_selected = df_incomes_grouped[
                            (df_incomes_grouped["category"] == categories_sel)
                            & (df_incomes_grouped["year"].isin(years_sel))
                        ]
                    df_incomes_selected = (
                        df_incomes_selected.groupby(["month", "year"])
                        .sum()["quantity"]
                        .reset_index()
                    )
                    fig = line_plot_unifiedhover(
                        df_incomes_selected,
                        "month",
                        "quantity",
                        "Mes",
                        "Cantidad",
                        y_ticksuffix="€",
                        series="year",
                        series_label="Año",
                        text="year",
                        height=370,
                    )
                    fig_legend_title = "Año"
                if how_sel == "Por categorías":
                    years_sel = st.selectbox(
                        "Año",
                        df_incomes_grouped["year"].unique(),
                        key="year_sel_incomes",
                        help = "Seleccione el año para filtrar."
                    )
                    categories_sel = st.multiselect(
                        "Categoría(s)",
                        df_incomes_grouped["category"].unique(),
                        default=df_incomes_grouped["category"].unique()[:3],
                        key="cat_mulsel_incomes",
                        help = "Seleccione las categorías a mostrar."
                    )
                    df_incomes_selected = df_incomes_grouped[
                        (df_incomes_grouped["category"].isin(categories_sel))
                        & (df_incomes_grouped["year"] == years_sel)
                    ]
                    df_incomes_selected = (
                        df_incomes_selected.groupby(["month", "category"])
                        .sum()["quantity"]
                        .reset_index()
                    )
                    fig = line_plot_unifiedhover(
                        df_incomes_selected,
                        "month",
                        "quantity",
                        "Mes",
                        "Cantidad",
                        y_ticksuffix="€",
                        series="category",
                        series_label="Categoría",
                        text="category",
                        color_discrete_map=income_subcategories_colors,
                        height=370,
                    )
                    fig_legend_title = "Categoría"

            with col2:
                fig.update_traces(mode="markers+lines")
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        font=dict(size=14),
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0.01,
                    ),
                    legend_title_text=fig_legend_title,
                )

                for i in fig["data"]:
                    i["line"]["width"] = 3
                    i["marker"]["size"] = 9

                fig.update_traces(connectgaps=False)
                fig.update_traces(
                    hovertemplate="Categoría: %{text}<br>Valor: %{y:.1f}€<extra></extra>"
                )
                fig.update_layout(
                    xaxis = dict(
                        tickmode = 'array',
                        tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        ticktext = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        with st.expander("Comparativa ingresos entre periodos"):
            col1, col2, col3 = st.columns([4,2,4])
            with col1:
                month_name, year = st.selectbox("Fecha", dates, index=0, key = "tab2comp1").split(" ")
                month_det_pie1_comp = int(spanish_month_num(month_name))
                year_det_pie1_comp = int(year)


                df_incomes_pie = df_incomes_grouped[
                    (df_incomes_grouped["year"] == year_det_pie1_comp)
                    & (df_incomes_grouped["month"] == month_det_pie1_comp)
                ]
                fig_pie1 = px.pie(
                    df_incomes_pie, values="quantity", names="category", color="category", height=430, color_discrete_map=income_subcategories_colors
                )
                fig_pie1.update_traces(
                    textinfo="percent+label",
                    hole=0.75,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                fig_pie1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig_pie1.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                fig_pie1.update_layout(
                    annotations=[
                        dict(
                            text=f"{month_name.capitalize()} {year}:",
                            x=0.5,
                            y=0.55,
                            font_size=20,
                            showarrow=False,
                        ),
                        dict(
                            text=f'{round(sum(df_incomes_pie["quantity"]),1)}€',
                            x=0.5,
                            y=0.45,
                            font_size=20,
                            showarrow=False,
                        ),
                    ]
                )
            with col3:

                month_name, year = st.selectbox("Fecha", dates, index=0, key = "tab2comp2").split(" ")
                month_det_pie2_comp = int(spanish_month_num(month_name))
                year_det_pie2_comp = int(year)
                df_incomes_pie = df_incomes_grouped[
                    (df_incomes_grouped["year"] == year_det_pie2_comp)
                    & (df_incomes_grouped["month"] == month_det_pie2_comp)
                ]
                fig_pie2 = px.pie(
                    df_incomes_pie, values="quantity", names="category", color="category", height=430, color_discrete_map=income_subcategories_colors
                )
                fig_pie2.update_traces(
                    textinfo="percent+label",
                    hole=0.75,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                fig_pie2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig_pie2.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                fig_pie2.update_layout(
                    annotations=[
                        dict(
                            text=f"{month_name.capitalize()} {year}:",
                            x=0.5,
                            y=0.55,
                            font_size=20,
                            showarrow=False,
                        ),
                        dict(
                            text=f'{round(sum(df_incomes_pie["quantity"]),1)}€',
                            x=0.5,
                            y=0.45,
                            font_size=20,
                            showarrow=False,
                        ),
                    ]
                )
        
                with col1:
                    st.plotly_chart(fig_pie1, use_container_width=True)
                with col3:
                    st.plotly_chart(fig_pie2, use_container_width=True)

    if selected == f"Gastos: {expenses_last} €":
        selection = "expenses"
        df_expenses_grouped = (
            df_expenses.groupby(["month", "year", "category"])
            .sum()["quantity"]
            .reset_index()
        )
        # Main detail
        with st.container():
            col1, col2 = st.columns([1, 1])

            with col1:
                df_expenses_last = df_expenses_grouped[
                    (df_expenses_grouped["year"] == year_det_main)
                    & (df_expenses_grouped["month"] == month_det_main)
                ]
            col1, col2 = st.columns([1.3, 1])
            # Pie
            with col1:
                fig = px.pie(
                    df_expenses_last, values="quantity", names="category", color="category", height=430, color_discrete_map=expenses_subcategories_colors
                )
                fig.update_traces(
                    textinfo="percent+label",
                    hole=0.00,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                st.plotly_chart(fig, use_container_width=True)
            # Table top
            with col2:
                df_table = df_expenses[
                    (df_expenses["year"] == year_det_main)
                    & (df_expenses["month"] == month_det_main)
                ].sort_values("quantity", ascending=False)
                df_table = df_table[
                    ["date", "category", "subcategory", "concept", "quantity"]
                ]
                df_table["quantity"] = df_table["quantity"].astype(str) + " €"
                df_table.columns = [
                    "Fecha",
                    "Categoría",
                    "Subcategoría",
                    "Concepto",
                    "Cantidad",
                ]
                st.write("#### Principales gastos")
                table = df_table.head(5).to_html(index=False, classes="zui-table")
                style = """.zui-table {
        border: solid 1px #DDEEEE;
        border-collapse: collapse;
        border-spacing: 0;
        font: normal 13px Arial, sans-serif;
        }
        .zui-table thead th {
        background-color: #DDEFEF;
        border: solid 1px #DDEEEE;
        color: #336B6B;
        padding: 10px;
        text-align: left;
        text-shadow: 1px 1px 1px #fff;
        }
        .zui-table tbody td {
        border: solid 1px #DDEEEE;
        color: #333;
        padding: 10px;
        text-shadow: 1px 1px 1px #fff;"""
                st.components.v1.html(
                    """<html><style>{}</style><body>{}</body></html>""".format(
                        style, table
                    ),
                    height=350,
                )

        with st.expander("Evolución gastos"):
            col1, col2 = st.columns([2, 5])
            with col1:
                how_sel = st.selectbox(
                    "¿Como quieres mostrar el gráfico?",
                    ["Por años", "Por categorías"],
                    key="how_expenses",
                    help="Por años: Cada línea representará la evolución por año; Por categorías: Cada línea representará la evolución por categoría"
                )
                if how_sel == "Por años":
                    categories_sel = st.selectbox(
                        "Categoría",
                        ["Todas"] + list(df_expenses_grouped["category"].unique()),
                        index=0,
                        key="cat_sel_expenses",
                        help = "Seleccione la categoría para filtrar."
                    )
                    try:
                        years_sel = st.multiselect(
                            "Año(s)",
                            sorted(df_expenses_grouped["year"].unique(), reverse=True),
                            default=[year_det_main],
                            key="year_mulsel_expenses",
                            help = "Seleccione los años a mostrar."
                        )
                    except:
                        years_sel = st.multiselect(
                            "Año(s)",
                            sorted(df_expenses_grouped["year"].unique(), reverse=True),
                            key="year_mulsel_expenses",
                            help = "Seleccione los años a mostrar."
                        )
                    if categories_sel == "Todas":
                        df_expenses_selected = df_expenses_grouped[
                            (df_expenses_grouped["year"].isin(years_sel))
                        ]
                    else:
                        df_expenses_selected = df_expenses_grouped[
                            (df_expenses_grouped["category"] == categories_sel)
                            & (df_expenses_grouped["year"].isin(years_sel))
                        ]
                    df_expenses_selected = (
                        df_expenses_selected.groupby(["month", "year"])
                        .sum()["quantity"]
                        .reset_index()
                    )
                    fig = line_plot_unifiedhover(
                        df_expenses_selected,
                        "month",
                        "quantity",
                        "Mes",
                        "Cantidad",
                        y_ticksuffix="€",
                        series="year",
                        series_label="Año",
                        text="year",
                        height=370,
                    )
                    fig_legend_title = "Año"
                if how_sel == "Por categorías":
                    years_sel = st.selectbox(
                        "Año",
                        sorted(df_expenses_grouped["year"].unique(), reverse=True),
                        index=0,
                        key="year_sel_expenses",
                        help = "Seleccione el año para filtrar."
                    )
                    categories_sel = st.multiselect(
                        "Categoría(s)",
                        df_expenses_grouped["category"].unique(),
                        default=df_expenses_grouped["category"].unique()[:3],
                        key="cat_mulsel_expenses",
                        help = "Seleccione las categorías a mostrar."
                    )
                    df_expenses_selected = df_expenses_grouped[
                        (df_expenses_grouped["category"].isin(categories_sel))
                        & (df_expenses_grouped["year"] == years_sel)
                    ]
                    df_expenses_selected = (
                        df_expenses_selected.groupby(["month", "category"])
                        .sum()["quantity"]
                        .reset_index()
                    )
                    fig = line_plot_unifiedhover(
                        df_expenses_selected,
                        "month",
                        "quantity",
                        "Mes",
                        "Cantidad",
                        y_ticksuffix="€",
                        series="category",
                        series_label="Categoría",
                        text="category",
                        color_discrete_map=expenses_subcategories_colors,
                        height=370,
                    )
                    fig_legend_title = "Categoría"

            with col2:
                fig.update_traces(mode="markers+lines")
                fig.update_layout(
                    legend=dict(
                        orientation="h",
                        font=dict(size=14),
                        yanchor="bottom",
                        y=1.02,
                        xanchor="left",
                        x=0.01,
                    ),
                    legend_title_text=fig_legend_title,
                )

                for i in fig["data"]:
                    i["line"]["width"] = 3
                    i["marker"]["size"] = 9

                fig.update_traces(connectgaps=False)
                fig.update_traces(
                    hovertemplate="Categoría: %{text}<br>Valor: %{y:.1f}€<extra></extra>"
                )
                fig.update_layout(
                    xaxis = dict(
                        tickmode = 'array',
                        tickvals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
                        ticktext = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']
                    )
                )

                st.plotly_chart(fig, use_container_width=True)

        with st.expander("Comparativa gastos entre periodos"):
            col1, col2, col3 = st.columns([4,2,4])
            with col1:
                month_name, year = st.selectbox("Fecha", dates, index=0, key = "tab2comp1").split(" ")
                month_det_pie1_comp = int(spanish_month_num(month_name))
                year_det_pie1_comp = int(year)


                df_expenses_pie = df_expenses_grouped[
                    (df_expenses_grouped["year"] == year_det_pie1_comp)
                    & (df_expenses_grouped["month"] == month_det_pie1_comp)
                ]
                fig_pie1 = px.pie(
                    df_expenses_pie, values="quantity", names="category", color="category", height=430, color_discrete_map=expenses_subcategories_colors
                )
                fig_pie1.update_traces(
                    textinfo="percent+label",
                    hole=0.75,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                fig_pie1.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig_pie1.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                fig_pie1.update_layout(
                    annotations=[
                        dict(
                            text=f"{month_name.capitalize()} {year}:",
                            x=0.5,
                            y=0.55,
                            font_size=20,
                            showarrow=False,
                        ),
                        dict(
                            text=f'{round(sum(df_expenses_pie["quantity"]),1)}€',
                            x=0.5,
                            y=0.45,
                            font_size=20,
                            showarrow=False,
                        ),
                    ]
                )
            with col3:
                month_name, year = st.selectbox("Fecha", dates, index=0, key = "tab2comp2").split(" ")
                month_det_pie2_comp = int(spanish_month_num(month_name))
                year_det_pie2_comp = int(year)
                df_expenses_pie = df_expenses_grouped[
                    (df_expenses_grouped["year"] == year_det_pie2_comp)
                    & (df_expenses_grouped["month"] == month_det_pie2_comp)
                ]
                fig_pie2 = px.pie(
                    df_expenses_pie, values="quantity", names="category", color="category", height=430, color_discrete_map=expenses_subcategories_colors
                )
                fig_pie2.update_traces(
                    textinfo="percent+label",
                    hole=0.75,
                    textfont_size=13,
                    marker=dict(line=dict(color="#000000", width=0.5)),
                    hovertemplate="%{label}: <br>Cantidad: %{value:.1f}€ </br>Porcentaje: %{percent}",
                )
                fig_pie2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    showlegend=False,
                    title=None,
                )
                fig_pie2.update_layout(
                    hovermode="x unified",
                    hoverlabel=dict(bgcolor="rgba(255,255,255,0.95)"),
                )
                fig_pie2.update_layout(
                    annotations=[
                        dict(
                            text=f"{month_name.capitalize()} {year}:",
                            x=0.5,
                            y=0.55,
                            font_size=20,
                            showarrow=False,
                        ),
                        dict(
                            text=f'{round(sum(df_expenses_pie["quantity"]),1)}€',
                            x=0.5,
                            y=0.45,
                            font_size=20,
                            showarrow=False,
                        ),
                    ]
                )
        
                with col1:
                    st.plotly_chart(fig_pie1, use_container_width=True)
                with col3:
                    st.plotly_chart(fig_pie2, use_container_width=True)


with tab3:
    start, end = date_range_picker("Selecciona un rango de fechas", error_message="Porfavor, seleccione fecha de inicio y final",
                key="sankey_date", default_start=datetime.date.today() - datetime.timedelta(days=30))
    
    if end > datetime.datetime.now().date():
        st.warning("El rango de fechas seleccionado no ha terminado a día de hoy, la gráfica se puede ver influenciada.")

    df_incomes["date"] = df_incomes["date"].astype(str)
    df_expenses["date"] = df_expenses["date"].astype(str)
    df_sankey_incomes =  df_incomes[(df_incomes["date"]>=str(start)) & (df_incomes["date"]<=str(end))]
    df_sankey_incomes = df_sankey_incomes.groupby("category")["quantity"].sum().reset_index()
    
    incomes_sankey = list(df_sankey_incomes["category"].values)
    incomes_values_sankey = list(df_sankey_incomes["quantity"].values)

    df_sankey_expenses =  df_expenses[(df_expenses["date"]>=str(start)) & (df_expenses["date"]<=str(end))]
    df_sankey_expenses = df_sankey_expenses.groupby("category")["quantity"].sum().reset_index()
    
    expenses_sankey = list(df_sankey_expenses["category"].values)
    expenses_values_sankey = list(df_sankey_expenses["quantity"].values)

    query = "select cash, investment, donation from safes_distribution where user_id=%s and month=%s and year=%s"
    safes_percentages = db.fetchall(query, (user_id, month, year))

    safes_sankey = ["Efectivo", "Inversión", "Donación"]
    if safes_percentages != []:
        safes_percentages_df = pd.DataFrame(safes_percentages, columns=safes_sankey).T
        safes_percentages = list(
            safes_percentages_df.replace(0, np.nan)
            .dropna()
            .T.iloc[0]
            .astype(float)
            .values
        )
        safes_sankey = list(safes_percentages_df.replace(0, np.nan).dropna().T.columns)
    else:
        safes_percentages = [1]
        safes_sankey = ["Efectivo"]
    fig = sankey_movements_plot(
        incomes_sankey,
        incomes_values_sankey,
        expenses_sankey,
        expenses_values_sankey,
        safes_sankey,
        safes_percentages,
    )
    st.plotly_chart(fig)
