# Esquema del benchmark

Un ítem por línea (JSONL). Las etiquetas se escriben antes de correr el verificador y no se cambian después.

## `es.jsonl` y `ay.jsonl`

```json
{
  "id": "es-001",
  "lengua": "es",
  "respuesta": "Texto completo de la respuesta del asistente, con varias frases.",
  "afirmaciones": [
    {"texto": "Las entidades de regulación deberán adecuar su normativa en un plazo de noventa (90) días.", "esperada": "contradicha", "pagina": 14, "frase_fuente": "en un plazo de sesenta (60) días de aprobada la reglamentación", "tipo_error": "plazo", "tramo_error": "noventa (90) días"},
    {"texto": "La ley protege a usuarias y usuarios de servicios.", "esperada": "respaldada", "pagina": 2, "frase_fuente": "..."}
  ],
  "confirmado_por": null
}
```

- `lengua`: `es` o `ay`.
- `esperada`: `respaldada`, `no_respaldada` o `contradicha`.
- `tipo_error`: `fecha`, `plazo`, `modal` (puede/debe, permite/prohíbe), `obligado`, `condicion`, `articulo`. Solo en afirmaciones no respaldadas o contradichas. La Ley 453 casi no trae montos ni plazos en días, por eso pesan más los modales, el obligado y las fechas de normas citadas.

`es.jsonl` no se edita a mano: se genera con `python scripts/construir_es.py`, que comprueba cada `frase_fuente` contra el PDF y calcula la página. `ay.jsonl` se escribe con la persona hablante.
- `tramo_error`: las palabras exactas que cambiaron. Permite medir si el verificador señaló el tramo correcto.
- `frase_fuente`: la frase real del PDF, copiada textual.
- `confirmado_por`: obligatorio en `ay`. Nombre de la persona hablante que revisó el texto. Sin este campo el ítem no entra en la tabla.

Cada ítem tiene varias afirmaciones verdaderas y **una** con error.

## `americasnli_aym.jsonl`

Control externo. No se busca en el PDF: `premise` es la fuente y `hypothesis` la afirmación.

```json
{"id": "anli-001", "premise": "...", "hypothesis": "...", "label": "contradiction"}
```

Mapa de etiquetas: `entailment` → `respaldada`, `neutral` → `no_respaldada`, `contradiction` → `contradicha`.

Fuente: AmericasNLI, split `dev`, filas con `language == aym`. Descargar con `python -m benchmark.descargar_anli`.
