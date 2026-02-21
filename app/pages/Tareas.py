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

from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all
# Filtros en sidebar
with st.sidebar:
    st.subheader("🔍 Filtros")
    estado = st.selectbox(
        "Estado",
        ["(todas)", "pendiente", "en_progreso", "hecha", "cancelada"],
        index=0,
    )
    solo_importantes = st.toggle("Solo importantes", value=False)
    solo_urgentes = st.toggle("Solo urgentes", value=False)
    st.markdown("---")
    

db_path = get_db_path()
conn = get_conn(db_path)

query = """
SELECT
    t.idTarea,
    t.estadoTarea,
    t.esImportante,
    t.esUrgente,
    t.cuadranteEisenhower,
    t.minutosEstimados,
    t.fechaVencimiento,
    t.fechaCreacion,
    p.nombreProyecto,
    a.nombreArea,
    te.nombreTema
FROM tarea t
LEFT JOIN proyecto p ON t.idProyecto = p.idProyecto
LEFT JOIN area a ON t.idArea = a.idArea
LEFT JOIN tema te ON t.idTema = te.idTema
WHERE 1=1
"""
params = []

if estado != "(todas)":
    query += " AND t.estadoTarea = ?"
    params.append(estado)

if solo_importantes:
    query += " AND t.esImportante = 1"

if solo_urgentes:
    query += " AND t.esUrgente = 1"

query += " ORDER BY COALESCE(t.fechaVencimiento, t.fechaCreacion) ASC"

rows = fetch_all(conn, query, params)
conn.close()

# Resumen rápido
if rows:
    total = len(rows)
    st.metric("Tareas mostradas", total)

st.subheader("📋 Lista")
if not rows:
    st.warning("No hay tareas aún. Cuando insertes datos dummy, aparecerán aquí.")
else:
    data = [dict(r) for r in rows]
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "idTarea": st.column_config.NumberColumn("ID", width="small"),
            "estadoTarea": st.column_config.TextColumn("Estado", width="small"),
            "esImportante": st.column_config.CheckboxColumn("Importante", width="small"),
            "esUrgente": st.column_config.CheckboxColumn("Urgente", width="small"),
            "cuadranteEisenhower": st.column_config.TextColumn("Eisenhower", width="small"),
            "minutosEstimados": st.column_config.NumberColumn("Min est.", width="small"),
            "fechaVencimiento": st.column_config.DatetimeColumn("Vencimiento", format="DD/MM/YYYY"),
            "fechaCreacion": st.column_config.DatetimeColumn("Creación", format="DD/MM/YYYY HH:mm"),
            "nombreProyecto": st.column_config.TextColumn("Proyecto"),
            "nombreArea": st.column_config.TextColumn("Área"),
            "nombreTema": st.column_config.TextColumn("Tema"),
        },
    )
