"""Consta: verifica afirmaciones de un chatbot contra un solo PDF.

Flujo: fuente -> claims -> (puente si aymara) -> buscar -> revisor_reglas + revisor_juez -> combinar.
"""

from dotenv import load_dotenv

load_dotenv()  # lee .env (clave del juez) para el benchmark y la pantalla

ETIQUETAS = ("respaldada", "no_respaldada", "contradicha")
