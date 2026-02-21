import sys
import os
import pandas as pd
import streamlit as st
import plotly.express as px

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from noetia.sidebar import render_sidebar
from noetia.config import get_db_path
from noetia.sqlite import get_conn, fetch_all, update_query
from noetia.voice_note_render import render_voice_note_section
from noetia.image_note_render import render_image_note_section
from noetia.chatbot_render import renderizar_chatbot

st.set_page_config(page_title="NoetIA - Tareas Pro", layout="wide")
render_sidebar()

conn = get_conn(get_db_path())

# --- LÓGICA DE FILTROS ---
# Nota: He ajustado los filtros para que coincidan con la lógica numérica de Eisenhower
filtro_eisenhower = st.sidebar.multiselect("Prioridad Eisenhower (1-4)", [1, 2, 3, 4])
query = "SELECT * FROM tarea WHERE 1=1"
params = []

if filtro_eisenhower:
    placeholders = ', '.join(['?'] * len(filtro_eisenhower))
    query += f" AND cuadranteEisenhower IN ({placeholders})"
    params.extend(filtro_eisenhower)

rows = fetch_all(conn, query, params)
df = pd.DataFrame([dict(r) for r in rows])

if df.empty:
    st.warning("No hay tareas.")
    st.stop()

# --- PREPARACIÓN DEL EDITOR ---
# Creamos la columna lógica para el Checkbox inicial
df['Completar'] = df['estadoTarea'] == 'hecha'

st.title("📋 Gestión de Actividades")

# --- 1. KPIs SUPERIORES ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total", len(df))
c2.metric("Pendientes", len(df[df['estadoTarea'] != 'hecha']))
c3.metric("Completadas", len(df[df['estadoTarea'] == 'hecha']))
c4.metric("Urgentes", len(df[df['esUrgente'] == 1]))

st.divider() # Línea divisoria elegante

# --- 2. EDITOR DE TABLA ---
st.subheader("🎯 Matriz de Acción")

# Columnas importantes a mostrar
cols_to_show = ['Completar', 'estadoTarea', 'esImportante', 'esUrgente', 'cuadranteEisenhower', 'fechaVencimiento']

# --- PREPARACIÓN DEL EDITOR (CORRECCIÓN CRÍTICA) ---

# 1. Convertir la columna de fecha a objetos datetime de Pandas
if 'fechaVencimiento' in df.columns:
    df['fechaVencimiento'] = pd.to_datetime(df['fechaVencimiento'], errors='coerce')

# 2. Asegurar que Eisenhower sea numérico (para evitar conflictos con el Selectbox)
if 'cuadranteEisenhower' in df.columns:
    df['cuadranteEisenhower'] = pd.to_numeric(df['cuadranteEisenhower'], errors='coerce')

# 3. Crear la columna de checkbox
df['Completar'] = df['estadoTarea'] == 'hecha'

edited_df = st.data_editor(
    df,
    use_container_width=True,
    hide_index=True,
    column_order=cols_to_show,
    column_config={
        "idTarea": None,
        "Completar": st.column_config.CheckboxColumn("✅", help="Marcar como hecha"),
        "estadoTarea": st.column_config.SelectboxColumn("Estado", options=["pendiente", "en_progreso", "hecha", "cancelada"]),
        "esImportante": st.column_config.CheckboxColumn("Imp."),
        "esUrgente": st.column_config.CheckboxColumn("Urg."),
        "cuadranteEisenhower": st.column_config.SelectboxColumn("Eis.", options=[1, 2, 3, 4]),
        "fechaVencimiento": st.column_config.DateColumn("Vencimiento", format="DD/MM/YYYY"),
    }
)

if st.button("🚀 Guardar Cambios", type="primary"):
    for index, row in edited_df.iterrows():
        # --- LÓGICA AUTOMÁTICA DE EISENHOWER ---
        imp = bool(row['esImportante'])
        urg = bool(row['esUrgente'])
        
        if imp and urg:   nuevo_cuadrante = 1
        elif imp and not urg: nuevo_cuadrante = 2
        elif not imp and urg: nuevo_cuadrante = 3
        else:                 nuevo_cuadrante = 4
        
        # Lógica de estado
        nuevo_estado = 'hecha' if row['Completar'] else row['estadoTarea']
        
        # Conversión de fecha
        fecha_str = row['fechaVencimiento'].strftime('%Y-%m-%d') if pd.notnull(row['fechaVencimiento']) else None
        
        # Actualización
        update_query(
            conn, 
            """UPDATE tarea 
               SET estadoTarea = ?, 
                   esImportante = ?, 
                   esUrgente = ?, 
                   cuadranteEisenhower = ?, 
                   fechaVencimiento = ? 
               WHERE idTarea = ?""",
            (nuevo_estado, int(imp), int(urg), 
             nuevo_cuadrante, fecha_str, row['idTarea'])
        )
    
    st.toast("¡Tareas actualizadas y cuadrante recalculado!", icon="✅")
    st.rerun()

conn.close()

# --- 3. GRÁFICAS INFERIORES ---
st.subheader("📊 Análisis de Tareas")
g1, g2 = st.columns(2)

with g1:
    fig_pie = px.pie(df, names='estadoTarea', title="Distribución por Estado", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with g2:
    st.subheader("⚠️ Matriz de Eisenhower (Distribución)")
    
    # Creamos un gráfico de dispersión para ver dónde caen las tareas
    # Usamos jitter para que los puntos no se encimen si tienen los mismos valores
    fig_scatter = px.scatter(
        df, 
        x='esUrgente', 
        y='esImportante', 
        color='cuadranteEisenhower',
        size_max=15,
        title="Distribución de Tareas por Urgencia/Importancia",
        labels={'esUrgente': '¿Urgente?', 'esImportante': '¿Importante?'},
        category_orders={"cuadranteEisenhower": [1, 2, 3, 4]}
    )
    
    # Ajustamos los ejes para que solo sean 0 y 1
    fig_scatter.update_xaxes(tickvals=[0, 1], ticktext=["No", "Sí"])
    fig_scatter.update_yaxes(tickvals=[0, 1], ticktext=["No", "Sí"])
    
    st.plotly_chart(fig_scatter, use_container_width=True)

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