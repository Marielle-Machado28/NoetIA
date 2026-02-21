import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI
from noetia.config import OPENAI_MODEL, OPENAI_API_KEY
from noetia.model_area import procesar_y_clasificar_areas
from noetia.model_tema import procesar_y_clasificar_tema
from noetia.model_intencion import procesar_y_clasificar_intencion
from noetia.model_prioridad import clasificar_prioridad
from noetia.model_proyecto import inferir_proyecto
from datetime import datetime, timedelta
from noetia.arquitectura import guardar_en_db_clasificado

from pathlib import Path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
raiz_proyecto = Path(os.getcwd()).parent
sys.path.append(str(raiz_proyecto / 'src'))


def obtener_contexto_temporal():
    ahora = datetime.now()
    inicio_semana = ahora - timedelta(days=ahora.weekday()) # Lunes
    fin_semana = ahora + timedelta(days=(6 - ahora.weekday())) # Domingo
    proxima_semana_inicio = inicio_semana + timedelta(days=7)
    proxima_semana_fin = fin_semana + timedelta(days=7)

    return f"""
    CONTEXTO TEMPORAL (Fecha actual: {ahora.strftime('%Y-%m-%d %A')}):
    1. HOY: {ahora.strftime('%Y-%m-%d')}
    2. MAÑANA: {(ahora + timedelta(days=1)).strftime('%Y-%m-%d')}
    3. PASADO MAÑANA: {(ahora + timedelta(days=2)).strftime('%Y-%m-%d')}
    4. FIN DE SEMANA ACTUAL: {(ahora + timedelta(days=(5-ahora.weekday()))).strftime('%Y-%m-%d')} al {fin_semana.strftime('%Y-%m-%d')}
    5. ESTA SEMANA (rango): {inicio_semana.strftime('%Y-%m-%d')} al {fin_semana.strftime('%Y-%m-%d')}
    6. PRÓXIMA SEMANA (rango): {proxima_semana_inicio.strftime('%Y-%m-%d')} al {proxima_semana_fin.strftime('%Y-%m-%d')}
    7. MES ACTUAL: {ahora.strftime('%B %Y')}
    8. AÑO ACTUAL: {ahora.year}
    
    INSTRUCCIÓN DE PROCESAMIENTO:
    - Si el usuario usa términos relativos, mapealos estrictamente a estos valores.
    - Si el usuario dice "el próximo lunes", identifica la fecha exacta del {proxima_semana_inicio.strftime('%Y-%m-%d')}.
    - Siempre devuelve un JSON con 'fecha_detectada' en formato YYYY-MM-DD.
    """


def agente_estandarizador(texto_crudo: str) -> dict:
    
    contexto_tiempo = obtener_contexto_temporal()
    
    prompt_sistema = f"""
    Eres NoetIA, un asistente de tareas.
    CONTEXTO: {contexto_tiempo}
    
    TAREA:
    1. CORRECCIÓN: Toma la entrada del usuario, corrige ortografía/gramática y conviértela en una frase clara, en infinitivo, y en tono profesional. Este será tu "texto_estandar".
    2. DETECCIÓN: Analiza si la frase resultante tiene:
       - Una fecha clara (usando el contexto temporal).
       - Un lugar definido (si aplica).
       - Una intención clara.
       
    RESPUESTA:
    - Si falta fecha o lugar crítico, devuelve este JSON:
      {{"necesita_info": true, "mensaje_pregunta": "Entendido. ¿Para qué fecha y en qué lugar tienes contemplada esta tarea?"}}
      
    - Si la información está completa, devuelve este JSON:
      {{
        "necesita_info": false,
        "texto_estandar": "Frase profesional y corregida",
        "fecha_detectada": "YYYY-MM-DDTHH:MM:SS",
        "lugar": "nombre_lugar o null",
        "verbo_principal": "verbo",
        "es_fecha_default": boolean
      }}

    Entrada del usuario: {texto_crudo}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Responde SOLO en formato JSON."},
            {"role": "user", "content": prompt_sistema}
        ],
        response_format={ "type": "json_object" }
    )
    return json.loads(response.choices[0].message.content)


def procesar_flujo_completo(texto_usuario: str):
    datos = agente_estandarizador(texto_usuario)
    
    if datos.get("necesita_info"):
        return {"estado": "pendiente", "pregunta": datos["mensaje_pregunta"]}
    
    # Aquí pasamos los datos normalizados a tus modelos
    final = procesar_y_clasificar_areas(datos)
    return {"estado": "listo", "registro": final}
    

def procesar_flujo_completo(texto_usuario: str, id_entrada_cruda: int = None):
    datos = agente_estandarizador(texto_usuario)
    
    # 1. Protección contra KeyError y manejo de estado pendiente
    if datos.get("necesita_info", False):
        return {"estado": "pendiente", "pregunta": datos.get("mensaje_pregunta")}
    
    # 2. Pipeline de clasificación
    resultado_area = procesar_y_clasificar_areas(datos)
    datos_para_tema = {**datos, **resultado_area}
    
    resultado_tema = procesar_y_clasificar_tema(datos_para_tema)
    resultado_intencion = procesar_y_clasificar_intencion({**resultado_tema})
    resultado_prioridad = clasificar_prioridad({**resultado_tema})
    
    id_proj = inferir_proyecto(resultado_tema)
    
    # 3. Construcción del registro
    registro = {
        **resultado_tema, 
        **resultado_intencion, 
        **resultado_prioridad, 
        'idProyecto': id_proj,
        'fecha_detectada': datos.get('fecha_detectada')
    }

    # 4. Inserción condicional
    id_item = None
    if id_entrada_cruda:
        try:
            id_item = guardar_en_db_clasificado(registro, id_entrada_cruda)
        except Exception as e:
            print(f"Error al guardar en DB: {e}")

    return {"estado": "listo", "idItem": id_item, "registro": registro}
    

if __name__ == "__main__":
    texto_usuario = input("¿Qué tienes en mente?: ")
    resultado = procesar_flujo_completo(texto_usuario)
    
    # Si el agente necesita más info, entramos en un ciclo de pregunta-respuesta
    while resultado["estado"] == "pendiente":
        print(f"\nAgente: {resultado['pregunta']}")
        respuesta = input("Tú: ")
        
        # Combinamos lo que ya tenías con la nueva respuesta del usuario
        nuevo_texto = f"{texto_usuario} - {respuesta}"
        resultado = procesar_flujo_completo(nuevo_texto)
    
    print("\n¡Actividad completada y clasificada!")
    print(json.dumps(resultado["registro"], indent=4, ensure_ascii=False))