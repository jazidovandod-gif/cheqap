"""Revisor 2: un solo modelo devuelve etiqueta + cita. La cita se valida textual en el PDF.

Responsable: B. Listo a las 12:30.

Regla central (no negociable): si la cita no aparece en el PDF normalizado, la etiqueta
"respaldada" se anula y baja a "no_respaldada", con motivo "cita no encontrada en la fuente".

Proveedor por variable de entorno:
  JUEZ_PROVEEDOR=gemini   usa GEMINI_API_KEY y JUEZ_MODELO (p. ej. gemini-3.5-flash)
  JUEZ_PROVEEDOR=openai   usa OPENAI_API_KEY y JUEZ_MODELO (y OPENAI_BASE_URL para Groq, etc.)
  JUEZ_PROVEEDOR=adaption usa ADAPTION_API_KEY y JUEZ_MODELO (p. ej. qwen3.5-397b)
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


PROMPT_JUEZ_AY = """Eres un verificador que entiende aymara (aymar aru). Tienes una AFIRMACIÓN y un TEXTO FUENTE, ambos en aymara.
Primero traduce mentalmente los dos al español, con cuidado con las negaciones (jani, janiw, janiwa = no; -ti al final del verbo refuerza la negación) y con los sufijos de persona y tiempo.
Luego decide una sola etiqueta:
- "respaldada": si el texto fuente es cierto, la afirmación tiene que ser cierta.
- "contradicha": si el texto fuente es cierto, la afirmación tiene que ser falsa.
- "no_respaldada": la afirmación podría ser cierta o falsa; el texto fuente no alcanza para saberlo.
Si la afirmación repite la idea del texto fuente con otras palabras, es "respaldada", no "no_respaldada".
{ejemplos}
Devuelve SOLO un JSON con: {{"etiqueta": "...", "cita": "frase copiada EXACTAMENTE del texto fuente, sin cambiar una letra", "motivo": "una oración en español con tu traducción de ambos", "tramo": "palabras de la afirmación que chocan con la fuente, o null"}}
Si la etiqueta es "no_respaldada", "cita" puede ser null.

AFIRMACIÓN:
{afirmacion}

TEXTO FUENTE:
{parrafos}
"""

_MAPA_ANLI = {"entailment": "respaldada", "neutral": "no_respaldada", "contradiction": "contradicha"}


def formatear_ejemplos(filas: list[dict]) -> str:
    """Filas con premise/hypothesis/label (AmericasNLI). Nunca deben ser las del lote de prueba."""
    if not filas:
        return ""
    partes = ["\nEJEMPLOS RESUELTOS (fuente / afirmación / etiqueta):"]
    for f in filas:
        partes.append(f'- Fuente: "{f["premise"]}" | Afirmación: "{f["hypothesis"]}" -> {_MAPA_ANLI[f["label"]]}')
    return "\n".join(partes) + "\n"


@dataclass
class Veredicto:
    etiqueta: str
    cita: str | None
    cita_valida: bool
    motivo: str
    tramo: str | None
    pagina: int | None


_claves_openai: list[str] = []
_idx_clave = 0


def _claves() -> list[str]:
    """OPENAI_API_KEY, OPENAI_API_KEY_2, OPENAI_API_KEY_3: claves del mismo proveedor para rotar ante 429."""
    global _claves_openai
    if not _claves_openai:
        _claves_openai = [k for k in (os.getenv("OPENAI_API_KEY"), os.getenv("OPENAI_API_KEY_2"), os.getenv("OPENAI_API_KEY_3")) if k]
    return _claves_openai


def llamar_modelo(prompt: str) -> str:
    """Llama al modelo con reintentos ante errores temporales (503 alta demanda, 429 límite).
    Con varias claves OpenAI/Groq, un 429 cambia de clave antes de esperar."""
    global _idx_clave
    espera = 4.0
    for intento in range(8):
        try:
            return _llamar_una_vez(prompt)
        except Exception as e:  # noqa: BLE001 - se re-lanza si no es temporal
            texto = str(e)
            temporal = any(c in texto for c in ("503", "429", "500", "UNAVAILABLE", "RESOURCE_EXHAUSTED", "504", "timed out", "Timeout"))
            if not temporal or intento == 7:
                raise
            if "429" in texto and len(_claves()) > 1:
                _idx_clave += 1
                time.sleep(1.0)
                continue
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
    if proveedor == "adaption":
        from adaption import Adaption

        cliente = Adaption(timeout=300.0)  # lee ADAPTION_API_KEY; los modelos que razonan tardan
        return cliente.responses.create(model=modelo, input=prompt).output_text or ""
    if proveedor == "openai":
        from openai import OpenAI

        claves = _claves()
        cliente = OpenAI(api_key=claves[_idx_clave % len(claves)]) if claves else OpenAI()
        extra = {}
        if os.getenv("JUEZ_RAZONAMIENTO"):  # low | medium | high (gpt-oss en Groq)
            extra["reasoning_effort"] = os.getenv("JUEZ_RAZONAMIENTO")
        r = cliente.chat.completions.create(model=modelo, messages=[{"role": "user", "content": prompt}], temperature=0, **extra)
        return r.choices[0].message.content or ""
    raise ValueError(f"JUEZ_PROVEEDOR desconocido: {proveedor}")


def _parsear(salida: str) -> dict:
    m = re.search(r"\{.*\}", salida, flags=re.DOTALL)
    try:
        return json.loads(m.group(0)) if m else {}
    except json.JSONDecodeError:
        return {}


def juzgar(
    afirmacion: str,
    candidatos: list[Parrafo],
    texto_fuente_norm: str,
    lengua: str = "es",
    ejemplos: list[dict] | None = None,
) -> Veredicto:
    """lengua="ay" usa el prompt que sabe aymara; `ejemplos` añade casos resueltos al prompt."""
    parrafos_txt = "\n\n".join(f"[pág. {p.pagina}] {p.texto}" for p in candidatos)
    if lengua == "ay":
        prompt = PROMPT_JUEZ_AY.format(afirmacion=afirmacion, parrafos=parrafos_txt, ejemplos=formatear_ejemplos(ejemplos or []))
    else:
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
