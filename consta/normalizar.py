"""Normalización compartida. Aquí se define qué significa "la cita existe textual en el PDF"."""

import re
import unicodedata


def normalizar(texto: str) -> str:
    """Minúsculas, sin tildes, sin espacios dobles, sin comillas tipográficas.

    Se usa tanto sobre el PDF como sobre la cita devuelta por el juez,
    así la comparación de subcadena no falla por una tilde o un salto de línea.
    """
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    # "N°" (grado) y "Nº" (ordinal) se escriben indistintamente en los PDF oficiales.
    texto = texto.replace("°", "o").replace("º", "o")
    texto = texto.replace("“", '"').replace("”", '"').replace("’", "'")
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def cita_existe(cita: str, texto_fuente_norm: str, minimo_palabras: int = 4) -> bool:
    """True si la cita (ya normalizada o no) aparece como subcadena de la fuente normalizada.

    Citas de menos de `minimo_palabras` palabras no cuentan: son demasiado fáciles de acertar por azar.
    """
    cita_norm = normalizar(cita)
    if len(cita_norm.split()) < minimo_palabras:
        return False
    return cita_norm in texto_fuente_norm
