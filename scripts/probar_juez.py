"""Prueba rápida del juez con una afirmación verdadera y una con error.

    python scripts/probar_juez.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

load_dotenv()

from consta import buscar, revisor_juez
from consta.fuente import cargar_fuente, texto_completo_norm

RAIZ = Path(__file__).resolve().parent.parent
parrafos = cargar_fuente(RAIZ / "data" / "fuente" / "fuente.json")
texto_norm = texto_completo_norm(parrafos)

CASOS = [
    "Los procedimientos sancionatorios en trámite culminarán con lo establecido en el Decreto Supremo Nº 27172 de 15 de septiembre de 2003 y el Decreto Supremo Nº 71 de 9 de abril de 2009.",
    "Los procedimientos sancionatorios en trámite culminarán con lo establecido en el Decreto Supremo Nº 27172 de 15 de septiembre de 2005 y el Decreto Supremo Nº 71 de 9 de abril de 2009.",
]
for c in CASOS:
    cand = buscar.top_parrafos(c, parrafos)
    r = revisor_juez.juzgar(c, cand, texto_norm)
    print(r.etiqueta, "|", c[90:150])
    print("   ", r)
