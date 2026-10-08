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
- [PCB-003 — Spike de captura e placement do core](items/PCB-003.md) (M2, S03; exploratório, não fecha gates)
- [PCB-001 — Stackup, placement e térmica](items/PCB-001.md) (M3, S04)
- [PCB-002 — Rotear e revisar layout](items/PCB-002.md) (M3, S04)
- [FAB-001 — Fechar BOM/CPL e aprovar fabricação](items/FAB-001.md) (M3, S04)
- [BENCH-002 — Bring-up e carga resistiva](items/BENCH-002.md) (M4, S05)
- [ACOU-001 — Integrar woofer e medir resposta](items/ACOU-001.md) (M4, S05)

- [TOOL-001 — Investigar warnings KiCad](items/TOOL-001.md) (M1, backlog; avaliar antes de captura prolongada)

## Prioridade técnica após D-018/D-019
- [ELEC-002](items/ELEC-002.md)/[PWR-001](items/PWR-001.md): qualificar
  envelope/parts D-018, proteger RCA/INPUT_A/B e demonstrar power-order/pré-carga.
- [ELEC-003](items/ELEC-003.md): integrar mute/isolation/supervisor e funções
  pendentes no schematic; resolver 13 footprints, sem fechar G1 por ERC0.
- [MECH-001](items/MECH-001.md)/[PCB-003](items/PCB-003.md): cotas/contacto OEM,
  revisão independente e posterior integração/roteamento. Galeria só do core.
[Estado/evidências](../docs/development-status.md); esta ordem não altera status,
dependências, WIP ou ativação de sprint, nem autoriza produção/energização.

Backlog futuro não comprometido: auto-standby, EMI formal e revisão B de crossover; criar tasks apenas após priorização.
