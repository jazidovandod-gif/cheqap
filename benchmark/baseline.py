"""Línea de base: palabras compartidas. Si la afirmación se parece bastante al mejor párrafo, la da por respaldada.

Es el "de qué partimos" del pitch. Se equivoca justo en el error sutil.
"""

from consta import buscar
from consta.fuente import Parrafo
from consta.normalizar import normalizar

UMBRAL = 0.35


def etiqueta_baseline(afirmacion: str, parrafos: list[Parrafo]) -> str:
    top = buscar.top_parrafos(afirmacion, parrafos, k=1)
    if not top:
        return "no_respaldada"
    puntaje = buscar.puntuar(normalizar(afirmacion), top[0])
    return "respaldada" if puntaje >= UMBRAL else "no_respaldada"
