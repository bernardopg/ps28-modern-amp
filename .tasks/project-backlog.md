# Project backlog

Estado canônico nos arquivos de task; espelho em
[github-mirror.json](github-mirror.json). Atualização: **2026-10-16**.
21 tasks: **12 Done, 1 In Progress, 8 To Do**; nenhum gate humano inferido desses totais.

## Trabalho atual e próximo

- **In Progress:** [PCB-002 — revisão global de layout/G2](items/PCB-002.md).
  Rotas conectadas, revisão local do TPA e fit térmico nominal concluídos.
- **To Do:** [ELEC-003 — auditoria elétrica/G1](items/ELEC-003.md),
  [SYS-002 — limites de aceitação](items/SYS-002.md),
  [BUY-001 — cotação/suprimento](items/BUY-001.md),
  [FAB-001 — BOM/CPL e G3](items/FAB-001.md),
  [BENCH-001 — instrumentos/limites](items/BENCH-001.md),
  [BENCH-002 — bring-up/fit físico/térmica](items/BENCH-002.md),
  [ACOU-001 — resposta acústica](items/ACOU-001.md),
  [TOOL-001 — warnings da instalação](items/TOOL-001.md).

## Projeto concluído e referências

- [SETUP-001 — estrutura/docs/skills](items/SETUP-001.md)
- [SETUP-002 — toolchain e CI](items/SETUP-002.md)
- [SETUP-003 — GitHub e setup](items/SETUP-003.md)
- [SYS-001 — woofer](items/SYS-001.md)
- [MECH-001 — envelope OEM](items/MECH-001.md)
- [PWR-001 — fonte e proteção](items/PWR-001.md)
- [ELEC-001 — baseline PBTL](items/ELEC-001.md)
- [ELEC-002 — simulações de front-end](items/ELEC-002.md)
- [ELEC-004 — front-end D-032 por reaproveitamento OEM](items/ELEC-004.md)
- [PCB-003 — estudo do núcleo](items/PCB-003.md)
- [PCB-001 — placement e projeto térmico](items/PCB-001.md)
- [PCB-004 — test points, LEDs e fan](items/PCB-004.md)

Done significa trabalho de projeto encerrado com a evidência aplicável, não
aprovação física ou autorização de fabricar. Ensaios ficam em BENCH-002.

## Sequência

Uma placa: `kicad/system-candidate/`. Conferir revisão global e G1/G2, qualificar
BOM/CPL e cotação; conferir gabarito/fit e obter G3 antes do pedido. Depois,
bring-up resistivo e woofer. Não avançar gate por calendário nem ativar sprint
implicitamente; dependências originais continuam nas tasks.

[Roadmap](ROADMAP.md) · [Próximos passos de produção](../docs/production-roadmap.md)
