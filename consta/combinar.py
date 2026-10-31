"""Regla fija que junta los dos revisores. Responsable: B. Listo a las 14:30.

  rojo   si cualquiera ve contradicción
  verde  si el juez dice respaldada con cita válida y las reglas no vieron número cambiado
  ámbar  el resto
"""

from dataclasses import dataclass

from .revisor_juez import Veredicto


@dataclass
class Resultado:
    afirmacion: str
    etiqueta: str  # respaldada | no_respaldada | contradicha | no_verificable
    color: str  # verde | ambar | rojo | gris
    cita: str | None
    pagina: int | None
    tramo: str | None
    motivo: str
    fuente_decision: str  # reglas | juez | ambos | abstencion

    def cita_valida_o_none(self) -> bool:
        return bool(self.cita)


def combinar(afirmacion: str, reglas: tuple, juez: Veredicto) -> Resultado:
    r_et, r_tramo, r_motivo = reglas
    if r_et == "contradicha" and juez.etiqueta == "contradicha":
        return Resultado(afirmacion, "contradicha", "rojo", juez.cita, juez.pagina, r_tramo or juez.tramo, r_motivo, "ambos")
    if r_et == "contradicha":
        return Resultado(afirmacion, "contradicha", "rojo", juez.cita if juez.cita_valida else None, juez.pagina, r_tramo, r_motivo, "reglas")
    if juez.etiqueta == "contradicha":
        return Resultado(afirmacion, "contradicha", "rojo", juez.cita, juez.pagina, juez.tramo, juez.motivo, "juez")
    if juez.etiqueta == "respaldada" and juez.cita_valida:
        return Resultado(afirmacion, "respaldada", "verde", juez.cita, juez.pagina, None, juez.motivo, "juez")
    return Resultado(afirmacion, "no_respaldada", "ambar", None, None, None, juez.motivo or "sin respaldo en la fuente", "juez")


def combinar_ay(afirmacion: str, reglas: tuple, juez: Veredicto) -> Resultado:
    """Aymara. Igual que `combinar`, más una vía al verde por la regla de solapamiento de raíces
    (precisión 70 % en 713 filas aparte) cuando el juez no vio contradicción. El juez en aymara
    reconoce lo verdadero 3 de 10 veces; la regla cubre parte de ese hueco."""
    r_et, r_tramo, r_motivo = reglas
    if r_et == "contradicha" or juez.etiqueta == "contradicha":
        return combinar(afirmacion, reglas, juez)
    if juez.etiqueta == "respaldada" and juez.cita_valida:
        return combinar(afirmacion, reglas, juez)
    if r_et == "respaldada":
        return Resultado(afirmacion, "respaldada", "verde", None, None, None, r_motivo, "reglas")
    return combinar(afirmacion, reglas, juez)


def no_verificable(afirmacion: str, traduccion: str, desconocidas: int, total: int, pista: Resultado) -> Resultado:
    """Aymara: el benchmark (AmericasNLI, 30 pares, 8 modelos) no pasa de 17/30 con azar en 10, y la
    traducción de trabajo deja la mayoría de las palabras sin reconocer. Cheqap no da verde ni rojo;
    muestra la traducción, cuántas palabras no reconoció y la opinión del juez solo como pista."""
    motivo = (
        f"Aymara: Cheqap no alcanza fiabilidad medible en esta lengua (ver README, sección Resultados). "
        f"Traducción de trabajo: «{traduccion}». Palabras sin reconocer: {desconocidas} de {total}. "
        f"Pista no confiable del juez: {pista.etiqueta}."
    )
    return Resultado(afirmacion, "no_verificable", "gris", pista.cita if pista.cita_valida_o_none() else None, pista.pagina, None, motivo, "abstencion")
