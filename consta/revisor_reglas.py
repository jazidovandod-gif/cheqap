"""Revisor 1, determinista. Compara números, montos, días y «puede/debe» con el párrafo.

Responsable: B. Listo a las 12:00, con tests en tests/test_revisor_reglas.py.

Devuelve:
  ("contradicha", tramo, motivo)  si hay un número o un modal que no coincide con ningún párrafo candidato
  (None, None, None)             si no tiene opinión (ni confirma ni niega)

Nunca devuelve "respaldada": eso solo lo hace el juez con cita.
"""

import re

from .fuente import Parrafo
from .normalizar import normalizar

_NUM = re.compile(r"\b\d+(?:[.,]\d+)?\b")
_MODALES = {"debe", "debera", "deberan", "puede", "podra", "podran", "obligatorio", "opcional"}
_GRUPO_OBLIGA = {"debe", "debera", "deberan", "obligatorio"}
_GRUPO_PERMITE = {"puede", "podra", "podran", "opcional"}


def _numeros(texto_norm: str) -> set[str]:
    return {n.replace(",", ".") for n in _NUM.findall(texto_norm)}


def _modales(texto_norm: str) -> set[str]:
    return {t for t in re.findall(r"[a-zñ]+", texto_norm) if t in _MODALES}


def revisar(afirmacion: str, candidatos: list[Parrafo]) -> tuple[str | None, str | None, str | None]:
    a_norm = normalizar(afirmacion)
    nums_a = _numeros(a_norm)
    mods_a = _modales(a_norm)
    nums_fuente = set().union(*(_numeros(p.texto_norm) for p in candidatos)) if candidatos else set()
    mods_fuente = set().union(*(_modales(p.texto_norm) for p in candidatos)) if candidatos else set()

    # Número presente en la afirmación que no aparece en ningún párrafo candidato.
    faltan = nums_a - nums_fuente
    if faltan and nums_fuente:
        tramo = sorted(faltan)[0]
        return "contradicha", tramo, f"el número {tramo} no aparece en los párrafos candidatos"

    # Modal invertido: la afirmación obliga y la fuente solo permite, o al revés.
    if mods_a & _GRUPO_OBLIGA and mods_fuente and not (mods_fuente & _GRUPO_OBLIGA):
        tramo = sorted(mods_a & _GRUPO_OBLIGA)[0]
        return "contradicha", tramo, "la afirmación obliga; la fuente solo permite"
    if mods_a & _GRUPO_PERMITE and mods_fuente and not (mods_fuente & _GRUPO_PERMITE):
        tramo = sorted(mods_a & _GRUPO_PERMITE)[0]
        return "contradicha", tramo, "la afirmación permite; la fuente obliga"

    return None, None, None
