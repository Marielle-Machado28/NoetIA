from noetia.get_db_connection import get_db_connection

def guardar_en_db_clasificado(resultado, id_entrada_cruda):
    """
    Orquestador que asegura la inserción jerárquica:
    entradaCruda -> itemParseado -> (tarea/cita/nota) -> clasificacion
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Crear el ítem parseado
            cursor.execute("""
                INSERT INTO itemParseado (idEntradaCruda, idPerfil, contenido) 
                VALUES (?, ?, ?)
            """, (id_entrada_cruda, 1, None))
            id_item = cursor.lastrowid
            
            # 2. Inserción condicional según tipo
            tipo = resultado.get('intencion', 'nota')
            if tipo == 'tarea':
                cursor.execute("INSERT INTO tarea (idItem, prioridad, fechaVencimiento) VALUES (?, ?, ?)",
                               (id_item, resultado.get('prioridad'), resultado.get('fecha_detectada')))
            elif tipo == 'cita':
                cursor.execute("INSERT INTO cita (idItem, fechaCita) VALUES (?, ?)",
                               (id_item, resultado.get('fecha_detectada')))
            
            # 3. Clasificación final
            cursor.execute("""
                INSERT INTO clasificacion (idItem, idArea, idTema, idProyecto)
                VALUES (?, ?, ?, ?)
            """, (id_item, resultado.get('idArea'), resultado.get('idTema'), resultado.get('idProyecto')))
            
            conn.commit()
            return id_item
            
    except Exception as e:
        print(f"❌ Error crítico en arquitectura: {e}")
        return None