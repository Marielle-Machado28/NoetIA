import sqlite3
import joblib
import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_area.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'

datos_cargados = joblib.load(MODEL_PATH)

modelo_cargado = datos_cargados['pipeline']

conn = sqlite3.connect(DB_PATH)
df_areas_db = pd.read_sql("SELECT idArea, nombreArea FROM area", conn)
conn.close()

# Crear un diccionario para convertir rápido: {'Amistad': 1, 'Salud': 2...}
mapeo_nombres_a_ids = dict(zip(df_areas_db['nombreArea'], df_areas_db['idArea']))

def procesar_y_clasificar_areas(datos_recibidos: dict):
    # 1. Creamos el DataFrame para el modelo

    columnas_modelo = ['texto_estandar', 'verbo_principal', 'es_fecha_default', 'tiene_fecha', 'tiene_lugar']
    datos_limpios = {k: datos_recibidos.get(k) for k in columnas_modelo}

    df_input = pd.DataFrame([datos_limpios])
    
    # 2. Obtenemos el nombre del área desde el modelo
    nombre_area_predicho = modelo_cargado.predict(df_input)[0]
    
    # 3. Obtenemos el ID desde nuestro diccionario
    id_final = mapeo_nombres_a_ids.get(nombre_area_predicho)
    
    # 4. Construimos el objeto de retorno (tu paquete completo)
    resultado = {
        'texto_estandar': datos_limpios['texto_estandar'],
        'verbo_principal': datos_limpios['verbo_principal'],
        'es_fecha_default': datos_limpios['es_fecha_default'],
        'tiene_fecha': datos_limpios['tiene_fecha'],
        'tiene_lugar': datos_limpios['tiene_lugar'],
        'idArea': id_final  # El ID real de tu SQL
    }
    
    return resultado
