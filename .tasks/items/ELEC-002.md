---
id: ELEC-002
title: Simular front-end físico e tolerâncias
status: Blocked
milestone: M2
sprint: S03
depends_on: ELEC-001, PWR-001
updated: 2026-10-08
---

# ELEC-002 — Simular front-end físico e tolerâncias

## Objetivo

Simular front-end físico e tolerâncias, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Modelo NE5532/VMID real com licença e compatibilidade
- [ ] LR4/ganho/headroom/impedância/startup/fase e tolerâncias verificados

## Evidência

Preparação de estudo realizada, sem fechar os critérios acima:
- Circuito SPICE com R/C explícitos: duas SK unitárias14k/200nF feedback/100nF referência,
  divisor10k/10k e inversor diferencial10k/10k; fn80,385Hz/Q0,7071.
-151 pontos de magnitude/fase conferidos contra equação independente;16.384
  combinações extremas e2048 amostras com seed20261008.
- Transiente com2Vrms/10,8V avaliado SOMENTE em modelo comportamental próprio.
- Datasheets TI SLOA024B/SLOS075K arquivados localmente com hashes; CM/swing
  de NE5532 a±15V não extrapolados para10,8–13,2V totais.
Ver `docs/analog-lr4-study.md` e `tests/reports/analog-lr4-study.json`.
Bloqueada pelas dependências ELEC-001/PWR-001 e por modelo/validação real de
NE5532/VMID, MPNs, impedâncias, ruído, bias/offset, startup e integração completos.
Nenhuma captura na PCB, Done ou gate de hardware aprovado.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
