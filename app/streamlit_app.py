"""Pantalla de demo. Responsable: D. Con etiquetas falsas a las 12:00; conectada a las 12:30.

    streamlit run app/streamlit_app.py
"""

import html
import re
import sys
from collections import Counter
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from consta.pipeline import Cheqap  # noqa: E402

FUENTE = "Ley N.º 453 de derechos de usuarios y consumidores"

# color -> (etiqueta, verbo en singular, verbo en plural)
VEREDICTOS = {
    "rojo": ("Contradice la ley", "contradice la ley", "contradicen la ley"),
    "ambar": ("Sin respaldo en la ley", "no tiene respaldo en la ley", "no tienen respaldo en la ley"),
    "gris": ("No verificable", "no se puede verificar", "no se pueden verificar"),
    "verde": ("Respaldada por la ley", "está respaldada", "están respaldadas"),
}

DECISION = {
    "reglas": "Decidieron las reglas de números y modales.",
    "juez": "Decidió el juez.",
    "ambos": "Coinciden las reglas y el juez.",
}

SIN_CITA = {
    "rojo": "Sin cita textual verificada en la ley.",
    "ambar": "Cheqap no encontró en la ley un pasaje que diga esto.",
    "gris": "El juez no propuso un pasaje de la ley.",
    "verde": "Sin cita textual.",
}

NOTA_AYMARA = (
    "En aymara Cheqap no da verde ni rojo: en el benchmark (AmericasNLI, 30 pares, 6 modelos medidos) ningún modelo "
    "pasa de 17/30 con azar en 10, y la traducción de trabajo no reconoce la mayoría de las palabras. "
    "Se muestra la traducción, las palabras sin reconocer y la opinión del juez solo como pista."
)

NOTA_PREGUNTA_AY = (
    "La pregunta se traduce al español para buscar en la ley. La respuesta se redacta y se verifica en español: "
    "generarla en aymara no alcanza fiabilidad medible."
)

ESTILOS = """
<style>
@import url("https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,400..800;1,400..800&family=Archivo:wdth,wght@62..125,100..900&display=swap");

:root {
  --cq-papel: #f1f2ed;
  --cq-hoja: #ffffff;
  --cq-tinta: #22203a;
  --cq-tenue: #5f6170;
  --cq-regla: #d5d6ce;
  --cq-sello: #5b3e96;
  --cq-sello-fondo: #e9e5f2;
  --cq-verde: #1b7f3b; --cq-verde-fondo: #e3efe6; --cq-verde-texto: #16662f;
  --cq-ambar: #b7791f; --cq-ambar-fondo: #f6ecd8; --cq-ambar-texto: #82540e;
  --cq-rojo: #b42318; --cq-rojo-fondo: #f7e1de; --cq-rojo-texto: #9f1f15;
  --cq-gris: #6b7280; --cq-gris-fondo: #e7e8ea; --cq-gris-texto: #474c59;
  --cq-sans: "Archivo", system-ui, sans-serif;
  --cq-serif: "Alegreya", Georgia, serif;
}
.cq-v-verde { --c: var(--cq-verde); --c-fondo: var(--cq-verde-fondo); --c-texto: var(--cq-verde-texto); }
.cq-v-ambar { --c: var(--cq-ambar); --c-fondo: var(--cq-ambar-fondo); --c-texto: var(--cq-ambar-texto); }
.cq-v-rojo { --c: var(--cq-rojo); --c-fondo: var(--cq-rojo-fondo); --c-texto: var(--cq-rojo-texto); }
.cq-v-gris { --c: var(--cq-gris); --c-fondo: var(--cq-gris-fondo); --c-texto: var(--cq-gris-texto); }

[data-testid="stMainBlockContainer"] { max-width: 1180px; padding-top: 4rem; padding-bottom: 6rem; }
[data-testid="stDecoration"], [data-testid="InputInstructions"] { display: none; }
[data-testid="stWidgetLabel"] p { font-size: 0.9375rem; font-weight: 600; }
[data-testid="stTextArea"] textarea { font-size: 1.0625rem; line-height: 1.55; }
[data-testid="stCheckbox"] label > div:first-of-type { background-color: var(--cq-tenue); }
[data-testid="stCheckbox"] label > div:first-of-type > div { background-color: var(--cq-hoja); }

.cq-cabeza { max-width: 44rem; margin: 0 0 2.25rem; }
.cq-cabeza .cq-marca {
  font-family: var(--cq-sans); font-stretch: 125%; font-variation-settings: "wdth" 125;
  font-weight: 800; font-size: clamp(2.75rem, 6vw, 4rem); line-height: 1; letter-spacing: -0.015em;
  color: var(--cq-sello); margin: 0 0 1rem; padding: 0;
}
.cq-bajada { font-family: var(--cq-sans); font-size: 1.1875rem; line-height: 1.5; color: var(--cq-tinta); margin: 0 0 0.5rem; }
.cq-fuente { font-family: var(--cq-sans); font-size: 0.9375rem; color: var(--cq-tenue); margin: 0; }

.cq-nota, .cq-aviso {
  font-family: var(--cq-sans); font-size: 0.9375rem; line-height: 1.5; color: var(--cq-tinta);
  max-width: 44rem; margin: 0 0 0.5rem; padding: 0.75rem 1rem;
  border-left: 4px solid var(--c, var(--cq-sello)); background: var(--c-fondo, var(--cq-sello-fondo));
}

.cq-resultado { margin-top: 2.5rem; font-family: var(--cq-sans); color: var(--cq-tinta); }
.cq-veredicto { font-size: 1.375rem; line-height: 1.4; max-width: 44rem; margin: 0 0 0.875rem; }
.cq-veredicto strong { font-weight: 700; }
.cq-tira { display: flex; gap: 4px; max-width: 44rem; margin: 0 0 2.75rem; }
.cq-seg {
  flex: 1; height: 12px; border-radius: 2px; background: var(--c);
  transform-origin: left center; animation: cq-sellar 0.32s cubic-bezier(0.2, 0.7, 0.2, 1) both;
  animation-delay: calc(var(--i) * 90ms);
}
.cq-seg:focus-visible { outline: 2px solid var(--cq-sello); outline-offset: 3px; }
@keyframes cq-sellar { from { transform: scaleX(0); } to { transform: scaleX(1); } }

.cq-cab, .cq-fila {
  display: grid; grid-template-columns: 2.25rem minmax(0, 1fr) minmax(0, 1fr); column-gap: 1.75rem;
}
.cq-cab { font-size: 0.875rem; font-weight: 600; color: var(--cq-tenue); padding-bottom: 0.625rem; }
.cq-cab span:nth-child(2) { padding-left: calc(5px + 1.125rem); }
.cq-fila { padding: 1.75rem 0; border-top: 1px solid var(--cq-regla); scroll-margin-top: 4rem; }
.cq-num {
  font-weight: 700; font-size: 1.125rem; line-height: 1.5; color: var(--cq-tenue);
  text-align: right; font-variant-numeric: tabular-nums;
}
.cq-dicho { border-left: 5px solid var(--c); padding-left: 1.125rem; }
.cq-afirmacion { font-size: 1.1875rem; line-height: 1.5; margin: 0 0 0.875rem; }
.cq-tramo {
  background: var(--cq-rojo-fondo); color: var(--cq-rojo-texto); font-weight: 700; padding: 0 0.04em; border-radius: 2px;
  text-decoration: underline wavy var(--cq-rojo); text-decoration-thickness: 1.5px; text-underline-offset: 5px;
}
.cq-etiqueta {
  display: inline-block; font-size: 0.9375rem; font-weight: 700; color: var(--c-texto);
  background: var(--c-fondo); padding: 0.2rem 0.625rem; border-radius: 3px; margin: 0 0 0.625rem;
}
.cq-motivo { font-size: 0.9375rem; line-height: 1.55; color: var(--cq-tenue); margin: 0; max-width: 62ch; }
.cq-ley {
  align-self: start; background: var(--cq-hoja); border: 1px solid var(--cq-regla);
  border-radius: 4px; padding: 1rem 1.25rem 1.125rem;
}
.cq-pagina { font-size: 0.875rem; font-weight: 600; color: var(--cq-sello); margin: 0 0 0.375rem; }
.cq-cita { font-family: var(--cq-serif); font-size: 1.25rem; line-height: 1.6; margin: 0; }
.cq-dudosa, .cq-dudosa + .cq-cita { color: var(--cq-tenue); }
.cq-sin-cita { font-size: 0.9375rem; line-height: 1.5; color: var(--cq-tenue); margin: 0; }
.cq-publicada { max-width: 44rem; margin: 2rem 0 0; }
.cq-publicada h2 { font-size: 1.375rem; line-height: 1.3; font-weight: 700; margin: 0 0 0.75rem; }
.cq-publicada .cq-frase { font-size: 1.1875rem; line-height: 1.55; margin: 0 0 0.625rem; padding-left: 0.875rem; border-left: 5px solid var(--c); }

@media (max-width: 760px) {
  .cq-cab { display: none; }
  .cq-fila { grid-template-columns: 1.5rem minmax(0, 1fr); column-gap: 0.875rem; }
  .cq-ley { grid-column: 2; margin-top: 1rem; }
}
@media (prefers-reduced-motion: reduce) {
  .cq-seg { animation: none; }
}
</style>
"""

# Papel y tinta se invierten; el violeta y los colores de veredicto se aclaran para leerse sobre fondo oscuro.
ESTILOS_OSCURO = """
<style>
:root {
  color-scheme: dark;
  --cq-papel: #1d1b2f;
  --cq-hoja: #27253d;
  --cq-tinta: #ecede6;
  --cq-tenue: #a9aab8;
  --cq-regla: #3a3852;
  --cq-sello: #a993e6;
  --cq-sello-fondo: #2e2948;
  --cq-verde: #4fb574; --cq-verde-fondo: #1e3327; --cq-verde-texto: #8fd8a8;
  --cq-ambar: #d9a03f; --cq-ambar-fondo: #3a2f1a; --cq-ambar-texto: #f0c67a;
  --cq-rojo: #e8675a; --cq-rojo-fondo: #43211f; --cq-rojo-texto: #ffaea4;
  --cq-gris: #8e93a1; --cq-gris-fondo: #2c2d3a; --cq-gris-texto: #c8cad3;
}
.stApp, [data-testid="stHeader"] { background-color: var(--cq-papel); color: var(--cq-tinta); }
[data-testid="stToolbar"] { color: var(--cq-tenue); }
[data-testid="stWidgetLabel"] p, [data-testid="stRadio"] label p, [data-testid="stCheckbox"] label p,
[data-testid="stSpinner"] p { color: var(--cq-tinta); }
[data-baseweb="textarea"] { background-color: var(--cq-hoja); border-color: var(--cq-regla); }
[data-testid="stTextArea"] textarea { background-color: var(--cq-hoja); color: var(--cq-tinta); caret-color: var(--cq-tinta); }
[data-testid="stTextArea"] textarea::placeholder { color: var(--cq-tenue); opacity: 1; }
[data-testid="stBaseButton-primaryFormSubmit"] { background-color: var(--cq-sello); border-color: var(--cq-sello); color: var(--cq-papel); }
[data-testid="stBaseButton-primaryFormSubmit"]:hover { filter: brightness(1.1); color: var(--cq-papel); }
[data-testid="stRadioOption"] > div > div:first-child { background-color: var(--cq-hoja); border-color: var(--cq-tenue); }
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child { background-color: var(--cq-sello); border-color: var(--cq-sello); }
[data-testid="stRadioOption"] > div > div:first-child > div { background-color: var(--cq-papel); }
[data-testid="stCheckbox"] label > div:first-of-type { background-color: var(--cq-sello); }
[data-testid="stCheckbox"] label > div:first-of-type > div { background-color: var(--cq-papel); }
</style>
"""


def frase(texto: str | None) -> str:
    texto = (texto or "").strip()
    if not texto:
        return ""
    texto = texto[0].upper() + texto[1:]
    return texto if texto[-1] in ".!?…»" else texto + "."


def marcar_tramo(afirmacion: str, tramo: str | None) -> tuple[str, bool]:
    """HTML de la afirmación con el tramo marcado. False si el tramo no aparece en la oración."""
    if not tramo or not tramo.strip():
        return html.escape(afirmacion), True
    t = re.escape(tramo.strip())
    m = re.search(rf"(?<!\w){t}(?!\w)", afirmacion, re.IGNORECASE) or re.search(t, afirmacion, re.IGNORECASE)
    if not m:
        return html.escape(afirmacion), False
    a, b = m.span()
    marcado = f'<mark class="cq-tramo">{html.escape(afirmacion[a:b])}</mark>'
    return html.escape(afirmacion[:a]) + marcado + html.escape(afirmacion[b:]), True


def resumen(resultados: list) -> str:
    total = len(resultados)
    cuenta = Counter(r.color for r in resultados)
    partes = []
    for color in ("rojo", "ambar", "gris", "verde"):
        n = cuenta.get(color, 0)
        if not n:
            continue
        _, uno, varios = VEREDICTOS[color]
        verbo = uno if n == 1 else varios
        if partes:
            partes.append(f"{n}&nbsp;{verbo}.")
        elif n == total:
            sujeto = "La afirmación" if total == 1 else f"Las {total} afirmaciones"
            partes.append(f"<strong>{sujeto} {verbo}.</strong>")
        else:
            partes.append(f"<strong>{n} de {total} afirmaciones {verbo}.</strong>")
    return " ".join(partes)


def fila(i: int, r) -> str:
    afirmacion, tramo_visible = marcar_tramo(r.afirmacion, r.tramo)
    notas = [frase(r.motivo)]
    if r.tramo and not tramo_visible:
        notas.append(f"Tramo que cambió: «{r.tramo.strip()}».")
    notas.append(DECISION.get(r.fuente_decision, ""))
    motivo = " ".join(html.escape(n) for n in notas if n)

    if r.cita:
        # Sin página, la cita no se ubicó en los párrafos revisados: no se presenta como texto de la ley.
        pagina = f"Página {r.pagina}" if r.pagina else "Cita del juez sin página verificada"
        if r.color == "gris":
            pagina += ", pista no confiable"
        dudosa = " cq-dudosa" if r.color == "gris" or not r.pagina else ""
        ley = f'<p class="cq-pagina{dudosa}">{pagina}</p><p class="cq-cita">«{html.escape(r.cita.strip())}»</p>'
    else:
        ley = f'<p class="cq-sin-cita">{SIN_CITA[r.color]}</p>'

    return (
        f'<article class="cq-fila cq-v-{r.color}" id="cq-af-{i}">'
        f'<div class="cq-num">{i}</div>'
        f'<div class="cq-dicho"><p class="cq-afirmacion">{afirmacion}</p>'
        f'<p class="cq-etiqueta">{VEREDICTOS[r.color][0]}</p>'
        f'<p class="cq-motivo">{motivo}</p></div>'
        f'<div class="cq-ley">{ley}</div>'
        "</article>"
    )


def html_publicada(respuesta) -> str:
    """Texto que sí se entrega: verde y ámbar. El rojo no entra aquí."""
    frases = [
        f'<p class="cq-frase cq-v-{r.color}">{html.escape(r.afirmacion)}</p>' for r in respuesta.publicadas
    ]
    if frases:
        cuerpo = "".join(frases)
    elif respuesta.retenidas:
        cuerpo = '<p class="cq-aviso">Ninguna frase se publica: todas contradicen la ley.</p>'
    else:
        cuerpo = '<p class="cq-aviso">El redactor no produjo oraciones revisables.</p>'
    n = len(respuesta.retenidas)
    aviso = ""
    if n:
        aviso = (
            f'<p class="cq-nota cq-v-rojo">{n} {"frase contradice" if n == 1 else "frases contradicen"} '
            "la ley y no se publican. Quedan abajo, en el detalle.</p>"
        )
    paginas = ", ".join(str(p) for p in dict.fromkeys(respuesta.borrador.paginas))
    traduccion = ""
    if respuesta.lengua == "ay" and respuesta.trabajo.strip() != respuesta.pregunta.strip():
        traduccion = (
            f'<p class="cq-motivo">Traducción de trabajo: «{html.escape(respuesta.trabajo.strip())}».</p>'
        )
    return (
        '<section class="cq-publicada">'
        "<h2>Respuesta publicada</h2>"
        f"{traduccion}{aviso}{cuerpo}"
        f'<p class="cq-fuente">Fragmentos usados: páginas {html.escape(paginas)}.</p>'
        "</section>"
    )


def html_resultados(resultados: list, titulo_dicho: str = "Lo que dijo el asistente") -> str:
    tira = "".join(
        f'<a class="cq-seg cq-v-{r.color}" href="#cq-af-{i}" style="--i:{i}" '
        f'title="{i}. {VEREDICTOS[r.color][0]}" aria-label="Afirmación {i}: {VEREDICTOS[r.color][0]}"></a>'
        for i, r in enumerate(resultados, 1)
    )
    filas = "".join(fila(i, r) for i, r in enumerate(resultados, 1))
    return (
        '<section class="cq-resultado">'
        f'<p class="cq-veredicto">{resumen(resultados)}</p>'
        f'<nav class="cq-tira" aria-label="Afirmaciones en orden">{tira}</nav>'
        f'<div class="cq-cab"><span></span><span>{html.escape(titulo_dicho)}</span><span>Lo que dice la ley</span></div>'
        f"{filas}</section>"
    )


@st.cache_resource
def cargar_cheqap() -> Cheqap:
    return Cheqap()


st.set_page_config(page_title="Cheqap", page_icon=":material/fact_check:", layout="wide")
st.html(ESTILOS)

with st.container(horizontal=True, horizontal_alignment="right"):
    oscuro = st.toggle("Modo oscuro", key="oscuro", bind="query-params")
if oscuro:
    st.html(ESTILOS_OSCURO)

try:
    paginas = f", {max(p.pagina for p in cargar_cheqap().parrafos)} páginas"
except Exception:  # noqa: BLE001 - la fuente se vuelve a cargar al verificar y ahí se muestra el error
    paginas = ""

st.html(
    '<header class="cq-cabeza"><h1 class="cq-marca">Cheqap</h1>'
    '<p class="cq-bajada">Pregunta sobre la ley, o pega una respuesta ya hecha. Cheqap redacta con los artículos '
    "recuperados y no publica una frase que los contradiga. Una cita solo cuenta si aparece tal cual en el PDF.</p>"
    f'<p class="cq-fuente">Fuente: {FUENTE}{paginas}.</p></header>'
)

modo = st.radio(
    "Qué hacer",
    ["preguntar", "verificar"],
    horizontal=True,
    format_func=lambda x: {"preguntar": "Preguntar a la ley", "verificar": "Verificar una respuesta"}[x],
)
lengua = st.radio(
    "Lengua",
    ["es", "ay"],
    horizontal=True,
    format_func=lambda x: {"es": "Español", "ay": "Aymara"}[x],
)
if lengua == "ay" and modo == "verificar":
    st.html(f'<p class="cq-nota cq-v-gris">{NOTA_AYMARA}</p>')
elif lengua == "ay":
    st.html(f'<p class="cq-nota cq-v-gris">{NOTA_PREGUNTA_AY}</p>')

if modo == "preguntar":
    with st.form("preguntar", border=False):
        pregunta = st.text_area(
            "Pregunta",
            height=120,
            placeholder="¿En qué plazo debe el Órgano Ejecutivo reglamentar la ley?",
        )
        enviar_p = st.form_submit_button("Preguntar", type="primary")
    if enviar_p:
        st.session_state.pop("ultima_pregunta", None)
        if not pregunta.strip():
            st.html('<p class="cq-aviso">Escribe primero la pregunta.</p>')
        else:
            try:
                with st.spinner("Buscando en la ley, redactando y revisando cada frase…"):
                    st.session_state.ultima_pregunta = (pregunta, lengua, cargar_cheqap().responder(pregunta, lengua))
            except Exception as e:  # noqa: BLE001
                st.html(
                    f'<p class="cq-aviso cq-v-rojo">No se pudo responder ({type(e).__name__}: '
                    f"{html.escape(str(e))}). Revisa la clave del juez en .env o vuelve a intentar en un minuto.</p>"
                )
    ultima = st.session_state.get("ultima_pregunta")
    if ultima and ultima[:2] == (pregunta, lengua):
        resp = ultima[2]
        st.html(html_publicada(resp))
        if resp.resultados:
            st.html(html_resultados(resp.resultados, "Lo que redactó Cheqap"))
        else:
            st.html(
                '<p class="cq-aviso">El redactor no produjo oraciones de al menos cuatro palabras. '
                f"Borrador: «{html.escape(resp.borrador.texto[:400])}».</p>"
            )
else:
    with st.form("verificar", border=False):
        respuesta = st.text_area(
            "Respuesta del asistente",
            height=180,
            placeholder="Pega aquí la respuesta del asistente. Cheqap la parte en oraciones y revisa cada una contra la ley.",
        )
        enviar = st.form_submit_button("Verificar respuesta", type="primary")

    if enviar:
        st.session_state.pop("ultimo", None)
        if not respuesta.strip():
            st.html('<p class="cq-aviso">Pega primero la respuesta del asistente.</p>')
        else:
            try:
                with st.spinner("Contrastando cada afirmación con la ley…"):
                    st.session_state.ultimo = (respuesta, lengua, cargar_cheqap().verificar_respuesta(respuesta, lengua))
            except Exception as e:  # noqa: BLE001
                st.html(
                    f'<p class="cq-aviso cq-v-rojo">No se pudo completar la verificación ({type(e).__name__}: '
                    f"{html.escape(str(e))}). Revisa la clave del juez en .env o vuelve a intentar en un minuto.</p>"
                )

    ultimo = st.session_state.get("ultimo")
    if ultimo and ultimo[:2] == (respuesta, lengua):
        if ultimo[2]:
            st.html(html_resultados(ultimo[2]))
        else:
            st.html(
                '<p class="cq-aviso">No hay afirmaciones que revisar. Cheqap revisa oraciones completas '
                "de al menos cuatro palabras; pega la respuesta tal como la dio el asistente.</p>"
            )
