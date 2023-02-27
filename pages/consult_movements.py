from gen_functions import (load_css_file, multile_button_inline, logged_in, 
                           check_columns, check_data_types, verify_column_values,
                           progressbar)
from db_functions import create_temporary_token, check_temporary_token
from init_exceptions import if_reconnect
from styles.aggrid_styles import posneg_cellstyle, euro_cellstyle, date_cellstyle
from mappers import incomes_subcategories, expenses_subcategories
import streamlit as st


load_css_file("styles/add_movements.css")
load_css_file("styles/sidebar.css")
load_css_file("styles/buttons.css")

css_style = "styles/buttons.css"

import pandas as pd
import datetime

from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

from streamlit_extras.mandatory_date_range import date_range_picker
from streamlit_extras.switch_page_button import switch_page
from streamlit_toggle import st_toggle_switch
from streamlit_extras.no_default_selectbox import selectbox
from streamlit_option_menu import option_menu
from st_pages import add_indentation

with open('error.txt', 'r') as error_file:
    error_text = error_file.read()
add_indentation()



try:
    search_params = st.experimental_get_query_params()
    page = search_params.get("page")[0]
except:
    page = None

if page!="modify_movement" and not logged_in():
        switch_page("Mi perfil")

elif page!="modify_movement":
    authenticator = st.session_state["authenticator"]
    db = st.session_state["db"]
    authenticator.logout("Salir", "sidebar")

    # Get the user's ID from the database
    username = st.session_state["username"]
    query_id = "SELECT id from users where username=%s"
    try:
        user_id = db.fetchone(query_id, (username,))[0]
    except:
        st.markdown("Ha habido un error durante el proceso, porfavor vuelva al inicio.")
        multile_button_inline(["Volver a Inicio"],["Inicio"])
        st.stop()

    selected = option_menu(None, ["Consultar", "Añadir"], 
        icons=['arrow-left-right', 'bookmark-plus'], 
        menu_icon="cast", default_index=1, orientation="horizontal",
        styles={
        "container": {"width":"30%"},
        "nav": {"margin-left": "1rem", "margin-right": "1rem"},
        "nav-link-selected": {"background-color": "#8041f5"}})


    if selected == "Consultar":
        # Get the user's income movements from the database
        query = """SELECT "incomes" AS movement,
                                incomes.*
                            FROM incomes_movements AS incomes
                            WHERE user_id=%s
                            UNION ALL
                            SELECT "expenses" AS movement,
                                expenses.id,
                                expenses.user_id,
                                expenses.date,
                                expenses.category,
                                expenses.subcategory,
                                expenses.concept,
                                expenses.quantity*-1
                            FROM expenses_movements AS expenses
                            WHERE user_id=%s
                            ORDER BY date DESC;
                        """

        data = db.fetchall(query, (user_id, user_id))
        columns = db.get_columns(query, (user_id, user_id))

        # Convert the data to a pandas DataFrame
        df = pd.DataFrame(data=data, columns=columns)

        # If the user has not added any income movements, show a warning and a button to go to the add movements page
        if len(df) == 0:
            st.warning("No ha añadido ningún movimiento")
            st.stop()

        with st.expander("Filtrar"):
            start, end = date_range_picker("Selecciona un rango de fechas", error_message="Porfavor, seleccione fecha de inicio y final",
                key="movements_date")
            types = st.selectbox("Tipo de movimiento",["Ingresos y gastos", "Solo ingresos", "Solo gastos"], key="movements_type")
            categories = st.multiselect("Categorías",
                    df["category"].unique(),
                    df["category"].unique(),
                    key="movements_cat")
            min_quantity = st.text_input("Importe desde (opcional)",key="movements_min")
            max_quantity = st.text_input("Importe hasta (opcional)", key="movements_key")

            try:
                if float(max_quantity)<float(min_quantity):
                    st.error(f"El importe no puede ser inferior a {round(float(min_quantity),2)} €")
                    st.stop()
            except: 
                pass


        if len(min_quantity) == 0:
            min_quantity = 0
        if len(max_quantity) == 0 and types == "Ingresos y gastos":
            max_quantity = max(abs(df["quantity"]))
        elif len(max_quantity) == 0 and types == "Solo ingresos":
            max_quantity = max(abs(df[df["quantity"]>=0]["quantity"]))
        elif len(max_quantity) == 0 and types == "Solo gastos":
            max_quantity = max(abs(df[df["quantity"]<=0]["quantity"]))

        try:
            max_quantity = float(max_quantity)
            min_quantity = float(min_quantity)
        except:
            st.error("Algún valor introducido no es un número valido")
            st.stop()
        if types == "Ingresos y gastos":
            df = df[
                ((df["date"]>=start) & (df["date"]<=end)) & 
                (df["category"].isin(categories)) & 
                (((df["quantity"] >= abs(min_quantity)) & (df["quantity"] <= abs(max_quantity))) |
                ((df["quantity"] <= -1*min_quantity) & (df["quantity"] >= -1*max_quantity)))
                ]
        elif types == "Solo ingresos":
            df = df[
                ((df["date"]>=start) & (df["date"]<=end)) & 
                (df["category"].isin(categories)) & 
                ((df["quantity"] >= abs(min_quantity)) & (df["quantity"] <= abs(max_quantity)))
                ]
        elif types == "Solo gastos":
            df = df[
                ((df["date"]>=start) & (df["date"]<=end)) & 
                (df["category"].isin(categories)) & 
                ((df["quantity"] <= -1*min_quantity) & (df["quantity"] >= -1*max_quantity))
                ]
        else:
            df = df.copy()

        # Select the data to be displayed in the grid
        df_selection = df[
            ["date", "category", "subcategory", "concept", "quantity"]
        ].sort_values("date", ascending=False)
        df_selection["date"] = pd.to_datetime(
            df_selection["date"].astype(str), format="%Y/%m/%d"
        )
        df_selection["quantity"] = df_selection["quantity"].astype(float)

        # Build the grid
        # Define a cell style function to change the color of the quantity cells based on their value
        st.cache_data()
        gb = GridOptionsBuilder.from_dataframe(df_selection)
        gb.configure_default_column(filterable=False, sortable=False)
        gb.configure_selection("multiple", use_checkbox=True, header_checkbox=True, suppressRowClickSelection=True)
        gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
        gb.configure_column("date",header_name="Fecha", cellRenderer=JsCode(date_cellstyle),width=300)
        gb.configure_column("category",header_name="Categoría", width=300)
        gb.configure_column("subcategory",header_name="Subcategoría", width=300)
        gb.configure_column("concept",header_name="Concepto", width=400)
        gb.configure_column("quantity", header_name="Valor", cellStyle=JsCode(posneg_cellstyle), cellRenderer=JsCode(euro_cellstyle), width = 150)

        # Build the grid options
        grid_options = gb.build()

        # Create the AgGrid
        grid_response = AgGrid(
            df_selection,
            gridOptions=grid_options,
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True
            )

        # Delete or Modify register buttons
        delete = st.button("Eliminar registro(s)", key="movements_del")
        modify = st.button("Modificar registro", key="movements_modi")

        # If there is no register selected and click button, show a warning
        if len(grid_response["selected_rows"]) == 0:
            if delete or modify:
                st.warning("No ha seleccionado ningún registro, seleccione antes de eliminar")
                
        elif len(grid_response["selected_rows"]) == 1:
            # Get response from selection
            response = dict(grid_response)["selected_rows"][0]
            selected_row = int(response["_selectedRowNodeInfo"]["nodeId"])
            movement_id = int(df.iloc[selected_row]["id"])
            
            # Define variable table depending on whether it is income or expense
            if response["quantity"] >= 0:
                table_name = "incomes_movements"
                option = "Ingresos"
            elif response["quantity"] < 0:
                table_name = "expenses_movements"
                option = "Gastos"
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
            if modify:
                token = create_temporary_token(table="modify_movement_tokens")
                nav_script = """
                    <meta http-equiv="refresh" content="0; url='%s'">
                    """ % (f"""/Movimientos?page=modify_movement&token={token}-{movement_id}&username={username}&option={option}&date={str(df.iloc[selected_row]["date"])}&quantity={str(abs(df.iloc[selected_row]["quantity"]))}&concept={df.iloc[selected_row]["concept"]}""")
                st.write(nav_script, unsafe_allow_html=True)

        else:
            response = dict(grid_response)["selected_rows"]
            incomes = []
            expenses = []
            for selection in response:
                if selection["quantity"] >= 0:
                    incomes.append(selection["_selectedRowNodeInfo"]["nodeId"]) 
                else:
                    expenses.append(selection["_selectedRowNodeInfo"]["nodeId"])
            
            incomes_ids = tuple(df.iloc[incomes]["id"].values)
            expenses_ids = tuple(df.iloc[expenses]["id"].values)
            if len(incomes_ids) == 1:
                incomes_query = f"DELETE FROM incomes_movements where id ={incomes_ids[0]}"
            else:
                incomes_query = f"DELETE FROM incomes_movements where id in {incomes_ids}"
            
            if len(expenses_ids) == 1:
                expenses_query = f"DELETE FROM expenses_movements where id = {expenses_ids[0]}"
            else:
                expenses_query = f"DELETE FROM expenses_movements where id in {expenses_ids}"

            if delete:
                if incomes_ids and expenses_ids:
                    db.commit(incomes_query)
                    db.commit(expenses_query)
                    st.success(
                    "Registros eliminados correctamente, la página se volvera a cargar automáticamente en un instante."
                    )
                    progressbar()
                    st.experimental_rerun()
                
                elif incomes_ids and not expenses_ids:
                    db.commit(incomes_query)
                    st.success(
                    "Registros eliminados correctamente, la página se volvera a cargar automáticamente en un instante."
                    )
                    progressbar()
                    st.experimental_rerun()
                
                elif expenses_ids and not incomes_ids:
                    db.commit(expenses_query)
                    st.success(
                    "Registros eliminados correctamente, la página se volvera a cargar automáticamente en un instante."
                    )
                    progressbar()
                    st.experimental_rerun()
                else:
                    pass
                

            if modify:
                st.warning("Solo se puede modificar en registro de una vez.")

    if selected == "Añadir":
        col1, col2 = st.columns([1,1.5])
        with col1:
            st.header("Registra tus gastos e ingresos")
            option = selectbox("¿Como quieres hacerlo?",["Manual", "Archivo"], help="Puedes añadir tus movimientos rellenando manualmente un formulario o bien adjuntando un archivo excel seguiendo la plantilla proporcionada.")
            if option == "Manual":
                movement_type = None
                movement_type = selectbox("Elija el tipo de movimiento",["Ingresos", "Gastos"])
                form_response = None

                # Display income or expense form according to user's choice
                # Incomes form
                if movement_type == "Ingresos":
                    table_name = "incomes_movements"
                    date = st.date_input("Fecha", )
                    # Create drop-down list of categories
                    category = st.selectbox("Categoría", list(incomes_subcategories.keys()))
                    # Create drop-down list of subcategories according to the chosen category
                    subcategory = st.selectbox("Subcategoría", incomes_subcategories[category])
                    concept = st.text_input("Concepto")
                    quantity = st.number_input("Cantidad")
                    
                    movement_form = st.form("add-movement")
                    form_response = movement_form.form_submit_button("Añadir ingreso")
                    

                # Expenses Form
                if movement_type == "Gastos":
                    table_name = "expenses_movements"
                    date = st.date_input("Fecha")
                    # Create drop-down list of categories
                    category = st.selectbox("Categoría", list(expenses_subcategories.keys()))
                    # Create drop-down list of subcategories according to the chosen category
                    subcategory = st.selectbox("Subcategoría", expenses_subcategories[category])
                    concept = st.text_input("Concepto")
                    quantity = st.number_input("Cantidad")
                    movement_form = st.form("add-movement")
                    form_response = movement_form.form_submit_button("Añadir gasto")

                try:
                    if form_response and len(category)>0 and len(subcategory)>0 and len(concept)>0 and quantity is not None:
                        query = f"""INSERT INTO {table_name}  
                                (user_id, date, category, subcategory, concept, quantity)
                                values (%s, %s, %s, %s, %s, %s)"""
                        db.commit(query,(user_id, date, category, subcategory, concept, quantity))
                        st.success(f"{movement_type[:-1].capitalize()} registrado correctamente")
                        st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")
                        user_id, date, category, subcategory, concept, quantity = [None]*6

                    elif form_response and len(category)>0 and len(subcategory)==0 and len(concept)>0 and quantity is not None:
                        query = f"""INSERT INTO {table_name}  
                                (user_id, date, category, subcategory, concept, quantity)
                                values (%s, %s, %s, "Sin categoría", %s, %s)"""
                        db.commit(query,(user_id, date, category, subcategory, concept, quantity))
                        st.success(f"{movement_type[:-1].capitalize()} registrado correctamente")
                        st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")
                        user_id, date, category, subcategory, concept, quantity = [None]*6
                    
                    elif form_response and (len(category)<=0 or len(subcategory)<=0 or len(concept)<=0 or quantity is None):
                        st.error("Rellene todos los campos del formulario.")
                    
                    else:
                        pass
                except Exception as e: 
                    st.write(error_text, unsafe_allow_html=True)
                
            
            elif option == "Archivo":
                movement_type = None
                with open("movements_template.xlsx", "rb") as file:
                    btn = st.download_button(
                            label="Descargar plantilla",
                            data=file,
                            file_name="plantilla_movimientos.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                movement_type = selectbox("Elija el tipo de movimiento",["Ingresos", "Gastos"])


                expected_columns_es = ['Fecha', 'Categoría', 'Subcategoría', 'Concepto', 'Cantidad']
                expected_columns_en = ['date', 'category', 'subcategory', 'concept', 'quantity']
                expected_types = ['datetime64[ns]', 'object', 'object', 'object', 'float64']

                # Display income or expense form according to user's choice
                # Incomes form
                if movement_type == "Ingresos":
                    table_name = "incomes_movements"
                    subcategories = incomes_subcategories
                if movement_type == "Gastos":
                    table_name = "expenses_movements"
                    subcategories = expenses_subcategories
                show_movement_subcat = st_toggle_switch(
                    label=f"Mostrar las categorías y subcategorías",
                    key="switch_1",
                    default_value=False,
                    label_after=True,
                    inactive_color="#D3D3D3",  
                    active_color="#6630cc",
                    track_color="#6630cc",
                )
                if show_movement_subcat:
                    try:
                        st.json(subcategories, expanded=False)
                    except:
                        st.warning("No ha seleccionado el tipo de movimiento.")

                if movement_type:
                    file = st.file_uploader("Subir el archivo", type="xlsx")
                    # Check if a file was uploaded
                    if file is not None:
                        # Read the file into a dataframe
                        df = pd.read_excel(file)
                        existing_columns = df.columns
                        if "subcategory" in existing_columns:
                            try:
                                df["subcategory"] = df["subcategory"].fillna("Otros")
                                check_columns(df, expected_columns_es)
                            except Exception as e:
                                st.error(e)
                                st.stop()
                        else: 
                            try:
                                df["subcategory"] = "Otros"
                                check_columns(df, expected_columns_es)
                            except Exception as e:
                                st.error(e)
                                st.stop()
                        df = df.rename(columns=dict(zip(expected_columns_es, expected_columns_en)))
                        
                        try:
                            verify_column_values(df, "category", list(subcategories))
                        except Exception as e:
                            st.error("Algunos de las categorías que intenta introducir no son válidas.")
                            st.stop()
                    

                        for cat in list(subcategories):
                            mask = (df["category"]==cat)
                            if not df[mask]["subcategory"].isin(subcategories[cat]).all():
                                df.loc[mask & ~df["subcategory"].isin(subcategories[cat]), "subcategory"] = "Otros"
                                not_in_subcategories = True
                        if not_in_subcategories:
                            st.error("Hay subcategorias que no están dentro de las del sistema")

                        try:
                            df['date'] = pd.to_datetime(df['date'])
                        except Exception as e:
                            st.error("La columna `date` no se ha podido convetir a formato fecha. Asegurese de que sigue el siguiente formato DD/MM/YYYY.")
                            
                        try:
                            df['quantity'] = df['quantity'].astype(float)
                        except Exception as e:
                            st.error("La columna `quantity` no es del tipo númerico. Por favor, revísela.")

                        try: 
                            check_data_types(df, expected_columns_en, expected_types)
                        except Exception as e:
                            st.error("Algunas columnas no son del tipo adecuado.")

                        
                        try:
                            df["user_id"] = user_id
                            df = df[["user_id"] + expected_columns_en]
                            df['date'] = df['date'].astype(str)
                            
                            column_names = ",".join(df.columns)
                            query = f"""INSERT INTO {table_name} (user_id, date, category, subcategory, concept, quantity) VALUES """
                            for index, row in df.iterrows():
                                query += f"{tuple(row)},"
                            query = query[:-1] + ";"
                            db.commit(query)
                            st.success('Archivo cargado correctamente en el sistema.')

                        except Exception as e:
                            st.error("Ha habido un error al cargar su archivo en el sistema. Por favor, inténtelo de nuevo")
                else:
                    movement_type = None
            else: 
                pass


else:
    if_reconnect()
    authenticator = st.session_state["authenticator"]
    db = st.session_state["db"]
    try:
        token, movement_id = search_params.get("token")[0].split("-")
        username = search_params.get("username")[0]
        movement_type = search_params.get("option")[0]
        concept_placeholder = search_params.get("concept")[0]
        date_placeholder = datetime.datetime.strptime(search_params.get("date")[0], "%Y-%m-%d").date()
        quantity_placeholder = float(search_params.get("quantity")[0])
        # Get id from database
        user_id, user_name = db.fetchone("SELECT id, name from users where username=%s", (username,))
    except:
        st.warning("El enlace proporcionado no es válido.")
        multile_button_inline(["Volver a iniciar sesión"],["Mi perfil"], css=css_style)
        st.stop()

    # check if token is valid, if not show error and stop
    try:
        check_temporary_token("modify_movement_tokens", token)
        st.session_state["authentication_status"] = True
        st.session_state["username"] = username
        st.session_state["logout"] = None
        st.session_state["name"] = user_name
    except Exception as e:
        st.warning("El enlace proporcionado no es válido.")
        multile_button_inline(["Ir a mi perfil"],["Mi perfil"], css=css_style)
        st.stop()

    authenticator.logout("Salir", "sidebar")
    st.subheader(f"Rellene el formulario para modificar el {movement_type[:-1].lower()} seleccionado")

    def disable(boolean = False):
        if boolean:
            st.session_state.disabled = True
    # Initialize disabled for form_submit_button to False
    if "disabled" not in st.session_state:
        st.session_state.disabled = False
    # Incomes form
    if movement_type == "Ingresos":
        table_name = "incomes_movements"
        date = st.date_input("Fecha", date_placeholder)
        # Create drop-down list of categories
        category = st.selectbox("Categoría", list(incomes_subcategories.keys()))
        # Create drop-down list of subcategories according to the chosen category
        subcategory = st.selectbox("Subcategoría", incomes_subcategories[category])
        concept = st.text_input("Concepto", placeholder=concept_placeholder)
        quantity = st.number_input("Cantidad", value=quantity_placeholder)
        movement_form = st.form("add-movement")
        form_response = movement_form.form_submit_button("Modificar movimiento", on_click=disable, disabled=st.session_state.disabled)

    # Expenses Form
    if movement_type == "Gastos":
        table_name = "expenses_movements"
        date = st.date_input("Fecha", date_placeholder)
        # Create drop-down list of categories
        category = st.selectbox("Categoría", list(expenses_subcategories.keys()))
        # Create drop-down list of subcategories according to the chosen category
        subcategory = st.selectbox("Subcategoría", expenses_subcategories[category])
        concept = st.text_input("Concepto", placeholder=concept_placeholder)
        quantity = st.number_input("Cantidad", value=quantity_placeholder)
        movement_form = st.form("add-movement")
        form_response = movement_form.form_submit_button("Modificar movimiento", on_click=disable, disabled=st.session_state.disabled)


    multile_button_inline(["Pulsar para volver"],["Seguimiento"], css=css_style)

    try:
        if form_response and len(category)>0 and len(subcategory)>0 and len(concept)>0 and quantity is not None:
            query = f"UPDATE {table_name} SET date=%s,category=%s,subcategory=%s,concept=%s,quantity=%s WHERE id=%s"
            db.commit(query,(date, category, subcategory, concept, quantity, movement_id))
            st.success(f"Movimiento actualizado correctamente, pulse el botón para volver.")
            disable(True)
        
        elif form_response and (len(category)<=0 or len(subcategory)<=0 or len(concept)<=0 or quantity is None):
            st.error("Rellene todos los campos del formulario.")
        else:
            pass
    except Exception as e: 
        st.write(error_text, unsafe_allow_html=True)
