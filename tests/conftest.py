from __future__ import annotations

import os
import sys
from pathlib import Path


# Forzar base de datos efímera para tests (evita conflictos con esquemas antiguos)
test_db = Path(__file__).resolve().parents[1] / "test.db"
# Resetear base de datos de pruebas para garantizar esquema limpio
try:
	if test_db.exists():
		test_db.unlink()
except Exception:
	pass
os.environ.setdefault("DATABASE_URL", f"sqlite:///{test_db}")

# Asegura que la raíz del repo esté en sys.path para poder importar el paquete `src`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


