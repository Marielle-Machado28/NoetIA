import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.io as pio
from pathlib import Path

# 1. Configuración de página (Única y primera)
st.set_page_config(
    page_title="NoetIA - Dashboard",
    page_icon="assets/logo-minimal.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 3. Importaciones propias
from noetia.sidebar import render_sidebar
from noetia.db_utils import get_db_connection 
from noetia.streamlit_ui import hero_logo
from noetia.chatbot_render import renderizar_chatbot

# --- PALETA MAR ---
MAR = {
    "bg": "#FAF7F2", "ink": "#2C2C2C", "accent1": "#D4A373",
    "accent2": "#9C89B8", "accent3": "#6D6875", "accent4": "#B5838D",
    "accent5": "#83AFA1", "accent6": "#F2CC8F"
}
MAR_COLORS = [MAR["accent1"], MAR["accent2"], MAR["accent5"], MAR["accent4"], MAR["accent6"]]
pio.templates["MAR_THEME"] = pio.templates["plotly_white"]
pio.templates["MAR_THEME"].layout.paper_bgcolor = MAR["bg"]
pio.templates["MAR_THEME"].layout.plot_bgcolor = MAR["bg"]
pio.templates["MAR_THEME"].layout.font.color = MAR["ink"]
pio.templates.default = "MAR_THEME"

render_sidebar()
hero_logo("assets/logo-main.png")


def cargar_datos_completos():
    conn = get_db_connection()
    datos = {}
    
    
    try:
        perfil_df = pd.read_sql_query("SELECT * FROM perfil LIMIT 1", conn)
        datos['idPerfil'] = perfil_df.iloc[0]['idPerfil'] if not perfil_df.empty else "NoetIA-User"
        # Usamos iloc[0] porque es el primer y único registro
        datos['nombrePerfil'] = perfil_df.iloc[0]['nombrePerfil'] if 'nombrePerfil' in perfil_df.columns else "Marielle"
    except Exception:
        datos['idPerfil'], datos['nombrePerfil'] = "Usuario", "Marielle"

    # 2. Cargar TODAS las tablas de entorno
    tablas = ['area', 'tema', 'proyecto', 'tarea']
    for tabla in tablas:
        try:
            datos[f'df_{tabla}'] = pd.read_sql_query(f"SELECT * FROM {tabla}", conn)
        except Exception:
            datos[f'df_{tabla}'] = pd.DataFrame() 

    conn.close()
    return datos

# Cargamos toda la base de datos a la memoria de la vista
datos_db = cargar_datos_completos()
df_tarea = datos_db['df_tarea']
df_area = datos_db['df_area']
df_tema = datos_db['df_tema']
df_proyecto = datos_db['df_proyecto']


if not df_tarea.empty and not df_area.empty and 'idArea' in df_tarea.columns and 'idArea' in df_area.columns:
    col_nombre_area = 'nombreArea' if 'nombreArea' in df_area.columns else df_area.columns[-1]
    df_tarea = df_tarea.merge(df_area[['idArea', col_nombre_area]], on='idArea', how='left')

if not df_tarea.empty and not df_tema.empty and 'idTema' in df_tarea.columns and 'idTema' in df_tema.columns:
    col_nombre_tema = 'nombreTema' if 'nombreTema' in df_tema.columns else df_tema.columns[-1]
    df_tarea = df_tarea.merge(df_tema[['idTema', col_nombre_tema]], on='idTema', how='left')

# --- UI DASHBOARD ---
st.title("Centro de Comando")
st.markdown("### 🧠 NoetIA: Tu mente extendida.")

# --- FILTROS GLOBALES ---
st.sidebar.markdown("### 🔍 Filtros")
# Extraemos los nombres de áreas directamente de la tabla cruzada
lista_areas = df_tarea['nombreArea'].dropna().unique().tolist() if 'nombreArea' in df_tarea.columns else []
areas_filtros = st.sidebar.multiselect("Filtrar por Área", lista_areas)

# Aplicar filtro a las tareas
df_filtrado = df_tarea.copy()
if areas_filtros and 'nombreArea' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['nombreArea'].isin(areas_filtros)]

# --- CABECERA Y PERFIL ---
col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("**Bienvenida:** NoetIA estructura tu caos en acciones claras. \n\nEste demo refleja el estado actual de tu base de datos en tiempo real.")
with col2:
    with st.container(border=True):

        if st.session_state.get('editando_perfil', False):
            nuevo_nombre = st.text_input("Editar nombre:", value=datos_db['nombrePerfil'])
            col_b1, col_b2 = st.columns(2)
            if col_b1.button("💾 Guardar"):
                # AQUÍ LLAMAS A TU FUNCIÓN DE ACTUALIZACIÓN EN DB
                # Ejemplo: conn.execute("UPDATE perfil SET nombrePerfil = ?", (nuevo_nombre,))
                st.session_state.editando_perfil = False
                st.rerun()
            if col_b2.button("❌ Cancelar"):
                st.session_state.editando_perfil = False
                st.rerun()
            
        # --- MODO VISTA ---
        else:
            st.subheader(f"👤 Hola: **{datos_db['nombrePerfil']}**")
            st.write(f"ID: **{datos_db['idPerfil']}**")
            if st.button("✏️ Editar Perfil"):
                st.session_state.editando_perfil = True
        if st.button("🛠 Modificar Entorno", type="primary"):
            # Alterna el modo de edición
            st.session_state.edit_mode = not st.session_state.get('edit_mode', False)

# --- KPI DINÁMICOS ---
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric("Tareas Totales", len(df_filtrado))

col_estado = 'estadoTarea' if 'estadoTarea' in df_filtrado.columns else 'status' if 'status' in df_filtrado.columns else None
atrasadas = len(df_filtrado[df_filtrado[col_estado].astype(str).str.contains('Atrasada|Vencida|Pendiente', case=False, na=False)]) if col_estado else 0
kpi2.metric("Atención Requerida", atrasadas, delta_color="inverse")

kpi3.metric("Temas Involucrados", df_filtrado['idTema'].nunique() if 'idTema' in df_filtrado.columns else 0)

# --- GRÁFICOS ---
st.markdown("### 📊 Análisis de Flujo")
col_g1, col_g2 = st.columns(2)

if not df_filtrado.empty:
    with col_g1:
        st.subheader("Distribución por Área")
        if 'nombreArea' in df_filtrado.columns:
            fig = px.pie(df_filtrado, names='nombreArea', color_discrete_sequence=MAR_COLORS, hole=0.6)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Sin datos de área para graficar.")
            
    with col_g2:
        st.subheader("Estado de Tareas")
        if col_estado:
            df_bar = df_filtrado[col_estado].value_counts().reset_index()
            df_bar.columns = ['Estado', 'Cantidad']
            fig_bar = px.bar(df_bar, x='Estado', y='Cantidad', color_discrete_sequence=[MAR["accent5"]])
            st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("No hay tareas registradas o no coinciden con los filtros.")

# --- SECCIÓN: MODIFICAR ENTORNO ---
# Esto solo aparece si le dan clic al botón
# --- SECCIÓN: MODIFICAR ENTORNO ---
if st.session_state.get('edit_mode', False):
    st.divider()
    st.markdown("### 🛠 Administrador de Entorno")
    st.caption("Modifica tus catálogos y guarda los cambios en la base de datos.")
    
    tab_area, tab_tema, tab_proy = st.tabs(["🗂 Áreas", "🏷 Temas", "🚀 Proyectos"])
    
    # --- Pestaña Áreas ---
    with tab_area:
        df_area_editado = st.data_editor(df_area, use_container_width=True, num_rows="dynamic", key="editor_area")
        if st.button("Guardar cambios en Áreas"):
            conn = get_db_connection()
            try:
                df_area_editado.to_sql('area', conn, if_exists='replace', index=False)
                st.success("¡Áreas actualizadas!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close()

    # --- Pestaña Temas ---
    with tab_tema:
        df_tema_editado = st.data_editor(df_tema, use_container_width=True, num_rows="dynamic", key="editor_tema")
        if st.button("Guardar cambios en Temas"):
            conn = get_db_connection()
            try:
                df_tema_editado.to_sql('tema', conn, if_exists='replace', index=False)
                st.success("¡Temas actualizados!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close()

    # --- Pestaña Proyectos ---
    with tab_proy:
        df_proy_editado = st.data_editor(df_proyecto, use_container_width=True, num_rows="dynamic", key="editor_proy")
        if st.button("Guardar cambios en Proyectos"):
            conn = get_db_connection()
            try:
                df_proy_editado.to_sql('proyecto', conn, if_exists='replace', index=False)
                st.success("¡Proyectos actualizados!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
            finally:
                conn.close()

renderizar_chatbot()