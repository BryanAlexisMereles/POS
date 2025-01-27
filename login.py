import streamlit as st
import pandas as pd

# Ocultar el menú y el botón de "Deploy" de Streamlit con CSS
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;} /* Oculta el menú superior */
    footer {visibility: hidden;} /* Oculta el footer */
    header {visibility: hidden;} /* Oculta la cabecera */
    </style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)

# Validación simple de usuario y clave con un archivo CSV
def validarUsuario(usuario, clave):
    """
    Permite la validación de usuario y clave.
    :param usuario: Usuario ingresado
    :param clave: Clave ingresada
    :return: True si el usuario y clave son válidos, False en caso contrario
    """
    try:
        dfusuarios = pd.read_csv('usuarios.csv')  # Cambia la ruta según sea necesario
        # Verifica si existe un usuario y clave que coincidan
        if len(dfusuarios[(dfusuarios['usuario'] == usuario) & (dfusuarios['clave'] == clave)]) > 0:
            return True
    except FileNotFoundError:
        st.error("El archivo 'usuarios.csv' no se encontró.")
    except Exception as e:
        st.error(f"Error al validar usuario: {e}")
    return False

def generarMenu(usuario):
    """
    Genera el menú en la barra lateral dependiendo del usuario.
    :param usuario: Usuario autenticado
    """
    with st.sidebar:
        try:
            dfusuarios = pd.read_csv('usuarios.csv')  # Cambia la ruta según sea necesario
            dfUsuario = dfusuarios[dfusuarios['usuario'] == usuario]
            nombre = dfUsuario['nombre'].values[0]

            # Bienvenida al usuario
            st.write(f"### Bienvenido/a, **{nombre}**")
            st.divider()
            # Menú principal
            st.subheader("Préstamos")
            st.page_link("pages/venta.py", label="venta", icon=":material/sell:")
            st.page_link("pages/ingreso.py", label="ingreso", icon=":material/sell:")
            st.page_link("pages/historial.py", label="historial", icon=":material/sell:")

            # Botón de cierre de sesión
            if st.button("Salir",key='salir'):
                st.session_state.clear()
                st.switch_page('inicio.py')
                st.rerun()  # Redirige al login
        except FileNotFoundError:
            st.error("El archivo 'usuarios.csv' no se encontró.")
        except Exception as e:
            st.error(f"Error al generar el menú: {e}")

def generarLogin():
    """
    Genera la ventana de login o muestra el menú si el login es válido.
    """
    if 'usuario' in st.session_state:
        generarMenu(st.session_state['usuario'])  # Muestra el menú si ya está autenticado
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

# Llama a la función principal
if __name__ == "__main__":
    generarLogin()
