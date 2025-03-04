import streamlit as st
import sqlite3
import pandas as pd

# Función para conectar a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('base.db')  # Archivo local en el directorio de la app
    return conn

# Crear la tabla si no existe
conn = get_db_connection()


# Título de la app
st.title("CRUD Básico con SQLite")

# Crear un nuevo cliente
st.subheader("Agregar")
codigo = st.text_input("Codigo")
proveedor = st.text_input("Proveedor")
descripcion = st.text_input("Descripción")
cantidad=st.number_input('Cantidad', min_value=1, step=1)
costo=st.number_input('Costo', min_value=0.0, step=100.0)
venta=st.number_input('Venta', min_value=0.0, step=100.0)
estado='Disponible' if cantidad>0 else 'Agotado'

if st.button("Agregar"):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO stock (codigo, proveedor, descripcion, cantidad, costo, venta, estado) VALUES (?, ?, ?,?, ?, ?,?)",
        (codigo, proveedor, descripcion, cantidad, costo, venta, estado)
    )
    conn.commit()
    conn.close()
    st.success("Cargado")

# Mostrar todos los clientes
st.subheader("stock")
conn = get_db_connection()
df = pd.read_sql("SELECT * FROM stock", conn)
conn.close()
st.dataframe(df)