"""Corre las cuatro columnas sobre los tres lotes e imprime la tabla.

    python -m benchmark.run                 # todos los lotes
    python -m benchmark.run --lote es       # solo español
    python -m benchmark.run --sin-juez      # baseline + reglas (sin red)

Escribe results/tabla.md y results/detalle.jsonl.

Responsable: C. Listo a las 12:00 con columnas vacías; completo a las 14:30.

Métricas por lote y columna:
  detectados      afirmaciones esperadas contradicha/no_respaldada que la columna marcó como tal
  total_errores   cuántas afirmaciones con error hay
  falsos_pos      afirmaciones esperadas respaldada que la columna marcó con error
  total_verdad    cuántas afirmaciones verdaderas hay
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path

from consta import buscar, combinar, revisor_juez, revisor_reglas
from consta.fuente import Parrafo, cargar_fuente, texto_completo_norm
from consta.normalizar import normalizar

from .baseline import etiqueta_baseline

RAIZ = Path(__file__).resolve().parent.parent
DATOS = RAIZ / "data" / "benchmark"
RESULTADOS = RAIZ / "results"
COLUMNAS = ("baseline", "reglas", "juez", "juntos")
MAPA_ANLI = {"entailment": "respaldada", "neutral": "no_respaldada", "contradiction": "contradicha"}


def _leer(ruta: Path) -> list[dict]:
    if not ruta.exists():
        return []
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def _es_error(etiqueta: str) -> bool:
    return etiqueta in ("contradicha", "no_respaldada")


def _columnas(afirmacion: str, candidatos: list[Parrafo], texto_norm: str, sin_juez: bool) -> dict[str, str]:
    reglas = revisor_reglas.revisar(afirmacion, candidatos)
    col = {
        "baseline": etiqueta_baseline(afirmacion, candidatos) if candidatos else "no_respaldada",
        "reglas": reglas[0] or "respaldada",  # sin opinión cuenta como "no vio error"
    }
    if sin_juez:
        col["juez"] = col["juntos"] = "sin_correr"
        return col
    juez = revisor_juez.juzgar(afirmacion, candidatos, texto_norm)
    col["juez"] = juez.etiqueta
    col["juntos"] = combinar.combinar(afirmacion, reglas, juez).etiqueta
    return col


def correr_lote_pdf(items: list[dict], parrafos: list[Parrafo], texto_norm: str, sin_juez: bool) -> list[dict]:
    from consta import puente

    filas = []
    for it in items:
        if it.get("lengua") == "ay" and not it.get("confirmado_por"):
            continue  # regla 3: sin confirmación no entra
        for af in it["afirmaciones"]:
            prep = puente.preparar(af["texto"], it["lengua"], revisor_juez.llamar_modelo) if not sin_juez else None
            trabajo = prep.trabajo if prep else af["texto"]
            candidatos = buscar.top_parrafos(trabajo, parrafos)
            col = _columnas(trabajo, candidatos, texto_norm, sin_juez)
            filas.append({"lote": it["lengua"], "id": it["id"], "afirmacion": af["texto"], "esperada": af["esperada"], **col})
    return filas


def correr_lote_anli(items: list[dict], sin_juez: bool) -> list[dict]:
    filas = []
    for it in items:
        p = Parrafo(it["id"], 0, it["premise"], normalizar(it["premise"]))
        col = _columnas(it["hypothesis"], [p], p.texto_norm, sin_juez)
        filas.append({"lote": "anli", "id": it["id"], "afirmacion": it["hypothesis"], "esperada": MAPA_ANLI[it["label"]], **col})
    return filas


def resumir(filas: list[dict]) -> dict:
    res: dict = defaultdict(lambda: {c: {"detectados": 0, "falsos_pos": 0, "exactos": 0, "corridas": 0} for c in COLUMNAS} | {"total_errores": 0, "total_verdad": 0})
    for f in filas:
        r = res[f["lote"]]
        if _es_error(f["esperada"]):
            r["total_errores"] += 1
        else:
            r["total_verdad"] += 1
        for c in COLUMNAS:
            if f[c] == "sin_correr":
                continue
            r[c]["corridas"] += 1
            if f[c] == f["esperada"]:
                r[c]["exactos"] += 1
            if _es_error(f["esperada"]) and _es_error(f[c]):
                r[c]["detectados"] += 1
            if not _es_error(f["esperada"]) and _es_error(f[c]):
                r[c]["falsos_pos"] += 1
    return res


def tabla_md(res: dict) -> str:
    out = ["| lote | columna | errores detectados | falsos positivos | exactitud (3 clases) |", "|---|---|---|---|---|"]
    for lote, r in res.items():
        for c in COLUMNAS:
            if r[c]["corridas"] == 0:
                out.append(f"| {lote} | {c} | sin correr | sin correr | sin correr |")
                continue
            total = r["total_errores"] + r["total_verdad"]
            out.append(
                f"| {lote} | {c} | {r[c]['detectados']} / {r['total_errores']} "
                f"| {r[c]['falsos_pos']} / {r['total_verdad']} | {r[c]['exactos']} / {total} |"
            )
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", choices=["es", "ay", "anli", "todos"], default="todos")
    ap.add_argument("--sin-juez", action="store_true")
    ap.add_argument("--por-etiqueta", type=int, default=0, help="AmericasNLI: usar solo K pares por etiqueta (0 = todos)")
    ap.add_argument("--sufijo", default="", help="guarda en results/tabla_<sufijo>.md para no pisar otra corrida")
    args = ap.parse_args()

    filas: list[dict] = []
    if args.lote in ("es", "ay", "todos"):
        parrafos = cargar_fuente(RAIZ / "data" / "fuente" / "fuente.json")
        texto_norm = texto_completo_norm(parrafos)
        for lote in ("es", "ay"):
            if args.lote in (lote, "todos"):
                filas += correr_lote_pdf(_leer(DATOS / f"{lote}.jsonl"), parrafos, texto_norm, args.sin_juez)
    if args.lote in ("anli", "todos"):
        items_anli = _leer(DATOS / "americasnli_aym.jsonl")
        if args.por_etiqueta:
            vistos: dict[str, int] = defaultdict(int)
            recortados = []
            for it in items_anli:
                if vistos[it["label"]] < args.por_etiqueta:
                    vistos[it["label"]] += 1
                    recortados.append(it)
            items_anli = recortados
        filas += correr_lote_anli(items_anli, args.sin_juez)

    res = resumir(filas)
    md = tabla_md(res)
    print(md)
    RESULTADOS.mkdir(exist_ok=True)
    s = f"_{args.sufijo}" if args.sufijo else ""
    (RESULTADOS / f"tabla{s}.md").write_text(md + "\n", encoding="utf-8")
    (RESULTADOS / f"detalle{s}.jsonl").write_text("\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
