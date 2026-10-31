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
4. Pegar una afirmación en aymara tomada de AmericasNLI y mostrar que el verificador no la resuelve bien. Decirlo de frente: es el resultado, y es la razón por la que el benchmark existe.

## 2:10–2:40 · Evidencia

Tabla por lote (es / AmericasNLI aymara) y por columna (palabras / reglas / juez / juntos):

- Errores inyectados detectados (español, Ley 453): palabras compartidas 0 de 11; reglas 4 de 11; juez con cita textual 10 de 11.
- Afirmaciones verdaderas marcadas mal: 0 de 25.
- El error que se escapa: una negación («no podrán realizar el corte»).
- Aymara (AmericasNLI, 30 pares, etiquetas de terceros): 10 de 30 aciertos, igual que el azar. Con este modelo el verificador no funciona en aymara. Eso es lo que mide el benchmark.
- Modelo: gpt-oss-120b en Groq.

## 2:40–3:00 · Límites y siguiente paso

- Límite real: 12 ítems en español, una sola ley, un solo modelo; el aymara se mide solo con datos de terceros y no con la ley; las negaciones se escapan.
- Siguiente paso: no publicar una respuesta del asistente mientras una afirmación siga en rojo.

## Pregunta probable del jurado

"¿Cómo saben que el modelo no inventó la cita?" — La cita tiene que aparecer textual en el PDF. Si no aparece, el respaldo se anula. Está en `revisor_juez.py` y tiene test.
