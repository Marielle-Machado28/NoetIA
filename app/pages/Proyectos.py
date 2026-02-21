import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

import streamlit as st
from noetia.sidebar import render_sidebar
from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all, update_query
from noetia.voice_note_render import render_voice_note_section
from noetia.image_note_render import render_image_note_section
from noetia.chatbot_render import renderizar_chatbot

st.set_page_config(page_title="NoetIA - Proyectos", layout="wide")
render_sidebar()

# Conexión
conn = get_conn(get_db_path())
proyectos = [dict(r) for r in fetch_all(conn, "SELECT idProyecto, nombreProyecto FROM proyecto ORDER BY nombreProyecto ASC")]

if not proyectos:
    st.warning("No hay proyectos.")
    st.stop()

# Selector estilizado
col_sel, _ = st.columns([1, 2])
with col_sel:
    proyecto_sel = st.selectbox("Selecciona un proyecto", proyectos, format_func=lambda r: r["nombreProyecto"])

id_proyecto = proyecto_sel["idProyecto"]
st.header(f"Dashboard de: {proyecto_sel['nombreProyecto']}")
st.markdown("---")

# Métricas con mejor UI
c1, c2, c3 = st.columns(3)
# (Tu lógica de métricas aquí...)

# --- MEJORA DE TABLAS ---
st.subheader("📌 Detalle de Actividades")
tabs = st.tabs(["✅ Tareas", "📝 Notas", "📅 Citas"])

with tabs[0]:
    st.write("### Tareas Pendientes y Completadas")
    rows = fetch_all(conn, "SELECT * FROM tarea WHERE idProyecto = ?", [id_proyecto])
    if rows:
        st.dataframe(
            [dict(r) for r in rows],
            use_container_width=True,
            column_config={
                "idTarea": None, # Ocultar ID
                "estadoTarea": st.column_config.SelectboxColumn("Estado", options=["Pendiente", "En progreso", "Hecho"]),
                "fechaVencimiento": st.column_config.DateColumn("Vencimiento", format="DD/MM/YYYY")
            }
        )
    else:
        st.info("No hay tareas registradas en este proyecto.")

with tabs[1]:
    st.write("### Notas del Proyecto")
    rows = fetch_all(conn, "SELECT * FROM nota WHERE idProyecto = ?", [id_proyecto])
    if rows:
        for r in rows:
            with st.expander(f"Nota del {r['fechaCreacion']}"):
                st.write(r['contenidoNota'])
    else:
        st.info("Sin notas.")

with tabs[2]:
    st.write("### Agenda de Citas")
    rows = fetch_all(conn, "SELECT * FROM cita WHERE idProyecto = ?", [id_proyecto])
    if rows:
        st.table(rows) # Tabla estática clara para citas
    else:
        st.info("Sin citas programadas.")

conn.close()

st.divider()

# --- GRID DE 3 COLUMNAS IGUALES ---
# Al pasar el entero 3, Streamlit divide el espacio en partes iguales
grid_col1, grid_col2, grid_col3 = st.columns(3)

with grid_col1:
    st.subheader("🤖 Chat NoetIA")
    with st.container(border=True, height=300):
        renderizar_chatbot()

with grid_col2:
    st.subheader("🎙️ Voice Note")
    with st.container(border=True, height=300):
        # Aquí renderizamos el componente de voz
        render_voice_note_section()

with grid_col3:
    st.subheader("📸 Foto")
    with st.container(border=True, height=300):
        # Aquí renderizamos el componente de voz
        render_image_note_section()