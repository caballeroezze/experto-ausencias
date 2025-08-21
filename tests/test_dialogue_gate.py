from __future__ import annotations

from src.dialogue.manager import DialogueManager
from src.session_store import clear_store
from src.persistence.seed import ensure_schema, seed_employees_synthetic


def test_dialogue_gate_without_legajo_then_with_command():
	clear_store()
	ensure_schema()
	seed_employees_synthetic(200)
	mgr = DialogueManager()
	# Sin legajo → debe pedir legajo
	res1 = mgr.process_message("u1", "quiero avisar por enfermedad")
	assert "legajo" in (res1.get("ask") or [])
	# Simular comando /id
	res2 = mgr.process_message("u1", "/id 1001")
	# Primero valida y confirma
	assert "verificado" in (res2.get("reply_text") or "")
	# Ahora puede avanzar con slot-filling
	res3 = mgr.process_message("u1", "enfermedad")
	assert isinstance(res3.get("reply_text"), str)


def test_dialogue_legajo_text_then_continue():
	clear_store()
	ensure_schema()
	seed_employees_synthetic(200)
	mgr = DialogueManager()
	res1 = mgr.process_message("u2", "legajo 1010")
	assert "verificado" in (res1.get("reply_text") or "")
	res2 = mgr.process_message("u2", "quiero avisar")
	assert isinstance(res2.get("reply_text"), str)


