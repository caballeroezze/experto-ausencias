from datetime import date, timedelta

from src.engine.kb_loader import load_knowledge_base
from src.engine.inference import forward_chain, backward_chain


def _base_facts_ok():
	return {
		"legajo": "1234",
		"empleado_nombre": "Juan Perez",
		"motivo": "enfermedad_inculpable",
		"fecha_inicio": date.today().isoformat(),
		"duracion_estimdays": 2,
		"area": "producción",
		"documento_legible": True,
	}


def test_identidad_legajo_inexistente():
	# Falta empleado_nombre → pendiente_validacion + RRHH
	load_knowledge_base()
	facts = {
		"legajo": "9999",
		"motivo": "enfermedad_inculpable",
		"fecha_inicio": date.today().isoformat(),
		"duracion_estimdays": 1,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["estado_aviso"] == "pendiente_validacion"
	assert "rrhh" in vars_dict.get("notificar_a", [])


def test_identidad_legajo_valido():
	load_knowledge_base()
	facts = _base_facts_ok()
	# Con empleado_nombre presente no debe quedar pendiente_validacion
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict.get("estado_aviso") != "pendiente_validacion"


def test_certificados_por_motivo_mapping():
	load_knowledge_base()
	# Enfermedad inculpable → certificado_medico
	facts = _base_facts_ok() | {"adjunto_certificado": "cert.pdf"}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["documento_tipo"] == "certificado_medico"
	assert vars_dict["estado_certificado"] == "validado"

	# Fallecimiento → acta_defuncion
	facts = _base_facts_ok() | {"motivo": "fallecimiento", "adjunto_certificado": "acta.pdf"}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["documento_tipo"] == "acta_defuncion"


def test_estado_final_aviso_enfermedad_inculpable():
	# Certificado validado → completo
	load_knowledge_base()
	facts = _base_facts_ok() | {
		"adjunto_certificado": "cert.pdf",
		"documento_legible": True,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["estado_aviso"] == "completo"

	# Certificado pendiente → incompleto
	facts = _base_facts_ok() | {
		"adjunto_certificado": None,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["estado_aviso"] == "incompleto"


def test_plazos_termino_y_fuera_de_termino():
	load_knowledge_base()
	inicio = date.today() - timedelta(days=5)
	# Dentro de término (48h)
	facts = _base_facts_ok() | {
		"adjunto_certificado": "cert.pdf",
		"fecha_inicio": inicio.isoformat(),
		"fecha_recepcion": (inicio + timedelta(days=1)).isoformat(),
		"plazo_cert_horas": 48,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict.get("fuera_de_termino", False) is False

	# Fuera de término (72h de ejemplo P-10)
	facts = _base_facts_ok() | {
		"adjunto_certificado": "cert.pdf",
		"fecha_inicio": inicio.isoformat(),
		"fecha_recepcion": (inicio + timedelta(days=4)).isoformat(),
		"plazo_cert_horas": 72,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["fuera_de_termino"] is True


def test_medico_laboral_notificacion_enfermedad_inculpable():
	load_knowledge_base()
	facts = _base_facts_ok() | {
		"adjunto_certificado": "cert.pdf",
		"politica_medico_laboral": True,
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	notif = vars_dict.get("notificar_a", [])
	assert "medico_laboral" in notif
	assert "rrhh" in notif


def test_notificaciones_fallecimiento_supervisor():
	load_knowledge_base()
	facts = _base_facts_ok() | {
		"motivo": "fallecimiento",
		"adjunto_certificado": "acta.pdf",
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	notif = vars_dict.get("notificar_a", [])
	assert "supervisor" in notif and "rrhh" in notif


def test_estado_art_incompleto():
	load_knowledge_base()
	facts = _base_facts_ok() | {
		"motivo": "art",
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["estado_aviso"] == "incompleto"
	assert vars_dict["estado_certificado"] == "no_requerido"


def test_duplicado_solapado():
	load_knowledge_base()
	inicio = date.today()
	facts = _base_facts_ok() | {
		"fecha_inicio": inicio.isoformat(),
		"duracion_estimdays": 3,
		"avisos_abiertos": [
			{"legajo": "1234", "inicio": (inicio - timedelta(days=1)).isoformat(), "fin": (inicio + timedelta(days=1)).isoformat()}
		],
	}
	res = forward_chain(facts)
	vars_dict = res["facts"]
	assert vars_dict["estado_aviso"] == "rechazado"
	assert "rrhh" in vars_dict.get("notificar_a", [])


def test_backward_chain_slots_incompletos():
	load_knowledge_base()
	facts = {
		"legajo": "1234",
		"motivo": "enfermedad_inculpable",
	}
	res = backward_chain("crear_aviso", facts)
	assert res["status"] == "need_info"
	# Debe pedir fecha_inicio y duracion_estimdays
	assert set(res["ask"]) >= {"fecha_inicio", "duracion_estimdays"}


def test_backward_enfermedad_familiar_pide_vinculo():
	load_knowledge_base()
	facts = {
		"legajo": "1234",
		"motivo": "enfermedad_familiar",
	}
	res = backward_chain("crear_aviso", facts)
	assert res["status"] == "need_info"
	assert "vinculo_familiar" in res["ask"]
