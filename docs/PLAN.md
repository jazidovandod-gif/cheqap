# Plan de construcción — Consta

Entrega: sábado 31 de octubre de 2026, 16:00, portal de equipos de Cursor Bolivia. Pitch a las 17:00, 3 minutos más una pregunta.

## 1. Qué se entrega

Un verificador de afirmaciones contra un solo PDF, con una pantalla de demo y un benchmark reproducible en español y aymara. Cuatro lecturas sobre el mismo set: palabras compartidas (línea de base), revisor de reglas, juez con cita textual, y los dos revisores juntos.

Fuera de alcance hoy: varios documentos, chat propio, ranking de modelos, prompt injection, exportación a Promptfoo (solo si sobra tiempo después de las 15:00).

## 2. Stack

- Python 3.11+ (hay 3.13 en la máquina).
- `pypdf` para extraer texto por página.
- `streamlit` para la pantalla. Una sola página, sin frontend aparte.
- Juez: un solo modelo vía API, detrás de `consta/revisor_juez.py`. Proveedor configurable por `.env` (`JUEZ_PROVEEDOR=gemini|openai`). Las respuestas del juez se guardan en `results/cache/` para que el benchmark se pueda volver a correr sin red.
- Sin embeddings, sin vector DB, sin fine-tuning.

## 3. Estructura

```
consta/                 paquete con la lógica
  fuente.py             PDF -> párrafos con página
  claims.py             respuesta -> afirmaciones cortas
  puente.py             afirmación en aymara -> español de trabajo (conserva original)
  buscar.py             afirmación -> top-3 párrafos por palabras ponderadas
  revisor_reglas.py     números, montos, días, puede/debe -> contradicha o sin opinión
  revisor_juez.py       modelo -> etiqueta + cita; cita validada textual en el PDF
  combinar.py           regla fija -> verde / ámbar / rojo
  cache.py              cache en disco de llamadas al juez
app/streamlit_app.py    pantalla de demo
benchmark/
  run.py                corre las 4 columnas sobre los 3 lotes, imprime tabla, escribe results/
  baseline.py           línea de base por palabras compartidas
data/
  fuente/               PDF original + fuente.json extraído
  benchmark/es.jsonl    ~20 ítems en español
  benchmark/ay.jsonl    ~8 ítems en aymara, con quien confirmó
  benchmark/americasnli_aym.jsonl   30 pares del corte aym (control)
results/                tablas y cache; se versiona el resultado final
tests/                  pruebas de la cita textual y del revisor de reglas
docs/                   este plan, pitch, declaración previa
```

Esquema de cada ítem en `data/benchmark/README.md`.

## 4. Reglas que no se negocian

1. Las etiquetas del benchmark se escriben antes de correr el verificador. El commit con los `.jsonl` etiquetados va antes del commit con `results/`.
2. Una cita solo cuenta si aparece textual en `fuente.json` tras normalizar espacios, mayúsculas y tildes. Si no, la afirmación baja a `no_respaldada`.
3. Un ítem en aymara sin `confirmado_por` no entra en la tabla.
4. El número que se dice en el pitch es el que imprime `benchmark/run.py`, no una meta.
5. Nada de claves en el repo. `.env.example` sin valores.

## 5. Reloj y reparto

Cuatro personas. Cada una tiene un módulo propio y una franja fija.

| Hora | A: Fuente y datos | B: Núcleo | C: Benchmark | D: Pantalla y pitch |
|---|---|---|---|---|
| 11:15–12:00 | PDF elegido, `fuente.py`, `fuente.json` con páginas. 8 ítems `es` escritos y etiquetados | `claims.py`, `buscar.py`, `revisor_reglas.py` con sus tests | `baseline.py`, `run.py` leyendo `es.jsonl` e imprimiendo tabla aunque las columnas estén vacías | `streamlit_app.py` pegando texto y pintando con etiquetas falsas. Busca hablante de aymara en la sala |
| 12:00–12:30 | 4 ítems `ay` con hablante, `confirmado_por` | `revisor_juez.py` con cache y validación de cita | `run.py` corre baseline + reglas sobre los 8 | Pantalla conectada a `combinar.py` con 3 casos reales |
| 13:30–14:30 | Completar hacia 20 `es` y 8 `ay`. Bajar 30 filas `aym` de AmericasNLI | `combinar.py`, `puente.py`. Corregir citas que no existan | `run.py` corre las 4 columnas en los 3 lotes | Grabar demo de respaldo (60–90 s) |
| 14:30–15:15 | Revisión cruzada: cada ítem lo lee otra persona | Arreglos del juez solo si rompen el flujo | `results/tabla.md` final, commit | `docs/PITCH.md` cerrado con los números reales |
| 15:15–16:00 | `docs/DECLARACION_PREVIA.md`, README final | Congelar. Nada nuevo | Verificar que `python -m benchmark.run` reproduce desde cache | Subir al portal: identificación, repo, evidencia, video. Ensayo x2 |

Si a las 14:30 el juez no responde, la tabla sale con baseline + reglas y se dice así.

## 6. Qué entregar al portal

- Identificación: equipo, integrantes, título, Track 1, resumen de hasta 120 palabras.
- Material técnico: este repo. README con `pip install -r requirements.txt`, `python -m benchmark.run`, `streamlit run app/streamlit_app.py`.
- Contribución y evidencia: `docs/DECLARACION_PREVIA.md`, `results/tabla.md`, origen del PDF y de AmericasNLI, sección de límites.
- Pitch: `docs/PITCH.md`, video de respaldo.

## 7. Recomendaciones según la rúbrica

Estos son los cambios que subirían la nota frente a la versión original de la idea.

**Contribución propia (30).** El riesgo es que el jurado vea un "evaluador de respuestas" igual al ejemplo del sprint. Lo que lo separa es la comparación de cuatro columnas y la fila en aymara. Por eso: cortar AmericasNLI a 30 filas como control (no es el proyecto, es el contraste), y dejar Promptfoo fuera salvo tiempo sobrante. Declarar en `DECLARACION_PREVIA.md` que antes de las 09:00 solo existían la idea y este plan.

**Calidad técnica y funcionamiento (25).** La demo tiene que correr sin red. Por eso `cache.py` es obligatorio desde el inicio, no un extra: cada llamada al juez se guarda por hash de (afirmación, párrafos). El `revisor_reglas.py` es determinista y lleva tests. Si el juez falla, la pantalla sigue pintando con reglas y lo dice.

**Evidencia y pruebas (20).** Dos commits separados: primero datos etiquetados, después resultados. Reportar falsos positivos, no solo recall. Sección "Límites" en el README con al menos tres puntos reales (tamaño del set, aymara con pocos ítems, dependencia del corte en afirmaciones). Un resultado bajo en aymara se reporta tal cual.

**Relevancia e impacto (15).** Una frase de usuario en el README y en el pitch: una persona que pregunta en aymara sobre una ley o un reglamento que solo existe en español. Fuente local: Ley 453 o reglamento UTEPSA.

**Claridad (10).** Pitch con el corte de tiempos del sprint. Un caso rojo, la tabla, un límite. Sin arquitectura.

## 8. Qué cambiaría de la idea original

- El benchmark en aymara con frases propias es el punto débil si no hay hablante en la mesa. Por eso AmericasNLI entra como control desde el diseño, y los 8 ítems propios se hacen con la persona que se encuentre; si son 4, son 4.
- La línea de base por palabras es necesaria para el tramo "de qué partieron", pero sola no alcanza para contribución. El revisor de reglas es barato, determinista y atrapa el 80% de los errores inyectados; es la columna que hace visible el aporte.
- La cita textual validada es la regla que más confianza le da al jurado y cuesta 10 líneas. Va primero, antes de afinar el prompt del juez.
