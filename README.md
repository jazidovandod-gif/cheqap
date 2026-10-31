# Cheqap

Verificador de afirmaciones para el Track 1 del [Grok Bot Santa Cruz Hackathon](https://luma.com/3f65kl5u) (Cursor Bolivia, 31 de octubre de 2026).

Cheqap toma la respuesta de un chatbot, la parte en afirmaciones y contrasta cada una con un solo PDF: la **Ley N° 453** de derechos de usuarios y consumidores (15 páginas). Cada afirmación sale **respaldada** (verde), **no respaldada** (ámbar) o **contradicha** (rojo), con el pasaje de la ley y la página. Si el modelo cita una frase que no está textual en el PDF, la cita no cuenta y el verde se anula.

## Resultado en una línea

En español, sobre 36 afirmaciones con errores sutiles inyectados, el chequeo por palabras compartidas detecta **0 de 11** errores y Cheqap detecta **10 de 11**, sin marcar mal **ninguna de las 25** verdaderas. En aymara, ocho modelos quedan entre el azar y 17 de 30; por eso, en aymara, Cheqap dice **«no verificable»** (gris) en vez de inventar un veredicto.

## Cómo correrlo

Repositorio: https://github.com/jazidovandod-gif/cheqap

```bash
pip install -r requirements.txt
cp .env.example .env                 # claves del juez (ver abajo); no hace falta para reproducir las tablas
streamlit run app/streamlit_app.py   # pantalla de demo
python -m benchmark.run --lote es    # tabla del español (sale del cache, sin red)
python scripts/comparar_modelos_anli.py   # todas las corridas de aymara, sin red
pytest                               # 17 tests
```

Las respuestas de los modelos se guardan en `results/cache/` con el proveedor y el modelo dentro de la clave, así que **todas las tablas se reproducen sin red ni claves**. Con red, el juez se elige por variables de entorno (`.env.example`):

- `JUEZ_PROVEEDOR=openai` con `OPENAI_BASE_URL` de Groq y `JUEZ_MODELO=openai/gpt-oss-120b` (juez del español).
- `JUEZ_PROVEEDOR=adaption` con `JUEZ_MODELO=gemma-4-31b-it` (mejor resultado en aymara).
- `JUEZ_PROVEEDOR=gemini` con `JUEZ_MODELO=gemini-3.5-flash`.

Para regenerar los datos: `python -m consta.fuente data/fuente/fuente.pdf` (fragmentos de la ley), `python scripts/construir_es.py` (ítems en español, con cada cita comprobada contra el PDF) y `python -m benchmark.descargar_anli` (30 pares de AmericasNLI). Las corridas de aymara: `python -m benchmark.run --lote anli --anli-modo {directo,aymara,ejemplos,similares,traducido} --sufijo <nombre>`.

## Cómo decide

1. **Fuente.** La ley partida en 106 fragmentos, uno por artículo, sin cruzar páginas (`consta/fuente.py`).
2. **Búsqueda.** Para cada afirmación, los fragmentos que más se le parecen (`consta/buscar.py`).
3. **Revisor de reglas**, sin modelo (`consta/revisor_reglas.py`): números que no están en la fuente y «debe» / «puede» invertidos.
4. **Juez con cita textual** (`consta/revisor_juez.py`): un modelo da la etiqueta y copia la frase de la ley que la sostiene. La cita se busca normalizada en el PDF; si no está, «respaldada» baja a «no respaldada».
5. **Combinación** (`consta/combinar.py`): rojo si cualquiera ve contradicción; verde solo con cita válida.
6. **Aymara** (`consta/puente.py`, `consta/revisor_reglas_ay.py`): traducción de trabajo al español (la ley nunca se traduce), dos reglas propias del aymara y, al final, **abstención**: color gris con la traducción, las palabras que no reconoció y la opinión del juez solo como pista.

## Resultados en español

Juez `openai/gpt-oss-120b` en Groq. 12 ítems, 36 afirmaciones: 11 con un error sutil (modal, plazo, fecha, obligado, condición, número de artículo) y 25 verdaderas. Las etiquetas se subieron en el commit `ac84069`, antes de la primera corrida. Detalle en `results/tabla.md` y `results/detalle.jsonl`.

| columna | errores detectados | falsos positivos | exactitud (3 clases) |
|---|---|---|---|
| palabras compartidas (línea de base) | 0 / 11 | 0 / 25 | 25 / 36 |
| reglas | 4 / 11 | 0 / 25 | 29 / 36 |
| juez con cita textual | 10 / 11 | 0 / 25 | 35 / 36 |
| reglas + juez | 10 / 11 | 0 / 25 | 35 / 36 |

- La línea de base no detecta nada porque un error sutil comparte casi todas las palabras con la ley.
- El error que se escapa es `es-005`, una negación («no podrán realizar el corte»): el juez la dio por respaldada.
- Las reglas no suben la cifra: sus 4 aciertos (plazos, fechas de decretos, número de artículo) el juez ya los tenía. Su valor es que funcionan sin red ni modelo.

## Resultados en aymara

El equipo no tiene hablante de aymara, así que **no se inventaron ítems propios** (`data/benchmark/ay.jsonl` queda vacío). Se usó [AmericasNLI](https://github.com/nala-cub/AmericasNLI) (Ebrahimi et al., ACL 2022), con etiquetas de hablantes: **30 pares** de prueba (10 por clase) y las **713 filas restantes** del mismo split solo para derivar reglas y sacar ejemplos. Nunca se mezclan; las 57 filas que comparten premisa con un par de prueba también se excluyen de los ejemplos. El azar acierta 10 de 30.

**Punto de partida, cinco modelos con el prompt original** («verde falso» = dar por respaldada una afirmación que no lo es, el error más peligroso):

| modelo | exactitud | verdaderas reconocidas | verde falso |
|---|---|---|---|
| gpt-oss-120b (Groq) | 10 / 30 | 0 / 10 | 1 / 20 |
| qwen3.8-27b (Groq) | 9 / 30 | 1 / 10 | 0 / 20 |
| glm-5.2 (Adaption) | 13 / 30 | 1 / 10 | 0 / 20 |
| gemma-4-31b-it (Adaption) | 15 / 30 | 2 / 10 | 0 / 20 |
| deepseek-v4-flash (Adaption) | 16 / 30 | 3 / 10 | 1 / 20 |

`gemini-3.5-flash-lite` se corrió en 18 pares (9 / 18) por la cuota gratuita de Gemini; `qwen3.5-397b` en Adaption no se pudo medir (504 del servidor).

**Lo que se intentó para mejorar:**

| intento | efecto |
|---|---|
| Prompt que sabe aymara (modo `aymara`); el original decía que la fuente estaba en español | gpt-oss 10 → 15; gemma 15 → 16 |
| 4 ejemplos resueltos por etiqueta, al azar (modo `ejemplos`) | gemma 17; gpt-oss 15 |
| 10 ejemplos por etiqueta, con el banco limpio | gemma 17; qwen 14 |
| 9 ejemplos elegidos por raíces en común (modo `similares`) | gemma 17; **qwen 9 → 16**; glm 14 |
| Traducir primero y juzgar en español (modo `traducido`) | gemma 13: peor. El traductor deja la mayoría de las palabras sin reconocer |
| Voto entre los tres mejores; abstención por unanimidad | 15–17; con unanimidad habla en 11–18 pares y acierta 62–67 %, casi todo neutras |
| Segunda clave de Groq y razonamiento alto | sin medir: el límite diario de Groq es por organización |

**Reglas propias del aymara**, medidas en las 713 filas aparte antes de tocar el test (`scripts/medir_regla_ay.py`, `scripts/medir_factores_ay.py`):

- **Negación:** `jani / janiw…` en la afirmación y no en la fuente → contradicha. Precisión 82 %, atrapa el 35 % de las contradicciones. En el test: 3 de 10 contradicciones, 2 falsos positivos.
- **Raíces compartidas:** el aymara es aglutinante, así que se comparan los primeros 5 caracteres de cada palabra; con 60 % o más en común → respaldada. Precisión 70 %, cobertura 21 %. En el test: 4 disparos, 2 aciertos.

**Lectura honesta:**

- El techo es **17 de 30**, alcanzado por tres configuraciones distintas. Lo verdadero sigue reconociéndose 3 de cada 10 veces.
- Nadie da verdes falsos de forma notable (0 a 2 de 20): en aymara el sistema falla hacia el lado seguro, pero tampoco confirma lo cierto. Por eso el producto se abstiene.
- Un clasificador que siempre responda «no respaldada» acierta 10 de 30; buena parte de la subida viene de acertar neutras.
- Coincide con lo publicado: en el artículo de AmericasNLI ([Tabla 4](https://arxiv.org/abs/2104.08726)), XLM-R saca 36–37 % en aymara sin adaptación, 43,5–43,9 % con preentrenamiento continuo, 39,7 % traduciendo antes y 50,0 % entrenando con datos traducidos.
- Lo que haría falta y no cabe en seis horas: un traductor entrenado para aymara (NLLB-200 soporta `ayr_Latn`) o ajuste fino con datos en aymara, y una persona hablante que valide.
- Corrección: dos corridas que primero se describieron con 4 ejemplos por etiqueta usaron 10, por una variable de entorno que quedó activa. Se detectó contando los ejemplos en los prompts del cache; los archivos se renombraron (`*_gemma431bit10limpio_*`, `*_qwen10_*`). Ninguna cifra cambió.

## Estructura

- `consta/`: fuente, afirmaciones, búsqueda, puente, revisores (español y aymara), juez, combinación, cache y `pipeline.py` (punto de entrada de la pantalla).
- `benchmark/`: línea de base, corredor de columnas y modos, descarga de AmericasNLI.
- `app/` y `.streamlit/`: pantalla de demo y su tema.
- `data/fuente/`: la ley en PDF y sus fragmentos. `data/benchmark/`: ítems etiquetados; esquema en su README.
- `scripts/`: construcción de los ítems, medición de reglas, comparación de modelos, voto y diagnóstico.
- `results/`: tablas, detalle fila por fila y cache de respuestas.
- `docs/`: plan, guion del pitch y declaración de material previo.

## Límites

- Set pequeño: 12 ítems y 36 afirmaciones en español, sobre una sola ley y con un solo modelo como juez.
- Las negaciones en español todavía se escapan (`es-005`).
- El aymara solo se midió con AmericasNLI, donde premisa e hipótesis están en aymara. No se midió el flujo real del producto (ley en español, afirmación en aymara) porque no hay datos de terceros ni hablante en el equipo.
- Se probaron 8 modelos y 5 modos sobre los mismos 30 pares: cualquier «mejor configuración» elegida después de verlos es optimista. Los números más confiables del aymara son los de las reglas, medidos en 713 filas aparte.
- El corte en afirmaciones es por oración: una oración con dos hechos se juzga junta.
- La cabecera del compendio dice «5 de Febrero de 2013», pero la ley fue promulgada el 4 de diciembre de 2013; el benchmark no usa esa fecha.

## Equipo

Leonardo Durán Cuenca, Liz Mariel Caballero Salazar, Jazid Andrey Ovando Durán y Miguel Angel Vega Moreno. Material previo y de terceros en `docs/DECLARACION_PREVIA.md`.
