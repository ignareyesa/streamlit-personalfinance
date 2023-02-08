from gen_functions import load_css_file, logged_in, progressbar
from styles.aggrid_styles import posneg_cellstyle, euro_cellstyle, date_cellstyle
load_css_file("styles/add_movements.css")
load_css_file("styles/sidebar.css")


import pandas as pd
import streamlit as st
import datetime

# Import the necessary libraries
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from init_app import db, authenticator

from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.switch_page_button import switch_page
from streamlit_option_menu import option_menu
from st_pages import add_indentation


add_indentation()
st.experimental_set_query_params()
css_style = "styles/buttons.css"

if not logged_in():
    switch_page("Comienza a explorar")

authenticator.logout("Salir", "sidebar")

# Get the user's ID from the database
username = st.session_state["username"]
query_id = "SELECT id from users where username=%s"
user_id = db.fetchone(query_id, (username,))[0]

selected = option_menu(None, ["Consultar", "Añadir"], 
    icons=['cash', 'house'], 
    menu_icon="cast", default_index=1, orientation="horizontal",
    styles={
    "container": {"width":"40%"},
    "nav": {"margin-left": "1rem", "margin-right": "1rem"}})


if selected == "Consultar":
    query = """SELECT "actives" AS movement,
                            actives.*
                        FROM actives_movements AS actives
                        WHERE user_id=%s
                        UNION ALL
                        SELECT "pasives" AS movement,
                            pasives.id,
                            pasives.user_id,
                            pasives.date,
                            pasives.category,
                            pasives.concept,
                            pasives.quantity*-1
                        FROM pasives_movements AS pasives
                        WHERE user_id=%s
                        ORDER BY date DESC;"""
    data = db.fetchall(query, (user_id, user_id))
    columns = db.get_columns(query, (user_id, user_id))

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(data=data, columns=columns)

    # If the user has not added any income movements, show a warning and a button to go to the add movements page
    if len(df) == 0:
        st.warning("No ha añadido ningún activo/pasivo")
        st.stop()

    with st.expander("Filtrar"):
        start, end = date_range_picker("Selecciona un rango de fechas", error_message="Porfavor, seleccione fecha de inicio y final",
            key="heritage_date")
        types = st.selectbox("Tipo de movimiento",["Activos y pasivos", "Solo activos", "Solo pasivos"], key="heritage_types")
        categories = st.multiselect("Categorías",
                df["category"].unique(),
                df["category"].unique(),
                key="heritage_cat")
        min_quantity = st.text_input("Importe desde (opcional)",key="heritage_min")
        max_quantity = st.text_input("Importe hasta (opcional)",key="heritage_max")

        try:
            if float(max_quantity)<float(min_quantity):
                st.error(f"El importe no puede ser inferior a {round(float(min_quantity),2)} €")
                st.stop()
        except: 
            pass


    if len(min_quantity) == 0:
        min_quantity = 0
    if len(max_quantity) == 0 and types == "Activos y pasivos":
        max_quantity = max(abs(df["quantity"]))
    elif len(max_quantity) == 0 and types == "Solo activos":
        max_quantity = max(abs(df[df["quantity"]>=0]["quantity"]))
    elif len(max_quantity) == 0 and types == "Solo pasivos":
        max_quantity = max(abs(df[df["quantity"]<=0]["quantity"]))

    try:
        max_quantity = float(max_quantity)
        min_quantity = float(min_quantity)
    except:
        st.error("Algún valor introducido no es un número valido")
        st.stop()
    if types == "Activos y pasivos":
        df = df[
            ((df["date"]>=start) & (df["date"]<=end)) & 
            (df["category"].isin(categories)) & 
            (((df["quantity"] >= abs(min_quantity)) & (df["quantity"] <= abs(max_quantity))) |
            ((df["quantity"] <= -1*min_quantity) & (df["quantity"] >= -1*max_quantity)))
            ]
    elif types == "Solo activos":
        df = df[
            ((df["date"]>=start) & (df["date"]<=end)) & 
            (df["category"].isin(categories)) & 
            ((df["quantity"] >= abs(min_quantity)) & (df["quantity"] <= abs(max_quantity)))
            ]
    elif types == "Solo pasivos":
        df = df[
            ((df["date"]>=start) & (df["date"]<=end)) & 
            (df["category"].isin(categories)) & 
            ((df["quantity"] <= -1*min_quantity) & (df["quantity"] >= -1*max_quantity))
            ]
    else:
        df = df.copy()

    # Select the data to be displayed in the grid
    df_selection = df[
        ["date", "category", "concept", "quantity"]
    ].sort_values("date", ascending=False)
    df_selection["date"] = pd.to_datetime(
        df_selection["date"].astype(str), format="%Y/%m/%d"
    )
    df_selection["quantity"] = df_selection["quantity"].astype(float)

    # Build the grid
    gb = GridOptionsBuilder.from_dataframe(df_selection)
    gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True, suppressRowClickSelection=True)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    gb.configure_column("date",header_name="Fecha", cellRenderer=JsCode(date_cellstyle),width=300)
    gb.configure_column("category",header_name="Categoría", width=400)
    gb.configure_column("concept",header_name="Concepto", width=400)
    gb.configure_column("quantity", header_name="Valor", cellStyle=JsCode(posneg_cellstyle), cellRenderer=JsCode(euro_cellstyle), width = 150)

    # Build the grid options
    grid_options = gb.build()

    # Create the AgGrid
    grid_response = AgGrid(
        df_selection,
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        allow_unsafe_jscode=True)

    # Delete or Modify register buttons
    delete = st.button("Eliminar registro(s)", key="heritage_del")

    # If there is no register selected and click button, show a warning
    if len(grid_response["selected_rows"]) == 0:
        if delete:
            st.warning("No ha seleccionado ningún registro, seleccione antes de eliminar")
            
    elif len(grid_response["selected_rows"]) == 1:
        # Get response from selection
        response = dict(grid_response)["selected_rows"][0]
        selected_row = int(response["_selectedRowNodeInfo"]["nodeId"])
        movement_id = int(df.iloc[selected_row]["id"])
        
        # Define variable table depending on whether it is income or expense
        if response["quantity"] >= 0:
            table_name = "actives_movements"
            option = "Activos"
        elif response["quantity"] < 0:
            table_name = "pasives_movements"
            option = "Pasivos"
        else:
            st.error("Hay algun error")
        if delete:
            query = f"DELETE FROM {table_name} where id=%s"
            db.commit(query, (movement_id,))
            st.success(
                "Registro eliminado correctamente, la página se volvera a cargar automáticamente en un instante."
            )
            progressbar()
            st.experimental_rerun()

if selected == "Añadir":
    # List of possible pasive and active
    activos = ['Propiedad', 'Cuenta bancaria', 'Inversiones', 'Vehículo', 'Ahorros']
    pasivos = ['Deuda', 'Préstamo', 'Tarjeta de crédito', 'Hipoteca']
    col1, col2 = st.columns([1,1.5])
    with col1:
        st.header("Registra tus activos y pasivos")
        option = st.radio("Selecciona el tipo de activo o pasivo", ('Activo', 'Pasivo'))
        if option == 'Activo':
            table_name = "actives_movements"
            category = st.selectbox("Selecciona el tipo de activo", activos)
            quantity = st.number_input("Valor activo fin de mes")
            date = st.date_input("Mes de registro")
            concept = st.text_input("Descripción del activo")
            heritage_form = st.form("add-heritage")
            form_response = heritage_form.form_submit_button("Añadir activo")
        if option == 'Pasivo':
            table_name = "pasives_movements"
            category = st.selectbox("Selecciona el tipo de pasivo", pasivos)
            quantity = st.number_input("Valor pasivo fin de mes")
            date = st.date_input("Mes de registro")
            concept = st.text_input("Descripción del pasivo")
            heritage_form = st.form("add-heritage")
            form_response = heritage_form.form_submit_button("Añadir pasivo")

        try:
            # Check if current month
            now = datetime.datetime.now()
            current_year = now.year
            current_month = now.month

            if form_response and date.year == current_year and date.month == current_month:
                st.info("El mes seleccionado todavía no ha finalizado, por lo que todavía no se puede añadir registros.")

            elif form_response and len(category)>0 and len(concept)>0 and quantity is not None:
                query = f"""INSERT INTO {table_name}  
                        (user_id, date, category, concept, quantity)
                        values (%s, %s, %s, %s, %s)"""
                db.commit(query,(user_id, date, category, concept, quantity))
                st.success(f"{option.capitalize()} registrado correctamente")
                st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")

            elif form_response and (len(category)<=0 or len(concept)<=0 or quantity is None):
                st.error("Rellene todos los campos del formulario.")
            
            else:
                pass
        except Exception as e: 
            st.write(e)