import whisper
import os

# Al estar en tu PATH, esto usará el FFmpeg recién verificado
# Usamos 'tiny' para mayor velocidad y menos uso de RAM
model = whisper.load_model("tiny", device="cpu")

def transcribir_audio(ruta_archivo: str) -> str:
    if not os.path.exists(ruta_archivo):
        return "Error: Archivo no encontrado"
    
    # 'fp16=False' es necesario en CPU
    # 'language="es"' fuerza el reconocimiento de español
    result = model.transcribe(ruta_archivo, language="es", fp16=False)
    return result["text"].strip()