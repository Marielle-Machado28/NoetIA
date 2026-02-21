import streamlit as st
import os
# Importa tus herramientas (asegúrate de que las rutas sean correctas)
from noetia.voice_processor import procesar_y_registrar # Función que debes tener
from noetia.llm_model import procesar_flujo_completo

def render_voice_note_section():
    st.subheader("🎙️ Nota de Voz")
    
    # Este componente genera un archivo de audio
    from audio_recorder_streamlit import audio_recorder

    audio_bytes = audio_recorder(text="Presiona para grabar")

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        
        if st.button("Procesar Nota de Voz"):
            with st.spinner("Transcribiendo y analizando..."):
                # 1. Guardar temporalmente
                temp_file = "temp_audio.wav"
                with open(temp_file, "wb") as f:
                    f.write(audio_bytes)
                
                # 2. Procesar transcripción
                transcription = procesar_y_registrar(temp_file)
                st.info(f"Transcripción: {transcription}")
                
                # 3. Enviar al LMM
                response = procesar_flujo_completo(transcription)
                st.success(f"Respuesta IA: {response}")
                
                # Limpiar
                os.remove(temp_file)