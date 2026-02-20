import sqlite3
import os

# Función para conectar
def get_conn():
    ruta = r"C:\Users\marie\Documents\development_projects\NoetIA\sql\noetia.db"
    if not os.path.exists(ruta):
        # Intento de respaldo si la ruta absoluta falla
        ruta = "sql/noetia.db"
        
    conn = sqlite3.connect(ruta)
    conn.row_factory = sqlite3.Row
    return conn

# Función que te está dando el error de importación
def fetch_all(query, params=()):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    finally:
        conn.close()

# Por si acaso alguna otra página pide fetch_one
def fetch_one(query, params=()):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    finally:
        conn.close()