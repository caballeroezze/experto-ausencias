from src.dialogue.manager import DialogueManager
from src.session_store import set_legajo, clear_store


def test_p16_crear_aviso_slots_incompletos():
	mgr = DialogueManager()
	out = mgr.process_message("s1", "quiero avisar por enfermedad")
	assert isinstance(out["reply_text"], str)
	assert out.get("ask") is not None


def test_p17_adjuntar_certificado_luego():
	mgr = DialogueManager()
	# crear aviso incompleto
	s = "legajo: L1005\nmotivo: enf\nfecha_inicio: 17/08/2025\nduracion_estimdays: 2"
	out = mgr.process_message("s2", s)
	# ahora adjuntar
	out2 = mgr.process_message("s2", "adjunto certificado cert.pdf")
	assert isinstance(out2["reply_text"], str)


def test_p18_cancelar_aviso_flow_minimo():
	mgr = DialogueManager()
	out = mgr.process_message("s3", "cancelar aviso")
	assert isinstance(out["reply_text"], str)


def test_p19_extender_aviso_flow_minimo():
	mgr = DialogueManager()
	out = mgr.process_message("s4", "quiero cambiar dias")
	assert isinstance(out["reply_text"], str)


def test_p20_consultar_estado_minimo():
	mgr = DialogueManager()
	out = mgr.process_message("s5", "consultar estado del aviso")
	assert isinstance(out["reply_text"], str)


def test_ui_matrimonio_mananamecaso_then_confirm():
	# Usuario: "mañana me caso" → set motivo=matrimonio, fecha=mañana; falta días.
	mgr = DialogueManager()
	out1 = mgr.process_message("ux1", "mañana me caso")
	assert isinstance(out1["reply_text"], str)
	# Pide días; usuario responde 3 y luego confirma
	out2 = mgr.process_message("ux1", "3")
	assert isinstance(out2["reply_text"], str)
	# Debería estar pidiendo confirmación o ya crear con confirmación
	out3 = mgr.process_message("ux1", "Confirmar")
	assert isinstance(out3["reply_text"], str)


def test_ui_teclados_simulados_matrimonio_hoy_3_confirmar():
	mgr = DialogueManager()
	# Inicia flujo crear_aviso
	mgr.process_message("ux2", "quiero avisar")
	# Motivo por "botón" simulado
	out_m = mgr.process_message("ux2", "matrimonio")
	assert isinstance(out_m["reply_text"], str)
	# Fecha "Hoy"
	out_f = mgr.process_message("ux2", "Hoy")
	assert isinstance(out_f["reply_text"], str)
	# Días "3"
	out_d = mgr.process_message("ux2", "3")
	assert isinstance(out_d["reply_text"], str)
	# Confirmar
	out_c = mgr.process_message("ux2", "Confirmar")
	assert isinstance(out_c["reply_text"], str)


def test_store_legajo_precarga_en_manager():
	clear_store()
	set_legajo("chat123", "L1001")
	mgr = DialogueManager()
	# No enviamos legajo en el texto; el manager debería precargarlo del store
	out = mgr.process_message("chat123", "quiero avisar")
	assert isinstance(out["reply_text"], str)