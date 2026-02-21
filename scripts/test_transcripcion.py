from noetia.voice_processor import procesar_y_registrar
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ARCHIVO_PATH = BASE_DIR / 'assets'/'voice_notes' /'prueba.mp3'

def ejecutar_test():
    # Validamos el archivo específico, no la carpeta
    if not ARCHIVO_PATH.exists():
        print(f"Error: El archivo no existe en la ruta: {ARCHIVO_PATH}")
        return
    
    try:
        print(f"--- Iniciando prueba con: {ARCHIVO_PATH.name} ---")
        
        # Ejecutamos tu función
        texto_resultado = procesar_y_registrar(str(ARCHIVO_PATH))
        
        print("\n" + "="*50)
        print("EL RESULTADO QUE OBTUVISTE ES:")
        print(f"\n{texto_resultado}\n")
        print("="*50)
        
    except Exception as e:
        print(f"--- Hubo un problema al probar la función: {e} ---")
        # Esto te ayudará a ver el error técnico real (ej: problemas de FFmpeg)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ejecutar_test()