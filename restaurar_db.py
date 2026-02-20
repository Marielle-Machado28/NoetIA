import sqlite3
import os

def restaurar_con_datos():
    folder_sql = "sql"
    db_path = os.path.join(folder_sql, "noetia.db")
    schema_path = os.path.join(folder_sql, "schema.sql")

    if not os.path.exists(folder_sql):
        os.makedirs(folder_sql)

    if not os.path.exists(schema_path):
        print(f"Error: No se encontró {schema_path}")
        return

    try:

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        with open(schema_path, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        print("Estructura de tablas creada.")

        cursor.execute("""
            INSERT OR IGNORE INTO perfil (idPerfil, nombrePerfil, zonaHoraria, horaInicioDia, horaFinDia) 
            VALUES (1, 'Marielle Lozano', 'America/Mexico_City', '08:00', '20:00')
        """)

        areas = [
            (1, 'Salud', 'Nutrición, ejercicio', 1, '2026-02-20 07:16:31'),
            (2, 'Finanzas', 'Gestión de dinero y ahorro.', 1, '2026-02-20 07:16:31'),
            (3, 'Trabajo', 'Metas profesionales y crecimiento.', 1, '2026-02-20 07:16:31'),
            (4, 'Familia', 'Relaciones y hogar.', 1, '2026-02-20 07:16:31'),
            (5, 'Espiritualidad', 'Propósito y paz mental.', 1, '2026-02-20 07:16:31'),
            (6, 'Amistad', 'Círculo social y conexión.', 1, '2026-02-20 07:16:31'),
            (7, 'Contribución', 'Ayuda y legado.', 1, '2026-02-20 07:16:31'),
            (8, 'Desarrollo Personal', 'Aprendizaje y curiosidad.', 1, '2026-02-20 07:16:31'),
            (9, 'Entorno Físico', 'Hogar y espacios.', 1, '2026-02-20 07:16:31'),
            (10, 'Romance', 'Relación de pareja.', 1, '2026-02-20 07:16:31'),
            (11, 'Diversión', 'Viajes y risas.', 1, '2026-02-20 07:16:31'),
            (12, 'Ocio', 'Tiempo libre y hobbies.', 1, '2026-02-20 07:16:31')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO area (idArea, nombreArea, descripcion, idPerfil, fechaCreacion) 
                VALUES (?, ?, ?, ?, ?)
            """, areas)

        temas = [
            (1, 1, 1, 'Comida y Dieta', 'Seguir habitos', '2026-02-20 07:16:31'), 
            (2, 1, 2, 'Gastos', 'Control', '2026-02-20 07:16:31'), 
            (3, 1, 3, 'Diplomado', 'Estudio','2026-02-20 07:16:31'), 
            (4, 1, 3, 'Gestión Proyectos', 'Organización', '2026-02-20 07:16:31'), 
            (5, 1, 12, 'Hobbies', 'Descanso', '2026-02-20 07:16:31'), 
            (6, 1, 1, 'Ejercicio', 'Deporte', '2026-02-20 07:16:31'),
            (7, 1, 3, 'Python Backend', 'Código','2026-02-20 07:16:31'),
            (8, 1, 9, 'Casa y Orden', 'Setup', '2026-02-20 07:16:31'),
            (9, 1, 2, 'Ahorro', 'Futuro', '2026-02-20 07:16:31'),
            (10,1,1,'Doctor', 'citas medicas', '2026-02-20 07:16:31'),
            (11, 1, 6, 'Salida con amigos', 'reuniones',  '2026-02-20 07:16:31'),
            (12, 1, 3, 'Entregables', 'Entregar pendientes del trabajo', '2026-02-20 07:16:31'),
            (13, 1, 3, 'Reuniones Laborales', 'Reuniones presenciales o en linea', '2026-02-20 07:16:31'),
            (14, 1, 8, 'Estudio', 'Sesiones de estudio', '2026-02-20 07:16:31'),
            (15, 1, 3, 'Perfil Profesional', 'Mejoas al perfil profesional', '2026-02-20 07:16:31'),
            (16, 1, 10, 'Cita Romantica', 'Salidas en Pareja', '2026-02-20 07:16:31'),
            (17, 1, 11, 'Viajes', 'Planeacion de viajes', '2026-02-20 07:16:31'),
            (18, 1, 11, 'Concierto', 'Eventos importantes', '2026-02-20 07:16:31'),
            (19, 1, 11, 'Salida Social', 'Salidas Casuales', '2026-02-20 07:16:31'),
            (20, 1, 8, 'Entregable', 'Entregas de cursos', '2026-02-20 07:16:31'),
            (21, 1, 8, 'Lectura', 'Lectura de informes o libros', '2026-02-20 07:16:31'),
            (22, 1, 8, 'Organización', 'Organizacion para mi crecimiento', '2026-02-20 07:16:31'),
            (23, 1, 9, 'Tramite', 'Tramites personales o renovacion de membresias', '2026-02-20 07:16:31'),
            (24, 1, 9, 'Mantenimiento', 'Modificaciones o actividades que involucren cuidar tu espacio', '2026-02-20 07:16:31'),
            (25, 1, 9, 'Limpieza', 'Tareas de limpieza del hogar', '2026-02-20 07:16:31'),
            (26, 1, 9, 'Super', 'Compras pendientes', '2026-02-20 07:16:31'),
            (27, 1, 4, 'Responzabilidades', 'Responsabilidades con mi familia', '2026-02-20 07:16:31'),
            (28, 1, 4, 'Salida Familiar', 'Eventos Familiares', '2026-02-20 07:16:31'),
            (29, 1, 2, 'Pagos', 'Pagos pendientes', '2026-02-20 07:16:31'),
            (30, 1, 2, 'Revisión financiera', 'Manejo de mis finanzas', '2026-02-20 07:16:31'),
            (31, 1, 2, 'Ahorro', 'Fondo de ahorro', '2026-02-20 07:16:31'),
            (32, 1, 7, 'Apoyo Social', 'eventos y ayuda a la comunidad', '2026-02-20 07:16:31'),
            (33, 1, 5, 'Religion', 'Tareas o eventos de mi religion', '2026-02-20 07:16:31'),
            (34, 1, 12, 'Sin asignar', 'Actividades que no siempre pertenezcan a un tema', '2026-02-20 07:16:31')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO tema (idTema, idPerfil, idArea, nombreTema, descripcionTema, fechaCreacion
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, temas)

        # 4. Proyectos
        
        proyectos = [
            (1, 1, 1, 1, 'Bajar de Peso', 'bajar mi indice de grasa', 'En Progreso', '2026-05-28 00:00:00'),
            
            (2, 1, 3, 3, 'Presentación walmart', 'Relacionado con área trabajo', 'En Progreso', '2026-02-23 09:30:00'),
            
            (3, 1, 3, 3, 'Módulo 5 Diplomado', 'Proyecto integrador final', 'Pendiente', '2026-02-21 08:00:00'),
            
            (4, 1, 12, 5, 'Gran Fondo de México', 'Entrenamiento ciclismo', 'En Progreso', '2026-11-17 00:00:00')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO proyecto (
                idProyecto, idPerfil, idArea, idTema, nombreProyecto, descripcionProyecto, estadoProyecto, fechaCreacion
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, proyectos)
 
        entradacruda = [
            (1, 1, 'Texto', 'Cita nutriologo', '2026-03-27 00:00:00'),
            (2, 1, 'Texto', 'Gasolina', '2027-05-05 00:00:00'),
            (3, 1, 'Voz', 'Presentación delta sharing', '2027-09-22 00:00:00'),
            (4, 1, 'Texto', 'Pagar tarjeta', '2026-03-07 00:00:00'), # Agregué el 0 al día
            (5, 1, 'Voz', 'entrenar 5 kilometros en bici', '2026-02-20 00:00:00')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO entradaCruda (
                idEntradaCruda, idPerfil, fuente, textoOriginal, fechaCreacion
            ) VALUES (?, ?, ?, ?, ?)
        """, entradacruda)

        
        cursor.execute("""
            INSERT OR IGNORE INTO itemParseado (
                idItemParseado, idEntradaCruda, tipoDetectado, titulo, contenido, fechaDetectada, fechaCreacion
            ) VALUES 
                (1, 1, 'cita', 'Cita nutriologo', 'Asistir a mi cita con el nutriólogo', '2026-03-27 17:30:00', '2026-02-20 07:16:31'), 
                (2, 2, 'nota', 'Gasolina', 'Ponerle gasolina a mi coche cuando pueda', '2027-05-05 00:00:00', '2026-02-20 07:16:31'), 
                (3, 3, 'tarea', 'Presentación delta sharing', 'Terminar la presentación', '2027-09-22 00:00:00', '2026-02-20 07:16:31'),
                (4, 4, 'tarea', 'Pagar tarjeta', 'Fecha de pago 07 de marzo', '2026-03-07 00:00:00', '2026-02-20 07:16:31'),
                (5, 5, 'tarea', 'Entrenar 5 kilómetros en bici', 'Regresando al entrenamiento', '2026-02-20 00:00:00', '2026-02-20 07:16:31')
        """)
        
        cursor.execute("""
            INSERT OR IGNORE INTO clasificacion (idClasificacion, idItemParseado, idPerfil, idTema, tipoFinal, idArea, idProyecto, versionModelo) 
            VALUES 
                (1, 1, 1, 1, 'cita', 1, 1, 'v1'), 
                (2, 2, 1, 3, 'nota', 3, NULL, 'v1'), 
                (3, 3, 1, 7, 'tarea', 3, 2, 'v1'),
                (4, 4, 1, 3, 'tarea', 2, null, 'v1'),
                (5, 5, 1, 5, 'tarea', 12, 1, 'v1')
        """)

        tareas = [
            # 1. Presentación (Clasificación 3, Area 3, Proyecto 2, Tema 7)
            (1, 3, 1, 3, 2, 7, 'Presentación delta sharing', '2027-09-22', 'Pendiente', 1, 1, 1, 60),
            
            # 2. Pagar Tarjeta (Clasificación 4, Area 2, Proyecto NULL, Tema 3)
            (2, 4, 1, 2, None, 3, 'Pagar Tarjeta de Crédito', '2026-03-07', 'Pendiente', 0, 0, 4, 10),
            
            # 3. Entrenar (Clasificación 5, Area 12, Proyecto 1, Tema 5)
            # Cambié None por 1 para que coincida con la Clasificación 5
            (3, 5, 1, 12, 1, 5, 'Entrenar 5 km bici', '2026-02-20', 'Pendiente', 1, 0, 2, 120)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO tarea (
                idTarea, idClasificacion, idPerfil, idArea, idProyecto, idTema, 
                titulo, fechaVencimiento, estadoTarea, esImportante, esUrgente, 
                cuadranteEisenhower, minutosEstimados
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, tareas)

        # Citas
        citas = [
            (1, 1, 1, 1, 1, 1, 'Cita nutriologo', 'Asistir a consulta', '2026-03-27 17:30:00', '2026-03-27 18:30:00', 'Consultorio', 'g_id_1', 0)
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO cita (
                idCita, idClasificacion, idPerfil, idArea, idProyecto, idTema, 
                tituloCita, descripcionCita, fechaInicio, fechaFin, ubicacion, 
                eventoGoogleId, sincronizacionGoogle
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, citas)

        # Notas
        notas = [
            (1, 2, 1, 3, None, 3, 'Ponerle gasolina al coche')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO nota (
                idNota, idClasificacion, idPerfil, idArea, idProyecto, idTema, contenidoNota
            ) VALUES (?,?,?,?,?,?,?)
        """, notas)

        conn.commit()
        print("¡Base de datos restaurada con éxito!")

    except sqlite3.Error as e:
        print(f"Error de SQLite: {e}")
    finally:
        if conn: conn.close()

if __name__ == "__main__":
    restaurar_con_datos()