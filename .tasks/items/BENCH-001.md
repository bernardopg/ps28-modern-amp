---
id: BENCH-001
title: Inventariar bancada e aprovar limites
status: To Do
milestone: M1
sprint: S02
depends_on: SYS-002, ELEC-001
updated: 2026-10-12
---

# BENCH-001 — Inventariar bancada e aprovar limites

## Objetivo

Inventariar bancada e aprovar limites, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Instrumentos e carga/sonda/cooling confirmados
- [ ] tests/bench-plan.md sem limites TBD e revisão humana registrada
- [ ] D-029: fonte de bancada da Rev A definida (tensão PVDD, limite de corrente, OVP
  da própria fonte ≤ janela aprovada, polaridade/condutores para J1)
- [ ] D-027/D-029: medir inrush/I²t e corrente CT de T1 com retificador de teste fora
  da PCB, para qualificar F301/D301/D302/C301/C302 da Rev B

## Evidência

Pendente. Não marcar critérios sem evidência.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
