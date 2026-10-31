"""Renombra las entradas del cache antiguo (sin modelo en la clave) a la clave nueva.

    python scripts/migrar_cache.py gemini gemini-3.5-flash
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from consta.cache import RAIZ, _ruta

etiqueta = f"{sys.argv[1]}|{sys.argv[2]}"
movidos = 0
for archivo in list(RAIZ.glob("*/*.json")):
    espacio = archivo.parent.name
    datos = json.loads(archivo.read_text(encoding="utf-8"))
    nueva = _ruta(espacio, datos["entrada"], etiqueta)
    if nueva != archivo:
        archivo.rename(nueva)
        movidos += 1
print(f"{movidos} entradas migradas a {etiqueta}")
