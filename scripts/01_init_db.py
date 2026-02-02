import sqlite3
from pathlib import Path

# Ruta al schema
SCHEMA_PATH = Path("sql/schema.sql")

# Ruta a la base de datos
DB_PATH = Path("data/noetia.db")

def init_db():
    # Crear carpeta data si no existe
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Conectar (crea el archivo si no existe)
    conn = sqlite3.connect(DB_PATH)

    # Activar foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Leer schema.sql
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    # Ejecutar schema
    conn.executescript(schema_sql)

    conn.commit()
    conn.close()

    print("Base de datos creada correctamente en:", DB_PATH)

if __name__ == "__main__":
    init_db()
