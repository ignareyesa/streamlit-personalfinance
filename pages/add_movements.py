import streamlit as st
from init_db import commit_query, run_query
from gen_functions import load_css_file, logged_in, switch_page_button

load_css_file("styles/add_movements.css")


# Check if user is logged in, if not, show warning message and stop execution of code
if not logged_in():
    st.warning("Para poder cambiar tu contraseña tienes que haber iniciado sesión.")
    # Show a button to go back to the login page
    switch_page_button(["Volver a iniciar sesión"],["Comienza a explorar"])
    st.stop()

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

# Create selection for form type
st.subheader("¿Qué tipo de movimiento quieres registrar?")
option = st.radio("",("Ingresos", "Gastos"))

# Display income or expense form according to user's choice
# Incomes form
if option == "Ingresos":
    table_name = "incomes_movements"
    st.subheader("Ingresos")
    date = st.date_input("Fecha")
    # Create drop-down list of categories
    category = st.selectbox("Categoría", list(incomes_subcategories.keys()))
    # Create drop-down list of subcategories according to the chosen category
    subcategory = st.selectbox("Subcategoría", incomes_subcategories[category])
    concept = st.text_input("Concepto")
    quantity = st.number_input("Cantidad")
    
    movement_form = st.form("add-movement", clear_on_submit=True)
    form_response = movement_form.form_submit_button("Añadir ingreso")

# Expenses Form
if option == "Gastos":
    table_name = "expenses_movements"
    st.subheader("Gastos")
    date = st.date_input("Fecha")
    # Create drop-down list of categories
    category = st.selectbox("Categoría", list(expenses_subcategories.keys()))
    # Create drop-down list of subcategories according to the chosen category
    subcategory = st.selectbox("Subcategoría", expenses_subcategories[category])
    concept = st.text_input("Concepto")
    quantity = st.number_input("Cantidad")
    movement_form = st.form("add-movement", clear_on_submit=True)
    form_response = movement_form.form_submit_button("Añadir gasto")

try:
    username = st.session_state["username"]
    query_id = "SELECT id from users where username=%s"
    # Get id from database
    user_id = run_query(query_id, (username,))[0][0]
    if form_response and len(category)>0 and len(subcategory)>0 and len(concept)>0 and quantity is not None:
        query = f"""INSERT INTO {table_name}  
                   (user_id, date, category, subcategory, concept, quantity)
                   values (%s, %s, %s, %s, %s, %s)"""
        commit_query(query,(user_id, date, category, subcategory, concept, quantity))
        st.success(f"{option[:-1].capitalize()} registrado correctamente")
        st.warning(f"Para registrar otro movimiento rellene el formulario de nuevo")
        user_id, date, category, subcategory, concept, quantity = [None]*6
    
    elif form_response and (len(category)<=0 or len(subcategory)<=0 or len(concept)<=0 or quantity is None):
        st.error("Rellene todos los campos del formulario.")
    
    else:
        pass
except Exception as e: 
    st.write(e)

