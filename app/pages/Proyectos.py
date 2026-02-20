import streamlit as st
from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all

st.set_page_config(page_title="NoetIA | Por Proyecto", page_icon="assets/logo-minimal.png", layout="wide")

st.title("Por Proyecto")
st.caption("Agrupación de tareas, notas y citas por proyecto (vista resumen)")

with st.sidebar:
    st.image("assets/logo-secondary.png", use_container_width=True)

db_path = get_db_path()
conn = get_conn(db_path)

proyectos_rows = fetch_all(
    conn,
    """
SELECT idProyecto, nombreProyecto
FROM proyecto
ORDER BY nombreProyecto ASC
""",
)

if not proyectos_rows:
    st.warning("No hay proyectos aún. Ejecuta el seed de datos dummy y vuelve aquí.")
    conn.close()
    st.stop()

# Convertir sqlite3.Row a diccionarios para que sean serializables
proyectos = [dict(r) for r in proyectos_rows]

proyecto_sel = st.selectbox(
    "Selecciona un proyecto",
    proyectos,
    format_func=lambda r: r["nombreProyecto"],
)
id_proyecto = proyecto_sel["idProyecto"]

st.divider()

# Métricas en cards
col1, col2, col3 = st.columns(3)

with col1:
    tareas = fetch_all(
        conn,
        """
    SELECT estadoTarea, COUNT(*) as total
    FROM tarea
    WHERE idProyecto = ?
    GROUP BY estadoTarea
    """,
        [id_proyecto],
    )
    with st.container(border=True):
        st.subheader("✅ Tareas")
        if tareas:
            for r in tareas:
                st.caption(f"{r['estadoTarea']}: **{r['total']}**")
            total_t = sum(int(r["total"]) for r in tareas)
            st.metric("Total", total_t)
        else:
            st.metric("Total", 0)
            st.caption("Sin tareas.")

with col2:
    notas = fetch_all(
        conn,
        """
    SELECT COUNT(*) as total
    FROM nota
    WHERE idProyecto = ?
    """,
        [id_proyecto],
    )
    with st.container(border=True):
        st.subheader("📝 Notas")
        total_n = int(notas[0]["total"]) if notas else 0
        st.metric("Total", total_n)

with col3:
    citas = fetch_all(
        conn,
        """
    SELECT COUNT(*) as total
    FROM cita
    WHERE idProyecto = ?
    """,
        [id_proyecto],
    )
    with st.container(border=True):
        st.subheader("📅 Citas")
        total_c = int(citas[0]["total"]) if citas else 0
        st.metric("Total", total_c)

st.divider()

st.subheader("📌 Detalle")
tabs = st.tabs(["Tareas", "Notas", "Citas"])

with tabs[0]:
    rows = fetch_all(
        conn,
        """
    SELECT idTarea, estadoTarea, esImportante, esUrgente, cuadranteEisenhower, minutosEstimados, fechaVencimiento, fechaCreacion
    FROM tarea
    WHERE idProyecto = ?
    ORDER BY COALESCE(fechaVencimiento, fechaCreacion) ASC
    """,
        [id_proyecto],
    )
    if rows:
        st.dataframe(
            [dict(r) for r in rows],
            hide_index=True,
            use_container_width=True,
            column_config={
                "idTarea": st.column_config.NumberColumn("ID", width="small"),
                "estadoTarea": st.column_config.TextColumn("Estado"),
                "esImportante": st.column_config.CheckboxColumn("Importante", width="small"),
                "esUrgente": st.column_config.CheckboxColumn("Urgente", width="small"),
                "cuadranteEisenhower": st.column_config.TextColumn("Eisenhower"),
                "minutosEstimados": st.column_config.NumberColumn("Min est."),
                "fechaVencimiento": st.column_config.DatetimeColumn("Vencimiento", format="DD/MM/YYYY"),
                "fechaCreacion": st.column_config.DatetimeColumn("Creación", format="DD/MM/YYYY HH:mm"),
            },
        )
    else:
        st.write("Sin tareas.")

with tabs[1]:
    rows = fetch_all(
        conn,
        """
    SELECT idNota, substr(contenidoNota, 1, 160) as preview, fechaCreacion
    FROM nota
    WHERE idProyecto = ?
    ORDER BY fechaCreacion DESC
    """,
        [id_proyecto],
    )
    if rows:
        st.dataframe(
            [dict(r) for r in rows],
            hide_index=True,
            use_container_width=True,
            column_config={
                "idNota": st.column_config.NumberColumn("ID", width="small"),
                "preview": st.column_config.TextColumn("Vista previa"),
                "fechaCreacion": st.column_config.DatetimeColumn("Creación", format="DD/MM/YYYY HH:mm"),
            },
        )
    else:
        st.write("Sin notas.")

with tabs[2]:
    rows = fetch_all(
        conn,
        """
    SELECT idCita, tituloCita, fechaInicio, fechaFin, ubicacion, sincronizacionGoogle
    FROM cita
    WHERE idProyecto = ?
    ORDER BY fechaInicio ASC
    """,
        [id_proyecto],
    )
    if rows:
        st.dataframe(
            [dict(r) for r in rows],
            hide_index=True,
            use_container_width=True,
            column_config={
                "idCita": st.column_config.NumberColumn("ID", width="small"),
                "tituloCita": st.column_config.TextColumn("Título"),
                "fechaInicio": st.column_config.DatetimeColumn("Inicio", format="DD/MM/YYYY HH:mm"),
                "fechaFin": st.column_config.DatetimeColumn("Fin", format="DD/MM/YYYY HH:mm"),
                "ubicacion": st.column_config.TextColumn("Ubicación"),
                "sincronizacionGoogle": st.column_config.CheckboxColumn("Sync Google", width="small"),
            },
        )
    else:
        st.write("Sin citas.")

conn.close()
