from __future__ import annotations
import os

from src.persistence.seed import ensure_schema, seed_employees_synthetic
from src.persistence.dao import session_scope
from src.persistence.models import Employee
from src.persistence.export_powerbi import export_all_csv


def test_seed_employees_synthetic_crea_al_menos_100():
	ensure_schema()
	seed_employees_synthetic(200)
	with session_scope() as s:
		total = s.query(Employee).count()
	assert total >= 100


def test_export_all_csv_genera_5_archivos(tmp_path):
	ensure_schema()
	out_dir = tmp_path / "exports"
	files = export_all_csv(out_dir=str(out_dir))
	assert len(files) == 5
	for fp in files:
		assert os.path.isfile(fp)


