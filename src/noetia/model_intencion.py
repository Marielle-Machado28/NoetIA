import sqlite3
import joblib
import pandas as pd
from pathlib import Path
from noetia.text_correction import normalizar_texto


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_intencion.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'

modelo_cargado = joblib.load(MODEL_PATH)

modelo_cargado_intencion = joblib.load('src/noetia/models/modelo_intencion.joblib')

def cargar_mapeo_intencion(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT idClasificacion, tipoFinal FROM clasificacion where idClasificacion <= 3", conn)
    conn.close()

    df["nombreintencion_normalizado"] = df["tipoFinal"].apply(normalizar_texto)
    
    return dict(zip(df['tipoFinal'], df['idClasificacion']))

mapeo_nombres_intencion_a_id = cargar_mapeo_intencion()

def procesar_y_clasificar_intencion(datos_recibidos: dict) -> dict:

    columnas_modelo = ['texto_estandar', 'verbo_principal', 'es_fecha_default', 'tiene_fecha', 'tiene_lugar']
    datos_limpios = {k: datos_recibidos.get(k) for k in columnas_modelo}

    df_input = pd.DataFrame([datos_limpios])

    id_predicho = int(modelo_cargado_intencion.predict(df_input)[0])
    
    mapeo_id_a_nombre = {v: k for k, v in mapeo_nombres_intencion_a_id.items()}
    nombre_intencion = mapeo_id_a_nombre.get(id_predicho, "Desconocido")

    if id_predicho is None:
        raise ValueError(f"Tema predicho '{nombre_intencion}' no existe en tabla tema.")

    resultado = {
        'texto_estandar': datos_limpios.get('texto_estandar'),
        'verbo_principal': datos_limpios.get('verbo_principal'),
        'es_fecha_default': datos_limpios.get('es_fecha_default'),
        'tiene_fecha': datos_limpios.get('tiene_fecha'),
        'tiene_lugar': datos_limpios.get('tiene_lugar'),
        'intencion': nombre_intencion,
        'idClasificacion': id_predicho,
        'nombreIntención': nombre_intencion
    }
    return resultado


