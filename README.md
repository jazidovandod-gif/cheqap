# Consta

Verificador de afirmaciones para el Track 1 del [Grok Bot Santa Cruz Hackathon](https://luma.com/3f65kl5u) (Cursor Bolivia, 31 de octubre de 2026).

Consta toma la respuesta de un chatbot, la parte en afirmaciones y las contrasta con un solo PDF. Cada afirmación queda **respaldada**, **no respaldada** o **contradicha**. Si el modelo cita una frase que no está en el PDF, esa cita no cuenta.

## Qué se mide

Un benchmark reproducible, en español y en aymara, contra el mismo documento en español:

- cerca de 20 respuestas en español, cada una con un error sutil (fecha, monto, «puede» / «debe», obligado, condición o artículo);
- cerca de 8 respuestas en aymara, confirmadas por una persona que habla la lengua;
- un control con pares ya publicados de [AmericasNLI](https://github.com/abteen/americasnli) (corte `aym`).

La tabla compara cuatro lecturas: palabras compartidas, un revisor de números y modales, un juez con cita textual, y los dos revisores juntos.

## De qué parte

- [Ragas](https://www.cursorbolivia.com/sprint/recursos/ragas), métricas de respaldo documental.
- [AmericasNLI](https://aclanthology.org/2022.acl-long.435), inferencia en aymara con etiquetas de hablantes.
- [ALCE](https://github.com/princeton-nlp/ALCE), calidad de las citas.
- [FActScore](https://github.com/shmsw25/FActScore) y [MiniCheck](https://github.com/Liyan06/MiniCheck), partir la respuesta antes de juzgarla.
- [RAGTruth](https://github.com/ParticleMedia/RAGTruth), marcar el tramo exacto del error.

El aporte de este sprint es el banco sobre una fuente boliviana, la regla de cita textual y la fila en aymara.
