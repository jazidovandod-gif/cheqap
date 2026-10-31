"""Consta: verifica afirmaciones de un chatbot contra un solo PDF.

Flujo: fuente -> claims -> (puente si aymara) -> buscar -> revisor_reglas + revisor_juez -> combinar.
"""

ETIQUETAS = ("respaldada", "no_respaldada", "contradicha")
