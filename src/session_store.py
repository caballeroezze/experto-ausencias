from __future__ import annotations

from typing import Dict, Optional


_legajo_by_user: Dict[str, str] = {}


def set_legajo(user_id: str, legajo: str) -> None:
	"""Guarda el legajo preferido para un usuario/chat en memoria."""
	_legajo_by_user[str(user_id)] = str(legajo)


def get_legajo(user_id: str) -> Optional[str]:
	"""Obtiene el legajo guardado para un usuario/chat si existe."""
	return _legajo_by_user.get(str(user_id))


def clear_store() -> None:
	"""Limpia el store en memoria (útil para tests)."""
	_legajo_by_user.clear()


