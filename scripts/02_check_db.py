import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH")

if not DB_PATH:
    raise ValueError("DB_PATH no está definido")

DB_PATH = Path(DB_PATH)

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [r[0] for r in cur.fetchall()]

    print("Tablas encontradas:")
    for t in tables:
        print(" -", t)

    conn.close()

if __name__ == "__main__":
    main()