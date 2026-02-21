import sqlite3
from noetia.text_processor import procesar_texto_y_registrar
from noetia.get_db_connection import get_db_connection

def verificar_en_db(id_buscado):
    """Consulta la BD para confirmar el guardado real."""
    with get_db_connection() as conn:
        # Usamos row_factory para acceder por nombre de columna
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Asegúrate de que 'idEntrada' coincida con el nombre real en tu tabla
        cursor.execute("SELECT * FROM entradaCruda WHERE idEntradaCruda = ?", (id_buscado,))
        return cursor.fetchone()

def ejecutar_test_texto():
    texto_ejemplo = "Revisar los pendientes del proyecto NoetIA"
    fuente_ejemplo = ".txt"
    
    print(f"--- Iniciando Test de Procesador de Texto ---")
    
    # 1. Ejecutar el procesador
    resultado = procesar_texto_y_registrar(texto_ejemplo, fuente_ejemplo)
    
    # 2. Validar respuesta del procesador
    if resultado.get("idEntradaCruda"):
        print(f"✅ Procesador retornó ID: {resultado['idEntradaCruda']}")
        
        # 3. Verificar en la base de datos (Validación Cruzada)
        registro_db = verificar_en_db(resultado['idEntradaCruda'])
        
        if registro_db:
            print("✅ VERIFICACIÓN OK: El texto está en la base de datos.")
            print(f"   -> Contenido guardado: {registro_db['textoOriginal']}")
            print(f"   -> Fuente guardada: {registro_db['fuente']}")
        else:
            print("❌ ERROR: El procesador indicó éxito pero no se encontró en la BD.")
    else:
        print(f"❌ ERROR: El procesador no retornó un ID válido. Resultado: {resultado}")

if __name__ == "__main__":
    ejecutar_test_texto()