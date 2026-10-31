"""Cache en disco de llamadas al modelo. Obligatorio: la demo y el benchmark deben correr sin red.

Clave = sha256(espacio + entrada). Archivo = results/cache/<espacio>/<hash>.json
"""

import hashlib
import json
from pathlib import Path
from typing import Callable

RAIZ = Path(__file__).resolve().parent.parent / "results" / "cache"


def _ruta(espacio: str, entrada: str) -> Path:
    h = hashlib.sha256(entrada.encode("utf-8")).hexdigest()[:24]
    return RAIZ / espacio / f"{h}.json"


def con_cache(espacio: str, entrada: str, calcular: Callable[[], str]) -> str:
    ruta = _ruta(espacio, entrada)
    if ruta.exists():
        return json.loads(ruta.read_text(encoding="utf-8"))["salida"]
    salida = calcular()
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(json.dumps({"entrada": entrada, "salida": salida}, ensure_ascii=False), encoding="utf-8")
    return salida
