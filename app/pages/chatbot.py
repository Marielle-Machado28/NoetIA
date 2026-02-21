import streamlit as st
import json
import os
import pandas as pd
from openai import OpenAI
from noetia.arquitectura import guardar_en_db_clasificado
from noetia.sqlite import get_conn, fetch_all
from noetia.config import get_db_path

from noetia.sidebar import render_sidebar
render_sidebar()

st.set_page_config(page_title="NoetIA - Segundo Cerebro", layout="wide")


client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# --- 1. SYSTEM PROMPT (Socio Operativo) ---
SYSTEM_PROMPT = """
Eres NoetIA, un sistema avanzado de gestión de conocimiento basado en la metodología P.A.R.A. 
y las 12 Áreas de Vida. Tu rol es gestionar, editar y organizar la base de datos del usuario.
- Categoriza en Proyectos, Áreas, Recursos y Archivos.
- Ejecuta cambios y registros inmediatamente mediante herramientas.
- Si detectas que es una 'demo', muestra proactividad, claridad y análisis de datos en tiempo real.
- Mantén el equilibrio en las 12 Áreas de Vida.
"""

# --- 2. CONFIGURACIÓN DE HERRAMIENTAS ---
tools = [{
    "type": "function",
    "function": {
        "name": "gestionar_entrada",
        "description": "Registra tareas, citas o notas.",
        "parameters": {
            "type": "object",
            "properties": {
                "nombreIntención": {"type": "string", "enum": ["tarea", "cita", "nota"]},
                "texto_estandar": {"type": "string"},
                "idArea": {"type": "integer"},
                "idTema": {"type": "integer"},
                "idProyecto": {"type": "integer"},
                "fecha_detectada": {"type": "string"},
                "es_importante": {"type": "integer"},
                "es_urgente": {"type": "integer"},
                "prioridad": {"type": "integer"}
            },
            "required": ["nombreIntención", "texto_estandar", "idArea", "idTema", "idProyecto", "es_importante", "es_urgente", "prioridad"]
        }
    }
}]

# --- 3. INICIALIZACIÓN ---
if "messages_noetia" not in st.session_state:
    st.session_state.messages_noetia = []

st.title("🧠 NoetIA: Segundo Cerebro")

# --- 4. RENDERIZADO (Solo los últimos 2) ---
for msg in st.session_state.messages_noetia[-2:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- 5. PROCESAMIENTO ---
if prompt := st.chat_input("¿Qué vamos a gestionar hoy?"):
    st.session_state.messages_noetia.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Contexto de BD
        conn = get_conn(get_db_path())
        df = pd.DataFrame([dict(r) for r in fetch_all(conn, "SELECT * FROM tarea", [])])
        conn.close()
        
        # Llamada a OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": SYSTEM_PROMPT + f"\nContexto actual: {df.to_string()[:1500]}"}] 
            + st.session_state.messages_noetia,
            tools=tools
        )
        
        msg_obj = response.choices[0].message
        
        if msg_obj.tool_calls:
            for tool_call in msg_obj.tool_calls:
                args = json.loads(tool_call.function.arguments)
                try:
                    guardar_en_db_clasificado(args, id_entrada_cruda=0)
                    res = f"✅ Registrado exitosamente: {args.get('texto_estandar')}"
                    st.success(res)
                    st.session_state.messages_noetia.append({"role": "assistant", "content": res})
                except Exception as e:
                    error_msg = f"❌ Error: {e}"
                    st.error(error_msg)
                    st.session_state.messages_noetia.append({"role": "assistant", "content": error_msg})
        else:
            st.markdown(msg_obj.content)
            st.session_state.messages_noetia.append({"role": "assistant", "content": msg_obj.content})