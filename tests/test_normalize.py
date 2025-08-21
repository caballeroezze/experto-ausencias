from datetime import date, timedelta

from src.utils.normalize import (
	parse_date,
	normalize_motivo,
	sanitize_number_of_days,
	extract_pairs,
)


def test_parse_date_keywords():
	today = date(2025, 8, 17)
	assert parse_date("hoy", today=today) == today.isoformat()
	assert parse_date("mañana", today=today) == (today + timedelta(days=1)).isoformat()
	assert parse_date("ayer", today=today) == (today - timedelta(days=1)).isoformat()


def test_parse_date_formats():
	assert parse_date("2025-08-17") == "2025-08-17"
	assert parse_date("17/08/2025") == "2025-08-17"
	assert parse_date("32/01/2025") is None  # inválida


def test_normalize_motivo_synonyms():
	assert normalize_motivo("enf") == "enfermedad_inculpable"
	assert normalize_motivo("licencia médica") == "enfermedad_inculpable"
	assert normalize_motivo("permiso gremial") == "permiso_gremial"
	assert normalize_motivo("fallecimiento") == "fallecimiento"
	assert normalize_motivo("nada") is None


def test_sanitize_number_of_days_variants():
	assert sanitize_number_of_days("3 días") == 3
	assert sanitize_number_of_days("tres") == 3
	assert sanitize_number_of_days("x3d") == 3
	assert sanitize_number_of_days("durará 10") == 10
	assert sanitize_number_of_days(None) is None


def test_extract_pairs_basic_pairs():
	text = "legajo: 1234\nmotivo: enf\nfecha_inicio: 17/08/2025\nduracion_estimdays: 3"
	res = extract_pairs(text)
	assert res["legajo"] == "1234"
	assert res["motivo"] == "enfermedad_inculpable"
	assert res["fecha_inicio"] == "2025-08-17"
	assert res["duracion_estimdays"] == 3


def test_extract_pairs_sentence_matrimonio():
	res = extract_pairs("me caso el 17/08/2025")
	assert res["motivo"] == "matrimonio"
	assert res["fecha_inicio"] == "2025-08-17"


def test_extract_pairs_days_detected():
	res = extract_pairs("me caso x3d")
	assert res["motivo"] == "matrimonio"
	assert res["duracion_estimdays"] == 3


def test_extract_pairs_ignores_unknown_keys():
	res = extract_pairs("foo: bar\nlegajo: 77")
	assert res["legajo"] == "77"
	assert "foo" not in res


def test_parse_date_accepts_date_type():
	d = date(2024, 1, 2)
	assert parse_date(d) == "2024-01-02"


def test_normalize_motivo_with_spaces():
	assert normalize_motivo("enfermedad familiar") == "enfermedad_familiar"


def test_extract_pairs_combined_sentence_and_pairs():
	text = "me caso; legajo: 888; duracion_estimdays: x5d"
	res = extract_pairs(text)
	assert res["motivo"] == "matrimonio"
	assert res["legajo"] == "888"
	assert res["duracion_estimdays"] == 5


def test_parse_legajo_variants():
	from src.utils.normalize import parse_legajo
	assert parse_legajo("1234") == "1234"
	assert parse_legajo("legajo 5678") == "5678"
	assert parse_legajo("legajo: 9012") == "9012"
	assert parse_legajo("L1000") is None


