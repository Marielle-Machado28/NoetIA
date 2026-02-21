import streamlit as st
import time
import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
# Importamos la conexión desde tu arquitectura existente
from noetia.sqlite import get_conn
from noetia.config import get_db_path

load_dotenv()

def marcar_como_sincronizada(id_cita):
    """Actualiza el flag en la BD para no repetir la sincronización."""
    conn = get_conn(get_db_path())
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cita SET sincronizacionGoogle = 1 WHERE idCita = ?", (id_cita,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"DEBUG: BD actualizada para ID: {id_cita}")
        else:
            print(f"DEBUG: No se encontró la cita {id_cita}")
    except Exception as e:
        print(f"DEBUG: Error al actualizar BD: {e}")
    finally:
        conn.close()

def sync_event_to_google(event_data):
    """Manda la cita a Google Calendar y maneja el token."""
    try:
        print(f"DEBUG: Sincronizando: {event_data.get('tituloCita')}")
        
        creds = Credentials(
            token=None,
            refresh_token=st.secrets["TOKENS"]["REFRESH_TOKEN"],
            client_id=st.secrets["TOKENS"]["CLIENT_ID"],
            client_secret=st.secrets["TOKENS"]["CLIENT_SECRET"],
            token_uri="https://oauth2.googleapis.com/token"
        )
        
        # Renovación obligatoria
        creds.refresh(Request())
        service = build('calendar', 'v3', credentials=creds)
        
        # --- CORRECCIÓN DE FECHAS ---
        # Google necesita: YYYY-MM-DDTHH:MM:SSZ
        # Si tu BD tiene espacios, cambiamos espacio por 'T' y aseguramos la 'Z'
        def formatear_cita_db(fecha_db):
            # fecha_db viene como '2026-02-21 06:07:15' (visto en image_86615f.png)
            # 1. Reemplazamos el espacio por la 'T'
            # 2. Agregamos la 'Z' al final
            return fecha_db.replace(" ", "T") + "Z"

        # Así quedaría tu payload para Google:
        event = {
            'summary': event_data['tituloCita'],
            'start': {
                'dateTime': formatear_cita_db(event_data['fechaInicio']), # La de tu DB
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': formatear_cita_db(event_data['fechaFin']),    # La de tu DB
                'timeZone': 'UTC',
            },
        }
        
        print(f"DEBUG: Enviando payload: {event}")
        response = service.events().insert(calendarId='primary', body=event).execute()
        
        # Si llegamos aquí, fue éxito
        marcar_como_sincronizada(event_data['idCita'])
        return True
        
    except Exception as e:
        st.error(f"Error en sincronización: {e}")
        return False

def procesar_citas_pendientes():
    """Busca citas en la BD que no tengan el flag de sincronización."""
    conn = get_conn(get_db_path())
    # Usar Row para acceder por nombre de columna
    conn.row_factory = None # Depende de cómo esté tu get_conn, pero mejor asegurar diccionarios
    cursor = conn.cursor()
    
    # Solo traemos las que tengan sincronizacionGoogle = 0 o NULL
    query = "SELECT idCita, tituloCita, fechaInicio, fechaFin FROM cita WHERE sincronizacionGoogle IS NULL OR sincronizacionGoogle = 0"
    cursor.execute(query)
    citas_pendientes = cursor.fetchall()
    conn.close()

    if not citas_pendientes:
        st.toast("Todo sincronizado ✅")
        return

    for cita in citas_pendientes:
        # Mapeamos los datos (ajusta los índices si no usas sqlite3.Row)
        data = {
            'idCita': cita[0],
            'tituloCita': cita[1],
            'fechaInicio': cita[2],
            'fechaFin': cita[3]
        }
        if sync_event_to_google(data):
            st.success(f"Sincronizada: {data['tituloCita']}")
            time.sleep(1) # Un respiro para la API