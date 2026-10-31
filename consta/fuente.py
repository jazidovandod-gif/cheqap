"""PDF -> lista de párrafos con número de página.

Uso:
    python -m consta.fuente data/fuente/fuente.pdf
Escribe data/fuente/fuente.json.

Responsable: A. Listo a las 12:00.
"""

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from .normalizar import normalizar


@dataclass
class Parrafo:
    id: str
    pagina: int
    texto: str
    texto_norm: str


MAX_CARACTERES = 700

# Inicio de bloque: "Artículo 14." o inciso "a." / numeral romano "II." / numeral "3." al comienzo de línea.
_INICIO_ARTICULO = re.compile(r"^\s*Art[ií]culo\s+\d+", re.IGNORECASE)
_INICIO_BLOQUE = re.compile(r"\n(?=\s*(?:Art[ií]culo\s+\d+|[a-z]\.\s|[IVX]{1,4}\.\s|\d{1,2}\.\s))")


def _limpiar_pagina(texto: str) -> str:
    """Quita el número de página de la primera línea y une las palabras cortadas con guion."""
    lineas = texto.split("\n")
    if lineas and lineas[0].strip().isdigit():
        lineas = lineas[1:]
    texto = "\n".join(lineas)
    return re.sub(r"(\w)-\n\s*(\w)", r"\1\2", texto)


def _fragmentos_de_pagina(texto: str) -> list[str]:
    """Un fragmento por artículo; los artículos largos se parten por inciso hasta MAX_CARACTERES."""
    bloques = [re.sub(r"\s+", " ", b).strip() for b in _INICIO_BLOQUE.split(texto)]
    bloques = [b for b in bloques if b]
    fragmentos: list[str] = []
    actual = ""
    for b in bloques:
        abre_articulo = bool(_INICIO_ARTICULO.match(b))
        if actual and (abre_articulo or len(actual) + len(b) > MAX_CARACTERES) and len(actual) >= 40:
            fragmentos.append(actual)
            actual = b
        else:
            actual = f"{actual} {b}".strip()
    if actual:
        fragmentos.append(actual)
    return fragmentos


def extraer_parrafos(ruta_pdf: Path) -> list[Parrafo]:
    """Lee el PDF página por página y devuelve fragmentos con su número de página.

    Un fragmento nunca cruza de página: así la cita siempre apunta a una página concreta.
    """
    from pypdf import PdfReader

    lector = PdfReader(str(ruta_pdf))
    parrafos: list[Parrafo] = []
    for num, pagina in enumerate(lector.pages, start=1):
        texto = _limpiar_pagina(pagina.extract_text() or "")
        for frag in _fragmentos_de_pagina(texto):
            pid = f"p{num}-{len(parrafos):03d}"
            parrafos.append(Parrafo(pid, num, frag, normalizar(frag)))
    return parrafos


def cargar_fuente(ruta_json: Path) -> list[Parrafo]:
    datos = json.loads(ruta_json.read_text(encoding="utf-8"))
    return [Parrafo(**d) for d in datos]


def texto_completo_norm(parrafos: list[Parrafo]) -> str:
    """Un solo string normalizado con todo el PDF, para validar citas por subcadena."""
    return " ".join(p.texto_norm for p in parrafos)


if __name__ == "__main__":
    pdf = Path(sys.argv[1])
    salida = pdf.with_name("fuente.json")
    parrafos = extraer_parrafos(pdf)
    salida.write_text(json.dumps([asdict(p) for p in parrafos], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{len(parrafos)} párrafos -> {salida}")
