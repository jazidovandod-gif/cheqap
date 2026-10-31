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
4. Cambiar a aymara y pegar «Janiw manuñax utxkiti». Sale gris: «no verificable», con la traducción de trabajo y la pista del juez. Decirlo de frente: medimos, no alcanza, y el producto lo admite en vez de inventar.

## 2:10–2:40 · Evidencia

Tabla por lote (es / AmericasNLI aymara) y por columna (palabras / reglas / juez / juntos):

- Errores inyectados detectados (español, Ley 453): palabras compartidas 0 de 11; reglas 4 de 11; juez con cita textual 10 de 11.
- Afirmaciones verdaderas marcadas mal: 0 de 25.
- El error que se escapa: una negación («no podrán realizar el corte»).
- Aymara (AmericasNLI, 30 pares, etiquetas de terceros): el primer modelo dio 10 de 30, igual que el azar. Probamos 8 modelos, 5 formas de preguntar y 2 reglas sin modelo, con 3 proveedores; lo mejor llegó a 17 de 30 con tres configuraciones distintas, y sigue sin reconocer lo verdadero (3 de 10). Traducir primero fue peor: el traductor no conoce las palabras.
- Lo que sí funciona en aymara sin modelo: una regla de negación (jani / janiw) con 82 % de precisión y una de raíces compartidas con 70 %, las dos medidas en 713 frases aparte, antes de tocar el test.
- Por eso en aymara Cheqap no da verde ni rojo: dice «no verificable», muestra la traducción y cuántas palabras no entendió. Un verificador que inventa un veredicto es peor que uno que se calla.
- Modelo del español: gpt-oss-120b en Groq. Del aymara: gemma-4-31b-it en Adaption.

## 2:40–3:00 · Límites y siguiente paso

- Límite real: 12 ítems en español, una sola ley, un solo modelo; el aymara se mide solo con datos de terceros y no con la ley; las negaciones se escapan.
- Siguiente paso: no publicar una respuesta del asistente mientras una afirmación siga en rojo.

## Pregunta probable del jurado

"¿Cómo saben que el modelo no inventó la cita?" — La cita tiene que aparecer textual en el PDF. Si no aparece, el respaldo se anula. Está en `revisor_juez.py` y tiene test.
