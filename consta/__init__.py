"""Consta: verifica afirmaciones de un chatbot contra un solo PDF.

Flujo: fuente -> claims -> (puente si aymara) -> buscar -> revisor_reglas + revisor_juez -> combinar.
"""

from dotenv import load_dotenv

# Lee .env (clave del juez). utf-8-sig tolera el BOM que algunos editores de Windows añaden.
load_dotenv(encoding="utf-8-sig")

ETIQUETAS = ("respaldada", "no_respaldada", "contradicha")
