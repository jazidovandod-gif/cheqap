"""Respuesta del chatbot -> afirmaciones cortas, una por hecho.

Responsable: B. Listo a las 12:00.

Versión 1 (determinista, sin modelo): corta por oración. Es la que corre si no hay red.
Versión 2 (opcional, tarde): pedir al modelo que separe hechos compuestos. Solo si la versión 1 ya
pasa la demo. La comparación entre ambas es una de las ablaciones posibles (FActScore/MiniCheck).
"""

import re

_CORTE = re.compile(r"(?<=[.;!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡\"“])")


def partir_en_afirmaciones(respuesta: str) -> list[str]:
    """Devuelve oraciones limpias, sin viñetas ni numeración, de al menos 4 palabras."""
    texto = re.sub(r"^\s*[-•*\d]+[.)]?\s+", "", respuesta, flags=re.MULTILINE)
    texto = re.sub(r"\s+", " ", texto).strip()
    partes = _CORTE.split(texto) if texto else []
    return [p.strip() for p in partes if len(p.split()) >= 4]
