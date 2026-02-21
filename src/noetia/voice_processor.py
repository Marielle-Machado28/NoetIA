from noetia.get_db_connection import get_db_connection
import whisper
import os
import shutil
from pathlib import Path

model = whisper.load_model("tiny", device="cpu")

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def procesar_y_registrar(ruta_origen: str) -> dict:

    destino_dir =  BASE_DIR / 'assetos' / 'voice_notes'
    os.makedirs(destino_dir, exist_ok=True)
    nombre_archivo = os.path.basename(ruta_origen)
    ruta_destino = os.path.join(destino_dir, nombre_archivo)
    

    if os.path.abspath(ruta_origen) != os.path.abspath(ruta_destino):
        shutil.copy2(ruta_origen, ruta_destino)
    

    texto = model.transcribe(ruta_destino, language="es", fp16=False)["text"].strip()
    

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO entradaCruda (textoOriginal, idPerfil, fuente, fechaCreacion)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (texto, 1, '.mp3'))
        id_registrado = cursor.lastrowid
        conn.commit()
        
    return {
        "idEntrada": id_registrado,
        "textoOriginal": texto,
        "fuente": nombre_archivo,
        "ruta": ruta_destino
    }