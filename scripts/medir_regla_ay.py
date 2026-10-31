"""Mide la regla de negación aymara sobre las 713 filas que NO están en el lote de 30.

    python scripts/medir_regla_ay.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

from consta import revisor_reglas_ay
from consta.fuente import Parrafo
from consta.normalizar import normalizar

RAIZ = Path(__file__).resolve().parent.parent
filas = [json.loads(l) for l in (RAIZ / "data" / "benchmark" / "americasnli_aym_resto.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

dispara = Counter()
total = Counter()
for f in filas:
    p = Parrafo("x", 0, f["premise"], normalizar(f["premise"]))
    et, _, _ = revisor_reglas_ay.revisar(f["hypothesis"], [p])
    total[f["label"]] += 1
    dispara[f["label"]] += et == "contradicha"

print(f"{len(filas)} filas fuera del lote de prueba")
for lab in ("contradiction", "entailment", "neutral"):
    print(f"  {lab:14} dispara {dispara[lab]:3} / {total[lab]}  ({dispara[lab] / total[lab]:.0%})")
aciertos = dispara["contradiction"]
disparos = sum(dispara.values())
print(f"precisión {aciertos}/{disparos} = {aciertos / disparos:.0%}; cobertura de contradicciones {aciertos / total['contradiction']:.0%}")
