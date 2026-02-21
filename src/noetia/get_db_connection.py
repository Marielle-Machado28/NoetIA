import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DB_PATH = BASE_DIR / 'sql' / 'noetia.db'


def get_db_connection():
    """Retorna una conexión activa a la base de datos existente."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn