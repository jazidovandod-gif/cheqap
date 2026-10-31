"""Baja 30 pares del corte aym de AmericasNLI (split dev) a data/benchmark/americasnli_aym.jsonl.

    python -m benchmark.descargar_anli

Fuente: https://raw.githubusercontent.com/nala-cub/AmericasNLI/main/dev.tsv
Cita: Ebrahimi et al., AmericasNLI, ACL 2022. Revisar la licencia antes de redistribuir las filas.
Se toman 10 de cada etiqueta, en el orden del archivo, con semilla fija.
"""

import csv
import io
import json
import random
import urllib.request
from pathlib import Path

URL = "https://raw.githubusercontent.com/nala-cub/AmericasNLI/main/dev.tsv"
SALIDA = Path(__file__).resolve().parent.parent / "data" / "benchmark" / "americasnli_aym.jsonl"
POR_ETIQUETA = 10


def main():
    datos = urllib.request.urlopen(URL, timeout=60).read().decode("utf-8")
    filas = [r for r in csv.DictReader(io.StringIO(datos), delimiter="\t") if r["language"] == "aym"]
    random.Random(453).shuffle(filas)
    elegidas: list[dict] = []
    for etiqueta in ("entailment", "neutral", "contradiction"):
        elegidas += [r for r in filas if r["label"] == etiqueta][:POR_ETIQUETA]
    with SALIDA.open("w", encoding="utf-8") as f:
        for i, r in enumerate(elegidas, 1):
            f.write(json.dumps({"id": f"anli-{i:03d}", "premise": r["premise"], "hypothesis": r["hypothesis"], "label": r["label"]}, ensure_ascii=False) + "\n")
    print(f"{len(elegidas)} pares -> {SALIDA}")


if __name__ == "__main__":
    main()
