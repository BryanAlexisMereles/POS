import streamlit as st
import login
import pages.historial as historial
import pandas as pd

login.generarLogin()

PATH = "stock.csv"
PATH_AGOTADO = "agotado.csv"
PATH_HISTORIAL = "historial.csv"
if 'agotados' not in st.session_state:
    st.session_state["agotados"] = pd.read_csv(PATH_AGOTADO)


# Función para cargar los datos
def load_data():
    return pd.read_csv(PATH)

# Función para guardar los datos
def save_data(dataframe):
    dataframe.to_csv(PATH, index=False)
    st.session_state['stock'] = dataframe

# Inicializar la base de datos y la página actual
if "stock" not in st.session_state:
    st.session_state["stock"] = load_data()

if "page" not in st.session_state:
    st.session_state["page"] = "lista"

if "producto_seleccionado" not in st.session_state:
    st.session_state["producto_seleccionado"] = None
# Inicialización de claves de sesión
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
# Función para guardar o actualizar un producto
def guardar_actualizar_producto(codigo, proveedor, descripcion, cantidad, costo, precio):
    df = st.session_state["stock"]

    # Buscar si el producto ya existe (por código o descripción)
    producto_existente = df[
        (df['codigo'].astype(str) == str(codigo)) |
        (df['descripcion'].str.lower() == descripcion.lower())
    ]

    if not producto_existente.empty:
        idx = producto_existente.index[0]
        stock_anterior = df.loc[idx, 'cantidad']

        # Actualizar valores
        df.loc[idx, 'venta'] = precio
        df.loc[idx, 'costo'] = costo

        if cantidad > df.loc[idx, 'cantidad']:
            if df.loc[idx, 'cantidad']==0:
                st.session_state['stock']=st.session_state['stock'].set_index("codigo")
                st.session_state['stock'].loc[producto_existente['codigo'],'estado']='disponible'
                st.session_state['stock']=st.session_state['stock'].reset_index()
                st.session_state['stock'].to_csv(PATH)
                st.session_state["agotados"] = st.session_state["agotados"].set_index("codigo")
                st.session_state["agotados"]=st.session_state["agotados"].drop(producto_existente['codigo'])
                st.session_state["agotados"] = st.session_state["agotados"].reset_index()
                st.session_state["agotados"].to_csv(PATH_AGOTADO)
                st.rerun()
            historial.registrar_actualizacion(producto_existente.iloc[0].to_dict(),abs(cantidad-stock_anterior), tipo='ingreso')
            st.session_state["producto_seleccionado"] = None
            st.rerun()
            df.loc[idx, 'cantidad'] = cantidad
            save_data(df)
        elif cantidad > 0 and cantidad < df.loc[idx, 'cantidad']:
            historial.registrar_actualizacion(producto_existente.iloc[0].to_dict(),-cantidad, tipo='perdida')
            st.session_state["producto_seleccionado"] = None
            st.rerun()
            df.loc[idx, 'cantidad'] = cantidad
            save_data(df)
        elif cantidad==stock_anterior:
            st.warning('no se actualizó el stock')
        else:
            if stock_anterior==0:
                st.warning('no se actualizó el stock')
            else:
                df.loc[idx, 'estado'] = "agotado"
                st.session_state["producto_seleccionado"] = None
                df.loc[idx, 'cantidad'] = cantidad
                historial.registrar_agotado(df.loc[idx])
                historial.registrar_actualizacion(producto_existente.iloc[0].to_dict(),-stock_anterior, tipo='perdida')
                save_data(df)
                st.rerun()
    else:
        # Crear nuevo producto
        nuevo_producto = {
            "codigo": codigo,
            "proveedor": proveedor,
            "descripcion": descripcion,
            "cantidad": cantidad,
            "costo": costo,
            "venta": precio,
            "estado": 'disponible'
        }
        df = pd.concat([df, pd.DataFrame([nuevo_producto])], ignore_index=True)
        save_data(df)

        # Registrar ingreso en historial
        historial.registrar_actualizacion(nuevo_producto, cantidad, tipo="ingreso")
        st.success("Producto creado y registrado exitosamente.")

    # Actualizar sesión
    st.session_state["stock"] = df

# Página de lista de productos
if st.session_state["page"] == "lista":
    st.title("Gestionar Stock")

    # Barra de búsqueda de productos
    search_query = st.text_input("Buscar producto (por descripción o código)")
    df = st.session_state["stock"]

    # Filtrar los productos según la búsqueda
    if search_query:
        df = df[
            df["descripcion"].str.contains(search_query, case=False, na=False) |
            df["codigo"].astype(str).str.contains(search_query, case=False, na=False)
        ]
    # Botón para agregar un nuevo producto
    if st.button("Agregar Nuevo Producto"):
        st.session_state["producto_seleccionado"] = None
        st.session_state["page"] = "registro"
        st.rerun()
    # Mostrar productos
    if not df.empty:
        df["estado"] = df["cantidad"].apply(lambda x: "agotado" if x == 0 else "disponible")

        for _, row in df.iterrows():
            color = "#3298a1" if row["cantidad"] == 0 else "#0f3336"  # Fondo según estado
            border_color = "#ff0000" if row["cantidad"] == 0 else "#cccccc"

            # Mostrar datos del producto
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
                    <b>Estado:</b> {row['estado']}
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button("Editar", key=f"edit_{row['codigo']}"):
                st.session_state["producto_seleccionado"] = row.to_dict()
                st.session_state["page"] = "registro"
                st.rerun()
    else:
        st.warning("No se encontraron productos en el stock.")

# Página de registro/edición de productos
elif st.session_state["page"] == "registro":
    st.title("Registrar/Editar Producto")

    # Prellenar datos si se seleccionó un producto previamente
    producto_seleccionado = st.session_state["producto_seleccionado"]
    codigo = producto_seleccionado['codigo'] if producto_seleccionado else ""
    proveedor = producto_seleccionado['proveedor'] if producto_seleccionado else ""
    descripcion = producto_seleccionado['descripcion'] if producto_seleccionado else ""
    costo = producto_seleccionado['costo'] if producto_seleccionado else 0.0
    precio = producto_seleccionado['venta'] if producto_seleccionado else 0.0
    cantidad = producto_seleccionado['cantidad'] if producto_seleccionado else 0

    # Formulario de registro
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código*", value=codigo, key="codigo_input")
            proveedor = st.text_input("Proveedor", value=proveedor, key="proveedor_input")
            descripcion = st.text_input("Descripción*", value=descripcion, key="descripcion_input")
        with col2:
            costo = st.number_input("Costo*", min_value=0.0, step=100.0, value=float(costo), key="costo_input")
            precio = st.number_input("Precio*", min_value=0.0, step=100.0, value=float(precio), key="precio_input")
            cantidad2 = st.number_input("Cantidad*", min_value=0, step=1, value=int(cantidad), key="cantidad_input")

        # Botones de formulario
        submit_btn = st.form_submit_button("Guardar/Actualizar Producto")

    # Lógica para guardar o actualizar
    if submit_btn:
        if not codigo or not descripcion:
            st.error("Por favor, complete todos los campos obligatorios.")
        else:
            guardar_actualizar_producto(codigo, proveedor, descripcion, cantidad2, costo, precio)
            st.rerun()
            st.session_state["page"] = "lista"

    # Botón para volver
    if st.button("Volver"):
        st.session_state["page"] = "lista"
        st.rerun()
# Página de edición
def show_editar_page():
    st.title("Edición Manual del CSV")
    st.session_state["stock"]=load_data()
    editable_df = st.data_editor(st.session_state["stock"], use_container_width=True, num_rows="dynamic")

    if st.button("Guardar Cambios",key='guardar'):
        save_data(editable_df)
        st.rerun()

    if st.button("Cancelar",key='cancelar'):
        st.session_state["page"] = 'lista'
        st.rerun()
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
if st.session_state["page"] == "editar":
    show_editar_page()