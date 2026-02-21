from noetia.get_db_connection import get_db_connection
import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def guardar_en_db_clasificado(resultado, id_entrada_cruda):

    folder_sql = "sql"
    db_path = os.path.join(folder_sql, "noetia.db")
    schema_path = BASE_DIR / 'sql' / 'noetia.db'

    if not os.path.exists(folder_sql):
        os.makedirs(folder_sql)

    if not os.path.exists(schema_path):
        print(f"Error: No se encontró {schema_path}")
        return

    try:

        tipo = resultado.get('nombreIntencion', 'nota').lower()
        titulo = resultado.get('texto_estandar')
        id_perfil = 1
        
        print(f"DEBUG: Iniciando inserción. Tipo: {tipo}, Título: {titulo}")

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
            
        # 1. Crear el ítem parseado
        cursor.execute("""
            INSERT INTO itemParseado (idEntradaCruda, contenido, tipoDetectado, titulo) 
            VALUES (?, ?, ?, ?)
        """, (id_entrada_cruda, titulo, tipo, titulo))
        id_parseado_generado = cursor.lastrowid
        print(f"DEBUG: ItemParseado creado con ID: {id_parseado_generado}")
        
        # 2. Clasificación
        # OJO: Verifica si tu columna se llama 'nombreIntención' (con tilde) o 'nombreIntencion'
        # He cambiado a 'nombreIntencion' para evitar errores de codificación
        cursor.execute("""
            INSERT INTO clasificacion (idArea, idTema, idProyecto, idItemParseado, idPerfil, tipoFinal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (resultado.get('idArea'), resultado.get('idTema'), resultado.get('idProyecto'), id_parseado_generado, 1, resultado.get('nombreIntención')))
        
        id_clasificacion = cursor.lastrowid
        print(f"DEBUG: Clasificacion creada con ID: {id_clasificacion}")
        
        # 3. Inserción condicional
        if tipo == 'tarea':
            print("DEBUG: Insertando en TAREA...")
            cursor.execute("""
                INSERT INTO tarea (idClasificacion, idPerfil, idArea, idProyecto, idTema, titulo, fechaVencimiento) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, 1, resultado.get('idArea'), resultado.get('idProyecto'), resultado.get('idTema'), titulo, resultado.get('fecha_detectada')))
            
        elif tipo == 'cita':
            cursor.execute("""
                INSERT INTO cita (idClasificacion, idPerfil, idArea, idProyecto, idTema, tituloCita, fechaFin) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, id_perfil, resultado.get('idArea'), resultado.get('idProyecto'), resultado.get('idTema'), titulo, resultado.get('fecha_detectada')))
            
        elif tipo == 'nota':
            cursor.execute("""
                INSERT INTO nota (idClasificacion, idPerfil, idArea, idProyecto, idTema, contenidoNota) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, id_perfil, resultado.get('idArea'), resultado.get('idProyecto'), resultado.get('idTema'), titulo))
        
        conn.commit()
        print("DEBUG: TODO GUARDADO EXITOSAMENTE")
        return id_parseado_generado
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        # conn.rollback() # Comenta esto mientras pruebas para ver si el error persiste
        raise e # Esto obligará a Python a mostrarte exactamente la línea del error