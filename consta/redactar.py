"""Pregunta -> borrador apoyado en los fragmentos de la ley. Cheqap lo revisa después.

El recuperador es el mismo que el verificador (palabras compartidas, sin embeddings).
El modelo solo redacta; no decide qué se publica. Una frase en rojo no entra en
`publicar`.
"""

from dataclasses import dataclass

from . import buscar, puente, revisor_juez
from .cache import con_cache
from .fuente import Parrafo

PROMPT = """Responde la PREGUNTA usando solo los PASAJES de una ley boliviana.
Reglas:
- Una oración por hecho, en español.
- Copia números, plazos, fechas y «debe» / «puede» tal como están en los pasajes. No los cambies.
- Si los pasajes no alcanzan para responder, escribe solo: «Los pasajes recuperados no dicen eso.»
- No agregues artículos, montos ni obligaciones que no aparezcan en los pasajes.

PREGUNTA:
{pregunta}

PASAJES:
{pasajes}
"""


@dataclass
class Borrador:
    pregunta: str
    trabajo: str  # español con el que se busca; igual a pregunta si ya venía en español
    texto: str
    paginas: list[int]


def armar_prompt(pregunta: str, candidatos: list[Parrafo]) -> str:
    pasajes = "\n\n".join(f"[pág. {p.pagina}] {p.texto}" for p in candidatos)
    return PROMPT.format(pregunta=pregunta, pasajes=pasajes)


def redactar(pregunta: str, lengua: str, parrafos: list[Parrafo], k: int = 6) -> Borrador:
    """Traduce la pregunta si viene en aymara, recupera k fragmentos y pide el borrador."""
    af = puente.preparar(pregunta, lengua, revisor_juez.llamar_modelo)
    candidatos = buscar.top_parrafos(af.trabajo, parrafos, k=k)
    prompt = armar_prompt(af.trabajo, candidatos)
    texto = con_cache("redactor", prompt, lambda: revisor_juez.llamar_modelo(prompt)).strip()
    return Borrador(pregunta, af.trabajo, texto, [p.pagina for p in candidatos])


def publicar(resultados: list) -> list:
    """Lo que se muestra como respuesta: todo menos lo que contradice la ley."""
    return [r for r in resultados if r.color != "rojo"]
