import streamlit as st
import pandas as pd
from datetime import date
import seaborn as sns
import matplotlib.pyplot as plt
import login

# Rutas de los archivos
PATH_HISTORIAL = "historial.csv"
PATH_STOCK = "stock.csv"
PATH_AGOTADO = "agotado.csv"

# Inicialización del login
login.generarLogin()

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
if 'agotados' not in st.session_state:
    st.session_state["agotados"] = pd.read_csv(PATH_AGOTADO)


# Función para guardar datos en un archivo
def guardar_datos(dataframe, path):
    try:
        dataframe.to_csv(path, index=False)
    except Exception as e:
        st.error(f"Error al guardar datos en {path}: {e}")

# Función para registrar una venta
def registrar_venta(producto, cantidad, detalle=""):
    historial = st.session_state["historial"]
    nueva_venta = {
        "fecha": date.today(),
        "vendedor": st.session_state['usuario'],
        "concepto": producto["descripcion"],
        'codigo':producto['codigo'],
        "monto": producto["venta"] * cantidad,
        "movimiento": "venta",
        "cantidad": cantidad,
        "detalle": detalle,
        "proveedor": producto["proveedor"],
    }
    historial = pd.concat([historial, pd.DataFrame([nueva_venta])], ignore_index=True)
    st.session_state["historial"] = historial
    guardar_datos(historial, PATH_HISTORIAL)
def registrar_actualizacion(producto,diferencia,tipo, detalle=""):
    historial = st.session_state["historial"]
    nuevo_ingreso = {
        "fecha": date.today(),
        "vendedor": st.session_state.get("usuario", "Desconocido"),
        "concepto": producto["descripcion"],
        'codigo':producto['codigo'],
        "monto": producto["costo"]*diferencia,
        "movimiento": tipo,
        "cantidad": diferencia,
        "detalle": detalle,
        "proveedor": producto["proveedor"],
    }
    historial = pd.concat([historial, pd.DataFrame([nuevo_ingreso])], ignore_index=True)
    st.session_state["historial"] = historial
    guardar_datos(historial, PATH_HISTORIAL)
# Función para registrar productos agotados
def registrar_agotado(producto, detalle=""):
    st.session_state["agotados"] = pd.read_csv(PATH_AGOTADO)
    agotados = st.session_state["agotados"]
    nuevo_agotado = {
        "fecha": date.today(),
        "concepto": producto["descripcion"],
        'codigo':producto['codigo'],
        "proveedor": producto.get("proveedor", ""),
        "costo": producto.get("costo", 0.0),
        "detalle":detalle
    }
    agotados = pd.concat([agotados, pd.DataFrame([nuevo_agotado])], ignore_index=True)
    st.session_state["agotados"] = agotados
    guardar_datos(agotados, PATH_AGOTADO)

    # Actualiza el estado en el stock
    try:
        stock = pd.read_csv(PATH_STOCK)
        stock.loc[stock["codigo"] == producto["codigo"], "estado"] = "agotado"
        guardar_datos(stock, PATH_STOCK)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo {PATH_STOCK}. No se pudo actualizar el estado del producto.")
    except Exception as e:
        st.error(f"Error al actualizar el archivo {PATH_STOCK}: {e}")
# Función para mostrar balance
def balance():
    historial = st.session_state["historial"]
    stock=st.session_state['stock']
    costo = stock['costo'].sum()
    ventas = historial[historial["movimiento"] == "venta"]["monto"].sum()
    perdidas=historial[historial["movimiento"]=="perdida"]["monto"].sum()
    st.metric("Costo", f"${costo:,.2f}")
    st.metric("Ventas", f"${ventas:,.2f}")
    st.metric("Perdida", f"${perdidas:,.2f}")
    st.metric("Balance", f"${ventas - costo+ perdidas:,.2f}")

# Función para generar gráficos
def generar_graficos():
    historial = st.session_state["historial"]
    ventas = historial[historial["movimiento"] == "venta"]

    if ventas.empty:
        st.warning("No hay ventas registradas para mostrar gráficos.")
        return

    st.subheader("Distribución de ventas por vendedor")
    frecs = ventas["vendedor"].value_counts(normalize=True) * 100
    if not frecs.empty:
        fig, ax = plt.subplots()
        ax.pie(frecs, labels=frecs.index, autopct="%1.1f%%")
        ax.set_title("Distribución de ventas por vendedor")
        st.pyplot(fig)

    st.subheader("Productos más vendidos")
    frecs_prod = ventas["concepto"].value_counts(normalize=True) * 100
    if not frecs_prod.empty:
        st.bar_chart(frecs_prod)

# Interfaz principal
st.title("Historial de Movimientos")

st.subheader("Movimientos del stock")
if st.button('limpiar historial',key='limphist'):
    st.session_state["historial"]=pd.DataFrame(columns=['fecha','vendedor','concepto','codigo','monto','movimiento','cantidad','detalle','proveedor'])
    guardar_datos(st.session_state["historial"],PATH_HISTORIAL)
    st.rerun()
if not st.session_state["historial"].empty:
    st.dataframe(st.session_state["historial"])
else:
    st.warning("No hay movimientos registrados.")
if st.button('limpiar registro de agotados',key='limpreg'):
    st.session_state["agotados"]=pd.DataFrame(columns=['fecha','codigo','proveedor','costo','concepto','detalle'])
    guardar_datos(st.session_state["agotados"],PATH_AGOTADO)
    st.rerun()
st.subheader("Productos agotados")
if not st.session_state["agotados"].empty:
    st.dataframe(st.session_state["agotados"])
else:
    st.warning("No hay productos agotados registrados.")

with st.sidebar:
    if st.button("Generar gráficos"):
        generar_graficos()
    if st.button("Mostrar balance"):
        balance()