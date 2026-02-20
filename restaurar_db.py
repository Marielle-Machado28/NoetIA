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

        # 1. Crear estructura desde el archivo SQL
        with open(schema_path, 'r', encoding='utf-8') as f:
            cursor.executescript(f.read())
        print("✅ Estructura de tablas creada.")

        # 2. Insertar Datos Dummy
        # Insertar Perfil
        cursor.execute("""
            INSERT OR IGNORE INTO perfil (idPerfil, nombrePerfil, zonaHoraria, horaInicioDia, horaFinDia) 
            VALUES (1, 'Marielle NoetIA', 'America/Mexico_City', '08:00', '20:00')
        """)

        # Insertar Áreas (Ejemplos típicos de NoetIA)
        areas = [
            (1, 'Personal', 'Cosas de la vida diaria', 1),
            (2, 'Trabajo', 'Proyectos y tareas laborales', 1),
            (3, 'Desarrollo', 'Aprendizaje y programación', 1)
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO area (idArea, nombreArea, descripcion, idPerfil) 
            VALUES (?, ?, ?, ?)
        """, areas)

        # Insertar Temas
        temas = [
            (1, 1, 3, 'Diplomado IA', 'Todo sobre el diplomado actual'),
            (2, 1, 3, 'Python Backend', 'Mejora de scripts de NoetIA'),
            (3, 1, 2, 'Gestión Proyectos', 'Organización de entregables')
        ]
        cursor.executemany("""
            INSERT OR IGNORE INTO tema (idTema, idPerfil, idArea, nombreTema, descripcionTema) 
            VALUES (?, ?, ?, ?, ?)
        """, temas)

        # Insertar un Proyecto de prueba para que la página de Proyectos no esté vacía
        cursor.execute("""
            INSERT OR IGNORE INTO proyecto (idProyecto, idPerfil, idArea, idTema, nombreProyecto, descripcionProyecto, estadoProyecto)
            VALUES (1, 1, 3, 1, 'NoetIA V1', 'Sistema de gestión inteligente', 'En Progreso')
        """)

        conn.commit()
        print("✅ Datos dummy (Áreas, Temas y Proyectos) insertados correctamente.")

    except sqlite3.Error as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    restaurar_con_datos()