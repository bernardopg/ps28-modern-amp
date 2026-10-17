---
id: ELEC-003
title: Auditoria elétrica e G1
status: To Do
milestone: M2
sprint: S04
depends_on: ELEC-001
updated: 2026-10-17
---
# ELEC-003 — Auditoria elétrica e G1

## Objetivo

Auditar o esquema integrado de `kicad/system-candidate/` pino a pino contra
datasheets e obter o gate G1. Trabalho de mesa.

## Critérios de aceite

- [ ] Pinagem dos CIs (TPA3255, LM5164, LP2985, TPS3700/3808, 74LVC, TMUX6219, OPA1656) conferida
- [ ] MPN ↔ footprint ↔ valor das 235 posições conferidos (BOM em `bom/`)
- [ ] Modo PBTL: M1/M2, INPUT_C/D e quatro OUTs conforme SLASEA8A Fig. 31
- [ ] Contrato RESET/FAULT conforme `docs/reset-supervisor-contract.md`
- [ ] G1 assinado pelo proprietário

## Evidência

ERC 0 e paridade 0; captura integrada (D-020/D-032). Simulações em CI:
[simulação](../../docs/simulation.md). Revisão independente ainda não feita.
