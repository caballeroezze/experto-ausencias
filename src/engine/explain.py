from __future__ import annotations

from typing import Any


def explain_traces(traces: list[dict[str, Any]]) -> list[dict[str, Any]]:
	"""Construye explicaciones compactas a partir de trazas.

	Cada traza esperada: {regla_id, porque, hechos_usados}
	"""
	return [
		{
			"regla_id": t.get("regla_id"),
			"porque": t.get("porque"),
			"hechos_usados": t.get("hechos_usados", {}),
		}
		for t in traces
	]


def format_explanation(traces: list[dict[str, Any]]) -> str:
	parts: list[str] = []
	for t in traces:
		regla_id = t.get("regla_id")
		porque = t.get("porque") or ""
		hechos = ", ".join(f"{k}={v}" for k, v in (t.get("hechos_usados") or {}).items())
		parts.append(f"[{regla_id}] {porque} ({hechos})")
	return " \n".join(parts)

