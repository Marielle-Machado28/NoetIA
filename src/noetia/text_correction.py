import unicodedata

def normalizar_texto(texto):
    # Quitar acentos y normalizar
    return unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8').lower()