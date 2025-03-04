import streamlit as st
import pandas as pd
import login
login.generarLogin()
st.title('en desarrollo!')
'''
import pages.historial as historial
# Configuración inicial

PATH = "stock.csv"
PATH_HISTORIAL = "historial.csv"

# Función para cargar los datos
def load_data():
    return pd.read_csv(PATH)

# Función para guardar los datos
def save_data(dataframe):
    dataframe.to_csv(PATH, index=False)
    st.session_state["stock"] = load_data()

# Inicializar variables en la sesión
if "stock" not in st.session_state:
    st.session_state["stock"] = load_data()

if "page" not in st.session_state:
    st.session_state["page"] = "lista"

if "selected_products" not in st.session_state:
    st.session_state["selected_products"] = pd.DataFrame(columns=['codigo', 'proveedor', 'descripcion', 'cantidad', 'costo', 'venta', 'estado'])

if "historial" not in st.session_state:
    try:
        st.session_state["historial"] = pd.read_csv(PATH_HISTORIAL)
    except FileNotFoundError:
        st.session_state["historial"] = pd.DataFrame(columns=[
            "fecha", "vendedor", "concepto", "monto", "movimiento", "cantidad", "descripcion", "proveedor", "costo"
        ])
    except Exception as e:
        st.error(f"Error al cargar {PATH_HISTORIAL}: {e}")
        st.session_state["historial"] = pd.DataFrame(columns=[
            "fecha", "vendedor", "concepto", "monto", "movimiento", "cantidad", "descripcion", "proveedor", "costo"
        ])

# Página principal
def main_page():
    if st.session_state["page"] == "lista":
        st.session_state["stock"] = load_data()

        if st.session_state['usuario'] == 'admin':
            st.sidebar.subheader("Gestión de Productos")
            uploaded_file = st.sidebar.file_uploader("Sube un archivo CSV para concatenar", type="csv")
            if uploaded_file:
                new_data = pd.read_csv(uploaded_file)
                if list(new_data.columns) == list(st.session_state["stock"].columns):
                    st.session_state["stock"] = pd.concat([st.session_state["stock"], new_data], ignore_index=True)
                    save_data(st.session_state["stock"])
                    st.success("Datos concatenados exitosamente.")
                else:
                    st.warning("Las columnas no coinciden.")

            st.sidebar.subheader("Edición Manual")
            if st.sidebar.button("Editar CSV"):
                st.session_state["page"] = "editar"
                st.rerun()

        if st.button('Limpiar selección', key='limpiar'):
            st.session_state['selected_products'] = pd.DataFrame(columns=['codigo', 'proveedor', 'descripcion', 'cantidad', 'costo', 'venta', 'estado'])

        show_venta_page()
        st.title("Lista de Productos")
        show_lista_page()

# Página de lista de productos
def show_lista_page():
    search_query = st.text_input("Buscar producto (por descripción o código)")
    df = st.session_state["stock"]
    if search_query:
        df = df[
            df["descripcion"].str.contains(search_query, case=False, na=False) |
            df["codigo"].astype(str).str.contains(search_query, case=False, na=False)
        ]

    if not df.empty:
        df["estado"] = df["cantidad"].apply(lambda x: "agotado" if x == 0 else "disponible")

        for _, row in df.iterrows():
            if row['cantidad']>0:
                color = "#3298a1" if row["cantidad"] == 0 else "#0f3336"
                border_color = "#ff0000" if row["cantidad"] == 0 else "#cccccc"

                st.markdown(
                    f"""
                    <div style="
                        border: 2px solid {border_color};
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 10px;
                        background-color: {color};
                    ">
                        <b>Código:</b> {row['codigo']} - <b>Descripción:</b> {row['descripcion']}<br>
                        <b>Stock:</b> {row['cantidad']} - <b>Precio:</b> {row['venta']}<br>
                        {"<b>Estado:</b> <span style='color: red;'>Agotado</span>" if row['cantidad'] == 0 else ""}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                if row["cantidad"] > 0 and st.button("Seleccionar", key=f"select_{row['codigo']}"):
                    if row["codigo"] not in st.session_state["selected_products"]["codigo"].values:
                        st.session_state["selected_products"] = pd.concat(
                            [st.session_state["selected_products"], pd.DataFrame([row])], ignore_index=True
                        )
                        st.rerun()
        for _, row in df.iterrows():
                if row['cantidad']==0:
                    color = "#3298a1" if row["cantidad"] == 0 else "#0f3336"
                    border_color = "#ff0000" if row["cantidad"] == 0 else "#cccccc"

                    st.markdown(
                        f"""
                        <div style="
                            border: 2px solid {border_color};
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 10px;
                            background-color: {color};
                        ">
                            <b>Código:</b> {row['codigo']} - <b>Descripción:</b> {row['descripcion']}<br>
                            <b>Stock:</b> {row['cantidad']} - <b>Precio:</b> {row['venta']}<br>
                            {"<b>Estado:</b> <span style='color: red;'>Agotado</span>" if row['cantidad'] == 0 else ""}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
    else:
        st.warning("No se encontraron resultados.")

# Función para manejar ventas
def venta(producto, cantidad, detalle):
    df = st.session_state["stock"]
    idx = df[df["codigo"] == producto["codigo"]].index[0]  # Encuentra el índice del producto en el DataFrame
    stock_actual = df.loc[idx, "cantidad"]  # Obtén el stock actual

    if cantidad > stock_actual:
        st.warning(f"No hay suficiente stock disponible para {producto['descripcion']}. Stock actual: {stock_actual}")
    elif cantidad<=stock_actual:
        if cantidad==stock_actual:
            historial.registrar_agotado(producto,detalle)
        # Actualiza el stock general
        df.loc[idx, "cantidad"] -= cantidad
        save_data(df)
        historial.registrar_venta(producto,cantidad,detalle)
        # Actualiza la lista de productos seleccionados
        st.session_state["selected_products"].loc[
            st.session_state["selected_products"]["codigo"] == producto["codigo"], "cantidad"
        ] -= cantidad


# Página de venta
def show_venta_page():
    st.title("Cerrar Venta")
    productos = st.session_state["selected_products"]
    total_venta = 0

    for _, producto in productos.iterrows():
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Código:** {producto['codigo']} - **Descripción:** {producto['descripcion']}")
            st.write(f"**Stock disponible:** {producto['cantidad']}")
            st.write(f"**Precio por unidad:** ${producto['venta']:.2f}")
        with col2:
            cantidad = st.number_input(
                f"Cantidad a vender ({producto['descripcion']})",
                min_value=0,
                max_value=int(producto['cantidad']),
                step=1,
                key=f"cantidad_{producto['codigo']}"
            )
            detalle = st.text_input(f"Detalle (opcional)", value="", key=f"detalle_{producto['codigo']}")
        if cantidad > 0:
                monto = cantidad * producto["venta"]
                total_venta += monto
                st.markdown(f"**monto:** ${monto:.2f}")

        st.markdown(f"**total de venta:** ${total_venta:.2f}")
    if st.button("Confirmar Venta",key="confirmar"):
        for _, producto in productos.iterrows():
            cantidad = st.session_state[f"cantidad_{producto['codigo']}"]
            detalle = st.session_state[f"detalle_{producto['codigo']}"]
            if cantidad > 0:
                venta(producto, cantidad, detalle)

        st.session_state["selected_products"] = st.session_state["selected_products"][
            st.session_state["selected_products"]["cantidad"] > 0
        ]  # Elimina productos con cantidad 0
        st.rerun()

# Página de edición
def show_editar_page():
    st.title("Edición Manual del CSV")
    editable_df = st.data_editor(st.session_state["stock"], use_container_width=True, num_rows="dynamic")

    if st.button("Guardar Cambios",key='guardar'):
        save_data(editable_df)
        st.success("Datos actualizados correctamente.")
        st.rerun()

    if st.button("Cancelar",key='cancelar'):
        st.rerun()

# Ejecutar la aplicación principal
if __name__ == "__main__":
    if st.session_state["page"] == "editar":
        show_editar_page()
    else:
        main_page()
'''