
import os
import shutil
from pathlib import Path
from openai import OpenAI
import base64
from noetia.get_db_connection import get_db_connection  
from noetia.config import OPENAI_MODEL, OPENAI_API_KEY

BASE_DIR = Path(__file__).resolve().parent.parent.parent
client = OpenAI(api_key=OPENAI_API_KEY)


def procesar_imagen_y_registrar(ruta_imagen: str) -> dict:

    with open(ruta_imagen, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode('utf-8')

    destino_dir = BASE_DIR / 'assetos' / 'screenshots'
    os.makedirs(destino_dir, exist_ok=True)
    
 
    nombre_archivo = os.path.basename(ruta_imagen)
    ruta_destino = os.path.join(destino_dir, nombre_archivo)
    
    if os.path.abspath(ruta_imagen) != os.path.abspath(ruta_destino):
        shutil.copy2(ruta_imagen, ruta_destino)


    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": [
                {"type": "text", "text": "Transcribe exactamente el texto escrito a mano en esta imagen."},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64_image}"}}
            ]}
        ]
    )
    
    texto_extraido = response.choices[0].message.content.strip()

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        query = """
        INSERT INTO entradaCruda (textoOriginal, idPerfil, fuente, fechaCreacion)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (texto_extraido, 1, nombre_archivo))
        id_registrado = cursor.lastrowid
        conn.commit()
        
    return {
        "idEntrada": id_registrado,
        "textoOriginal": texto_extraido,
        "fuente": nombre_archivo,
        "ruta": ruta_destino
    }