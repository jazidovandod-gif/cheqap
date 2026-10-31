"""Compara los modelos del juez sobre AmericasNLI (lee results/detalle*.jsonl, sin red).

    python scripts/comparar_modelos_anli.py

Imprime dos tablas: sobre los pares comunes a todos los modelos, y sobre los 30 pares
para los modelos que los corrieron completos.
"""

import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent / "results"

NOMBRES = {
    "detalle.jsonl": "gpt-oss-120b (Groq)",
    "detalle_qwen.jsonl": "qwen3.8-27b (Groq)",
    "detalle_gemini35lite.jsonl": "gemini-3.5-flash-lite",
    "detalle_ad_qwen35397b.jsonl": "qwen3.5-397b (Adaption)",
    "detalle_ad_gemma431bit.jsonl": "gemma-4-31b-it (Adaption)",
    "detalle_ad_glm52.jsonl": "glm-5.2 (Adaption)",
    "detalle_ad_deepseekv4flash.jsonl": "deepseek-v4-flash (Adaption)",
}


def leer(nombre):
    filas = [json.loads(l) for l in (R / nombre).read_text(encoding="utf-8").splitlines() if l.strip()]
    return {f["id"]: f for f in filas if f["lote"] == "anli"}


modelos = {n: leer(a) for a, n in NOMBRES.items() if (R / a).exists()}
modelos = {n: d for n, d in modelos.items() if d}


def tabla(ids, titulo):
    print(f"\n{titulo} ({len(ids)} pares; el azar acierta {len(ids) / 3:.1f})")
    print(f"{'modelo':30} {'exactitud':>9}  {'verdaderas':>10}  {'contradicc.':>11}  {'neutras':>8}  {'verde falso':>11}  {'P(azar)':>8}")
    n, p = len(ids), 1 / 3
    for nombre, d in modelos.items():
        if not all(i in d for i in ids):
            continue
        ok, tot = Counter(), Counter()
        for i in ids:
            f = d[i]
            tot[f["esperada"]] += 1
            ok[f["esperada"]] += f["juez"] == f["esperada"]
        k = sum(ok.values())
        verde_falso = sum(d[i]["juez"] == "respaldada" and d[i]["esperada"] != "respaldada" for i in ids)
        pv = sum(math.comb(n, j) * p**j * (1 - p) ** (n - j) for j in range(k, n + 1))
        print(
            f"{nombre:30} {k:>4}/{n:<4}  {ok['respaldada']:>4}/{tot['respaldada']:<5}  "
            f"{ok['contradicha']:>5}/{tot['contradicha']:<5}  {ok['no_respaldada']:>3}/{tot['no_respaldada']:<4}  {verde_falso:>5}/{tot['contradicha'] + tot['no_respaldada']:<5}  {pv:>8.3f}"
        )


comunes = sorted(set.intersection(*(set(d) for d in modelos.values())))
tabla(comunes, "Pares comunes a todos los modelos")
todos = sorted(set.union(*(set(d) for d in modelos.values())))
tabla(todos, "Los 30 pares (solo modelos que los corrieron completos)")
