"""Revisor de reglas para afirmaciones en aymara. Determinista, sin modelo.

Dos reglas, derivadas y medidas en las 713 filas aym del split dev de AmericasNLI que NO están
en nuestro lote de prueba de 30 (data/benchmark/americasnli_aym_resto.jsonl). Ver scripts/medir_regla_ay.py
y scripts/medir_factores_ay.py. Se midieron ANTES de aplicarlas al lote de 30.

1. Negación. Si la afirmación trae un marcador de negación aymara (jani, janiw, janiwa, janirakiw, ...)
   y la fuente no, se marca "contradicha". En las 713: dispara en 84 de 238 contradicciones (35 %),
   5 de 238 implicaciones (2 %) y 13 de 237 neutras (5 %): precisión 82 %.

2. Solapamiento de raíces. El aymara es aglutinante: la misma raíz cambia de sufijos. Se comparan los
   primeros 5 caracteres de cada palabra. Si casi todas las raíces de la afirmación están en la fuente
   (umbral UMBRAL_RESPALDO) y no hay negación desajustada, se marca "respaldada". El umbral y su
   precisión están en el script; si la precisión medida fuera baja, la regla no se activa (UMBRAL = None).

Límite conocido: una doble negación o una negación que ya está en la premisa no se maneja.
"""

import re

from .fuente import Parrafo

_NEGACION = re.compile(r"\bjan[iï]\w*", re.IGNORECASE)
_PALABRA = re.compile(r"[a-záéíóúüñï']+", re.IGNORECASE)
LARGO_RAIZ = 5
# Medido en las 713 filas aparte (scripts/medir_factores_ay.py): con >= 0.6 disparan 71 filas,
# 50 implicaciones (70 %), 14 neutras, 7 contradicciones. Cobertura: 50 de 238 implicaciones (21 %).
UMBRAL_RESPALDO: float | None = 0.6


def tiene_negacion(texto: str) -> bool:
    return bool(_NEGACION.search(texto))


def raices(texto: str) -> set[str]:
    return {w.lower()[:LARGO_RAIZ] for w in _PALABRA.findall(texto) if len(w) >= 3}


def solapamiento(afirmacion: str, fuente: str) -> float:
    a, f = raices(afirmacion), raices(fuente)
    return len(a & f) / len(a) if a else 0.0


def revisar(afirmacion: str, candidatos: list[Parrafo]) -> tuple[str | None, str | None, str | None]:
    m = _NEGACION.search(afirmacion)
    fuente_tiene_neg = any(tiene_negacion(p.texto) for p in candidatos)
    if m and not fuente_tiene_neg:
        return "contradicha", m.group(0), "negación en aymara que la fuente no tiene"
    if UMBRAL_RESPALDO is not None and bool(m) == fuente_tiene_neg and len(raices(afirmacion)) >= 3:
        mejor = max((solapamiento(afirmacion, p.texto) for p in candidatos), default=0.0)
        if mejor >= UMBRAL_RESPALDO:
            return "respaldada", None, f"{mejor:.0%} de las raíces de la afirmación están en la fuente"
    return None, None, None
