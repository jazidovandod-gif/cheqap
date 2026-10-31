"""Dos análisis sin red sobre AmericasNLI, a partir de results/detalle_*.jsonl:

1. Voto por mayoría entre varias corridas del juez (modelos o modos distintos).
2. Abstención: Cheqap solo da veredicto cuando la mayoría es clara (>= umbral de votos);
   si no, dice "no verificable". Se mide cuánto habla y cuánto acierta cuando habla.

    python scripts/voto_y_abstencion_anli.py detalle_ad_gemma431bit_ejemplos detalle_gptoss_ejemplos detalle_ad_deepseekv4flash
"""

import json
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent / "results"


def leer(nombre):
    filas = [json.loads(l) for l in (R / f"{nombre}.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    return {f["id"]: f for f in filas if f["lote"] == "anli"}


corridas = [leer(n) for n in sys.argv[1:]]
ids = sorted(set.intersection(*(set(c) for c in corridas)))
n_votantes = len(corridas)
print(f"{n_votantes} votantes, {len(ids)} pares\n")

for umbral in range(1, n_votantes + 1):
    habla = aciertos = verde_falso = 0
    por_clase = Counter()
    for i in ids:
        votos = Counter(c[i]["juez"] for c in corridas)
        etiqueta, k = votos.most_common(1)[0]
        if k < umbral:
            continue
        habla += 1
        esperada = corridas[0][i]["esperada"]
        aciertos += etiqueta == esperada
        verde_falso += etiqueta == "respaldada" and esperada != "respaldada"
        por_clase[esperada] += etiqueta == esperada
    mayoria = "mayoría simple" if umbral == 1 else f"al menos {umbral} de {n_votantes} de acuerdo"
    if habla:
        print(f"{mayoria:32} habla en {habla:2}/{len(ids)}  acierta {aciertos:2}/{habla} ({aciertos / habla:.0%})  verdes falsos {verde_falso}  "
              f"verdaderas {por_clase['respaldada']}  contradicciones {por_clase['contradicha']}  neutras {por_clase['no_respaldada']}")
    else:
        print(f"{mayoria:32} no habla nunca")
