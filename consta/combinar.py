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
    etiqueta: str  # respaldada | no_respaldada | contradicha
    color: str  # verde | ambar | rojo
    cita: str | None
    pagina: int | None
    tramo: str | None
    motivo: str
    fuente_decision: str  # reglas | juez | ambos


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
