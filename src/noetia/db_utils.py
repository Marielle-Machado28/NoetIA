import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def get_db_connection():
    """Crea una conexión a la BD y configura el retorno de resultados como dict."""
    db_path =BASE_DIR / 'sql' / 'noetia.db'
    conn = sqlite3.connect(db_path)
    
    # Esto permite acceder a las columnas por nombre: row['nombre_columna']
    conn.row_factory = sqlite3.Row
    return conn