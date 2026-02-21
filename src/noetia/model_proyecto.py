import sqlite3
import joblib
import pandas as pd
from pathlib import Path
from noetia.text_correction import normalizar_texto


BASE_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = BASE_DIR / 'src'/'noetia' /'models' / 'modelo_proyecto.joblib'
DB_PATH = BASE_DIR / 'sql' / 'noetia.db'

# Carga del modelo de proyecto (asegúrate de que esta línea esté al inicio de tu script)
modelo_cargado = joblib.load(MODEL_PATH)

def inferir_proyecto(datos_recibidos: dict) -> int:
    """
    Toma los datos procesados e infiere el idProyecto correspondiente.
    """
    # Creamos el DataFrame igual que con los otros modelos
    columnas_modelo =  ['texto_estandar', 'idArea', 'idTema']
    df_input = pd.DataFrame([datos_recibidos])[columnas_modelo]

    
    # Inferencia directa del ID
    id_proyecto_predicho = int(modelo_cargado.predict(df_input)[0])
    
    return id_proyecto_predicho

