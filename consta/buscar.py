"""Afirmación -> top-k párrafos del PDF por palabras compartidas, ponderando números y plazos.

Responsable: B. Listo a las 12:00.

Sin embeddings. Tiene que funcionar sin red.
"""

import re
from collections import Counter

from .fuente import Parrafo
from .normalizar import normalizar

_VACIAS = set(
    "de la el los las y o a en que por para con un una del al se su sus es son como mas o u e lo le les".split()
)
_NUMERO = re.compile(r"\d+")


def _tokens(texto_norm: str) -> list[str]:
    return [t for t in re.findall(r"[a-z0-9ñ]+", texto_norm) if t not in _VACIAS]


def puntuar(afirmacion_norm: str, parrafo: Parrafo) -> float:
    """Palabras compartidas; los números y las palabras clave de obligación pesan triple."""
    a = Counter(_tokens(afirmacion_norm))
    p = Counter(_tokens(parrafo.texto_norm))
    puntaje = 0.0
    for tok, n in a.items():
        if tok in p:
            peso = 3.0 if (_NUMERO.fullmatch(tok) or tok in {"debe", "puede", "dias", "plazo", "articulo"}) else 1.0
            puntaje += peso * min(n, p[tok])
    return puntaje / (1 + len(a))


def top_parrafos(afirmacion: str, parrafos: list[Parrafo], k: int = 3) -> list[Parrafo]:
    norm = normalizar(afirmacion)
    ordenados = sorted(parrafos, key=lambda p: puntuar(norm, p), reverse=True)
    return ordenados[:k]
