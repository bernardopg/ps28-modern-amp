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

- [ ] Modelo do op-amp selecionado/VMID real com licença e compatibilidade (D-016: OPA1656 candidato)
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

Incremento D-016: OPA1656ID candidato, modelo oficial TI SBOMAW6C/Final1.3
inteiro auditado e pin order conferido;9 casos10,8/12/13,2V ×0/27/70°C passaram.
Modelo permanece local, sem redistribuição; ngspice PSA configurado isoladamente.
Warnings/fallbacks de convergência estão no relatório. VMID continua ideal, logo
critério completo acima NÃO fechado. Captura independente21 componentes/58pinos,
ERC0 e14R/C comparados com SPICE;9 footprints pendentes.
Ver `docs/analog-capture.md` e `tests/reports/opa1656-model-study.json`.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
