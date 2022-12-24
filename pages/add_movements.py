import streamlit as st
import pandas as pd
from init_app import db, authenticator
from gen_functions import load_css_file, logged_in, multile_button_inline, check_temporary_token, check_columns, check_data_types
from streamlit_extras.no_default_selectbox import selectbox
from markdownlit import mdlit


load_css_file("styles/add_movements.css")
css_style = "styles/buttons.css"


incomes_subcategories = {
    "Salario": ["Trabajo", "Becas", "Ayuda financiera"],
    "Venta": ["Productos", "Servicios", "Propiedades"],
    "Inversión": ["Acciones", "Bonos", "Fondos"],
    "Intereses de ahorros": ["Cuenta corriente", "Cuenta de ahorro", "CDT"],
    "Dividendos": ["Acciones", "Fondos", "Inversiones"],
    "Ganancias de juegos de azar": ["Loteria", "Casino", "Apuestas deportivas"],
    "Pensiones": ["Jubilación", "Invalidez", "Viudez"]
}

expenses_subcategories = {
    'Comida y bebida': ['Supermercado', 'Restaurante', 'Bar'], 
    'Vivienda': ['Alquiler', 'Hipoteca', 'Reparaciones'], 
    'Transporte': ['Gasolina', 'Mantenimiento del vehículo', 'Pasajes de transporte público'], 
    'Salud': ['Medicamentos', 'Consultas médicas', 'Gastos dentales'], 
    'Entretenimiento': ['Cine', 'Teatro', 'Deportes'], 
    'Vestimenta': ['Ropa', 'Calzado', 'Accesorios'], 
    'Educación': ['Colegiaturas', 'Libros', 'Material escolar'], 
    'Servicios públicos': ['Agua', 'Luz', 'Gas'], 
    'Teléfono y Internet': ['Plan de datos', 'Línea fija', 'Servicio de TV por cable'], 
    'Impuestos': ['Impuesto sobre la renta', 'Impuesto predial', 'Impuestos vehiculares'], 
    'Seguros': ['Seguro de salud', 'Seguro de vida', 'Seguro del vehículo'], 
    'Bancos y finanzas': ['Comisiones bancarias'], 
    'Viajes y vacaciones': [], 
    'Deporte y fitness': ['Gym', 'Tenis']
    }


# check if page query parameter is given, if not show warning and stop
try:
    search_params = st.experimental_get_query_params()
    page = search_params.get("page")[0]
except:
    page = None
    
# check if page is "reset_pass", if not show warning and stop
if page not in ("modify_movement",None):
    st.warning("Página no encontrada. Página especificada no válida.")
    multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"], css=css_style)
    st.stop()

elif page is None:
    # Check if user is logged in, if not, show warning message and stop execution of code
    if not logged_in():
        st.warning("Para poder añadir movimientos tienes que haber iniciado sesión.")
        # Show a button to go back to the login page
        multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"], css=css_style)
        st.stop()
    authenticator.logout("Cerrar sesión", "sidebar")
    username = st.session_state["username"]
    query_id = "SELECT id from users where username=%s"
    # Get id from database
    user_id = db.fetchone(query_id, (username,))[0]
    # Create selection for form type
    st.header("Registra tus nuevos movimientos")
    st.subheader("Puedes hacerlo de forma manual rellenando un formulario o subiendo un archivo Excel o CSV.")
    option = selectbox("¿Como quieres hacerlo?",["Manual", "Archivo"])
    if option == "Manual":
        movement_type = None
        movement_type = selectbox("Elija el tipo de movimiento",["Ingresos", "Gastos"])
        form_response = None

        # Display income or expense form according to user's choice
        # Incomes form
        if movement_type == "Ingresos":
            table_name = "incomes_movements"
            date = st.date_input("Fecha")
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

        # multile_button_inline(["Ir a tus movimientos"],["Consultar movimientos"], css=css_style)

        try:
            if form_response and len(category)>0 and len(subcategory)>0 and len(concept)>0 and quantity is not None:
                query = f"""INSERT INTO {table_name}  
                        (user_id, date, category, subcategory, concept, quantity)
                        values (%s, %s, %s, %s, %s, %s)"""
                db.commit(query,(user_id, date, category, subcategory, concept, quantity))
                st.success(f"{option[:-1].capitalize()} registrado correctamente")
                st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")
                user_id, date, category, subcategory, concept, quantity = [None]*6

            elif form_response and len(category)>0 and len(subcategory)==0 and len(concept)>0 and quantity is not None:
                query = f"""INSERT INTO {table_name}  
                        (user_id, date, category, subcategory, concept, quantity)
                        values (%s, %s, %s, "Sin categoría", %s, %s)"""
                db.commit(query,(user_id, date, category, subcategory, concept, quantity))
                st.success(f"{option[:-1].capitalize()} registrado correctamente")
                st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")
                user_id, date, category, subcategory, concept, quantity = [None]*6
            
            elif form_response and (len(category)<=0 or len(subcategory)<=0 or len(concept)<=0 or quantity is None):
                st.error("Rellene todos los campos del formulario.")
            
            else:
                pass
        except Exception as e: 
            st.write(e)
        
    
    elif option == "Archivo":
        movement_type = None
        movement_type = selectbox("Elija el tipo de movimiento",["Ingresos", "Gastos"])
        
        st.markdown(f"""Para poder cargar el archivo de forma correcta es necesario que este siga unas reglas para poder cargarlo en el sistema:
Las columnas que debe contener el fichero son las siguiente:
- **date (DD/MM/YYYY)**: Contiene la fecha del movimiento.
- **category**: Categoría asignada al movimiento. Debe pertenecer a la lista existente. Desplegar lista lista
- **subcategory** (opcional): Subcategoría asignada al movimiento. Debe pertenecer a la lista existente. Desplegar lista. En caso de no tener ninguno asociado se etiquetara como *'Sin determinar'*    
- **concept**: Concepto asociado al movimiento.
- **quantity**: Cantidad perteneciente al movimiento. """)
        
        expected_columns = ['date', 'category', 'subcategory', 'concept', 'quantity']
        expected_types = ['datetime64[ns]', 'object', 'object', 'object', 'float64']

        option_types = selectbox("Formato del archivo",["Excel", "csv"])
        if option_types == "Excel":
            file_type = "xlsx"
        elif option_types == "csv": 
            file_type = "csv"
        else:
            file_type = None

        # Display income or expense form according to user's choice
        # Incomes form
        if movement_type == "Ingresos":
            table_name = "incomes_movements"
        if movement_type == "Gastos":
            table_name = "expenses_movements"

        if file_type:
            file = st.file_uploader("Subir el archivo", type=file_type)
            # Check if a file was uploaded
            if file is not None:
                # Read the file into a dataframe
                df = pd.read_excel(file)
                existing_columns = df.columns
                if "subcategory" in existing_columns:
                    try:
                        check_columns(df, expected_columns)
                    except Exception as e:
                        st.error(e)
                        raise e
                else: 
                    try:
                        df["subcategory"] = "Sin especificar"
                        check_columns(df, expected_columns)
                    except Exception as e:
                        st.error(e)
                        raise e

                try:
                    df['date'] = pd.to_datetime(df['date'])
                except Exception as e:
                    st.error("La columna `date` no se ha podido convetir a formato fecha. Asegurese de que sigue el siguiente formato DD/MM/YYYY.")
                    raise e
                try:
                    df['quantity'] = df['quantity'].astype(float)
                except Exception as e:
                    st.error("La columna `quantity` no es del tipo númerico. Por favor, revísela.")
                    raise e

                try: 
                    check_data_types(df, expected_columns, expected_types)
                except Exception as e:
                    st.error(e)
                    raise e

                
                try:
                    df["user_id"] = user_id
                    df = df[["user_id"] + expected_columns]
                    df['date'] = df['date'].astype(str)
                    
                    column_names = ",".join(df.columns)
                    query = f"""INSERT INTO {table_name} (user_id, date, category, subcategory, concept, quantity) VALUES """
                    for index, row in df.iterrows():
                        query += f"{tuple(row)},"
                    query = query[:-1] + ";"
                    db.commit(query)
                    st.success('Archivo cargado correctamente en el sistema.')

                except Exception as e:
                    st.exception(e)
                    st.error("Ha habido un error al cargar su archivo en el sistema. Por favor, inténtelo de nuevo")
        else:
            movement_type = None
            file_type = None
        # multile_button_inline(["Ir a tus movimientos"],["Consultar movimientos"], css=css_style)
    else: 
        pass
        # multile_button_inline(["Ir a tus movimientos"],["Consultar movimientos"], css=css_style)
    multile_button_inline(["Ir a tus movimientos"],["Consultar movimientos"], css=css_style)



elif page == "modify_movement":

    # check if token and username query parameters are given, if not show warning and stop
    try:
        token, movement_id = search_params.get("token")[0].split("-")
        username = search_params.get("username")[0]
        movement_type = search_params.get("option")[0]
        placeholder = search_params.get("placeholder")[0]
        # Get id from database
        user_id, user_name = db.fetchone("SELECT id, name from users where username=%s", (username,))
    except:
        st.warning("El enlace proporcionado no es válido.")
        multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"], css=css_style)
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
        multile_button_inline(["Volver a iniciar sesión"],["Comienza a explorar"], css=css_style)
        st.stop()

    authenticator.logout("Cerrar sesión", "sidebar")
    st.subheader(f"Rellene el formulario para modificar el {movement_type[:-1].lower()} seleccionado")
    # Incomes form
    if movement_type == "Ingresos":
        table_name = "incomes_movements"
        date = st.date_input("Fecha")
        # Create drop-down list of categories
        category = st.selectbox("Categoría", list(incomes_subcategories.keys()))
        # Create drop-down list of subcategories according to the chosen category
        subcategory = st.selectbox("Subcategoría", incomes_subcategories[category])
        concept = st.text_input("Concepto", placeholder=placeholder)
        quantity = st.number_input("Cantidad")
        movement_form = st.form("add-movement")
        form_response = movement_form.form_submit_button("Modificar movimiento")

    # Expenses Form
    if movement_type == "Gastos":
        table_name = "expenses_movements"
        date = st.date_input("Fecha")
        # Create drop-down list of categories
        category = st.selectbox("Categoría", list(expenses_subcategories.keys()))
        # Create drop-down list of subcategories according to the chosen category
        subcategory = st.selectbox("Subcategoría", expenses_subcategories[category])
        concept = st.text_input("Concepto", placeholder=placeholder)
        quantity = st.number_input("Cantidad")
        movement_form = st.form("add-movement")
        form_response = movement_form.form_submit_button("Modificar movimiento")

    multile_button_inline(["Ir a tus movimientos"],["Consultar movimientos"], css=css_style)

    try:
        if form_response and len(category)>0 and len(subcategory)>0 and len(concept)>0 and quantity is not None:
            query = f"UPDATE {table_name} SET date=%s,category=%s,subcategory=%s,concept=%s,quantity=%s WHERE id=%s"
            db.commit(query,(date, category, subcategory, concept, quantity, movement_id))
            st.success(f"Movimiento actualizado correctamente, la página se volvera a cargar automáticamente en un instante.")
        
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
        st.write(e)
    
else: 
    st.warning("Página no encontrada. Página especificada no válida.")
        