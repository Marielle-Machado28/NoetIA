import sqlite3
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_PATH")

if not DB_PATH:
    raise ValueError("DB_PATH no está definido")

DB_PATH = Path(DB_PATH)


def data_dummy_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    # PERFIL DEFAULT
    cur.execute("""
        INSERT OR IGNORE INTO perfil (
            idPerfil, nombrePerfil, zonaHoraria, horaInicioDia, horaFinDia
        ) VALUES (
            1, 'default', 'America/Mexico_City', '08:00', '18:00'
        );
    """)

    # AREAS DE VIDA
    areas = [
        (1, "Trabajo"),
        (2, "Estudio"),
        (3, "Salud"),
        (4, "Finanzas"),
        (5, "Amor"),
        (6, "Familia"),
        (7, "Amigos"),
        (8, "Crecimiento Personal"),
    ]

    for id_area, nombre in areas:
        cur.execute("""
            INSERT OR IGNORE INTO area (
                idArea, nombreArea, idPerfil
            ) VALUES (?, ?, 1);
        """, (id_area, nombre))

    # TEMAS (por área)
    temas = [
        # Trabajo
        (1, 1, "Trabajo"),
        (2, 1, "Proyectos IT"),

        # Estudio
        (3, 2, "Diplomado Ciencia de Datos"),
        (4, 2, "Aprendizaje Técnico"),

        # Salud
        (5, 3, "Rutina Física"),
        (6, 3, "Salud Mental"),

        # Finanzas
        (7, 4, "Presupuesto"),
        (8, 4, "Ahorro"),

        # Amor
        (9, 5, "Pareja"),

        # Crecimiento
        (10, 8, "Hábitos"),
    ]

    for id_tema, id_area, nombre in temas:
        cur.execute("""
            INSERT OR IGNORE INTO tema (
                idTema, idPerfil, idArea, nombreTema
            ) VALUES (?, 1, ?, ?);
        """, (id_tema, id_area, nombre))

    # PROYECTOS
    proyectos = [
        (1, 1, 1, "NoetIA", "Proyecto académico del diplomado"),
        (2, 2, 3, "Diplomado Ciencia de Datos", "Clases, prácticas y proyecto final"),
    ]

    for id_proyecto, id_area, id_tema, nombre, desc in proyectos:
        cur.execute("""
            INSERT OR IGNORE INTO proyecto (
                idProyecto, idPerfil, idArea, idTema,
                nombreProyecto, descripcionProyecto, estadoProyecto
            ) VALUES (?, 1, ?, ?, ?, ?, 'activo');
        """, (id_proyecto, id_area, id_tema, nombre, desc))

    # ESTIMACIONES DE TIEMPO
    estimaciones = [
        ("email", 10),
        ("reunion", 30),
        ("estudio", 60),
        ("ejercicio", 45),
        ("limpieza", 20),
        ("tramite", 25),
    ]

    for etiqueta, minutos in estimaciones:
        cur.execute("""
            INSERT OR IGNORE INTO estimacionTiempo (
                idPerfil, tipoEtiqueta, minutosPorDefecto
            ) VALUES (1, ?, ?);
        """, (etiqueta, minutos))

    # PIPELINE + ENTIDADES FINALES (tareas / notas / citas demo)
    #
    # Nota: usamos IDs fijos con INSERT OR IGNORE para que el script
    #       sea idempotente (no duplica datos si se vuelve a correr).

    # Entradas crudas
    entradas = [
        (1, 1, "manual", "Terminar funcionalidad de NoetIA", None),
        (2, 1, "manual", "Apuntes de la clase de Ciencia de Datos", None),
        (3, 1, "manual", "Cita con tutor del diplomado", "2026-02-20 18:00:00"),
    ]
    for id_entrada, id_perfil, fuente, contenido, fecha_creacion in entradas:
        cur.execute(
            """
            INSERT OR IGNORE INTO entradaCruda (
                idEntradaCruda, idPerfil, fuente, contenidoCrudo, fechaCreacion
            ) VALUES (?, ?, ?, ?, COALESCE(?, CURRENT_TIMESTAMP));
            """,
            (id_entrada, id_perfil, fuente, contenido, fecha_creacion),
        )

    # Items parseados
    items = [
        (1, 1, "tarea", "Implementar vistas Streamlit", "Terminar vistas de tareas, calendario y proyectos", None),
        (2, 2, "nota", "Apuntes módulo 3", "Resumen de conceptos clave de ML supervisado", None),
        (3, 3, "cita", "Reunión con tutor", "Revisar avance del proyecto NoetIA", "2026-02-20 18:00:00"),
    ]
    for (
        id_item,
        id_entrada,
        tipo,
        titulo,
        contenido,
        fecha_detectada,
    ) in items:
        cur.execute(
            """
            INSERT OR IGNORE INTO itemParseado (
                idItemParseado, idEntradaCruda, tipoDetectado, titulo, contenido, fechaDetectada
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            (id_item, id_entrada, tipo, titulo, contenido, fecha_detectada),
        )

    # Clasificación (ligar a área/tema/proyecto existentes)
    clasificaciones = [
        # tarea ligada al proyecto 1 (NoetIA)
        (1, 1, 1, 1, "tarea", 1, 1),
        # nota ligada al proyecto 2 (Diplomado Ciencia de Datos)
        (2, 2, 1, 3, "nota", 2, 2),
        # cita ligada al proyecto 1
        (3, 3, 1, 1, "cita", 1, 1),
    ]
    for (
        id_clasif,
        id_item,
        id_perfil,
        id_tema,
        tipo_final,
        id_area,
        id_proyecto,
    ) in clasificaciones:
        cur.execute(
            """
            INSERT OR IGNORE INTO clasificacion (
                idClasificacion, idItemParseado, idPerfil, idTema,
                tipoFinal, idArea, idProyecto
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (id_clasif, id_item, id_perfil, id_tema, tipo_final, id_area, id_proyecto),
        )

    # Tareas demo
    tareas = [
        (
            1,
            1,
            1,
            1,
            1,
            1,
            "2026-02-25 23:59:59",
            "pendiente",
            1,
            1,
            1,
            120,
        ),
    ]
    for (
        id_tarea,
        id_clasif,
        id_perfil,
        id_area,
        id_proyecto,
        id_tema,
        fecha_venc,
        estado,
        es_imp,
        es_urg,
        cuadrante,
        minutos,
    ) in tareas:
        cur.execute(
            """
            INSERT OR IGNORE INTO tarea (
                idTarea, idClasificacion, idPerfil, idArea, idProyecto, idTema,
                fechaVencimiento, estadoTarea, esImportante, esUrgente,
                cuadranteEisenhower, minutosEstimados
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                id_tarea,
                id_clasif,
                id_perfil,
                id_area,
                id_proyecto,
                id_tema,
                fecha_venc,
                estado,
                es_imp,
                es_urg,
                cuadrante,
                minutos,
            ),
        )

    # Notas demo
    notas = [
        (
            1,
            2,
            1,
            2,
            2,
            3,
            "Recordar repasar notebooks de ejemplo antes de la siguiente sesión.",
        ),
    ]
    for (
        id_nota,
        id_clasif,
        id_perfil,
        id_area,
        id_proyecto,
        id_tema,
        contenido,
    ) in notas:
        cur.execute(
            """
            INSERT OR IGNORE INTO nota (
                idNota, idClasificacion, idPerfil, idArea, idProyecto, idTema, contenidoNota
            ) VALUES (?, ?, ?, ?, ?, ?, ?);
            """,
            (
                id_nota,
                id_clasif,
                id_perfil,
                id_area,
                id_proyecto,
                id_tema,
                contenido,
            ),
        )

    # Citas demo
    citas = [
        (
            1,
            3,
            1,
            1,
            1,
            1,
            "Reunión con tutor",
            "Revisar avance del proyecto NoetIA",
            "2026-02-20 18:00:00",
            "2026-02-20 19:00:00",
            "En línea",
            None,
            0,
        ),
    ]
    for (
        id_cita,
        id_clasif,
        id_perfil,
        id_area,
        id_proyecto,
        id_tema,
        titulo,
        descripcion,
        f_inicio,
        f_fin,
        ubicacion,
        evento_google_id,
        sync_google,
    ) in citas:
        cur.execute(
            """
            INSERT OR IGNORE INTO cita (
                idCita, idClasificacion, idPerfil, idArea, idProyecto, idTema,
                tituloCita, descripcionCita, fechaInicio, fechaFin,
                ubicacion, eventoGoogleId, sincronizacionGoogle
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                id_cita,
                id_clasif,
                id_perfil,
                id_area,
                id_proyecto,
                id_tema,
                titulo,
                descripcion,
                f_inicio,
                f_fin,
                ubicacion,
                evento_google_id,
                sync_google,
            ),
        )

    conn.commit()
    conn.close()

    print("Base de datos lista con valores dummy.")


if __name__ == "__main__":
    data_dummy_db()