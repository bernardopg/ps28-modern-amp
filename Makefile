.PHONY: check core-check analog-check doctor simulate simulate-input-order simulate-opa simulate-vmid simulate-vmid-protected analog-protected-check eda-smoke erc drc fetch-reference

check:
	python3 scripts/validate.py
	python3 -m unittest discover -s tests/unit -v

core-check:
	python3 scripts/check_core.py

analog-check:
	python3 scripts/check_analog_capture.py

simulate-input-order:
	python3 scripts/simulate_input_power_order.py

simulate-opa:
	python3 scripts/simulate_opa1656.py

simulate-vmid-protected:
	python3 scripts/simulate_vmid_protection.py

analog-protected-check:
	python3 scripts/check_vmid_protection.py --integrated

simulate-vmid:
	python3 scripts/simulate_vmid.py

doctor:
	python3 scripts/doctor.py

simulate:
	python3 scripts/simulate.py
	python3 scripts/simulate_analog.py
	python3 scripts/simulate_input_power_order.py

eda-smoke:
	python3 scripts/eda_smoke.py

erc:
	python3 scripts/eda_check.py erc

drc:
	python3 scripts/eda_check.py drc

fetch-reference:
	python3 scripts/fetch_reference.py
