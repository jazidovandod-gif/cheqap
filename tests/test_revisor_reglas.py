from consta.fuente import Parrafo
from consta.normalizar import normalizar
from consta.revisor_reglas import revisar


def _p(texto: str) -> Parrafo:
    return Parrafo("p1", 7, texto, normalizar(texto))


FUENTE = [_p("El proveedor deberá responder el reclamo en un plazo máximo de 30 días hábiles.")]


def test_numero_cambiado_es_contradicha():
    et, tramo, _ = revisar("El proveedor debe responder el reclamo en 15 días hábiles.", FUENTE)
    assert et == "contradicha"
    assert tramo == "15"


def test_modal_invertido_es_contradicha():
    fuente = [_p("El usuario podrá presentar su reclamo por escrito.")]
    et, tramo, _ = revisar("El usuario debe presentar su reclamo por escrito.", fuente)
    assert et == "contradicha"
    assert tramo == "debe"


def test_sin_senal_no_opina():
    et, _, _ = revisar("La ley protege a usuarias y usuarios.", FUENTE)
    assert et is None
