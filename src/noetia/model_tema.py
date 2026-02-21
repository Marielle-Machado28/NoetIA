import sqlite3
import joblib
import pandas as pd
from pathlib import Path
from noetia.text_correction import normalizar_texto


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_tema.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'



modelo_cargado = joblib.load(MODEL_PATH)



def cargar_mapeo_temas(db_path=DB_PATH):
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT idTema, nombreTema FROM tema", conn)
    conn.close()

    df["nombreTema_normalizado"] = df["nombreTema"].apply(normalizar_texto)
    
    return dict(zip(df['nombreTema'], df['idTema']))

mapeo_nombres_tema_a_id = cargar_mapeo_temas()


def procesar_y_clasificar_tema(datos_recibidos: dict):
    # 1. Creamos el DataFrame para el modelo
    columnas_modelo = ['texto_estandar', 'verbo_principal', 'es_fecha_default', 'tiene_fecha', 'tiene_lugar', 'idArea', 'nombreArea']
    datos_limpios = {k: datos_recibidos.get(k) for k in columnas_modelo}

    df_input = pd.DataFrame([datos_limpios])
    
    nombre_tema_predicho = modelo_cargado.predict(df_input)[0]
    
    id_tema_final = mapeo_nombres_tema_a_id.get(nombre_tema_predicho)

    if id_tema_final is None:
        raise ValueError(f"Tema predicho '{nombre_tema_predicho}' no existe en tabla tema.")

    resultado = {
        'texto_estandar': datos_limpios['texto_estandar'],
        'verbo_principal': datos_limpios['verbo_principal'],
        'es_fecha_default':datos_limpios['es_fecha_default'],
        'tiene_fecha': datos_limpios['tiene_fecha'],
        'tiene_lugar': datos_limpios['tiene_lugar'],
        'idArea': datos_limpios['idArea'], 
        'nombreArea':datos_limpios['nombreArea'],
        'idTema': id_tema_final,
        'nombreTema': nombre_tema_predicho
    }
    return resultado
