import sqlite3
from pathlib import Path
from typing import Any, Iterable, Optional

def get_conn(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row  # para acceder por nombre de columna
    return conn

def fetch_all(conn: sqlite3.Connection, query: str, params: Optional[Iterable[Any]] = None):
    cur = conn.cursor()
    cur.execute(query, params or [])
    return cur.fetchall()
