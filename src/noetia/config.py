import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def check_env():
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "ERROR: Falta OPENAI_API_KEY. Revisa tu archivo .env"
        )
    print("Entorno listo. API Key cargada correctamente.")

def get_db_path() -> Path:
    default_path = Path.cwd() / "sql" / "noetia.db"
    db_path = os.getenv("DB_PATH", str(default_path))
    return Path(db_path)

