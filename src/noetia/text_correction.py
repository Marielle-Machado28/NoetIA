import unicodedata

def normalizar_texto(texto):
    # Forzar la conversión a string y manejar nulos
    if texto is None:
        return ""
    texto_str = str(texto)
    return unicodedata.normalize('NFKD', texto_str).encode('ASCII', 'ignore').decode('utf-8').lower()