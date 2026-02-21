import os
from noetia.get_db_connection import get_db_connection

def procesar_texto_y_registrar(texto: str, fuente: str = ".txt") -> dict:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Aquí insertamos '.txt' como el valor para la columna 'fuente'
        query = """
        INSERT INTO entradaCruda (textoOriginal, idPerfil, fuente, fechaCreacion)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        """
        cursor.execute(query, (texto, 1, '.txt'))
        id_registrado = cursor.lastrowid
        conn.commit()
        
    return {
        "idEntradaCruda": id_registrado,
        "textoOriginal": texto,
        "fuente": fuente
    }