from datetime import date, timedelta

from src.persistence.seed import ensure_schema, seed_employees
from src.persistence.dao import create_aviso, update_certificado, historial_empleado, session_scope
from src.persistence.models import Aviso



def test_seed_runs():
	ensure_schema()
	seed_employees()
	assert True


def test_crear_aviso_nominal_y_historial():
	ensure_schema()
	# limpiar avisos previos del legajo
	with session_scope() as s:
		s.query(Aviso).filter(Aviso.legajo == "L1000").delete()
	fi = date(2025, 8, 17)
	facts = {
		"legajo": "L1000",
		"motivo": "enfermedad_inculpable",
		"fecha_inicio": fi.isoformat(),
		"duracion_estimdays": 2,
		"documento_tipo": "certificado_medico",
		"estado_certificado": "pendiente",
		"estado_aviso": "incompleto",
	}
	res = create_aviso(facts)
	assert "id_aviso" in res
	hist = historial_empleado("L1000", limit=5)
	assert any(h["id_aviso"] == res["id_aviso"] for h in hist)


def test_detectar_solape():
	ensure_schema()
	with session_scope() as s:
		s.query(Aviso).filter(Aviso.legajo == "L1001").delete()
	fi = date(2025, 8, 20)
	base = {
		"legajo": "L1001",
		"motivo": "matrimonio",
		"fecha_inicio": fi.isoformat(),
		"duracion_estimdays": 3,
		"estado_aviso": "completo",
	}
	first = create_aviso(base)
	assert "id_aviso" in first
	# Intentar crear otro que solape rango
	try:
		create_aviso(base | {"duracion_estimdays": 5})
		assert False, "Debió fallar por solape"
	except ValueError:
		assert True


def test_adjuntar_certificado_y_cambiar_estado():
	ensure_schema()
	with session_scope() as s:
		s.query(Aviso).filter(Aviso.legajo == "L1002").delete()
	fi = date(2025, 8, 25)
	facts = {
		"legajo": "L1002",
		"motivo": "enfermedad_inculpable",
		"fecha_inicio": fi.isoformat(),
		"duracion_estimdays": 1,
		"documento_tipo": "certificado_medico",
		"estado_aviso": "incompleto",
	}
	created = create_aviso(facts)
	ida = created["id_aviso"]
	upd = update_certificado(ida, {
		"archivo_nombre": "cert.pdf",
		"documento_legible": True,
		"fecha_recepcion": (fi + timedelta(days=1)).isoformat(),
		"plazo_cert_horas": 72,
	})
	assert upd["estado_certificado"] == "validado"
	assert upd["estado_aviso"] == "completo"
