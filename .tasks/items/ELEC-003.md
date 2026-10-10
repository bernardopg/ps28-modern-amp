---
id: ELEC-003
title: Capturar schematic e revisar ERC
status: To Do
milestone: M2
sprint: S03
depends_on: ELEC-002
updated: 2026-10-08
---

# ELEC-003 — Capturar schematic e revisar ERC

## Objetivo

Capturar schematic e revisar ERC, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Pin mapping, MPN/footprints e TPs auditados
- [ ] ERC sem erros não justificados e revisão humana G1

## Evidência

D-024 (2026-10-09): interface D-019 capturada (`kicad/iso-d019`, ERC0) e ponte de
sinal fechada só via relé na candidata; ver `docs/iso-d019.md`. Critérios abertos.

D-023 (2026-10-09): sequenciador discreto capturado (`kicad/seq-d020`, ERC0) e
integrado à candidata com D-021; ver `docs/seq-d020.md`. Pin mapping conferido
contra datasheets TI; footprints não auditados, sem revisão G1. Critérios abertos.

Captura integrada pendente. Contrato preparatório do supervisor em
`docs/reset-supervisor-contract.md`, contra TI SLASEA8A p.20–21/30–31:
RESET baixo apaga FAULT; startup normalmente leva FAULT baixo. Proibido AND
combinacional ingênuo; memória de falha e intervalo mínimo de4ms exigidos.
Não é implementação nem teste de bancada; critérios acima continuam pendentes.

D-016: captura analógica ISOLADA em `kicad/analog-front-end`,21 componentes,
58 pinos, quatro unidades em dois OPA1656ID. ERC nativo0 sem exclusões,14R/C
comparados pin-a-pin/valor com SPICE e pinout SOIC8 contra TI. Fonte/VMID/supervisor
externos; RCA/LFE/volume/fase/proteção ainda não capturados,9 footprints pendentes.
Esquema INTEGRADO continua pendente. Ver `docs/analog-capture.md` e relatório.

D-018: revisão integrada `kicad/analog-protected/`,32 componentes/80 pinos/ERC0;
10 passivos/polaridade D201 auditados contra topologia independente;14 R/C LR4
mais pinagem TI dos4amps conferidos. U2/U3p8 exclusivamente ANALOG_12V;
J103p2 somente VMID monitor. Fonte+VMID capturados, não uma PCB adicional.
13 footprints e MPNs/ESR/pulso/temp pendentes; sinais externos/TPA power-order,
LINE/LFE/volume/DC/supervisor não completos. Não concluir task/gates por ERC0.

D-019 documenta contrato preparatório para INPUT_A/B: isolar depois de C20/C21,
controlar placa isolada, mute analógico e pré-carga observada antes do áudio.
A captura D-018 e o núcleo NÃO foram conectados. Chaves/retorno/capacitância/
comparadores, defaults e tempos seguem TBD; estudos RC não fecham G1 nem a
dependência ELEC-002. Ver `docs/input-power-order-study.md`.

Atualização docs/3D: `docs/development-status.md` e galeria agora explicitam que
D-018/D-019 não estão integrados à PCB. Nenhum schematic/PCB foi alterado; 13
footprints e pinagem/MPNs/control/proteção/supervisor finais seguem pendentes.
Status To Do/dependência ELEC-002 preservados; não fechar G1 por imagem/ERC0.

D-020: `kicad/system-candidate/` integra captura core+29 analógicos (76/212),
GND/AUX_RAW compartilhados, p8OPA emANALOG_12V. J101–103 eram interfaces lógicas,
removidas sem novos conectores OEM. Footprints/MPNs candidatos atribuídos;
saída permanece ABERTA e proteção/mute/control/fonte/funções RCA não completos.
Não fechar G1 nem marcar task Done. Baselines intactas; ver D-020.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
