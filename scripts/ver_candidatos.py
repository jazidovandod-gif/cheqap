"""Ayuda para armar el benchmark: lista los fragmentos con plazos, montos, prohibiciones y modales.

    python scripts/ver_candidatos.py > data/fuente/_candidatos.txt
"""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

RAIZ = Path(__file__).resolve().parent.parent
datos = json.loads((RAIZ / "data" / "fuente" / "fuente.json").read_text(encoding="utf-8"))
patron = re.compile(
    r"d[ií]as|plazo|multa|prohib|a[nñ]os|horas|meses|\bdiez\b|\bcinco\b|\bquince\b|\btreinta\b|\bveinte\b|\bsesenta\b|\bnoventa\b|\bdeber[aá]n?\b|\bpodr[aá]n?\b",
    re.IGNORECASE,
)
for p in datos:
    if patron.search(p["texto"]):
        print(f"[{p['id']} pag {p['pagina']}] {p['texto']}\n")
