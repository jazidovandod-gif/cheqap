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

## Resultados

Juez: `openai/gpt-oss-120b` en Groq, temperatura por defecto del proveedor. Fuente: Ley 453 (15 páginas). Las etiquetas se confirmaron en un commit anterior a la primera corrida. Tabla completa en `results/tabla.md` y fila por fila en `results/detalle.jsonl`.

| lote | columna | errores detectados | falsos positivos | exactitud (3 clases) |
|---|---|---|---|---|
| es | baseline (palabras compartidas) | 0 / 11 | 0 / 25 | 25 / 36 |
| es | reglas | 4 / 11 | 0 / 25 | 29 / 36 |
| es | juez con cita textual | 10 / 11 | 0 / 25 | 35 / 36 |
| es | juntos | 10 / 11 | 0 / 25 | 35 / 36 |
| AmericasNLI aym | baseline | 18 / 20 | 9 / 10 | 11 / 30 |
| AmericasNLI aym | reglas | 0 / 20 | 0 / 10 | 10 / 30 |
| AmericasNLI aym | juez | 19 / 20 | 10 / 10 | 10 / 30 |
| AmericasNLI aym | juntos | 19 / 20 | 10 / 10 | 10 / 30 |

Lectura honesta:

- **Español.** El baseline por palabras compartidas no detecta ningún error sutil (0 de 11). El juez con cita textual detecta 10 de 11 y no marca como error ninguna de las 25 afirmaciones verdaderas. El que se escapa es `es-005`, una negación («no podrán realizar el corte»): el juez la dio por respaldada.
- **Los dos revisores juntos no mejoran al juez solo en este set.** Las reglas atrapan 4 errores (plazos, fechas de decretos, número de artículo) y el juez ya los atrapaba. Su valor aquí es que funcionan sin red ni modelo, no que suban la cifra.
- **Aymara: resultado negativo.** En 30 pares de AmericasNLI, con este modelo, todas las columnas aciertan 10 de 30, lo mismo que el azar. «Errores detectados 19/20» no significa que funcione: el juez marca casi todo como error, y de 10 pares donde la hipótesis se sigue de la premisa, ninguno salió respaldado. La regla de cita textual no es la causa (ninguna etiqueta se anuló por cita falsa); lo que falla es que el modelo no entiende el texto en aymara. Se puede revisar con `python scripts/analizar_anli.py`.
- No se probó otro modelo para el aymara por el límite diario del plan gratuito de Gemini.

## Límites

- Set pequeño: ~20 ítems en español (12 al momento de escribir esto).
- Aymara: sin hablante en el equipo, solo se mide con AmericasNLI (30 pares). Ahí la premisa es el documento y la hipótesis la afirmación, que no es lo mismo que verificar contra una ley de 15 páginas. No se midió aymara contra la Ley 453.
- El aymara pasa por una traducción de trabajo antes de buscar en el PDF; el error puede venir de ahí y no del verificador.
- El corte en afirmaciones es por oración; una oración con dos hechos se juzga junta.
