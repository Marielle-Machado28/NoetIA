import os
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI
from noetia.config import OPENAI_MODEL, OPENAI_API_KEY
from noetia.model_area import procesar_y_clasificar_areas
import datetime

from pathlib import Path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
raiz_proyecto = Path(os.getcwd()).parent
sys.path.append(str(raiz_proyecto / 'src'))


def agente_estandarizador(texto_crudo: str) -> dict:
    
    ahora = datetime.datetime.now()
    fecha_hoy_str = ahora.strftime('%Y-%m-%d')
    dia_semana_str = ahora.strftime('%A')
    
    prompt_sistema = f"""
    Eres un asistente experto de NoetIA. Tu tarea es normalizar tareas y gestionar fechas.
    Hoy es {fecha_hoy_str} y es {dia_semana_str}. .
    
    Analiza la entrada:
    - Si el usuario dice "mañana", calcula { (ahora + datetime.timedelta(days=1)).strftime('%Y-%m-%d') }.
    - Si el usuario dice un día de la semana (ej: "martes"), calcula la fecha correspondiente a la semana actual.
    - Si el usuario dice "mañana", calcula la fecha de mañana.
    - Formato obligatorio: YYYY-MM-DDTHH:MM:SS.

    - Si falta información crítica (fecha o acción clara), 
      devuelve: {{"necesita_info": true, "mensaje_pregunta": "Tu pregunta corta"}}
    - Si tienes todo, devuelve exactamente este JSON:

    {{
        "texto_estandar": "string",
        "fecha_detectada": "YYYY-MM-DDTHH:MM:SS",
        "lugar": "string" | null,
        "longitud_tokens": integer,
        "verbo_principal": "string",
        "cambios": ["lista de ajustes"],
        "es_ambiguo": boolean,
        "es_fecha_default": boolean
    }}
    Texto original: <<<{texto_crudo}>>>
    """

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
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
    

def procesar_flujo_completo(texto_usuario: str):
    datos = agente_estandarizador(texto_usuario)
    
    # 1. Protección contra KeyError
    if datos.get("necesita_info", False):
        return {"estado": "pendiente", "pregunta": datos.get("mensaje_pregunta", "¿Puedes darme más info?")}
    
    # 2. Construcción explícita del dict que el modelo entiende
    # Esto evita que pasemos cosas raras al modelo
    datos_para_modelo = {
        'texto_estandar': datos.get('texto_estandar', 'tarea'),
        'verbo_principal': datos.get('verbo_principal', 'realizar'),
        'es_fecha_default': datos.get('es_fecha_default', True),
        'tiene_fecha': 1 if datos.get('tiene_fecha') else 0,
        'tiene_lugar': 1 if datos.get('tiene_lugar') else 0
    }
    
    # 3. Llamada segura
    final = procesar_y_clasificar_areas(datos_para_modelo)
    
    return {"estado": "listo", "registro": final}
    

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