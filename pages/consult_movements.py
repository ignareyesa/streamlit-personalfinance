import pandas as pd
import streamlit as st
from time import sleep

# Import the necessary libraries
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode
from init_db import run_query, commit_query, get_query_columns, authenticator
from gen_functions import load_css_file, switch_page_button, logged_in, create_temporary_token

st.experimental_set_query_params()
css_style = "styles/buttons.css"

# Load the CSS file for the page
load_css_file("styles/add_movements.css")

# Check if the user is logged in
if not logged_in():
    # If not, show a warning message and a button to go back to the login page
    st.warning("Para poder consultar tus movimientos tienes que haber iniciado sesión.")
    switch_page_button(["Volver a iniciar sesión"], ["Comienza a explorar"])
    st.stop()

authenticator.logout("Cerrar sesión", "sidebar")

# Get the user's ID from the database
username = st.session_state["username"]
query_id = "SELECT id from users where username=%s"
user_id = run_query(query_id, (username,))[0][0]

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

data = run_query(query, (user_id, user_id))
columns = get_query_columns(query, (user_id, user_id))

# Convert the data to a pandas DataFrame
df = pd.DataFrame(data=data, columns=columns)

# If the user has not added any income movements, show a warning and a button to go to the add movements page
if len(df) == 0:
    st.warning("No ha añadido ningún ingreso")
    switch_page_button(["Añadir movimiento"], ["add movements"])
    st.stop()

# Select the data to be displayed in the grid
df_selection = df[
    ["date", "category", "subcategory", "concept", "quantity"]
].sort_values("date", ascending=False)
df_selection.columns = ["Fecha", "Categoría", "Subcategoría", "Concepto", "Cantidad"]
df_selection["Fecha"] = pd.to_datetime(
    df_selection["Fecha"].astype(str), format="%Y/%m/%d"
)
df_selection["Fecha"] = df_selection["Fecha"].dt.normalize()
df_selection["Cantidad"] = df_selection["Cantidad"].astype(float)

# Build the grid
# Define a cell style function to change the color of the quantity cells based on their value
cellsytle_jscode = JsCode(
    """
function(params) {
    if (params.value < 0) {
        return {
            'color': 'red'
        }
    } else {
        return {
            'color': 'green'
        }
    }
};
"""
)
gb = GridOptionsBuilder.from_dataframe(df_selection)
gb.configure_selection("single", use_checkbox=True, header_checkbox=True)
gb.configure_pagination()
gb.configure_column("Cantidad", cellStyle=cellsytle_jscode)

# Build the grid options
grid_options = gb.build()

# Create the AgGrid
grid_response = AgGrid(
    df_selection,
    gridOptions=grid_options,
    enable_enterprise_modules=True,
    allow_unsafe_jscode=True,
)

# Delete or Modify register buttons
delete_register = st.button("Eliminar Registro")
modify_register = st.button("Modificar registro")

# If there is no register selected and click button, show a warning
if len(grid_response["selected_rows"]) == 0:
    if delete_register:
        st.warning("No ha seleccionado ningún registro, seleccione antes de eliminar")
    if modify_register:
        st.warning("No ha seleccionado ningún registro, seleccione antes de modificar")
else:
    # Get response from selection
    response = dict(grid_response)["selected_rows"][0]
    selected_row = int(response["_selectedRowNodeInfo"]["nodeId"])
    movement_id = int(df.iloc[selected_row]["id"])
    
    # Define variable table depending on whether it is income or expense
    if response["Cantidad"] > 0:
        table_name = "incomes_movements"
        option = "Ingresos"
    elif response["Cantidad"] < 0:
        table_name = "expenses_movements"
        option = "Gastos"
    else:
        st.error("Hay algun error")
    if delete_register:
        query = f"DELETE FROM {table_name} where id=%s"
        commit_query(query, (movement_id,))
        st.success(
            "Registro eliminado correctamente, la página se volvera a cargar automáticamente en un instante."
        )
        sleep(1.7)
        st.experimental_rerun()
    if modify_register:
        token = create_temporary_token(table="modify_movement_tokens")
        nav_script = """
            <meta http-equiv="refresh" content="0; url='%s'">
            """ % (f"""/Añadir movimientos?page=modify_movement&token={token}-{movement_id}&username={username}&option={option}&placeholder={df.iloc[selected_row]["concept"]}""")
        st.write(nav_script, unsafe_allow_html=True)

