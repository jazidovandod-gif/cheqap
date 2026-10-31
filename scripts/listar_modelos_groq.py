"""Lista los modelos del proveedor OpenAI-compatible configurado en .env (Groq).

    python scripts/listar_modelos_groq.py
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import consta  # noqa: F401  (carga .env)
from openai import OpenAI

c = OpenAI()
ids = sorted(m.id for m in c.models.list().data)
print(f"{len(ids)} modelos. Elegido: {os.environ['JUEZ_MODELO']} -> {'EXISTE' if os.environ['JUEZ_MODELO'] in ids else 'NO EXISTE'}")
for i in ids:
    if not any(x in i for x in ("whisper", "tts", "orpheus", "guard")):
        print(" ", i)
