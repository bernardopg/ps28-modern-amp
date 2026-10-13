# Project backlog

Ordem por dependência/risco; estado canônico nos arquivos de task.

- [SETUP-001 — Estrutura, documentação e skills](items/SETUP-001.md) (M0, S01)
- [SETUP-002 — Containers EDA, comandos e CI](items/SETUP-002.md) (M0, S01)
- [SETUP-003 — GitHub e revisão do setup](items/SETUP-003.md) (M0, S01)
- [SYS-001 — Identificar woofer e integridade](items/SYS-001.md) (M1, S02)
- [SYS-002 — Fechar requisitos e limites de aceitação](items/SYS-002.md) (M1, S02)
- [MECH-001 — Medir plate e modelar envelope](items/MECH-001.md) (M1, S02)
- [PWR-001 — Selecionar fonte e proteção](items/PWR-001.md) (M1, S02)
- [ELEC-001 — Escolher baseline PBTL e matriz de pinos](items/ELEC-001.md) (M1, S02)
- [BUY-001 — Cotação preliminar e estratégia de suprimento](items/BUY-001.md) (M1, S02)
- [BENCH-001 — Inventariar bancada e aprovar limites](items/BENCH-001.md) (M1, S02)
- [ELEC-002 — Simular front-end físico e tolerâncias](items/ELEC-002.md) (M2, S03)
- [ELEC-003 — Capturar schematic e revisar ERC](items/ELEC-003.md) (M2, S03)
- [ELEC-004 — Front-end completo D-022 e interface de áudio](items/ELEC-004.md) (M2, S03)
- [PCB-003 — Spike de captura e placement do core](items/PCB-003.md) (M2, S03; exploratório, não fecha gates)
- [PCB-001 — Stackup, placement e térmica](items/PCB-001.md) (M3, S04)
- [PCB-002 — Rotear e revisar layout](items/PCB-002.md) (M3, S04)
- [PCB-004 — Test points, LEDs de status/debug e conector de fan](items/PCB-004.md) (M3, S04)
- [FAB-001 — Fechar BOM/CPL e aprovar fabricação](items/FAB-001.md) (M3, S04)
- [BENCH-002 — Bring-up e carga resistiva](items/BENCH-002.md) (M4, S05)
- [ACOU-001 — Integrar woofer e medir resposta](items/ACOU-001.md) (M4, S05)

- [TOOL-001 — Investigar warnings KiCad](items/TOOL-001.md) (M1, backlog; avaliar antes de captura prolongada)

## Caminho até a fabricação — placa única (D-030, 2026-10-12)

Placa: `kicad/system-candidate/` (ERC 0, DRC 0, 471 conexões a rotear).
1. MECH-001 — cotas locais do contato TPA3255/perfil U (proprietário, multímetro/paquímetro).
2. ELEC-004 — front-end D-022 (crossover 50–150 Hz, nível, fase) na captura.
3. PCB-001 — placement manual de potência/Classe D com o dissipador definido.
4. PCB-002 — rota manual com planos; DRC 0 e revisão do proprietário (G1/G2).
5. BUY-001 + FAB-001 — BOM/CPL, cotação e pedido com "ok" do proprietário (G3).
6. BENCH-001/002 — energização controlada, carga resistiva; ACOU-001 com o woofer.
SYS-002/ELEC-002/ELEC-003 fecham junto com ELEC-004 e a revisão final (G0/G1).

## Prioridade técnica após D-021…D-024a (2026-10-10)

Caminho até produção em [docs/production-roadmap.md](../docs/production-roadmap.md).
Ordem: MECH-001 (cotas OEM) e ELEC-004 (front-end) destravam PCB-001; PWR-001 fecha
MPNs de potência e inrush; depois PCB-002, FAB-001 e gates G1–G3. Esta ordem não
altera status, WIP ou ativação de sprint, nem autoriza produção/energização.

Backlog futuro não comprometido: auto-standby, EMI formal e revisão B de crossover; criar tasks apenas após priorização.
