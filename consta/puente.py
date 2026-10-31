"""Afirmación en aymara -> español de trabajo. El PDF nunca se traduce.

Responsable: B. Listo a las 14:30.

Devuelve siempre el original junto con la versión de trabajo. La pantalla muestra ambos.
El puente usa el mismo modelo que el juez y pasa por el mismo cache.
"""

from dataclasses import dataclass

from .cache import con_cache


@dataclass
class Afirmacion:
    original: str
    lengua: str  # "es" | "ay"
    trabajo: str  # texto en español con el que se busca y se juzga


PROMPT_PUENTE = (
    "Traduce al español, de forma literal y sin agregar información, la siguiente oración en aymara. "
    "Si una palabra no la conoces, déjala tal cual entre corchetes. Responde solo con la traducción.\n\n{texto}"
)


def preparar(texto: str, lengua: str, llamar_modelo) -> Afirmacion:
    """`llamar_modelo(prompt: str) -> str` lo provee revisor_juez para no duplicar clientes."""
    if lengua == "es":
        return Afirmacion(texto, "es", texto)
    trabajo = con_cache("puente", texto, lambda: llamar_modelo(PROMPT_PUENTE.format(texto=texto)))
    return Afirmacion(texto, "ay", trabajo.strip())
