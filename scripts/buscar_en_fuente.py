"""Muestra cómo está escrito algo en la fuente.

    python scripts/buscar_en_fuente.py "27172"
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
datos = json.loads((Path(__file__).resolve().parent.parent / "data" / "fuente" / "fuente.json").read_text(encoding="utf-8"))
clave = sys.argv[1].lower()
for p in datos:
    i = p["texto"].lower().find(clave)
    if i >= 0:
        print(p["id"], "pág", p["pagina"], "->", repr(p["texto"][max(0, i - 80): i + 200]))
