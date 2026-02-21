import streamlit as st
import time
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
# Importamos la conexión desde tu arquitectura existente
from noetia.sqlite import get_conn
from noetia.config import get_db_path

load_dotenv()

def marcar_como_sincronizada(id_cita):
    conn = get_conn(get_db_path())
    cursor = conn.cursor()
    # Ejecutamos la actualización
    cursor.execute("UPDATE cita SET sincronizacionGoogle = 1 WHERE idCita = ?", (id_cita,))
    conn.commit()
    # IMPORTANTE: Confirma que la base de datos respondió
    if cursor.rowcount > 0:
        print(f"DEBUG: Base de datos actualizada correctamente para ID: {id_cita}")
    else:
        print(f"DEBUG: ALERTA: No se encontró la cita {id_cita} para actualizar.")
    conn.close()

def sync_event_to_google(event_data):
    try:
        print(f"DEBUG: Iniciando sincronización para: {event_data.get('tituloCita')}")
        
        creds = Credentials(
            token=None,
            refresh_token=st.secrets["TOKENS"]["REFRESH_TOKEN"],
            client_id=st.secrets["TOKENS"]["CLIENT_ID"],
            client_secret=st.secrets["TOKENS"]["CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        # FORZAR RENOVACIÓN DEL TOKEN
        from google.auth.transport.requests import Request
        creds.refresh(Request())
        print("DEBUG: Token renovado exitosamente.")
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Formato de fecha estricto
        start_fmt = event_data['fechaFin'].replace("T","").replace("Z","")
            
        end_fmt = event_data['fechaFin'].replace("T","").replace("Z","")
       

        event = {
            'summary': event_data['tituloCita'],
            'start': {'dateTime': start_fmt},
            'end': {'dateTime': end_fmt},
        }
        
        print(f"DEBUG: Enviando payload: {event}")
        response = service.events().insert(calendarId='primary', body=event).execute()
        print(f"DEBUG: Éxito! Google respondió: {response.get('id')}")
        
        return True 
        
    except Exception as e:
        st.error(f"Error técnico de API: {e}")
        return False