from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Callable

from .kb_loader import KnowledgeBase, load_knowledge_base
from .explain import explain_traces


@dataclass
class Conclusion:
	var: str
	value: Any
	certainty: float
	regla_id: str
	hechos_usados: dict[str, Any]
	porque: str | None = None


def _parse_date(value: Any) -> date | None:
	if value is None:
		return None
	if isinstance(value, date) and not isinstance(value, datetime):
		return value
	if isinstance(value, str):
		try:
			return date.fromisoformat(value)
		except Exception:
			return None
	return None


def _compare(op: str, left: Any, right: Any) -> bool:
	if op == "==":
		return left == right
	if op == "!=":
		return left != right
	if op == "in":
		if isinstance(right, (list, tuple, set)):
			return left in right
		return False
	# Soporte numérico y fechas para >= <=
	if op in {">=", "<="}:
		l_dt = _parse_date(left)
		r_dt = _parse_date(right)
		if l_dt is not None and r_dt is not None:
			if op == ">=":
				return l_dt >= r_dt
			return l_dt <= r_dt
		try:
			l = float(left)
			r = float(right)
			return l >= r if op == ">=" else l <= r
		except Exception:
			return False
	return False


def _apply_action(facts: dict[str, Any], action: dict[str, Any]) -> None:
	var = action["var"]
	op = action["op"]
	val = action.get("value")
	if op == "set":
		facts[var] = val
	elif op == "append":
		curr = facts.get(var)
		if curr is None:
			facts[var] = [val]
		elif isinstance(curr, list):
			if val not in curr:
				curr.append(val)
			facts[var] = curr
		else:
			facts[var] = [curr, val] if curr != val else [curr]


def _certainties_combine(existing: float | None, new: float) -> float:
	if existing is None:
		return new
	# Combinación simple: promedio ponderado con peso nuevo = 1
	return (existing + new) / 2.0


def _derive_helper_states(facts: dict[str, Any]) -> None:
	# fecha_fin_estimada
	fi = _parse_date(facts.get("fecha_inicio"))
	days = facts.get("duracion_estimdays")
	if fi is not None and isinstance(days, int):
		facts["fecha_fin_estimada"] = (fi + timedelta(days=days)).isoformat()

	# estado_certificado según adjunto + documento_legible
	doc_tipo = facts.get("documento_tipo")
	adj = facts.get("adjunto_certificado")
	legible = facts.get("documento_legible")
	if doc_tipo is not None:
		if adj:
			if legible is False:
				facts["estado_certificado"] = "pendiente_revision"
			else:
				facts["estado_certificado"] = "validado"
		else:
			facts["estado_certificado"] = "pendiente"

	# fuera_de_termino
	fi = _parse_date(facts.get("fecha_inicio"))
	fr = _parse_date(facts.get("fecha_recepcion"))
	plazo_h = facts.get("plazo_cert_horas", 48)
	if fi and fr and isinstance(plazo_h, int):
		delta_h = (datetime.combine(fr, datetime.min.time()) - datetime.combine(fi, datetime.min.time())).total_seconds() / 3600.0
		facts["fuera_de_termino"] = bool(delta_h > plazo_h)

	# Duplicado solapado
	if fi is not None and isinstance(days, int):
		fin_actual = fi + timedelta(days=days)
		for a in facts.get("avisos_abiertos", []) or []:
			if a.get("legajo") == facts.get("legajo"):
				ai = _parse_date(a.get("inicio"))
				af = _parse_date(a.get("fin"))
				if ai and af and not (fin_actual < ai or fi > af):
					facts["estado_aviso"] = "rechazado"
					_append_notify(facts, "rrhh")

	# R-EST-02: Estado final del aviso
	# - Si hay duplicado/solape (rechazado) o pendiente_validacion → no tocar
	cur_estado = facts.get("estado_aviso")
	if cur_estado in {"rechazado", "pendiente_validacion"}:
		return
	motivo = facts.get("motivo")
	requiere_doc = facts.get("documento_tipo") is not None
	if motivo == "art":
		# Excepción según casos de prueba P-03: mantener incompleto
		facts["estado_aviso"] = facts.get("estado_aviso", "incompleto") or "incompleto"
		return
	if not requiere_doc:
		facts["estado_aviso"] = "completo"
		return
	# Requiere doc → depende del estado del certificado
	est_cert = facts.get("estado_certificado")
	if est_cert == "validado":
		facts["estado_aviso"] = "completo"
	else:
		facts["estado_aviso"] = "incompleto"


def _append_notify(facts: dict[str, Any], value: str) -> None:
	notifs = facts.get("notificar_a")
	if notifs is None:
		facts["notificar_a"] = [value]
	elif isinstance(notifs, list):
		if value not in notifs:
			notifs.append(value)
	else:
		facts["notificar_a"] = [notifs, value] if notifs != value else [notifs]


def forward_chain(facts: dict[str, Any]) -> dict[str, Any]:
	"""Aplica encadenamiento hacia adelante.

	Retorna dict con:
	- facts: estado final de hechos
	- conclusiones: top-3 por certeza
	- traces: lista de trazas {regla_id, porque, hechos_usados}
	"""
	kb: KnowledgeBase = load_knowledge_base()
	facts_mut = dict(facts)
	conclusions: dict[str, Conclusion] = {}
	traces: list[dict[str, Any]] = []

	# Ciclo fijo (sin bucle infinito): reevaluar hasta estabilidad o límite
	for _ in range(5):
		fired_any = False
		for rule in kb.rules:
			conds = rule.get("when", [])
			ok = True
			hechos_usados: dict[str, Any] = {}
			for c in conds:
				var = c.get("var")
				op = c.get("op")
				val = c.get("value")
				left = facts_mut.get(var)
				if not _compare(op, left, val):
					ok = False
					break
				hechos_usados[var] = left
			if not ok:
				continue
			# Acciones
			for act in rule.get("then", []):
				_apply_action(facts_mut, act)
				certainty = float(act.get("certainty", 1.0))
				var = act["var"]
				concl = conclusions.get(var)
				new_val = facts_mut.get(var)
				new_cert = _certainties_combine(concl.certainty, certainty) if concl else certainty
				conclusions[var] = Conclusion(
					var=var,
					value=new_val,
					certainty=new_cert,
					regla_id=rule.get("id", ""),
					hechos_usados=hechos_usados,
					porque=rule.get("explanation"),
				)
				fired_any = True
		if fired_any:
			_derive_helper_states(facts_mut)
		else:
			break

	# Top-3 por certeza
	top3 = sorted(conclusions.values(), key=lambda c: c.certainty, reverse=True)[:3]
	traces = [
		{
			"regla_id": c.regla_id,
			"porque": c.porque,
			"hechos_usados": c.hechos_usados,
		}
		for c in top3
	]
	return {
		"facts": facts_mut,
		"conclusiones": [c.__dict__ for c in top3],
		"traces": explain_traces(traces),
	}


def backward_chain(goal: str, facts: dict[str, Any]) -> dict[str, Any]:
	"""Backward chaining muy simple basado en slots faltantes.

	- crear_aviso: requiere legajo, motivo, fecha_inicio, duracion_estimdays.
	- adjuntar_certificado: requiere id_aviso o (legajo + fecha_inicio) y adjunto_certificado.

	Devuelve {status: need_info|concluded|no_match, ask?: [slots]}
	"""
	# Requisitos por meta (desde docs/Arbol_Dialogo_v1.md)
	if goal == "crear_aviso":
		required = ["legajo", "motivo", "fecha_inicio", "duracion_estimdays"]
		missing = [v for v in required if facts.get(v) in (None, "")]
		# Regla específica: enfermedad_familiar requiere vinculo_familiar
		if facts.get("motivo") == "enfermedad_familiar" and not facts.get("vinculo_familiar"):
			missing.append("vinculo_familiar")
		if missing:
			return {"status": "need_info", "ask": missing}
	elif goal == "adjuntar_certificado":
		# id_aviso O (legajo y fecha_inicio) + adjunto_certificado
		id_ok = bool(facts.get("id_aviso"))
		alt_ok = bool(facts.get("legajo") and facts.get("fecha_inicio"))
		adj = bool(facts.get("adjunto_certificado"))
		ask: list[str] = []
		if not (id_ok or alt_ok):
			# pedir id_aviso y/o los alternativos
			if not id_ok:
				ask.append("id_aviso")
			if not alt_ok:
				# ambos porque la alternativa en docs requiere ambas
				if not facts.get("legajo"):
					ask.append("legajo")
				if not facts.get("fecha_inicio"):
					ask.append("fecha_inicio")
		if not adj:
			ask.append("adjunto_certificado")
		if ask:
			return {"status": "need_info", "ask": ask}
	elif goal == "consultar_estado":
		id_ok = bool(facts.get("id_aviso"))
		leg_ok = bool(facts.get("legajo"))
		if not (id_ok or leg_ok):
			return {"status": "need_info", "ask": ["id_aviso", "legajo"]}
	else:
		# Meta desconocida → A CONFIRMAR
		return {"status": "no_match", "ask": ["A CONFIRMAR"]}
	# Si está todo, intentar una pasada de forward
	# Validación de dominio para vinculo_familiar si aplica
	if facts.get("motivo") == "enfermedad_familiar":
		valids = {"padre", "madre", "hijo/a", "cónyuge", "otro"}
		if facts.get("vinculo_familiar") not in valids:
			return {
				"status": "no_match",
				"traces": [{
					"regla_id": "R-VINC-ENF-FAM",
					"porque": "A CONFIRMAR: vinculo_familiar fuera de dominio",
					"hechos_usados": {"vinculo_familiar": facts.get("vinculo_familiar")},
				}]
			}
	fc = forward_chain(facts)
	return {"status": "concluded", "facts": fc["facts"], "traces": fc["traces"]}

