from noetia.text_processor import procesar_texto_y_registrar
from noetia.llm_model import procesar_flujo_completo
from noetia.arquitectura import guardar_en_db_clasificado

def ejecutar_flujo_completo(input_usuario: str):
    print(f"\n--- Iniciando END-TO-END ---")
    print(f"Entrada: {input_usuario}")

    # 1. Registrar entrada cruda
    print("1. Registrando en entradaCruda...")
    registro_crudo = procesar_texto_y_registrar(input_usuario, fuente=".txt")
    id_cruda = registro_crudo["idEntradaCruda"] # Asegúrate de que este sea el nombre correcto
    print(f"   -> ID Crudo: {id_cruda}")

    # 2. Procesar con LLM (Clasificación)
    print("2. Consultando a LLM para clasificar...")
    resultado_llm = procesar_flujo_completo(input_usuario, id_cruda)
    
    if resultado_llm["estado"] == "pendiente":
        print(f"   -> El asistente necesita más info: {resultado_llm['pregunta']}")
        return

    # 3. Insertar en arquitectura (Tablas finales)
    print("3. Persistiendo en tablas finales...")
    id_final = guardar_en_db_clasificado(resultado_llm["registro"], id_cruda)
    
    print(f"✅ ¡Flujo completo finalizado! ID en Clasificación: {id_final}")
    print(f"Datos guardados: {resultado_llm['registro']}")

if __name__ == "__main__":
    # Prueba con un input real
    texto = "agendar cita con el dermatologo."
    ejecutar_flujo_completo(texto)