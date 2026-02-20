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

        
        # Insertar Perfil
        cursor.execute("""
            INSERT OR IGNORE INTO perfil (idPerfil, nombrePerfil, zonaHoraria, horaInicioDia, horaFinDia) 
            VALUES (1, 'Marielle Lozano', 'America/Mexico_City', '08:00', '20:00')
        """)

        # Insertar Áreas 
        areas = [
            (1, 'Salud', 'Nutrición, ejercicio, sueño, salud mental y vitalidad.', 1),
            (2, 'Finanzas', 'Gestión de dinero, ahorro, inversiones y libertad financiera.', 1),
            (3, 'Carrera', 'Metas profesionales, proyectos y crecimiento laboral.', 1),
            (4, 'Familia', 'Relaciones familiares, hogar y tiempo de calidad con seres queridos.', 1),
            (5, 'Espiritualidad', 'Propósito de vida, meditación, paz mental y conexión.', 1),
            (6, 'Ocio', 'Tiempo libre, hobbies y actividades que recargan tu energía.', 1),
            (7, 'Contribución', 'Ayuda a los demás, voluntariado y dejar un legado.', 1),
            (8, 'Desarrollo Personal', 'Aprendizaje, lectura, nuevas habilidades y curiosidad.', 1),
            (9, 'Entorno Físico', 'Organización de tu espacio, hogar y lugares que habitas.', 1),
            (10, 'Romance', 'Relación de pareja, intimidad y comunicación amorosa.', 1),
            (11, 'Amistad', 'Círculo social, lealtad y conexión con amigos.', 1),
            (12, 'Diversión', 'Aventuras, viajes, risas y disfrute de la vida.', 1)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO area (idArea, nombreArea, descripcion, idPerfil) 
            VALUES (?, ?, ?, ?)
        """, areas)

        # Insertar Temas
        temas = [
            # SALUD (1)
            (1, 1, 1, 'Comida y Dieta', 'Lo que como y bebo'),
            (2, 1, 1, 'Ejercicio', 'Gimnasio, caminar o deporte'),
            
            # FINANZAS (2)
            (3, 1, 2, 'Gastos', 'Control de lo que sale'),
            (4, 1, 2, 'Ahorro', 'Dinero para el futuro'),

            # TRABAJO (3)
            (5, 1, 3, 'Diplomado IA', 'Todo sobre el diplomado actual'),
            (6, 1, 3, 'Python Backend', 'Mejora de scripts de NoetIA'),
            (7, 1, 3, 'Gestión Proyectos', 'Organización de entregables'),

            # FAMILIA (4)
            (8, 1, 4, 'Hijos/Padres', 'Tiempo con la familia'),

            # ESPIRITUALIDAD (5)
            (9, 1, 5, 'Meditación', 'Paz mental y silencio'),

            # AMISTAD (6)
            (10, 1, 6, 'Salidas', 'Ver a mis amigos'),

            # CONTRIBUCIÓN (7)
            (11, 1, 7, 'Ayuda', 'Hacer algo por otros'),

            # DESARROLLO PERSONAL (8)
            (12, 1, 8, 'Lectura', 'Libros nuevos'),
            (13, 1, 8, 'Cursos', 'Aprender algo nuevo'),

            # ENTORNO FÍSICO (9)
            (14, 1, 9, 'Casa y Orden', 'Limpieza y setup'),

            # ROMANCE (10)
            (15, 1, 10, 'Pareja', 'Citas y tiempo juntos'),

            # DIVERSIÓN (11)
            (16, 1, 11, 'Viajes', 'Paseos y vacaciones'),

            # OCIO (12)
            (17, 1, 12, 'Hobbies', 'Juegos y descanso')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO tema (idTema, idPerfil, idArea, nombreTema, descripcionTema) 
            VALUES (?, ?, ?, ?, ?)
        """, temas)

        
        proyectos = [
            
            # 1. Proyecto: NoetIA V1 (Trabajo - Gestión Proyectos)
            (1, 1, 3, 7, 'NoetIA V1', 'Sistema de gestión inteligente con IA', 'En Progreso'),
            
            # 2. Proyecto: Diplomado IA (Trabajo - Diplomado IA)
            (2, 1, 3, 5, 'Diplomado IA - General', 'Relacionado con área trabajo y organización de entregables', 'En Progreso'),
            
            # 3. Proyecto: Módulo 5 (Trabajo - Diplomado IA)
            (3, 1, 3, 5, 'Módulo 5 Diplomado', 'Desarrollo del proyecto integrador final del diplomado', 'Pendiente'),
            
            # 4. Proyecto: Gran Fondo de México (Ocio - Hobbies)
            (4, 1, 12, 17, 'Gran Fondo de México', 'Entrenamiento y participación en el evento de ciclismo', 'En Progreso')
        ]

        cursor.executemany("""
            INSERT OR IGNORE INTO proyecto (idProyecto, idPerfil, idArea, idTema, nombreProyecto, descripcionProyecto, estadoProyecto)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, proyectos)

        conn.commit()
        print("Datos dummy (Áreas, Temas y Proyectos) insertados correctamente.")

    except sqlite3.Error as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    restaurar_con_datos()