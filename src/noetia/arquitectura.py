import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

def guardar_en_db_clasificado(resultado, id_entrada_cruda):
    folder_sql = "sql"
    db_path = os.path.join(BASE_DIR, folder_sql, "noetia.db")

    if not os.path.exists(db_path):
        print(f"Error: No se encontró {db_path}")
        return

    conn = None
    try:
        # Abrimos la conexión una sola vez con timeout
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        tipo = resultado.get('nombreIntención', '').lower()
        titulo = resultado.get('texto_estandar')
        
        # 1. Crear el ítem parseado
        cursor.execute("""
            INSERT INTO itemParseado (idEntradaCruda, contenido, tipoDetectado, titulo) 
            VALUES (?, ?, ?, ?)
        """, (id_entrada_cruda, titulo, tipo, titulo))
        id_parseado_generado = cursor.lastrowid
        
        # 2. Clasificación
        cursor.execute("""
            INSERT INTO clasificacion (idArea, idTema, idProyecto, idItemParseado, idPerfil, tipoFinal)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (resultado.get('idArea'), resultado.get('idTema'), resultado.get('idProyecto'), id_parseado_generado, 1, tipo))
        
        id_clasificacion = cursor.lastrowid
        
        # 3. Inserción condicional
        if tipo == 'tarea':
            cursor.execute("""
                INSERT INTO tarea (idClasificacion, idPerfil, idArea, idProyecto, idTema, titulo, fechaVencimiento, estadoTarea, esImportante, esUrgente, cuadranteEisenhower) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, 1, resultado.get('idArea'), resultado.get('idProyecto'), 
                  resultado.get('idTema'), titulo, resultado.get('fecha_detectada'), 'pendiente', resultado.get('es_importante'), resultado.get('es_urgente'), resultado.get('prioridad')))
            
        elif tipo == 'cita':
            cursor.execute("""
                INSERT INTO cita (idClasificacion, idPerfil, idArea, idProyecto, idTema, tituloCita, fechaFin, fechaInicio) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, 1, resultado.get('idArea'), resultado.get('idProyecto'), 
                  resultado.get('idTema'), titulo, resultado.get('fecha_detectada'), resultado.get('fecha_detectada')))
            
        elif tipo == 'nota':
            cursor.execute("""
                INSERT INTO nota (idClasificacion, idPerfil, idArea, idProyecto, idTema, contenidoNota) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (id_clasificacion, 1, resultado.get('idArea'), resultado.get('idProyecto'), 
                  resultado.get('idTema'), titulo))
        
        conn.commit()
        print("DEBUG: Todo guardado exitosamente.")
        return id_parseado_generado

    except Exception as e:
        if conn: conn.rollback()
        print(f"❌ ERROR CRÍTICO: {e}")
        raise e
    finally:
        if conn:
            conn.close()