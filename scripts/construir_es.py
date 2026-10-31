"""Arma data/benchmark/es.jsonl a partir de los ítems escritos aquí.

    python scripts/construir_es.py

Garantías (el script falla si alguna no se cumple):
  - cada `frase_fuente` aparece textual (normalizada) dentro de UN fragmento del PDF; la página se calcula, no se escribe a mano;
  - cada `tramo_error` aparece en el texto de la afirmación que lo contiene;
  - cada ítem con error tiene exactamente una afirmación con error; los controles, ninguna.

Las etiquetas se escribieron ANTES de correr el verificador. Este archivo va en un commit anterior a results/.
"""

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from consta.fuente import cargar_fuente  # noqa: E402
from consta.normalizar import normalizar  # noqa: E402


def V(texto, frase):
    """Afirmación verdadera."""
    return {"texto": texto, "esperada": "respaldada", "frase": frase}


def E(texto, frase, tipo, tramo=None, esperada="contradicha"):
    """Afirmación con el error inyectado. `frase` es la frase REAL del PDF que se distorsionó."""
    return {"texto": texto, "esperada": esperada, "frase": frase, "tipo_error": tipo, "tramo_error": tramo}


ITEMS = [
    ("es-001", [
        V("Las usuarias y los usuarios, las consumidoras y los consumidores tienen derecho a la reclamación cuando consideren que sus derechos han sido vulnerados.",
          "tienen derecho a la reclamación, cuando consideren que sus derechos han sido vulnerados"),
        E("Los proveedores podrán atender y resolver las reclamaciones, de acuerdo a la naturaleza del producto o servicio.",
          "quienes deberán atender y resolver las reclamaciones, de acuerdo a la naturaleza del producto o servicio",
          "modal", "podrán atender y resolver"),
        V("Además de reclamar ante el proveedor, las usuarias y los usuarios pueden presentar una reclamación administrativa ante entidades competentes.",
          "podrán realizar la reclamación administrativa ante entidades competentes"),
    ]),
    ("es-002", [
        V("El Órgano Ejecutivo desarrollará la reglamentación de la ley en el plazo de ciento veinte (120) días de publicada.",
          "El Órgano Ejecutivo en el plazo de ciento veinte (120) días de publicada la presente Ley, desarrollará la reglamentación correspondiente"),
        E("Las entidades de regulación y fiscalización sectorial deberán adecuar su normativa en un plazo de noventa (90) días de aprobada la reglamentación.",
          "en un plazo de sesenta (60) días de aprobada la reglamentación de la presente Ley, deberán adecuar su normativa",
          "plazo", "noventa (90) días"),
        V("La ley abroga y deroga todas las disposiciones contrarias a ella.",
          "Se abrogan y derogan todas las disposiciones contrarias a la presente Ley"),
    ]),
    ("es-003", [
        V("La protección del derecho al trato equitativo se hace efectiva conforme a la ley, sin perjuicio de la Ley Nº 045 Contra el Racismo y Toda Forma de Discriminación.",
          "sin perjuicio de las previsiones establecidas en la Ley Nº 045 Contra el Racismo y Toda Forma de Discriminación"),
        E("Los procedimientos sancionatorios en trámite culminarán con lo establecido en el Decreto Supremo Nº 27172 de 15 de septiembre de 2005 y el Decreto Supremo Nº 71 de 9 de abril de 2009.",
          "Decreto Supremo Nº 27172 de 15 de septiembre de 2003, Decreto Supremo Nº 71 de 9 de abril de 2009",
          "fecha", "15 de septiembre de 2005"),
        V("El proveedor deberá entregar el producto o suministrar el servicio en las modalidades y términos ofertados o convenidos.",
          "deberá entregar a las usuarias y los usuarios, las consumidoras y los consumidores el producto o suministrar el servicio en las modalidades y términos ofertados o convenidos"),
    ]),
    ("es-004", [
        V("Los proveedores deberán brindar atención sin discriminación, con respeto, calidez y cordialidad.",
          "Brindar atención sin discriminación, con respeto, calidez, cordialidad"),
        E("Las usuarias y los usuarios deberán obtener las licencias o autorizaciones respectivas para la realización de sus actividades de provisión de productos o el suministro de servicios.",
          "Obtener las licencias o autorizaciones respectivas para la realización de sus actividades de provisión de productos o el suministro de servicios",
          "obligado", "Las usuarias y los usuarios deberán obtener las licencias"),
        V("Las usuarias y los usuarios deberán observar y asumir las advertencias e instrucciones sobre el uso, consumo, instalación o conservación del producto o servicio.",
          "Observar y asumir las advertencias e instrucciones en relación al adecuado uso, consumo, instalación o conservación del producto o servicio"),
    ]),
    ("es-005", [
        V("Para acceder a la conexión de servicios básicos, los operadores no podrán solicitar más requisitos que los previstos en la normativa específica.",
          "no podrán solicitar a las usuarias y los usuarios, más requisitos que los que estén previstos en la normativa específica"),
        E("Los proveedores no podrán realizar el corte del suministro de servicios básicos.",
          "Los proveedores no podrán realizar el corte del suministro de servicios básicos, salvo las condiciones y procedimientos establecidos en la normativa específica",
          "condicion", None, esperada="no_respaldada"),
        V("El proveedor que cobre por error en la facturación deberá devolver el monto cobrado, de acuerdo con la normativa específica.",
          "deberá devolver el monto cobrado, de acuerdo a lo establecido en la normativa específica"),
    ]),
    ("es-006", [
        V("El Artículo 19 regula los contratos de adhesión.",
          "Artículo 19. (CONTRATOS DE ADHESIÓN)"),
        E("El Artículo 91 define el contrato de adhesión como aquel en el que las cláusulas son dispuestas unilateralmente por un proveedor.",
          "El contrato de adhesión es aquél en el que las cláusulas son dispuestas unilateralmente por un proveedor de productos o servicios",
          "articulo", "Artículo 91"),
        V("La resolución de la reclamación puede ser impugnada ante la misma autoridad que la pronunció.",
          "podrá ser impugnada ante la misma autoridad que la pronunció"),
    ]),
    ("es-007", [
        V("Las prácticas comerciales abusivas están prohibidas y serán sancionadas por las autoridades competentes.",
          "Las prácticas comerciales abusivas están prohibidas y serán sancionadas por las autoridades competentes"),
        E("Se permite la importación, distribución o comercialización de productos suspendidos, prohibidos o retirados en el país de origen por motivos de salud.",
          "Productos suspendidos, prohibidos o retirados en el país de origen por motivos de salud o riesgo a la integridad física",
          "modal", "Se permite"),
        V("Cobrar en moneda que no esté en curso legal y vigente es una práctica comercial abusiva.",
          "Cobrar en moneda que no se encuentre en curso legal y vigente"),
    ]),
    ("es-008", [
        V("La ley tiene por objeto regular los derechos y garantías de las usuarias y los usuarios, las consumidoras y los consumidores.",
          "tiene por objeto regular los derechos y garantías de las usuarias y los usuarios, las consumidoras y los consumidores"),
        E("La ley se apoya en el Artículo 72 de la Ley Nº 031 de 19 de julio de 2012, Marco de Autonomías y Descentralización.",
          "Artículo 72 de la Ley Nº 031 de 19 de julio de 2010, Marco de Autonomías y Descentralización",
          "fecha", "19 de julio de 2012"),
        V("Se asigna al nivel central del Estado la competencia exclusiva de desarrollar los derechos, garantías y políticas de las usuarias y los usuarios.",
          "se asigna al nivel central del Estado, la competencia exclusiva de desarrollar los derechos, garantías y políticas"),
    ]),
    ("es-009", [
        V("El procedimiento de reclamación administrativa no requiere patrocinio legal alguno.",
          "No requiere de patrocinio legal alguno"),
        E("El contrato de adhesión podrá hacer remisiones a otros documentos aunque no se entreguen a las usuarias y los usuarios.",
          "El contrato de adhesión no podrá hacer remisiones a otros documentos que no se entreguen a las usuarias y los usuarios",
          "modal", "podrá hacer remisiones"),
        V("Todo reclamo siempre deberá ser resuelto, inclusive si el reclamante lo abandonara.",
          "Todo reclamo siempre deberá ser resuelto, inclusive si el reclamante lo abandonara"),
    ]),
    ("es-010", [
        V("Si los proveedores advierten riesgos o peligros del producto después de introducirlo en el mercado, deberán comunicarlo inmediatamente a las autoridades y a las usuarias y los usuarios.",
          "deberán comunicar inmediatamente este hecho a las autoridades competentes y a las usuarias y los usuarios"),
        E("La autoridad competente que advierta un riesgo no previsto del producto dispondrá su retiro o suspensión solo si el proveedor lo solicita.",
          "dispondrá inmediatamente su retiro o suspensión",
          "condicion", "solo si el proveedor lo solicita"),
        V("Los proveedores no podrán ordenar o inducir a las usuarias y los usuarios a contratar con determinados proveedores.",
          "no podrán ordenar o inducir a las usuarias y los usuarios, las consumidoras y los consumidores a contratar con determinados proveedores"),
    ]),
    ("es-011", [
        V("Las entidades del sector público responsables asignarán los recursos necesarios al interior de su presupuesto institucional.",
          "asignarán los recursos necesarios al interior de su presupuesto institucional"),
        E("El Órgano Ejecutivo desarrollará la reglamentación en el plazo de sesenta (60) días de publicada la ley.",
          "El Órgano Ejecutivo en el plazo de ciento veinte (120) días de publicada la presente Ley, desarrollará la reglamentación correspondiente",
          "plazo", "sesenta (60) días"),
        V("La ley fue promulgada en el Palacio de Gobierno de la ciudad de La Paz.",
          "Palacio de Gobierno de la ciudad de La Paz"),
    ]),
    # Control sin error: mide falsos positivos puros.
    ("es-012", [
        V("Los proveedores de servicios alimenticios están obligados a tener información accesible sobre la calidad del producto o del servicio.",
          "está obligado a tener información accesible con relación a la calidad del producto o del servicio"),
        V("Las organizaciones de defensa de usuarias y usuarios no tendrán fines de lucro.",
          "Las organizaciones no tendrán fines de lucro"),
        V("El proveedor que preste servicios será el único responsable frente a la usuaria y al usuario.",
          "El proveedor que preste servicios será el único responsable frente a la usuaria y al usuario"),
    ]),
]


def main() -> int:
    parrafos = cargar_fuente(RAIZ / "data" / "fuente" / "fuente.json")
    problemas: list[str] = []
    filas = []
    for item_id, afs in ITEMS:
        n_err = sum(1 for a in afs if a["esperada"] != "respaldada")
        if item_id != "es-012" and n_err != 1:
            problemas.append(f"{item_id}: debe tener exactamente 1 error, tiene {n_err}")
        salida_afs = []
        for a in afs:
            frase_n = normalizar(a["frase"])
            pagina = next((p.pagina for p in parrafos if frase_n in p.texto_norm), None)
            if pagina is None:
                problemas.append(f"{item_id}: frase_fuente no está textual en un solo fragmento: {a['frase'][:70]!r}")
            if a.get("tramo_error") and normalizar(a["tramo_error"]) not in normalizar(a["texto"]):
                problemas.append(f"{item_id}: tramo_error no aparece en la afirmación: {a['tramo_error']!r}")
            fila = {"texto": a["texto"], "esperada": a["esperada"], "pagina": pagina, "frase_fuente": a["frase"]}
            if a["esperada"] != "respaldada":
                fila["tipo_error"] = a["tipo_error"]
                fila["tramo_error"] = a.get("tramo_error")
            salida_afs.append(fila)
        filas.append({
            "id": item_id,
            "lengua": "es",
            "respuesta": " ".join(a["texto"] for a in afs),
            "afirmaciones": salida_afs,
            "confirmado_por": None,
        })
    if problemas:
        print("PROBLEMAS:")
        for p in problemas:
            print(" -", p)
        return 1
    destino = RAIZ / "data" / "benchmark" / "es.jsonl"
    destino.write_text("\n".join(json.dumps(f, ensure_ascii=False) for f in filas) + "\n", encoding="utf-8")
    total = sum(len(f["afirmaciones"]) for f in filas)
    errores = sum(1 for f in filas for a in f["afirmaciones"] if a["esperada"] != "respaldada")
    print(f"{len(filas)} ítems, {total} afirmaciones ({errores} con error, {total - errores} verdaderas) -> {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
