"""Compara modelos y modos del juez sobre AmericasNLI (lee results/detalle*.jsonl, sin red).

    python scripts/comparar_modelos_anli.py

Columnas: exactitud en 3 clases, verdaderas reconocidas, contradicciones y neutras acertadas,
verdes falsos (dar por respaldada una afirmación que no lo es) y probabilidad de lograr esa
exactitud por azar (binomial, p = 1/3).
"""

import json
import math
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).resolve().parent.parent / "results"

MODELOS = {
    "detalle": "gpt-oss-120b (Groq)",
    "detalle_gptoss": "gpt-oss-120b (Groq)",
    "detalle_qwen": "qwen3.8-27b (Groq)",
    "detalle_gemini35lite": "gemini-3.5-flash-lite",
    "detalle_ad_qwen35397b": "qwen3.5-397b (Adaption)",
    "detalle_ad_gemma431bit": "gemma-4-31b-it (Adaption)",
    "detalle_ad_glm52": "glm-5.2 (Adaption)",
    "detalle_ad_deepseekv4flash": "deepseek-v4-flash (Adaption)",
}
MODOS = ("aymara", "ejemplos", "traducido")


def leer(ruta: Path):
    filas = [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    return {f["id"]: f for f in filas if f["lote"] == "anli"}


corridas: dict[tuple[str, str], dict] = {}
for ruta in sorted(R.glob("detalle*.jsonl")):
    base = ruta.stem
    modo = "directo"
    for m in MODOS:
        if base.endswith("_" + m):
            base, modo = base[: -len(m) - 1], m
    if base not in MODELOS:
        continue
    d = leer(ruta)
    if d:
        corridas[(MODELOS[base], modo)] = d


def fila(nombre, modo, d, ids, columna):
    ok, tot = Counter(), Counter()
    for i in ids:
        f = d[i]
        tot[f["esperada"]] += 1
        ok[f["esperada"]] += f[columna] == f["esperada"]
    k = sum(ok.values())
    n = len(ids)
    verde_falso = sum(d[i][columna] == "respaldada" and d[i]["esperada"] != "respaldada" for i in ids)
    pv = sum(math.comb(n, j) * (1 / 3) ** j * (2 / 3) ** (n - j) for j in range(k, n + 1))
    return (
        f"{nombre:30} {modo:10} {columna:7} {k:>4}/{n:<4}  {ok['respaldada']:>4}/{tot['respaldada']:<5}  "
        f"{ok['contradicha']:>5}/{tot['contradicha']:<5}  {ok['no_respaldada']:>3}/{tot['no_respaldada']:<4}  "
        f"{verde_falso:>5}/{tot['contradicha'] + tot['no_respaldada']:<5}  {pv:>8.3f}"
    )


todos = sorted(set.union(*(set(d) for d in corridas.values())))
completas = {k: d for k, d in corridas.items() if all(i in d for i in todos)}
print(f"{len(todos)} pares; el azar acierta {len(todos) / 3:.1f}\n")
print(f"{'modelo':30} {'modo':10} {'columna':7} {'exact.':>9}  {'verdaderas':>10}  {'contradicc.':>11}  {'neutras':>8}  {'verde falso':>11}  {'P(azar)':>8}")
for (nombre, modo), d in sorted(completas.items(), key=lambda kv: (kv[0][1] != "directo", kv[0][1], kv[0][0])):
    print(fila(nombre, modo, d, todos, "juez"))
    if modo != "directo":
        print(fila(nombre, modo, d, todos, "juntos"))

print("\nregla aymara sola (columna reglas; 'respaldada' = la regla no opinó):")
for (nombre, modo), d in completas.items():
    if modo == "aymara":
        print(fila(nombre, modo, d, todos, "reglas"))
        break

parciales = [k for k in corridas if k not in completas]
if parciales:
    print("\ncorridas parciales (no entran en la tabla):", ", ".join(f"{n} / {m} ({len(corridas[(n, m)])} pares)" for n, m in parciales))
