# Esquema del benchmark

Un ítem por línea (JSONL). Las etiquetas se escriben antes de correr el verificador y no se cambian después.

## `es.jsonl` y `ay.jsonl`

```json
{
  "id": "es-001",
  "lengua": "es",
  "respuesta": "Texto completo de la respuesta del asistente, con varias frases.",
  "afirmaciones": [
    {"texto": "El proveedor debe responder el reclamo en 15 días hábiles.", "esperada": "contradicha", "pagina": 7, "frase_fuente": "...responder en un plazo máximo de treinta días hábiles...", "tipo_error": "monto_o_plazo", "tramo_error": "15 días hábiles"},
    {"texto": "La ley protege a usuarias y usuarios de servicios.", "esperada": "respaldada", "pagina": 2, "frase_fuente": "..."}
  ],
  "confirmado_por": null
}
```

- `lengua`: `es` o `ay`.
- `esperada`: `respaldada`, `no_respaldada` o `contradicha`.
- `tipo_error`: `fecha`, `monto_o_plazo`, `modal` (puede/debe), `obligado`, `condicion`, `articulo_inexistente`. Solo en afirmaciones no respaldadas o contradichas.
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
