import unicodedata

def normalizar_texto(texto):
    # Si el valor no es string, lo convertimos a string primero
    # Esto evita el TypeError incluso si llega un número o un nulo
    texto_str = str(texto) if texto is not None else ""
    return unicodedata.normalize('NFKD', texto_str).encode('ASCII', 'ignore').decode('utf-8').lower()