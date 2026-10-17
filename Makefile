.PHONY: check doctor simulate simulate-input-order simulate-opa simulate-vmid simulate-vmid-protected simulate-power  render-3d erc drc fetch-reference

check:
	python3 scripts/validate.py
	python3 -m unittest discover -s tests/unit -v

simulate-input-order:
	python3 scripts/simulate_input_power_order.py

simulate-opa:
	python3 scripts/simulate_opa1656.py

simulate-vmid-protected:
	python3 scripts/simulate_vmid_protection.py

simulate-power:
	python3 scripts/simulate_power_d021.py

simulate-vmid:
	python3 scripts/simulate_vmid.py

doctor:
	python3 scripts/doctor.py

simulate:
	python3 scripts/simulate.py
	python3 scripts/simulate_analog.py
	python3 scripts/simulate_input_power_order.py

render-3d:
	python3 scripts/render_kicad_gallery.py --frames 16

.PHONY: render-studio
render-studio:
	mkdir -p build/studio
	kicad-cli pcb export glb --include-pads --include-silkscreen --include-soldermask --no-dnp --force -o build/studio/board.glb kicad/system-candidate/system-candidate.kicad_pcb > build/studio/export.log 2>&1
	xvfb-run -a blender --background --factory-startup --python scripts/blender_pcb_studio.py > build/studio/render.log 2>&1

erc:
	python3 scripts/eda_check.py erc

drc:
	python3 scripts/eda_check.py drc

fetch-reference:
	python3 scripts/fetch_reference.py

.PHONY: pcb-readiness
pcb-readiness:
	python3 scripts/check_pcb_readiness.py

.PHONY: fab
fab:
	python3 scripts/export_fab.py

.PHONY: thermal-fit thermal-model
thermal-fit:
	python3 scripts/check_thermal_fit.py

thermal-model:
	python3 scripts/check_thermal_fit.py --skip-mesh
	xvfb-run -a blender --background --factory-startup --python scripts/blender_thermal_block.py
	python3 scripts/check_thermal_fit.py
	python3 scripts/render_thermal_budget.py

.PHONY: body-models
body-models:
	python3 scripts/make_body_models.py
