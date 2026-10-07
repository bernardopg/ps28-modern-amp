# Core draft — evidências do primeiro incremento

Fontes e desvios em docs/core-draft.md; branch feat/pbtl-core-draft.
Snapshot antes da captura: 20261007_143646_693300.

- Capture/export XML/SVG/PDF no KiCad 10.0.7: sucesso de parsing/export.
- Captura: 47 componentes, 44 pinos U1; footprint DDV TopEP, não bottom exposed-pad.
- PCB: 35 footprints, 116 pads com nets conferidas contra a captura por checker stdlib.
- `make check`: 11 testes aprovados; mutações SPK_N→GND e TopEP→bottom-EP detectadas.
- `make core-check`: sem inconsistências do grafo; não é sign-off elétrico/térmico.
- `make erc`: falha esperada, oito erros mantidos. Quatro power_pin_not_driven em
  BST_A/B/C/D; quatro pin_to_pin nos outputs paralelados/duplicados. Revisão pendente.
- `make drc`: falha esperada, 85 unconnected_items e 12 missing_footprint.
  Zero violations geométricas reportadas no placement; não há trilhas nem zones.
- Ausências deliberadas: C1/C14/C15, C22/C23/C26/C27, L1/L2, J1/J5/J6.
- Não foram gerados Gerber/CPL, não houve simulação física de potência/medições.
- Imagens e schematic.pdf em build/core-draft; logs completos ERC/DRC em build/.

Revisão independente, MPNs, LC/snubbers, dimensões, dissipador e roteamento pendentes.
Nenhum gate G0–G5 fechado. Trabalho anterior existente no working tree foi preservado.
