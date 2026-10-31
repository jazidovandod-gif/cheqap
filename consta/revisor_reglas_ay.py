"""Revisor de reglas para afirmaciones en aymara. Determinista, sin modelo.

Regla única: si la afirmación trae un marcador de negación aymara (jani, janiw, janiwa, janirakiw, ...)
y ninguno de los párrafos candidatos lo trae, se marca "contradicha".

De dónde sale: de las 713 filas aym del split dev de AmericasNLI que NO están en nuestro lote de 30
(data/benchmark/americasnli_aym_resto.jsonl). Allí la regla dispara en 84 de 238 contradicciones (35 %),
en 5 de 238 implicaciones (2 %) y en 13 de 237 neutras (5 %): precisión 82 %, cobertura 35 %.
Se midió ANTES de aplicarla al lote de 30. Ver scripts/medir_regla_ay.py.

Límite conocido: una doble negación o una negación que ya está en la premisa no se maneja.
"""

import re

from .fuente import Parrafo

_NEGACION = re.compile(r"\bjan[iï]\w*", re.IGNORECASE)


def revisar(afirmacion: str, candidatos: list[Parrafo]) -> tuple[str | None, str | None, str | None]:
    m = _NEGACION.search(afirmacion)
    if not m:
        return None, None, None
    if any(_NEGACION.search(p.texto) for p in candidatos):
        return None, None, None
    return "contradicha", m.group(0), "negación en aymara que la fuente no tiene"
