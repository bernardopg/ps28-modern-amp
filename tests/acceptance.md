# Matriz de aceitação — Rev.B verificada sem bancada (D-037)

Limites em [requisitos](../docs/requirements.md). Método: **A** análise/cálculo,
**S** simulação (CI), **C** CAD (ERC/DRC/fit), **D** dimensional, **I** instalação
([procedimento](../docs/bringup.md)). Especificar um limite não comprova conformidade.

| Requisito | Método | Evidência / onde fecha | Situação |
|---|---|---|---|
| REQ-001 woofer | A, I | Woofer OEM identificado (SYS-001); uso no gabinete original | Identificado; instalação pendente |
| REQ-002 potência | A | Perdas e margem térmica: `tests/reports/thermal-fit-review.json`; OTW/OTSD do TPA | Calculado; não declarar 150 W contínuos |
| REQ-003 PVDD | A, S, I | `docs/power-d021.md`, derating; medida de PVDD na 1ª energização | Projeto fechado; medida na instalação |
| REQ-004 rails | A, I | Orçamento em `docs/capacitor-derating.md`; TPs na 1ª energização | Projeto fechado; medida na instalação |
| REQ-005/006 áudio | A, S | Preamp/crossover OEM sem alteração (D-032); simulações em `docs/simulation.md` | Reuso OEM; audição na instalação |
| REQ-007 proteção/sequência | A, S, C | `docs/seq-d020.md`, `docs/iso-d019.md`, `docs/reset-supervisor-contract.md`; ELEC-003 | Captura feita; auditoria G1 pendente |
| REQ-008 test points | C | PCB-004; TPs sem acesso a SPK± | Concluído |
| REQ-009 PCB/BOM | C, D | ERC/DRC/paridade 0; BOM 235 posições; PCB-002, MECH-002, FAB-001 | G2/G3 pendentes |
| REQ-010 térmica/ambiente | A, D, I | Fit térmico em `mechanical/thermal-block.md`; montagem BENCH-002 | Calculado; montagem pendente |

Falha observada na instalação não autoriza reduzir a especificação em silêncio:
abrir decisão com o dado observado. G4 é registro humano.
