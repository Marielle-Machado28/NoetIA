import sqlite3
import joblib
import pandas as pd
from pathlib import Path
from noetia.text_correction import normalizar_texto


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_prioridad.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'

modelo_cargado = joblib.load(MODEL_PATH)


def clasificar_prioridad(datos_recibidos: dict) -> dict:
    # 1. Preparar datos para el modelo
    columnas_modelo = ['texto_estandar', 'verbo_principal', 'es_fecha_default', 'tiene_fecha', 'tiene_lugar']
    df_input = pd.DataFrame([datos_recibidos])[columnas_modelo]

    # 2. Inferencia: El modelo nos da un número del 1 al 4
    # 1: Urgente e Importante (Hacer)
    # 2: No Urgente pero Importante (Planificar)
    # 3: Urgente pero No Importante (Delegar)
    # 4: Ni Urgente ni Importante (Eliminar/Ignorar)
    nivel = int(modelo_cargado.predict(df_input)[0])

    # 3. Mapeo a la Matriz de Eisenhower
    mapeo_eisenhower = {
        1: {"etiqueta": "Hacer", "descripcion": "Urgente e Importante"},
        2: {"etiqueta": "Planificar", "descripcion": "No Urgente pero Importante"},
        3: {"etiqueta": "Delegar", "descripcion": "Urgente pero No Importante"},
        4: {"etiqueta": "Eliminar", "descripcion": "Ni Urgente ni Importante"}
    }
    
    info_eisenhower = mapeo_eisenhower.get(nivel, {"etiqueta": "Desconocido", "descripcion": "N/A"})

    # 4. Construimos el resultado enriquecido
    # Agregamos los campos booleanos que pides para cada actividad
    datos_recibidos['prioridad_nivel'] = nivel
    datos_recibidos['etiqueta_eisenhower'] = info_eisenhower['etiqueta']
    datos_recibidos['es_urgente'] = True if nivel in [1, 3] else False
    datos_recibidos['es_importante'] = True if nivel in [1, 2] else False
    
    return datos_recibidos
