import sqlite3
import joblib
import pandas as pd
from pathlib import Path
from noetia.text_correction import normalizar_texto


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_area.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'

datos_cargados = joblib.load(MODEL_PATH)
modelo_cargado = datos_cargados['pipeline']



def cargar_mapeo_areas(db_path=DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT idArea, nombreArea FROM area", conn)
    conn.close()

    mapeo = {normalizar_texto(nombre): id_area for nombre, id_area in zip(df['idArea'], df['nombreArea'])}
    
    return mapeo

mapeo_nombres_area_a_id = cargar_mapeo_areas()


def procesar_y_clasificar_areas(datos_recibidos: dict):
    # 1. Creamos el DataFrame para el modelo
    columnas_modelo = ['texto_estandar', 'verbo_principal', 'es_fecha_default', 'tiene_fecha', 'tiene_lugar']
    datos_limpios = {k: datos_recibidos.get(k) for k in columnas_modelo}

    df_input = pd.DataFrame([datos_limpios])
    
    # 2. Obtenemos el ID directamente del modelo
    # Como el modelo ya predice el ID numérico, no necesitamos mapeo_nombres_area_a_id
    id_predicho = modelo_cargado.predict(df_input)[0]

    if id_predicho not in mapeo_nombres_area_a_id:
        nombre_area = "Desconocido"
    else:
        nombre_area = mapeo_nombres_area_a_id[id_predicho]

    # 3. Validación básica
    if id_predicho is None:
        raise ValueError("El modelo devolvió un valor nulo para el área.")
    
    # 4. Construimos el objeto de retorno con el ID ya obtenido
    resultado = {
        'texto_estandar': datos_limpios['texto_estandar'],
        'verbo_principal': datos_limpios['verbo_principal'],
        'es_fecha_default': datos_limpios['es_fecha_default'],
        'tiene_fecha': datos_limpios['tiene_fecha'],
        'tiene_lugar': datos_limpios['tiene_lugar'],
        'idArea': int(id_predicho),
        'nombreArea': nombre_area
    }
    
    return resultado
