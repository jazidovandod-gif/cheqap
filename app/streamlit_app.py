"""Pantalla de demo. Responsable: D. Con etiquetas falsas a las 12:00; conectada a las 12:30.

    streamlit run app/streamlit_app.py
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from consta.pipeline import Consta  # noqa: E402

COLORES = {"verde": "#1b7f3b", "ambar": "#b7791f", "rojo": "#b42318"}

st.set_page_config(page_title="Consta", layout="wide")
st.title("Consta")
st.caption("Cada afirmación del asistente, contrastada con el PDF. Una cita solo vale si existe textual en la fuente.")

lengua = st.radio("Lengua de la respuesta", ["es", "ay"], horizontal=True, format_func=lambda x: {"es": "Español", "ay": "Aymara"}[x])
respuesta = st.text_area("Pega la respuesta del asistente", height=160)

if st.button("Verificar", type="primary") and respuesta.strip():
    consta = Consta()
    resultados = consta.verificar_respuesta(respuesta, lengua)
    izq, der = st.columns([1, 1])
    with izq:
        st.subheader("Respuesta")
        for i, r in enumerate(resultados):
            st.markdown(
                f"<div style='border-left:6px solid {COLORES[r.color]};padding:6px 10px;margin:6px 0'>"
                f"<b>{i + 1}.</b> {r.afirmacion}</div>",
                unsafe_allow_html=True,
            )
    with der:
        st.subheader("Fuente")
        for i, r in enumerate(resultados):
            with st.expander(f"{i + 1}. {r.etiqueta} · {r.fuente_decision}", expanded=(r.color == "rojo")):
                if r.tramo:
                    st.markdown(f"**Tramo que cambió:** `{r.tramo}`")
                if r.cita:
                    st.markdown(f"**Cita (pág. {r.pagina}):** “{r.cita}”")
                st.write(r.motivo)
