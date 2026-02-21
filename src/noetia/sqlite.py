import sqlite3
import os

def get_conn(*args, **kwargs):
    """Retorna una conexión a la base de datos en la ruta fija."""
    ruta = r"C:\Users\marie\Documents\development_projects\NoetIA\sql\noetia.db"
    
    # Si la ruta no existe, intentamos ruta relativa por si acaso
    if not os.path.exists(ruta):
        ruta = os.path.join(os.getcwd(), "sql", "noetia.db")
        
    conn = sqlite3.connect(ruta, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def fetch_all(query_or_conn, query_text=None, params=()):
    """
    Se adapta a Proyectos.py:
    Si recibe (conn, "SELECT..."), usa el segundo argumento como SQL.
    Si recibe ("SELECT...", params), usa el primero.
    """
    # Caso 1: Proyectos.py manda fetch_all(conn, "SELECT ...")
    if not isinstance(query_or_conn, str):
        sql = query_text
        # Si params no se pasó, usamos los que vengan después
        actual_params = params
    # Caso 2: Se manda fetch_all("SELECT ...")
    else:
        sql = query_or_conn
        actual_params = query_text if query_text is not None else ()

    # Abrimos conexión interna (la de Proyectos.py se ignora para evitar fugas)
    db = get_conn()
    try:
        cursor = db.cursor()
        cursor.execute(sql, actual_params)
        return cursor.fetchall()
    finally:
        db.close()

def fetch_one(query_or_conn, query_text=None, params=()):
    """Igual que fetch_all pero para un solo resultado."""
    if not isinstance(query_or_conn, str):
        sql = query_text
        actual_params = params
    else:
        sql = query_or_conn
        actual_params = query_text if query_text is not None else ()

    db = get_conn()
    try:
        cursor = db.cursor()
        cursor.execute(sql, actual_params)
        return cursor.fetchone()
    finally:
        db.close()

def update_query (conn, query, params):
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()