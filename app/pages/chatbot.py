import sys
import os
import streamlit as st

# 1. Configuración de página (Única y primera)
st.set_page_config(page_title="NoetIA", layout="wide")

# 2. Configuración de paths (para que el sidebar encuentre tus módulos)
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
src_path = os.path.join(root_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 3. Sidebar y resto de lógica
from noetia.sidebar import render_sidebar
render_sidebar()

# ... (Ahora tu código específico de la página: tareas, calendario, etc.)