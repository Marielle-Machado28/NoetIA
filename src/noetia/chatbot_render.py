import streamlit as st
from noetia.text_processor import procesar_texto_y_registrar
from noetia.llm_model import procesar_flujo_completo

def renderizar_chatbot():
    st.divider()
    st.subheader("🤖 Asistente NoetIA")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Mostrar historial
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("¿Qué tienes en mente hoy?"):
        # 1. Mostrar y guardar el input del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        # 2. Construir el contexto para evitar el bucle
        # Buscamos si la última interacción fue una pregunta pendiente
        contexto_completo = prompt
        id_registro = None
        
        # Si el anterior fue el bot preguntando, unimos la tarea original con la respuesta
        if len(st.session_state.messages) > 1:
            ultimo_bot = st.session_state.messages[-2]
            if ultimo_bot["role"] == "assistant" and "Entendido" in ultimo_bot["content"]:
                # Recuperamos la tarea original (está dos posiciones atrás)
                tarea_original = st.session_state.messages[-3]["content"]
                contexto_completo = f"{tarea_original} - {prompt}"

        # 3. Procesar
        with st.spinner("NoetIA analizando..."):
            # Si es el primer mensaje, registramos en DB
            if id_registro is None:
                datos_crudos = procesar_texto_y_registrar(contexto_completo, fuente="Chat-NoetIA")
                id_registro = datos_crudos["idEntradaCruda"]
            
            resultado = procesar_flujo_completo(contexto_completo, id_registro)

        # 4. Respuesta
        if resultado["estado"] == "listo":
            reg = resultado["registro"]

            # Asegúrate de usar los campos que tu modelo realmente devuelve
            tipo = reg.get('nombreIntención') 
            titulo = reg.get('texto_estandar')
            fecha = reg.get('fecha_detectada')
            area = reg.get('nombreArea')
            prioridad = reg.get('prioridad')

            msg = f"""
            ### ✨ ¡NoetIA ha estructurado tu caos!

            **{tipo} confirmada:** > *{titulo}*

            ---
            **Detalles del registro:**
            * 📅 **Fecha:** `{fecha}`
            * 🗂️ **Área:** `{area}`
            * 🚩 **Prioridad:** `{prioridad}`
            """
            
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})
            
        elif resultado["estado"] == "pendiente":
            msg = f"🤖 {resultado['pregunta']}"
            with st.chat_message("assistant"):
                st.markdown(msg)
            st.session_state.messages.append({"role": "assistant", "content": msg})