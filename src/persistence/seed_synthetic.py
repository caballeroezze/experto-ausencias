from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Iterable

try:
	from faker import Faker
except Exception:  # pragma: no cover
	Faker = None  # type: ignore

from .models import Employee, Aviso, Certificado, Notificacion
from .dao import session_scope
from .seed import ensure_schema


_AREAS = ["producción", "logística", "calidad", "rrhh", "mantenimiento"]
_TURNOS = ["mañana", "tarde", "noche"]


def _ensure_faker() -> "Faker":
	if Faker is None:
		raise RuntimeError("Faker no está instalado. Agregar 'Faker' a requirements.txt")
	return Faker("es_AR")


def seed_employees_synthetic(n: int = 200) -> int:
	"""Crea empleados sintéticos 1000..1199 con datos realistas.

	Idempotente: si ya hay >=100 empleados, no hace nada. Usa legajo como PK (char(4)).
	"""
	ensure_schema()
	fake = _ensure_faker()
	created = 0
	with session_scope() as s:
		count = s.query(Employee).count()
		if count >= 100:
			return 0
		existing = {row[0] for row in s.query(Employee.legajo).all()}
		start = 1000
		for i in range(min(n, 200)):
			leg = str(start + i)
			if leg in existing:
				continue
			emp = Employee(
				legajo=leg,
				nombre=fake.name(),
				area=random.choice(_AREAS),
				puesto=fake.job(),
				fecha_ingreso=fake.date_between(start_date="-10y", end_date="-1d"),
				turno=random.choice(_TURNOS),
				activo=True,
			)
			s.add(emp)
			created += 1
	return created


def _pick_motivo_weighted() -> str:
	# Distribución: 50% enf inculpable, 15% familiar, 10% (matr/nac/pat), 10% art, 15% gremial
	r = random.random()
	if r < 0.50:
		return "enfermedad_inculpable"
	if r < 0.65:
		return "enfermedad_familiar"
	if r < 0.75:
		return random.choice(["matrimonio", "nacimiento", "paternidad"])
	if r < 0.85:
		return "art"
	return "permiso_gremial"


_DOC_MAP = {
	"enfermedad_inculpable": "certificado_medico",
	"enfermedad_familiar": "certificado_medico",
	"fallecimiento": "acta_defuncion",
	"matrimonio": "acta_matrimonio",
	"nacimiento": "acta_nacimiento",
	"paternidad": "acta_nacimiento",
	"permiso_gremial": "nota_gremial",
	"art": None,
}


def seed_absences_synthetic(m: int = 150) -> int:
	"""Crea avisos sintéticos y, si corresponde, certificados y notificaciones.

	- Usa create_aviso/update_certificado cuando aplica para respetar reglas
	- Idempotente: id_aviso es único, solapes son evitados por DAO (se saltean)
	"""
	ensure_schema()
	fake = _ensure_faker()
	created = 0
	with session_scope() as s:
		legajos = [row[0] for row in s.query(Employee.legajo).all()]
		if not legajos:
			return 0

	for _ in range(m):
		leg = random.choice(legajos)
		motivo = _pick_motivo_weighted()
		# fecha inicio en últimos 180 días
		delta_days = random.randint(0, 180)
		fi = date.today() - timedelta(days=delta_days)
		dur = random.randint(1, 7)
		doc_tipo = _DOC_MAP.get(motivo)
		facts = {
			"legajo": leg,
			"motivo": motivo,
			"fecha_inicio": fi.isoformat(),
			"duracion_estimdays": dur,
		}
		if doc_tipo:
			facts["documento_tipo"] = doc_tipo
		try:
			from .dao import create_aviso, update_certificado
			res = create_aviso(facts)
			ida = res.get("id_aviso")
			# Certificado (si aplica)
			if doc_tipo is not None:
				# 70% adjunta, 30% pendiente
				if random.random() < 0.7:
					legible = random.random() < 0.8
					recibida_en = (fi + timedelta(days=random.randint(0, 5))).isoformat()
					update_certificado(ida, {
						"archivo_nombre": f"{doc_tipo}.pdf",
						"documento_legible": legible,
						"fecha_recepcion": recibida_en,
						"plazo_cert_horas": 72,
					})
				# else: queda pendiente/incompleto
			# Notificaciones mínimas (directas)
			with session_scope() as s2:
				# rrhh siempre
				s2.add(Notificacion(id_aviso=ida, destino="rrhh"))
				if motivo in {"enfermedad_inculpable", "art"}:
					s2.add(Notificacion(id_aviso=ida, destino="medico_laboral"))
				if motivo == "fallecimiento":
					s2.add(Notificacion(id_aviso=ida, destino="supervisor"))
				if motivo == "permiso_gremial":
					s2.add(Notificacion(id_aviso=ida, destino="delegado_gremial"))
			created += 1
		except ValueError:
			# Solape u otros errores de validación → omitir
			continue
		except Exception:
			# Error inesperado → omitir para robustez de semillas
			continue
	return created


if __name__ == "__main__":
	ensure_schema()
	e_created = seed_employees_synthetic(200)
	a_created = seed_absences_synthetic(150)
	# Totales por tablas
	with session_scope() as s:
		t_e = s.query(Employee).count()
		t_a = s.query(Aviso).count()
		t_c = s.query(Certificado).count()
		t_n = s.query(Notificacion).count()
	print(
		f"Seed completado. Nuevos: employees={e_created}, avisos={a_created}. Totales: employees={t_e}, avisos={t_a}, certificados={t_c}, notificaciones={t_n}"
	)


