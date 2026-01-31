import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

def check_env():
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "ERROR: Falta OPENAI_API_KEY. Revisa tu archivo .env"
        )
    print("Entorno listo. API Key cargada correctamente.")
