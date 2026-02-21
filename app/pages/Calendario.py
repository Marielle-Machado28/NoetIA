import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
from streamlit_calendar import calendar
from noetia.sidebar import render_sidebar
from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all
from noetia.google_sync import sync_event_to_google, marcar_como_sincronizada

st.set_page_config(
    page_title="NoetIA - Dashboard",
    page_icon="assets/logo-minimal.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.set_page_config(page_title="NoetIA - Calendario", layout="wide")
render_sidebar()

# --- CARGA DE DATOS ---
def get_citas_data():
    conn = get_conn(get_db_path())
    query = "SELECT idCita, tituloCita, fechaInicio, fechaFin, sincronizacionGoogle FROM cita ORDER BY fechaInicio ASC"
    rows = fetch_all(conn, query, [])
    conn.close()
    return [dict(r) for r in rows]

# --- LÓGICA DE SINCRONIZACIÓN ---
if "sincronizando" not in st.session_state:
    st.session_state.sincronizando = False

with st.sidebar:
    st.subheader("Opciones")
    if st.button("🔄 Sincronizar con Google"):
        citas = get_citas_data()
        progreso = st.progress(0)
        exitos = 0
        
        for i, cita in enumerate(citas):
            # El flag es 1 (entero) o 0. Asegúrate de comparar bien.
            if cita.get("sincronizacionGoogle") == 0 or cita.get("sincronizacionGoogle") is None:
                with st.spinner(f"Sincronizando: {cita['tituloCita']}"):
                    if sync_event_to_google(cita):
                        marcar_como_sincronizada(cita['idCita'])
                        exitos += 1
            progreso.progress((i + 1) / len(citas))
        
        if exitos > 0:
            st.success(f"¡{exitos} citas sincronizadas!")
            st.rerun() # ESTO ES LO QUE TE FALTABA: Refresca para actualizar la vista
        else:
            st.info("No hay nuevas citas pendientes.")

# --- RENDERIZADO ---
data = get_citas_data()
events = [
    {
        "title": row["tituloCita"],
        "start": row["fechaInicio"],
        "end": row["fechaFin"],
        "resourceId": str(row["idCita"]),
    } for row in data
]

st.title("📅 Mi Calendario de Citas")
state = calendar(events=events, options={
    "initialView": "dayGridMonth", 
    "headerToolbar": {"left": "prev,next", "center": "title", "right": "dayGridMonth,timeGridWeek"}
})