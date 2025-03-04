import streamlit as st
st.set_page_config(layout='wide')
import login
login.generarLogin()
st.title("Punto de venta!")
if 'usuario' in st.session_state:
    st.switch_page('pages/nuevo.py')