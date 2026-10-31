"""Integridad del benchmark: nada de citas inventadas ni ítems en aymara sin confirmar."""

import json
from pathlib import Path

import pytest

from consta.fuente import cargar_fuente
from consta.normalizar import cita_existe, normalizar

RAIZ = Path(__file__).resolve().parent.parent
FUENTE = RAIZ / "data" / "fuente" / "fuente.json"
ETIQUETAS = {"respaldada", "no_respaldada", "contradicha"}


def _leer(nombre: str) -> list[dict]:
    ruta = RAIZ / "data" / "benchmark" / nombre
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


pytestmark = pytest.mark.skipif(not FUENTE.exists(), reason="falta data/fuente/fuente.json")


@pytest.mark.parametrize("archivo", ["es.jsonl", "ay.jsonl"])
def test_frases_de_la_fuente_existen_y_la_pagina_es_correcta(archivo):
    parrafos = cargar_fuente(FUENTE)
    texto_norm = " ".join(p.texto_norm for p in parrafos)
    for item in _leer(archivo):
        for a in item["afirmaciones"]:
            assert a["esperada"] in ETIQUETAS, (item["id"], a["esperada"])
            assert cita_existe(a["frase_fuente"], texto_norm), f"{item['id']}: frase inventada: {a['frase_fuente'][:60]}"
            paginas = {p.pagina for p in parrafos if normalizar(a["frase_fuente"]) in p.texto_norm}
            assert a["pagina"] in paginas, f"{item['id']}: página {a['pagina']} no coincide"


def test_tramo_del_error_esta_en_la_afirmacion():
    for item in _leer("es.jsonl"):
        for a in item["afirmaciones"]:
            if a.get("tramo_error"):
                assert normalizar(a["tramo_error"]) in normalizar(a["texto"]), item["id"]


def test_un_solo_error_por_item_salvo_controles():
    for item in _leer("es.jsonl"):
        errores = [a for a in item["afirmaciones"] if a["esperada"] != "respaldada"]
        assert len(errores) <= 1, item["id"]


def test_aymara_exige_confirmacion_humana():
    for item in _leer("ay.jsonl"):
        assert item.get("confirmado_por"), f"{item['id']}: sin confirmado_por"
