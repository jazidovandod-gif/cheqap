"""Revisor 2: un solo modelo devuelve etiqueta + cita. La cita se valida textual en el PDF.

Responsable: B. Listo a las 12:30.

Regla central (no negociable): si la cita no aparece en el PDF normalizado, la etiqueta
"respaldada" se anula y baja a "no_respaldada", con motivo "cita no encontrada en la fuente".

Proveedor por variable de entorno:
  JUEZ_PROVEEDOR=gemini   usa GEMINI_API_KEY y JUEZ_MODELO (p. ej. gemini-3.5-flash)
  JUEZ_PROVEEDOR=openai   usa OPENAI_API_KEY y JUEZ_MODELO
"""

import json
import os
import re
import time
from dataclasses import dataclass

from .cache import con_cache
from .fuente import Parrafo
from .normalizar import cita_existe

PROMPT_JUEZ = """Eres un verificador. Tienes una AFIRMACIÓN y PÁRRAFOS de un documento oficial en español.
Decide una sola etiqueta:
- "respaldada": los párrafos dicen eso.
- "contradicha": los párrafos dicen algo distinto (otra fecha, otro monto, otro obligado, "puede" vs "debe").
- "no_respaldada": los párrafos no hablan de eso.

Devuelve SOLO un JSON con: {{"etiqueta": "...", "cita": "frase copiada EXACTAMENTE de los párrafos, sin cambiar una letra", "motivo": "una oración", "tramo": "palabras de la afirmación que están mal, o null"}}
Si la etiqueta es "no_respaldada", "cita" puede ser null.

AFIRMACIÓN:
{afirmacion}

PÁRRAFOS:
{parrafos}
"""


@dataclass
class Veredicto:
    etiqueta: str
    cita: str | None
    cita_valida: bool
    motivo: str
    tramo: str | None
    pagina: int | None


def llamar_modelo(prompt: str) -> str:
    """Llama al modelo con reintentos ante errores temporales (503 alta demanda, 429 límite)."""
    espera = 4.0
    for intento in range(6):
        try:
            return _llamar_una_vez(prompt)
        except Exception as e:  # noqa: BLE001 - se re-lanza si no es temporal
            temporal = any(c in str(e) for c in ("503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED"))
            if not temporal or intento == 5:
                raise
            time.sleep(espera)
            espera *= 2
    raise RuntimeError("inalcanzable")


def _llamar_una_vez(prompt: str) -> str:
    proveedor = os.getenv("JUEZ_PROVEEDOR", "gemini")
    modelo = os.getenv("JUEZ_MODELO", "gemini-3.5-flash")
    if proveedor == "gemini":
        from google import genai

        cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        return cliente.models.generate_content(model=modelo, contents=prompt).text or ""
    if proveedor == "openai":
        from openai import OpenAI

        cliente = OpenAI()
        r = cliente.chat.completions.create(model=modelo, messages=[{"role": "user", "content": prompt}], temperature=0)
        return r.choices[0].message.content or ""
    raise ValueError(f"JUEZ_PROVEEDOR desconocido: {proveedor}")


def _parsear(salida: str) -> dict:
    m = re.search(r"\{.*\}", salida, flags=re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def juzgar(afirmacion: str, candidatos: list[Parrafo], texto_fuente_norm: str) -> Veredicto:
    parrafos_txt = "\n\n".join(f"[pág. {p.pagina}] {p.texto}" for p in candidatos)
    prompt = PROMPT_JUEZ.format(afirmacion=afirmacion, parrafos=parrafos_txt)
    salida = con_cache("juez", prompt, lambda: llamar_modelo(prompt))
    datos = _parsear(salida)

    etiqueta = datos.get("etiqueta", "no_respaldada")
    cita = datos.get("cita")
    valida = bool(cita) and cita_existe(cita, texto_fuente_norm)
    motivo = datos.get("motivo", "")
    if etiqueta == "respaldada" and not valida:
        etiqueta = "no_respaldada"
        motivo = "cita no encontrada en la fuente; " + motivo

    pagina = None
    if valida:
        from .normalizar import normalizar

        cn = normalizar(cita)
        for p in candidatos:
            if cn in p.texto_norm:
                pagina = p.pagina
                break

    return Veredicto(etiqueta, cita, valida, motivo, datos.get("tramo"), pagina)
