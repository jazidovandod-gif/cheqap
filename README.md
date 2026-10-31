# Consta

Verificador de afirmaciones para el Track 1 del [Grok Bot Santa Cruz Hackathon](https://luma.com/3f65kl5u) (Cursor Bolivia, 31 de octubre de 2026).

Consta toma la respuesta de un chatbot, la parte en afirmaciones y las contrasta con un solo PDF. Cada afirmación queda **respaldada**, **no respaldada** o **contradicha**. Si el modelo cita una frase que no está en el PDF, esa cita no cuenta.

## Qué se mide

Un benchmark reproducible, en español y en aymara, contra el mismo documento en español:

- cerca de 20 respuestas en español, cada una con un error sutil (fecha, monto, «puede» / «debe», obligado, condición o artículo);
- un control en aymara con 30 pares ya publicados de [AmericasNLI](https://github.com/abteen/americasnli) (corte `aym`), etiquetados por hablantes de terceros. El equipo no tiene hablante de aymara, así que **no se inventaron ítems propios en aymara**: `data/benchmark/ay.jsonl` queda vacío y el corredor lo ignora sin `confirmado_por`.

La tabla compara cuatro lecturas: palabras compartidas, un revisor de números y modales, un juez con cita textual, y los dos revisores juntos.

## De qué parte

- [Ragas](https://www.cursorbolivia.com/sprint/recursos/ragas), métricas de respaldo documental.
- [AmericasNLI](https://aclanthology.org/2022.acl-long.435), inferencia en aymara con etiquetas de hablantes.
- [ALCE](https://github.com/princeton-nlp/ALCE), calidad de las citas.
- [FActScore](https://github.com/shmsw25/FActScore) y [MiniCheck](https://github.com/Liyan06/MiniCheck), partir la respuesta antes de juzgarla.
- [RAGTruth](https://github.com/ParticleMedia/RAGTruth), marcar el tramo exacto del error.

El aporte de este sprint es el banco sobre una fuente boliviana, la regla de cita textual y la medición del mismo verificador sobre aymara con datos de terceros.

## Cómo correrlo

```bash
pip install -r requirements.txt
cp .env.example .env            # poner la clave del juez
python -m consta.fuente data/fuente/fuente.pdf       # genera data/fuente/fuente.json
python -m benchmark.descargar_anli                   # 30 pares aym de AmericasNLI
python -m benchmark.run                              # tabla en results/tabla.md
python -m benchmark.run --sin-juez                   # solo baseline + reglas, sin red
streamlit run app/streamlit_app.py                   # pantalla de demo
pytest                                               # cita textual y revisor de reglas
```

Las llamadas al modelo se guardan en `results/cache/`. Con el cache versionado, `benchmark.run` reproduce la tabla sin red.

## Estructura

- `consta/`: fuente, claims, puente (aymara a español de trabajo), buscar, revisor de reglas, juez con cita, combinar.
- `benchmark/`: línea de base, corredor de las cuatro columnas, descarga de AmericasNLI.
- `app/`: pantalla Streamlit.
- `data/benchmark/`: ítems etiquetados; esquema en su README.
- `docs/`: plan, pitch y declaración de material previo.

## Límites

Completar al cierre con los que aparezcan de verdad.

- Set pequeño: ~20 ítems en español (12 al momento de escribir esto).
- Aymara: sin hablante en el equipo, solo se mide con AmericasNLI (30 pares). Ahí la premisa es el documento y la hipótesis la afirmación, que no es lo mismo que verificar contra una ley de 15 páginas. No se midió aymara contra la Ley 453.
- El aymara pasa por una traducción de trabajo antes de buscar en el PDF; el error puede venir de ahí y no del verificador.
- El corte en afirmaciones es por oración; una oración con dos hechos se juzga junta.
