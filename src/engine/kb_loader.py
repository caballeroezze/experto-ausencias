from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import json


GLOSSARY_PATH = Path(__file__).resolve().parents[2] / "docs" / "glossary.json"
RULES_PATH = Path(__file__).resolve().parents[2] / "docs" / "rules.json"


@dataclass(frozen=True)
class KnowledgeBase:
	glossary: dict[str, Any]
	rules: list[dict[str, Any]]
	version: int


def _validate_glossary(gl: dict[str, Any]) -> None:
	if not isinstance(gl, dict) or "variables" not in gl:
		raise ValueError("glossary.json inválido: falta 'variables'")
	for var_name, spec in gl["variables"].items():
		if not isinstance(spec, dict) or "type" not in spec:
			raise ValueError(f"Variable '{var_name}' en glosario sin 'type'")
		type_name = spec["type"]
		if type_name not in {"string", "int", "date", "enum", "boolean", "list"}:
			raise ValueError(f"Tipo no soportado en glosario: {type_name}")
		if type_name == "enum" and "values" not in spec:
			raise ValueError(f"Enum '{var_name}' sin 'values'")
		if type_name == "list" and "values" not in spec:
			raise ValueError(f"List '{var_name}' sin 'values'")


def _validate_rules(rules_doc: dict[str, Any], glossary: dict[str, Any]) -> list[dict[str, Any]]:
	if not isinstance(rules_doc, dict) or "rules" not in rules_doc:
		raise ValueError("rules.json inválido: falta 'rules'")
	rules = rules_doc["rules"]
	if not isinstance(rules, list):
		raise ValueError("rules.json: 'rules' no es lista")
	variables = glossary["variables"].keys()
	for r in rules:
		if "id" not in r or "when" not in r or "then" not in r:
			raise ValueError("Regla inválida: falta id/when/then")
		for cond in r["when"]:
			if "var" not in cond or "op" not in cond:
				raise ValueError(f"Regla {r['id']}: condición inválida")
			if cond["var"] not in variables and cond["var"] is not None:
				raise ValueError(f"Regla {r['id']}: variable desconocida {cond['var']}")
			if cond["op"] not in {"==", "!=", "in", ">=", "<="}:
				raise ValueError(f"Operador no soportado en when: {cond['op']}")
		for act in r["then"]:
			if "var" not in act or "op" not in act:
				raise ValueError(f"Regla {r['id']}: acción inválida")
			if act["var"] not in variables:
				raise ValueError(f"Regla {r['id']}: variable desconocida en then {act['var']}")
			if act["op"] not in {"set", "append"}:
				raise ValueError(f"Operación no soportada en then: {act['op']}")
	return rules


def load_knowledge_base() -> KnowledgeBase:
	"""Carga y valida glossary.json y rules.json.

	Retorna un objeto KnowledgeBase con reglas y glosario.
	"""
	with GLOSSARY_PATH.open("r", encoding="utf-8") as f:
		glossary = json.load(f)
	_validate_glossary(glossary)
	with RULES_PATH.open("r", encoding="utf-8") as f:
		rules_doc = json.load(f)
	rules = _validate_rules(rules_doc, glossary)
	version = int(rules_doc.get("version", 1))
	return KnowledgeBase(glossary=glossary, rules=rules, version=version)

