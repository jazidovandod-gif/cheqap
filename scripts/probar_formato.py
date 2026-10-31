"""Muestra la salida cruda del modelo activo (¿trae razonamiento antes del JSON?).

    python scripts/probar_formato.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import os

import consta  # noqa: F401
from consta import revisor_juez

print("modelo:", os.environ.get("JUEZ_MODELO"))
print(repr(revisor_juez.llamar_modelo('Responde solo este JSON: {"ok": true}')[:400]))
