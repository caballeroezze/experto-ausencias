from __future__ import annotations

import re
import unicodedata
from datetime import date, timedelta
from typing import Iterable, Any

from rapidfuzz.distance import Levenshtein


def normalize_text(text: str) -> str:
	"""Normaliza cadenas: trim + lowercase.

	No elimina acentos (usar _strip_accents si se requiere comparar sin diacríticos).
	"""
	return text.strip().lower()


def _strip_accents(text: str) -> str:
	"""Elimina diacríticos para comparar/matchear sin acentos."""
	return "".join(
		c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c)
	)


def similarity(a: str, b: str) -> float:
	"""Similitud usando Levenshtein normalizado en [0,1]."""
	if not a and not b:
		return 1.0
	max_len = max(len(a), len(b)) or 1
	return 1 - (Levenshtein.distance(a, b) / max_len)


# --- Normalizaciones específicas según docs/ ---

_MOTIVOS = {
	"art",
	"enfermedad_inculpable",
	"enfermedad_familiar",
	"fallecimiento",
	"matrimonio",
	"nacimiento",
	"paternidad",
	"permiso_gremial",
}

_MOTIVO_SYNONYMS = {
	"enf": "enfermedad_inculpable",
	"licencia medica": "enfermedad_inculpable",
	"enfermedad": "enfermedad_inculpable",
	"permiso gremial": "permiso_gremial",
}


def parse_date(value: Any, *, today: date | None = None) -> str | None:
	"""Convierte expresiones a fecha ISO (YYYY-MM-DD).

	- Palabras clave: "hoy", "mañana", "ayer"
	- Formato DD/MM/AAAA → ISO
	- Si ya viene en ISO, la retorna
	- Si recibe date, lo convierte a ISO
	"""
	if value is None:
		return None
	if isinstance(value, date):
		return value.isoformat()
	text = normalize_text(str(value))
	today = today or date.today()
	no_acc = _strip_accents(text)
	if no_acc == "hoy":
		return today.isoformat()
	if no_acc == "manana":
		return (today + timedelta(days=1)).isoformat()
	if no_acc == "ayer":
		return (today - timedelta(days=1)).isoformat()
	# ISO directo
	if re.fullmatch(r"\d{4}-\d{2}-\d{2}", text):
		return text
	# DD/MM/AAAA
	m = re.fullmatch(r"(\d{1,2})/(\d{1,2})/(\d{4})", text)
	if m:
		d, mth, y = map(int, m.groups())
		try:
			return date(y, mth, d).isoformat()
		except ValueError:
			return None
	return None


def normalize_motivo(value: Any) -> str | None:
	"""Normaliza motivo al dominio del glosario.

	Mapea sinónimos: "enf", "licencia médica", "enfermedad" → "enfermedad_inculpable".
	Soporta separar por espacios/underscores y eliminación de acentos.
	"""
	if value is None:
		return None
	text = normalize_text(str(value))
	no_acc = _strip_accents(text)
	# Intento directo al formato con underscore
	candidate = no_acc.replace(" ", "_")
	if candidate in _MOTIVOS:
		return candidate
	# Sinónimos
	if no_acc in _MOTIVO_SYNONYMS:
		return _MOTIVO_SYNONYMS[no_acc]
	return None


_NUM_TEXT = {
	"tres": 3,
}


def sanitize_number_of_days(value: Any) -> int | None:
	"""Extrae número de días (int) a partir de expresiones admitidas por docs/.

	Casos: "3 días", "tres", "x3d", "3". Devuelve None si no puede inferir.
	"""
	if value is None:
		return None
	text = normalize_text(str(value))
	no_acc = _strip_accents(text)
	# x3d
	m = re.search(r"x(\d+)d\b", no_acc)
	if m:
		return int(m.group(1))
	# número explícito
	m = re.search(r"(\d+)", no_acc)
	if m:
		return int(m.group(1))
	# texto simple (limitado a docs)
	if no_acc in _NUM_TEXT:
		return _NUM_TEXT[no_acc]
	return None


_KNOWN_VARS = {"legajo", "motivo", "fecha_inicio", "duracion_estimdays"}


def extract_pairs(text: str) -> dict[str, Any]:
	"""Extrae pares var: valor y frases conocidas.

	- Pares "var: valor" para {legajo, motivo, fecha_inicio, duracion_estimdays}
	- Frases: "me caso" → motivo=matrimonio (del dominio)
	- Detecta "N días" y "xNd" si no se informó duracion_estimdays explícito
	"""
	result: dict[str, Any] = {}
	content = text or ""
	# 1) Pares "var: valor"
	for var, val in re.findall(r"([a-zA-Z_]+)\s*:\s*([^\n;]+)", content):
		var_l = normalize_text(var)
		if var_l not in _KNOWN_VARS:
			continue
		val = val.strip()
		if var_l == "motivo":
			mot = normalize_motivo(val)
			if mot:
				result["motivo"] = mot
		elif var_l == "fecha_inicio":
			fd = parse_date(val)
			if fd:
				result["fecha_inicio"] = fd
		elif var_l == "duracion_estimdays":
			d = sanitize_number_of_days(val)
			if d is not None:
				result["duracion_estimdays"] = d
		elif var_l == "legajo":
			result["legajo"] = val.strip()

	# 2) Frases: "me caso" → motivo=matrimonio y posible fecha
	flat = normalize_text(_strip_accents(content))
	if "me caso" in flat:
		result.setdefault("motivo", "matrimonio")
		# intentar fecha en la misma frase
		m = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", flat)
		if m:
			fd = parse_date(m.group(1))
			if fd:
				result.setdefault("fecha_inicio", fd)

	# 2.b) Si hay un legajo de 4 dígitos aislado, mapearlo a 'legajo'.
	# Evita que respuestas como "1111" se confundan con días.
	leg_cand = parse_legajo(content)
	if leg_cand and "legajo" not in result:
		result["legajo"] = leg_cand

	# 3) Detectar días si no vino explícito PERO solo si hay indicios de días
	# (palabras clave o formato xNd). De este modo, un legajo de 4 dígitos no
	# se interpreta erróneamente como duración.
	if "duracion_estimdays" not in result:
		has_days_hint = (
			bool(re.search(r"\bx\d+d\b", flat))
			or any(k in flat for k in ["dia", "dias", "día", "días", "duracion", "duración"])
		)
		if has_days_hint:
			cand = sanitize_number_of_days(flat)
			if cand is not None:
				result["duracion_estimdays"] = cand

	return result


def parse_legajo(text: str | None) -> str | None:
	"""Extrae un legajo de 4 dígitos desde texto.

	Reglas:
	- Si el texto completo es 4 dígitos: retorna ese valor
	- Si aparece patrón "legajo 1234" o "legajo: 1234": retorna 1234
	Devuelve None si no hay match.
	"""
	if not text:
		return None
	content = normalize_text(str(text))
	# 4 dígitos exacto
	if re.fullmatch(r"\d{4}", content):
		return content
	# frase con prefijo legajo
	m = re.search(r"\blegajo[:\s]+(\d{4})\b", content)
	if m:
		return m.group(1)
	# variantes naturales: "mi legajo es 1234", "legajo es 1234", "legajo nro 1234"
	m2 = re.search(r"\blegajo\b[^\d]{0,10}(\d{4})\b", content)
	if m2:
		return m2.group(1)
	return None
