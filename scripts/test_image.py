from noetia.image_processor import procesar_imagen_y_registrar
from pathlib import Path

# Asegúrate de tener una imagen de prueba en esta ruta
ARCHIVO_PRUEBA = Path("assets/screenshots/test_nota.png")

def ejecutar_test_imagen():
    if not ARCHIVO_PRUEBA.exists():
        print(f"Error: No encuentro la imagen de prueba en: {ARCHIVO_PRUEBA}")
        return
    
    print(f"--- Iniciando procesamiento de imagen: {ARCHIVO_PRUEBA.name} ---")
    
    try:
        # Ejecutamos el procesador
        resultado = procesar_imagen_y_registrar(str(ARCHIVO_PRUEBA))
        
        print("\n" + "="*50)
        print("RESULTADO DEL OCR Y REGISTRO:")
        print(f"ID en BD: {resultado['idEntrada']}")
        print(f"Texto extraído: {resultado['textoOriginal'][:100]}...") # Primeros 100 caracteres
        print(f"Guardado en: {resultado['ruta']}")
        print(f"{resultado['fuente']}")
        print("="*50)
        print("¡Test exitoso!")
        
    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    ejecutar_test_imagen()