# noetia/image_note_render.py
import streamlit as st
import os
# Asegúrate de que las rutas a tus módulos sean correctas
# Asume que image_processor toma la ruta de la imagen y hace OCR/descripción
from src.noetia.image_processor import procesar_imagen_y_registrar # Función que debe existir
from noetia.llm_model import procesar_flujo_completo

def render_image_note_section():
    st.subheader("📸 Analizar Imagen")
    
    uploaded_file = st.file_uploader("Sube una imagen", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        # Mostrar la imagen subida
        st.image(uploaded_file, caption="Imagen Subida", use_column_width=True)
        
        # Guardar temporalmente la imagen
        temp_image_path = "temp_uploaded_image.jpg"
        with open(temp_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        if st.button("Analizar Imagen con IA"):
            with st.spinner("Procesando imagen..."):
                # 1. Procesar la imagen (OCR, descripción, etc.)
                # Tu image_processor debería tomar la ruta o los bytes
                image_analysis_result = procesar_imagen_y_registrar(temp_image_path)
                st.info(f"Análisis Preliminar: {image_analysis_result}")
                
                # 2. Enviar el análisis al LMM para una respuesta más profunda
                llm_response = procesar_flujo_completo(f"Analiza esta información de imagen: {image_analysis_result}")
                st.success(f"Respuesta de la IA: {llm_response}")
                
                # Limpiar el archivo temporal
                os.remove(temp_image_path)