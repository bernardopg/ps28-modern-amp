.PHONY: check doctor simulate eda-smoke erc drc fetch-reference

check:
	python3 scripts/validate.py
	python3 -m unittest discover -s tests/unit -v

doctor:
	python3 scripts/doctor.py

simulate:
	python3 scripts/simulate.py

eda-smoke:
	python3 scripts/eda_smoke.py

erc:
	python3 scripts/eda_check.py erc

drc:
	python3 scripts/eda_check.py drc

fetch-reference:
	python3 scripts/fetch_reference.py
