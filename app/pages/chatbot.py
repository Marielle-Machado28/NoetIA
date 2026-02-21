import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st

# 1. Configuración de página (Única y primera)
st.set_page_config(page_title="NoetIA", layout="wide")



# 3. Sidebar y resto de lógica
from noetia.sidebar import render_sidebar
render_sidebar()

# ... (Ahora tu código específico de la página: tareas, calendario, etc.)