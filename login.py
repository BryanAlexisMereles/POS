import streamlit as st
import sqlite3
import pandas as pd

# Ocultar el menú y el pie de página de Streamlit
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Función para conectar a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('base.db')
    return conn

# Crear la tabla 'usuarios' si no existe
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            usuario TEXT PRIMARY KEY,
            clave TEXT NOT NULL,
            nombre TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


# Validación de usuario y clave con SQLite
def validarUsuario(usuario, clave):
    """
    Permite la validación de usuario y clave.
    :param usuario: Usuario ingresado
    :param clave: Clave ingresada
    :return: True si el usuario y clave son válidos, False en caso contrario
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND clave = ?", (usuario, clave))
        result = cursor.fetchone()
        conn.close()
        return result is not None  # True si hay coincidencia, False si no
    except sqlite3.Error as e:
        st.error(f"Error al validar usuario: {e}")
        return False

def generarMenu():
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            st.page_link("pages/venta.py", label="venta", icon=":material/sell:")
            st.page_link("pages/ingreso.py", label="ingreso", icon=":material/sell:")
            st.page_link("pages/historial.py", label="historial", icon=":material/sell:")
            st.page_link("pages/nuevo.py", label="nuevo", icon=":material/sell:")

            # Botón de cierre de sesión
            if st.button("Salir", key='salir'):
                st.session_state.clear()
                st.switch_page('inicio.py')
                st.rerun()  # Redirige al login
        except sqlite3.Error as e:
            st.error(f"Error al generar el menú: {e}")

def generarLogin():
    """
    Genera la ventana de login o muestra el menú si el login es válido.
    """
    # Inicializar la base de datos al cargar la app
    init_db()

    if 'usuario' in st.session_state:
        generarMenu()  # Muestra el menú si ya está autenticado
    else:
        with st.form(f"frmLogin_{id(generarLogin)}"):  # Clave única usando `id()` de la función
            st.subheader("Iniciar Sesión")
            parUsuario = st.text_input('Usuario')
            parPassword = st.text_input('Password', type='password')
            if st.form_submit_button('Ingresar'):
                if validarUsuario(parUsuario, parPassword):
                    st.session_state['usuario'] = parUsuario
                    st.rerun()  # Forzar redirección para aplicar cambios de estado
                else:
                    st.error("Usuario o clave inválidos")
