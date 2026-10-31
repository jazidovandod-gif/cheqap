from consta.fuente import Parrafo
from consta.normalizar import normalizar
from consta.revisor_reglas_ay import revisar


def _p(texto):
    return Parrafo("x", 1, texto, normalizar(texto))


def test_negacion_en_afirmacion_y_no_en_fuente_es_contradicha():
    et, tramo, _ = revisar("Janiw manuñax utxkiti", [_p("Manuñax utjiwa.")])
    assert et == "contradicha"
    assert tramo == "Janiw"


def test_negacion_en_ambos_no_opina():
    assert revisar("Janiw sarkiti", [_p("Jupax janiw sarkiti")]) == (None, None, None)


def test_sin_negacion_no_opina():
    assert revisar("Jupax sarawayxiwa", [_p("Jupax sarawayxiwa")]) == (None, None, None)


def test_no_confunde_palabras_que_empiezan_parecido():
    # "jan" solo, sin la i, no es el marcador
    assert revisar("Jan uka", [_p("Uka")]) == (None, None, None)
