from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import datetime
from dotenv import load_dotenv
from pathlib import Path
import streamlit as st

BASE_DIR = Path(__file__).resolve().parent.parent

ruta_token = BASE_DIR / 'credentials.json'

load_dotenv()

# 1. Ajusta esto con tus credenciales
creds = Credentials(
            token=None,
            refresh_token=st.secrets["TOKENS"]["REFRESH_TOKEN"],
            client_id=st.secrets["TOKENS"]["CLIENT_ID"],
            client_secret=st.secrets["TOKENS"]["CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token"
        )

service = build('calendar', 'v3', credentials=creds)

def test_calendar_connection():
    try:
        # Usamos tiempos simples y estándar
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        
        print("Intentando obtener eventos...")
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=now,
            maxResults=10, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"¡Éxito! Encontré {len(events)} eventos.")
        for event in events:
            print(f"- {event['summary']}")
            
    except Exception as e:
        print(f"ERROR DETECTADO: {e}")

if __name__ == "__main__":
    test_calendar_connection()