"""Punto de entrada único que usan la pantalla y el benchmark."""

from pathlib import Path

from . import buscar, claims, combinar, puente, revisor_juez, revisor_reglas
from .fuente import cargar_fuente, texto_completo_norm

RUTA_FUENTE = Path(__file__).resolve().parent.parent / "data" / "fuente" / "fuente.json"


class Consta:
    def __init__(self, ruta_fuente: Path = RUTA_FUENTE):
        self.parrafos = cargar_fuente(ruta_fuente)
        self.texto_norm = texto_completo_norm(self.parrafos)

    def verificar_afirmacion(self, texto: str, lengua: str = "es") -> combinar.Resultado:
        af = puente.preparar(texto, lengua, revisor_juez.llamar_modelo)
        candidatos = buscar.top_parrafos(af.trabajo, self.parrafos)
        reglas = revisor_reglas.revisar(af.trabajo, candidatos)
        juez = revisor_juez.juzgar(af.trabajo, candidatos, self.texto_norm)
        res = combinar.combinar(af.original, reglas, juez)
        return res

    def verificar_respuesta(self, respuesta: str, lengua: str = "es") -> list[combinar.Resultado]:
        return [self.verificar_afirmacion(a, lengua) for a in claims.partir_en_afirmaciones(respuesta)]
