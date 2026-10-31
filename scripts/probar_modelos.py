"""Prueba qué modelos Gemini responden ahora (una llamada mínima cada uno).

    python scripts/probar_modelos.py gemini-3.8-flash gemini-3.7-flash ...
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import consta  # noqa: F401  (carga .env)
from google import genai

from google.genai import types

cliente = genai.Client(api_key=os.environ["GEMINI_API_KEY"], http_options=types.HttpOptions(timeout=25000, retry_options=types.HttpRetryOptions(attempts=1)))
for modelo in sys.argv[1:]:
    t = time.time()
    try:
        r = cliente.models.generate_content(model=modelo, contents='Responde solo {"ok": true}')
        print(f"OK    {modelo:32} {time.time() - t:5.1f}s  {(r.text or '').strip()[:30]!r}")
    except Exception as e:  # noqa: BLE001
        print(f"FALLA {modelo:32} {time.time() - t:5.1f}s  {str(e)[:90]!r}")
