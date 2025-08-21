from __future__ import annotations
import os
import csv
from datetime import date, datetime
from typing import Iterable

from .dao import session_scope
from .models import Employee, Aviso, Certificado, Notificacion, Auditoria
import json


def _ensure_dir(path: str) -> None:
	if not os.path.isdir(path):
		os.makedirs(path, exist_ok=True)


def _iso(v):
	if isinstance(v, (date, datetime)):
		return v.isoformat()
	if isinstance(v, (dict, list)):
		return json.dumps(v, ensure_ascii=False)
	return v


def _export_table(query, fieldnames: list[str], out_path: str) -> None:
	with session_scope() as session:
		objects = [row[0] for row in session.execute(query).all()]
	with open(out_path, "w", newline="", encoding="utf-8") as f:
		w = csv.writer(f, delimiter=",")
		w.writerow(fieldnames)
		for obj in objects:
			w.writerow([_iso(getattr(obj, k)) for k in fieldnames])


def export_all_csv(out_dir: str = "./exports") -> list[str]:
	"""Exporta todas las tablas en CSV con separador coma y fechas en ISO.

	Devuelve lista de rutas de archivos generados.
	"""
	_ensure_dir(out_dir)
	from sqlalchemy import select

	outputs: list[str] = []

	# employees
	fn = ["legajo", "nombre", "area", "puesto", "fecha_ingreso", "turno", "activo"]
	p = os.path.join(out_dir, "employees.csv")
	_export_table(select(Employee), fn, p)
	outputs.append(p)

	# avisos
	fn = [
		"id_aviso",
		"legajo",
		"motivo",
		"fecha_inicio",
		"fecha_fin",
		"duracion_estimdays",
		"estado_aviso",
		"estado_certificado",
		"documento_tipo",
		"adjunto",
		"created_at",
	]
	p = os.path.join(out_dir, "avisos.csv")
	_export_table(select(Aviso), fn, p)
	outputs.append(p)

	# certificados
	fn = ["id", "id_aviso", "tipo", "recibido_en", "valido", "notas"]
	p = os.path.join(out_dir, "certificados.csv")
	_export_table(select(Certificado), fn, p)
	outputs.append(p)

	# notificaciones
	fn = ["id", "id_aviso", "destino", "enviado_en", "canal", "payload"]
	p = os.path.join(out_dir, "notificaciones.csv")
	_export_table(select(Notificacion), fn, p)
	outputs.append(p)

	# auditoria
	fn = ["id", "entidad", "entidad_id", "accion", "ts", "actor", "detalle"]
	p = os.path.join(out_dir, "auditoria.csv")
	_export_table(select(Auditoria), fn, p)
	outputs.append(p)

	return outputs


