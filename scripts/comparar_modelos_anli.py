"""Compara los modelos del juez sobre los mismos pares de AmericasNLI (usa los detalle_*.jsonl).

    python scripts/comparar_modelos_anli.py
"""

import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent / "results"


def leer(nombre):
    return {f["id"]: f for f in map(json.loads, (R / nombre).read_text(encoding="utf-8").splitlines()) if f["lote"] == "anli"}


modelos = {
    "gpt-oss-120b (Groq)": leer("detalle.jsonl"),
    "qwen3.8-27b (Groq)": leer("detalle_qwen.jsonl"),
    "gemini-3.5-flash-lite": leer("detalle_gemini35lite.jsonl"),
}
ids = sorted(modelos["gemini-3.5-flash-lite"])  # el conjunto más chico: 18 pares comunes
print(f"{len(ids)} pares comunes\n")
print(f"{'modelo':26} {'exactitud':>10}  {'respaldada bien':>16}  {'contradicha bien':>17}  {'neutral bien':>13}")
for nombre, d in modelos.items():
    ok = Counter()
    tot = Counter()
    for i in ids:
        f = d[i]
        tot[f["esperada"]] += 1
        ok[f["esperada"]] += f["juez"] == f["esperada"]
    n = sum(ok.values())
    print(f"{nombre:26} {n:>4}/{len(ids):<5}  {ok['respaldada']:>8}/{tot['respaldada']:<7}  {ok['contradicha']:>9}/{tot['contradicha']:<7}  {ok['no_respaldada']:>5}/{tot['no_respaldada']:<7}")

# ¿50 % sobre 18 pares es distinguible del azar (1/3)? Probabilidad binomial de acertar >= k por casualidad.
n, p = len(ids), 1 / 3
for nombre, d in modelos.items():
    k = sum(d[i]["juez"] == d[i]["esperada"] for i in ids)
    pv = sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))
    print(f"{nombre:26} acierta {k}/{n}; probabilidad de lograrlo por azar: {pv:.2f}")
