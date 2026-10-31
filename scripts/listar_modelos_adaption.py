"""Lista los modelos alojados que permite tu clave de Adaption.

    python scripts/listar_modelos_adaption.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.stdout.reconfigure(encoding="utf-8")

import consta  # noqa: F401  (carga .env)
from adaption import Adaption

cliente = Adaption()
for m in cliente.models.list(type="hosted").data:
    print(m.id)
