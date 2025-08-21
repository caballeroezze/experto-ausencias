from __future__ import annotations

from src.dialogue.manager import DialogueManager
from src.persistence.seed import ensure_schema, seed_employees_synthetic
from src.session_store import clear_store


def setup_module(module=None):  # noqa: D401
	"""Asegura esquema y datos sintéticos de empleados."""
	ensure_schema()
	seed_employees_synthetic(200)  # crea 1000..1199
	clear_store()


def test_legajo_valido_1111_validado_y_guardado():
	mgr = DialogueManager()
	res = mgr.process_message("u_t1", "1111")
	assert "verificado" in (res.get("reply_text") or "")
	# Guardado en facts y sesión
	sess = mgr.sessions.get("u_t1", {})
	assert sess.get("legajo_validado") == "1111"
	# Luego no debe volver a pedir legajo
	res2 = mgr.process_message("u_t1", "quiero avisar")
	assert "legajo" not in (res2.get("ask") or [])


def test_legajo_invalido_9999_mensaje_error():
	mgr = DialogueManager()
	res = mgr.process_message("u_t2", "9999")
	assert "inválido" in (res.get("reply_text") or "")


def test_flujo_mixto_legajo_luego_campos():
	mgr = DialogueManager()
	# Primero valida legajo
	res1 = mgr.process_message("u_t3", "1111")
	assert "verificado" in (res1.get("reply_text") or "")
	# Luego pasa motivo + fecha + dias
	res2 = mgr.process_message("u_t3", "enfermedad mañana 3")
	assert isinstance(res2.get("reply_text"), str)
	# No debe confundir legajo con días en los mensajes
	assert "Días: 1111" not in res2.get("reply_text")


