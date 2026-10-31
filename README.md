# Cheqap

Verificador de afirmaciones para el Track 1 del [Grok Bot Santa Cruz Hackathon](https://luma.com/3f65kl5u) (Cursor Bolivia, 31 de octubre de 2026).

Cheqap toma la respuesta de un chatbot, la parte en afirmaciones y las contrasta con un solo PDF. Cada afirmación queda **respaldada**, **no respaldada** o **contradicha**. Si el modelo cita una frase que no está en el PDF, esa cita no cuenta.

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
- **Se repitió con otro modelo y da lo mismo.** Con `qwen/qwen3.8-27b` en Groq (`results/tabla_qwen.md`) el juez acierta 9 de 30, también al nivel del azar. No es un modelo concreto el que falla.
- **Coincide con lo publicado.** En el artículo de [AmericasNLI](https://arxiv.org/abs/2104.08726) (Tabla 4, versión arXiv v2), XLM-R en aymara saca 36,1 % y 37,3 % en cero disparos (azar: 33,3 %). Con adaptación al idioma (preentrenamiento continuo) sube a 43,5–43,9 %; traducir al español antes (translate-test) da 39,7 %; entrenar con datos traducidos (translate-train) llega a 50,0 %. Incluso los métodos específicos para aymara están lejos de un resultado confiable. Que dos LLM generales queden en 33 % no es un fallo del verificador: es el estado del problema.
- **Límite del control.** El lote AmericasNLI trae premisa e hipótesis en aymara, sin el original en español, así que no reproduce el flujo del producto (PDF en español y solo la afirmación en aymara). No se pudo probar ese flujo con datos de terceros ni con ítems propios: el equipo no tiene hablante.
- **Cinco modelos sobre los 30 pares** (`python scripts/comparar_modelos_anli.py`). El azar acierta 10. «Verde falso» es dar por respaldada una afirmación que no lo es, que es el error más peligroso de un verificador:

  | modelo | exactitud | verdaderas reconocidas | contradicciones | neutras | verde falso |
  |---|---|---|---|---|---|
  | gpt-oss-120b (Groq) | 10 / 30 | 0 / 10 | 2 / 10 | 8 / 10 | 1 / 20 |
  | qwen3.8-27b (Groq) | 9 / 30 | 1 / 10 | 3 / 10 | 5 / 10 | 0 / 20 |
  | gemma-4-31b-it (Adaption) | 15 / 30 | 2 / 10 | 3 / 10 | 10 / 10 | 0 / 20 |
  | glm-5.2 (Adaption) | 13 / 30 | 1 / 10 | 3 / 10 | 9 / 10 | 0 / 20 |
  | deepseek-v4-flash (Adaption) | 16 / 30 | 3 / 10 | 4 / 10 | 9 / 10 | 1 / 20 |

  Además, `gemini-3.5-flash-lite` se corrió solo en 18 pares (9 / 18, 1 / 6 verdaderas reconocidas, 0 / 12 verdes falsos; la cuota gratuita de Gemini es de 20 llamadas diarias por modelo y `gemini-3.8-flash` estuvo saturado). `qwen3.5-397b` en Adaption no se pudo medir: el servidor devolvió 504 tras unos 3 minutos por llamada.

  Lectura honesta:
  - **Ningún modelo reconoce de forma fiable lo verdadero**: entre 0 y 3 de 10.
  - **Nadie da verdes falsos de forma notable** (0 o 1 de 20). En aymara el sistema falla hacia el lado seguro: casi nunca confirma algo falso, pero tampoco confirma lo cierto. Por eso en aymara la salida correcta es «no verificable».
  - **Las exactitudes de 13–16 / 30 no son una mejora real.** Un clasificador que responda siempre «no respaldada» acierta 10 / 30. Los modelos que suben a 15–16 lo hacen sobre todo acertando más neutras, no reconociendo verdaderas. Además se probaron 8 modelos sobre los mismos 30 pares: con tantas pruebas, un valor aislado como p = 0,02 (deepseek) no resiste una corrección por comparaciones múltiples.
  - La regla de cita textual anuló solo 1 respuesta «respaldada» (en gemma). No explica estos resultados.

### Qué se intentó para mejorar el aymara (y qué pasó)

Todo reproducible con `python -m benchmark.run --lote anli --anli-modo <modo>` y `python scripts/comparar_modelos_anli.py`.

1. **Regla de negación aymara** (`consta/revisor_reglas_ay.py`). Si la afirmación trae `jani / janiw / janiwa…` y la fuente no, se marca contradicha. Se derivó y midió en las **713 filas de AmericasNLI que no están en el lote de prueba** (`scripts/medir_regla_ay.py`): dispara en el 35 % de las contradicciones, 2 % de las implicaciones y 5 % de las neutras, precisión 82 %. En los 30 pares de prueba atrapa 3 de 10 contradicciones con 2 falsos positivos (precisión 60 %, muestra chica). Es la única pieza de aymara que no depende de un modelo.
2. **Prompt que sabe aymara** (modo `aymara`): el prompt original decía al modelo que la fuente era «un documento oficial en español». Al decirle que ambos textos están en aymara y definir las etiquetas como implicación/contradicción/neutral: gpt-oss sube de 10 a 15 / 30; gemma de 15 a 16 / 30.
3. **Ejemplos resueltos en el prompt** (modo `ejemplos`, 4 por etiqueta, tomados de las 713 filas de fuera del test): gemma 17 / 30, gpt-oss 15 / 30. Con **10 por etiqueta** (30 ejemplos), gemma sigue en 17 / 30. Techo.
4. **Traducir primero y juzgar en español** (modo `traducido`, el flujo real del producto): gemma baja a 13 / 30. La causa se ve en `results/cache/puente/`: las traducciones dejan la mayoría de las palabras entre corchetes (sin reconocer). Coincide con el artículo: translate-test fue el peor método.
5. **Voto entre modelos y abstención** (`scripts/voto_y_abstencion_anli.py`): la mayoría de las tres mejores corridas da 17 / 30, igual que gemma sola. Exigir unanimidad hace que el sistema hable en 11–16 de 30 pares y acierte 62–64 % de esas veces, casi todas neutras. No produce una zona de confianza útil.

| mejor configuración | exactitud | verdaderas reconocidas | verde falso |
|---|---|---|---|
| gemma-4-31b-it + prompt aymara + 4 ejemplos + regla de negación | 17 / 30 | 3 / 10 | 1 / 20 |

De 10 / 30 a 17 / 30 es real pero insuficiente: sigue sin reconocer lo verdadero (3 de 10). Por eso **el producto, en aymara, no da verde ni rojo**: muestra la traducción de trabajo, cuántas palabras no reconoció y la opinión del juez como pista (`combinar.no_verificable`, color gris). Lo que sí haría falta y no cabe en seis horas: un traductor entrenado para aymara (NLLB-200 soporta `ayr_Latn`; trabajos de 2025 lo llevan de 33 a 56 chrF++ con 35 000 pares) o ajuste fino con datos en aymara, y en ambos casos una persona hablante que valide.

## Límites

- Set pequeño: ~20 ítems en español (12 al momento de escribir esto).
- Aymara: sin hablante en el equipo, solo se mide con AmericasNLI (30 pares). Ahí la premisa es el documento y la hipótesis la afirmación, que no es lo mismo que verificar contra una ley de 15 páginas. No se midió aymara contra la Ley 453.
- El aymara pasa por una traducción de trabajo antes de buscar en el PDF; medido: la traducción deja la mayoría de las palabras sin reconocer, así que en aymara el producto se abstiene.
- Se probaron 8 modelos y 4 modos sobre los mismos 30 pares. Cualquier «mejor configuración» elegida después de ver esos 30 está optimista; el número que vale es el de la regla de negación, medido en 713 filas aparte.
- El corte en afirmaciones es por oración; una oración con dos hechos se juzga junta.
