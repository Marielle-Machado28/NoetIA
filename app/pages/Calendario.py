import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import streamlit as st
from streamlit_calendar import calendar
from pathlib import Path

# 1. Configuración de página (Única y primera)
st.set_page_config(page_title="NoetIA", layout="wide")

# 2. Configuración de paths (para que el sidebar encuentre tus módulos)
app_path = Path(__file__).resolve().parent
# 2. Configuración de rutas
root_path = app_path.parent
src_path = os.path.join(root_path, 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 3. Sidebar y resto de lógica
from noetia.sidebar import render_sidebar
from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all
from noetia.google_sync import sync_event_to_google
render_sidebar()

# --- CARGA DE DATOS ---
# Asegúrate de que estas variables estén disponibles en tu archivo calendario.py
db_path = get_db_path()
conn = get_conn(db_path)
rows = fetch_all(conn, "SELECT idCita, tituloCita, fechaInicio, fechaFin FROM cita ORDER BY fechaInicio ASC")
conn.close()

# Aquí defines 'data' convirtiendo el resultado de la base de datos a una lista de diccionarios
data = [dict(r) for r in rows]

# Ahora sí, el código de los eventos puede usar 'data'
events = [
    {
        "title": row["tituloCita"],
        "start": row["fechaInicio"],
        "end": row["fechaFin"],
        "resourceId": str(row["idCita"]),
    } for row in data
]

with st.sidebar:
    if st.button("🔄 Sincronizar con Google Calendar"):
        with st.spinner("Sincronizando..."):
            exitos = 0
            for cita in data:
                # Sincroniza cada cita que aún no tiene el flag
                if not cita.get("sincronizacionGoogle"):
                    if sync_event_to_google(cita):
                        exitos += 1
            
            if exitos > 0:
                st.success(f"¡{exitos} citas enviadas al calendario!")
            else:
                st.info("Ya están todas sincronizadas.")

st.title("📅 Mi Calendario de Citas")

# 2. Obtención de datos
db_path = get_db_path()
conn = get_conn(db_path)
rows = fetch_all(conn, "SELECT idCita, tituloCita, fechaInicio, fechaFin FROM cita ORDER BY fechaInicio ASC")
conn.close()

data = [dict(r) for r in rows]

# 3. Transformación a eventos para el calendario
events = [
    {
        "title": row["tituloCita"],
        "start": row["fechaInicio"],
        "end": row["fechaFin"],
        "resourceId": str(row["idCita"]),
    } for row in data
]

# 4. Configuración y renderizado
calendar_options = {
    "editable": "false",
    "selectable": "true",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay",
    },
    "initialView": "dayGridMonth",
    "height": 650,
}

state = calendar(events=events, options=calendar_options)

# 5. Interacción opcional
if state.get("eventClick"):
    clicked_event = state["eventClick"]["event"]
    st.info(f"Seleccionaste: {clicked_event['title']}")