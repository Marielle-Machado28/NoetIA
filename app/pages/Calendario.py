import streamlit as st
from noetia.config import get_db_path
from noetia.db import get_conn, fetch_all

st.set_page_config(page_title="NoetIA | Calendario", page_icon="assets/logo-minimal.png", layout="wide")

st.title("Calendario")
st.caption("Eventos (citas) guardados en la base de datos")

with st.sidebar:
    st.image("assets/logo-secondary.png", use_container_width=True)

db_path = get_db_path()
conn = get_conn(db_path)

rows = fetch_all(
    conn,
    """
SELECT
    c.idCita,
    c.tituloCita,
    c.descripcionCita,
    c.fechaInicio,
    c.fechaFin,
    c.ubicacion,
    c.sincronizacionGoogle,
    p.nombreProyecto,
    a.nombreArea,
    te.nombreTema
FROM cita c
LEFT JOIN proyecto p ON c.idProyecto = p.idProyecto
LEFT JOIN area a ON c.idArea = a.idArea
LEFT JOIN tema te ON c.idTema = te.idTema
ORDER BY c.fechaInicio ASC
""",
)

conn.close()

if not rows:
    st.warning("No hay citas aún. Ejecuta el seed de datos dummy para ver ejemplos.")
    st.info("💡 Más adelante: vista tipo calendario, filtros por rango de fechas y sincronización con Google Calendar.")
else:
    st.metric("Citas", len(rows))
    data = [dict(r) for r in rows]
    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "idCita": st.column_config.NumberColumn("ID", width="small"),
            "tituloCita": st.column_config.TextColumn("Título"),
            "descripcionCita": st.column_config.TextColumn("Descripción", width="large"),
            "fechaInicio": st.column_config.DatetimeColumn("Inicio", format="DD/MM/YYYY HH:mm"),
            "fechaFin": st.column_config.DatetimeColumn("Fin", format="DD/MM/YYYY HH:mm"),
            "ubicacion": st.column_config.TextColumn("Ubicación"),
            "sincronizacionGoogle": st.column_config.CheckboxColumn("Sync Google", width="small"),
            "nombreProyecto": st.column_config.TextColumn("Proyecto"),
            "nombreArea": st.column_config.TextColumn("Área"),
            "nombreTema": st.column_config.TextColumn("Tema"),
        },
    )
    with st.expander("💡 Próximamente"):
        st.markdown("Vista tipo calendario, filtros por rango de fechas y sincronización con Google Calendar.")
