# Pitch — 3 minutos + 1 pregunta

Completar los números con `results/tabla.md` antes de las 15:15.

## 0:00–0:30 · El problema

Un asistente contesta en español sobre una ley boliviana. Suena seguro. Cambió una fecha, un monto, o puso «debe» donde la ley dice «puede». Si la persona pregunta en aymara, nadie revisa nada.

## 0:30–1:00 · De qué partimos

Métricas de respaldo documental (Ragas) y un chequeo por palabras compartidas. Ese chequeo da por buena una frase si se parece al párrafo. El error sutil se parece al párrafo.

## 1:00–2:10 · Demo

1. Pegar una respuesta con una mentira sutil.
2. La frase falsa queda en rojo. Al lado, el párrafo real del PDF, la página y la palabra que cambió.
3. Una frase verdadera queda en verde: no pinta todo de rojo.
4. Pegar una afirmación en aymara tomada de AmericasNLI. Mostrar qué pasa, sin prometer más de lo medido.

## 2:10–2:40 · Evidencia

Tabla por lote (es / AmericasNLI aymara) y por columna (palabras / reglas / juez / juntos):

- Errores inyectados detectados: __ de __ (es). Aymara: __ de 30 pares de AmericasNLI (control con etiquetas de terceros; no tenemos hablante propio).
- Afirmaciones verdaderas marcadas mal: __.
- Errores que se le escaparon a la línea de base y los dos revisores atraparon: __.

## 2:40–3:00 · Límites y siguiente paso

- Límite real: __ (el aymara se mide solo con datos de terceros, no con la ley; y el tipo de error que todavía se escapa).
- Siguiente paso: no publicar una respuesta del asistente mientras una afirmación siga en rojo.

## Pregunta probable del jurado

"¿Cómo saben que el modelo no inventó la cita?" — La cita tiene que aparecer textual en el PDF. Si no aparece, el respaldo se anula. Está en `revisor_juez.py` y tiene test.
