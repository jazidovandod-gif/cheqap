"""Diagnóstico del lote AmericasNLI: ¿falla el modelo o la regla de cita textual? (usa el cache, sin red)

    python scripts/analizar_anli.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from consta import revisor_juez
from consta.fuente import Parrafo
from consta.normalizar import normalizar

RAIZ = Path(__file__).resolve().parent.parent
items = [json.loads(l) for l in (RAIZ / "data" / "benchmark" / "americasnli_aym.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

cont = Counter()
for it in items:
    p = Parrafo(it["id"], 0, it["premise"], normalizar(it["premise"]))
    v = revisor_juez.juzgar(it["hypothesis"], [p], p.texto_norm)
    anulada = "cita no encontrada" in (v.motivo or "").lower()
    palabras_premisa = len(it["premise"].split())
    cont[(it["label"], v.etiqueta, "cita_anulada" if anulada else "-")] += 1
    if it["label"] == "entailment":
        print(f"{it['id']} premisa={palabras_premisa} palabras | juez={v.etiqueta} | anulada={anulada} | cita_valida={v.cita_valida}")

print()
for k, n in sorted(cont.items()):
    print(n, k)
