from __future__ import annotations

import sqlite3
import joblib
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict

# Importaciones de tus otros scripts
from noetia.llm_normalizer import estandarizar_texto_con_llm
from noetia.text_cleaning import limpiar_texto
from noetia.config import get_db_path

BASE_DIR = Path(__file__).resolve().parent 
MODEL_DIR = BASE_DIR / "models"

@dataclass
class ModelBundle:
    area: Any
    tema: Any
    intencion: Any
    prioridad: Any

def cargar_modelos() -> ModelBundle:
    """Carga los modelos entrenados desde la carpeta models."""
    # Intentamos encontrar la ruta de los modelos
    try:
        bundle = ModelBundle(
            area=joblib.load(MODEL_DIR / "modelo_area.joblib"),
            tema=joblib.load(MODEL_DIR / "modelo_tema.joblib"),
            intencion=joblib.load(MODEL_DIR / "modelo_intencion.joblib"),
            prioridad=joblib.load(MODEL_DIR / "modelo_prioridad.joblib"),
        )
        print("Modelos cargados exitosamente.")
        return bundle

    except Exception as e:
        print(f"Error al cargar modelos: {e}")
        raise e

def guardar_en_db(payload: Dict[str, Any], id_perfil: int = 1):
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON;")
    cur = conn.cursor()

    try:
        # 1. Asegurar Áreas, Temas y Proyectos (Si es nuevo, inserta)
        cur.execute("INSERT OR IGNORE INTO area (idArea, nombreArea, idPerfil) VALUES (?, ?, ?)", 
                    (payload['id_area'], payload['nombre_area'], id_perfil))
        
        cur.execute("INSERT OR IGNORE INTO tema (idTema, idArea, idPerfil, nombreTema) VALUES (?, ?, ?, ?)", 
                    (payload['id_tema'], payload['id_area'], id_perfil, payload['nombre_tema']))
        
        cur.execute("INSERT OR IGNORE INTO proyecto (idProyecto, idPerfil, idArea, idTema, nombreProyecto) VALUES (?, ?, ?, ?, ?)", 
                    (1, id_perfil, payload['id_area'], payload['id_tema'], "General"))

        # 2. Entrada Cruda
        cur.execute("INSERT INTO entradaCruda (idPerfil, fuente, contenidoCrudo) VALUES (?, ?, ?)", 
                    (id_perfil, payload['fuente'], payload['texto_original']))
        id_entrada = cur.lastrowid

        # 3. Item Parseado (Normalizado por OpenAI)
        cur.execute("""INSERT INTO itemParseado (idEntradaCruda, tipoDetectado, titulo, contenido, fechaDetectada)
                       VALUES (?, ?, ?, ?, ?)""", 
                    (id_entrada, payload['intencion'], payload['texto_estandar'], payload['texto_original'], payload['fecha']))
        id_item = cur.lastrowid

        # 4. Clasificación (Relación con Metodología y Priorización)
        cur.execute("""INSERT INTO clasificacion (idItemParseado, idPerfil, idArea, idTema, idProyecto, tipoFinal)
                       VALUES (?, ?, ?, ?, ?, ?)""", 
                    (id_item, id_perfil, payload['id_area'], payload['id_tema'], 1, payload['intencion']))
        id_clasif = cur.lastrowid

        # 5. Asignación Final (Tarea, Cita o Nota)
        if payload['intencion'] == "tarea":
            cur.execute("""INSERT INTO tarea (idClasificacion, idPerfil, tituloTarea, idArea, idTema, idProyecto, 
                                            estadoTarea, esImportante, esUrgente, fechaVencimiento)
                           VALUES (?, ?, ?, ?, ?, ?, 'pendiente', ?, ?, ?)""", 
                        (id_clasif, id_perfil, payload['texto_estandar'], payload['id_area'], 
                         payload['id_tema'], 1, payload['es_importante'], payload['es_urgente'], payload['fecha']))
        
        elif payload['intencion'] == "cita":
            cur.execute("INSERT INTO cita (idClasificacion, idPerfil, tituloCita, fechaInicio, idProyecto) VALUES (?, ?, ?, ?, ?)", 
                        (id_clasif, id_perfil, payload['texto_estandar'], payload['fecha'], 1))
        
        elif payload['intencion'] == "nota":
            cur.execute("INSERT INTO nota (idClasificacion, idPerfil, contenidoNota, idProyecto) VALUES (?, ?, ?, ?)", 
                        (id_clasif, id_perfil, payload['texto_original'], 1))

        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error en persistencia: {e}")
        return False
    finally:
        conn.close()

def procesar_entrada_maestra(texto_crudo: str, fuente: str, bundle: ModelBundle) -> bool:
    # ... (parte de OpenAI y limpieza igual) ...
    res_llm = estandarizar_texto_con_llm(limpiar_texto(texto_crudo))
    texto_estandar = res_llm.get("texto_estandar", texto_crudo)
    
    # 1. Inferencia: El modelo devuelve texto (ej: 'Crecimiento Personal1')
    pred_area_raw = str(bundle.area.predict([texto_estandar])[0])
    pred_tema_raw = str(bundle.tema.predict([texto_estandar])[0])

    # 2. DICCIONARIO DE TRADUCCIÓN (Ajusta los nombres según tu modelo)
    # Este mapa convierte el TEXTO del modelo al ID de la DB
    mapa_areas = {
        'Crecimiento Personal1': 1,
        'Salud': 2,
        'Finanzas': 7,
        'Trabajo': 6,
        # Agrega aquí todos los que tu modelo prediga
    }

    # Intentamos convertir a ID, si no está en el mapa, usamos 12 (General)
    id_area_final = mapa_areas.get(pred_area_raw, 12) 
    id_tema_final = id_area_final # Por simplicidad para el demo

    # 3. Mapeo de Prioridad e Intención
    pred_intencion = str(bundle.intencion.predict([texto_estandar])[0]).lower()
    pred_prio = bundle.prioridad.predict([texto_estandar])[0]

    # ... (Resto del payload usando los IDs ya limpios) ...
    payload = {
        "texto_original": texto_crudo,
        "texto_estandar": texto_estandar,
        "fuente": fuente,
        "intencion": pred_intencion,
        "id_area": id_area_final,        # <--- ¡Ya es un entero!
        "nombre_area": pred_area_raw,    # <--- Guardamos el nombre para que se vea bien
        "id_tema": id_tema_final,
        "nombre_tema": pred_tema_raw,
        "fecha": res_llm.get("fecha"),
        "es_urgente": 1 if pred_prio in [1, 2] else 0,
        "es_importante": 1 if pred_prio in [1, 3] else 0
    }

    return guardar_en_db(payload)