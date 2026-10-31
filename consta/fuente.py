"""PDF -> lista de párrafos con número de página.

Uso:
    python -m consta.fuente data/fuente/fuente.pdf
Escribe data/fuente/fuente.json.

Responsable: A. Listo a las 12:00.
"""

import json
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


def extraer_parrafos(ruta_pdf: Path) -> list[Parrafo]:
    """Lee el PDF página por página y corta en párrafos por línea en blanco.

    Párrafos de menos de 40 caracteres se pegan al anterior (títulos, numeración suelta).
    """
    from pypdf import PdfReader

    lector = PdfReader(str(ruta_pdf))
    parrafos: list[Parrafo] = []
    for num, pagina in enumerate(lector.pages, start=1):
        texto = pagina.extract_text() or ""
        bloques = [b.strip() for b in texto.split("\n\n") if b.strip()]
        for bloque in bloques:
            if parrafos and len(bloque) < 40 and parrafos[-1].pagina == num:
                parrafos[-1].texto += " " + bloque
                parrafos[-1].texto_norm = normalizar(parrafos[-1].texto)
                continue
            pid = f"p{num}-{len(parrafos):03d}"
            parrafos.append(Parrafo(pid, num, bloque, normalizar(bloque)))
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
