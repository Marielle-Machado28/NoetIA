import sys
import os
import streamlit as st

st.set_page_config(
    page_title="NoetIA",
    page_icon="assets/logo-minimal.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. Configuración de rutas (Tu lógica de sys.path)
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
src_path = os.path.join(root_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 3. Importaciones propias
from noetia.config import get_db_path
from noetia.streamlit_ui import hero_logo
from noetia.sidebar import render_sidebar

# 4. Renderizado
render_sidebar()

# Header con logo principal grande
hero_logo("assets/logo-main.png")

st.divider()

# Bienvenida en card visual
with st.container():
    st.subheader("👋 Bienvenida")
    st.markdown(
        """
        **NoetIA** transforma entradas caóticas (brain dumps, notas, ideas) en una estructura accionable:
        **Área → Tema → Proyecto → Tarea / Nota / Cita**.

        Este demo se enfoca en la **visualización** del estado actual de la base de datos.
        """
    )

# Navegación en columnas tipo cards
st.markdown("### 🧭 Navegación")
nav_col1, nav_col2, nav_col3 = st.columns(3)
with nav_col1:
    with st.container(border=True):
        st.markdown("**✅ Tareas**")
        st.caption("Lista filtrable de tareas por estado, importancia y urgencia.")
with nav_col2:
    with st.container(border=True):
        st.markdown("**📅 Calendario**")
        st.caption("Eventos y citas guardados, ordenados por fecha.")
with nav_col3:
    with st.container(border=True):
        st.markdown("**📂 Por Proyecto**")
        st.caption("Resumen por proyecto: tareas, notas y citas.")

st.divider()

# Estado y DB en expander
with st.expander("📦 Estado y configuración", expanded=False):
    db_path = get_db_path()
    st.code(str(db_path), language=None)
    st.caption("Ruta de la base de datos SQLite. Si no hay registros, las vistas se mostrarán vacías.")
    st.info("Cuando ejecutes el seed de datos dummy, aquí verás la misma ruta y las páginas mostrarán contenido.")

