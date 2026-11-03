from consta.combinar import Resultado
from consta.fuente import Parrafo
from consta.normalizar import normalizar
from consta.redactar import armar_prompt, publicar


def _r(texto: str, color: str) -> Resultado:
    return Resultado(texto, "respaldada", color, None, 14, None, "", "juez")


def test_el_rojo_no_se_publica():
    resultados = [
        _r("El plazo es de ciento veinte (120) días.", "verde"),
        _r("El plazo es de sesenta (60) días.", "rojo"),
        _r("Los pasajes recuperados no dicen eso.", "ambar"),
    ]
    publicados = [r.afirmacion for r in publicar(resultados)]
    assert publicados == [
        "El plazo es de ciento veinte (120) días.",
        "Los pasajes recuperados no dicen eso.",
    ]


def test_el_prompt_lleva_la_pregunta_y_la_pagina():
    p = Parrafo("p14-104", 14, "ciento veinte (120) días", normalizar("ciento veinte (120) días"))
    prompt = armar_prompt("¿En qué plazo se reglamenta?", [p])
    assert "¿En qué plazo se reglamenta?" in prompt
    assert "[pág. 14]" in prompt
    assert "ciento veinte (120) días" in prompt
