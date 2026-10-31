"""Mide factores léxicos para aymara en las 713 filas que NO están en el lote de prueba.

    python scripts/medir_factores_ay.py

Factores:
  solapamiento  fracción de raíces (primeros 5 caracteres) de la afirmación que aparecen en la fuente
  negación      marcador jani/janiw en la afirmación y no en la fuente (regla ya existente)

Busca un umbral de solapamiento alto que señale "respaldada" con buena precisión.
"""

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from consta.revisor_reglas_ay import raices, solapamiento, tiene_negacion

RAIZ = Path(__file__).resolve().parent.parent
filas = [json.loads(l) for l in (RAIZ / "data" / "benchmark" / "americasnli_aym_resto.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

por_label = defaultdict(list)
for f in filas:
    por_label[f["label"]].append(solapamiento(f["hypothesis"], f["premise"]))

print("solapamiento medio por etiqueta:")
for lab, xs in por_label.items():
    print(f"  {lab:14} {sum(xs) / len(xs):.2f}   (n={len(xs)})")

print("\numbral -> cuántas filas superan el umbral (sin negación desajustada) y qué fracción es implicación:")
for umbral in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
    c = Counter()
    for f in filas:
        neg_h, neg_p = tiene_negacion(f["hypothesis"]), tiene_negacion(f["premise"])
        if neg_h != neg_p:
            continue
        if solapamiento(f["hypothesis"], f["premise"]) >= umbral and len(raices(f["hypothesis"])) >= 3:
            c[f["label"]] += 1
    n = sum(c.values())
    if n:
        print(f"  >= {umbral:.1f}: {n:3} filas | implicación {c['entailment']:3} ({c['entailment'] / n:.0%}) | neutral {c['neutral']:3} | contradicción {c['contradiction']:3}")
