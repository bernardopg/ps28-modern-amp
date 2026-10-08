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

Captura integrada pendente. Contrato preparatório do supervisor em
`docs/reset-supervisor-contract.md`, contra TI SLASEA8A p.20–21/30–31:
RESET baixo apaga FAULT; startup normalmente leva FAULT baixo. Proibido AND
combinacional ingênuo; memória de falha e intervalo mínimo de4ms exigidos.
Não é implementação nem teste de bancada; critérios acima continuam pendentes.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
