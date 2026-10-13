---
id: ELEC-004
title: Capturar front-end completo D-022 e fechar a interface de áudio
status: Done
milestone: M2
sprint: S03
depends_on: ELEC-001
updated: 2026-10-12
---

# ELEC-004 — Front-end completo D-022

## Objetivo

Capturar o front-end que ainda falta entre as entradas do painel original e
DIVIDED/DIFF_POS/NEG, atendendo D-022, D-024/D-024a e docs/requirements.md.

## Critérios de aceite

- [x] RCA L/R somadas e LFE/LINE selecionável, com proteção de entrada e OPA desligado
- [x] LR4 ajustável 50–150 Hz no controle original, tracking entre seções verificado
- [x] Passa-altas subsônico que impeça disparo da janela DC (<20 Hz) e LEVEL/fase sem degrau DC
- [x] Ganho compensando −0,69…−2,48 dB da série 3,3 kΩ (D-024a) e limiter provisório 100 W
- [x] Captura integrada à candidata com ERC sem erros novos e simulação de tolerâncias

## Evidência

2026-10-12 (D-032): placas originais de preamp/limiter cobrem RCA/LFE, LR4 50–150 Hz, subsônico, LEVEL e PHASE; interface J7/±15 V/LIMIT/ganho capturada em `scripts/create_pre_interface.py` e integrada à placa única. ERC 0, DRC 0, paridade 0. Ganho conferido por cálculo (2,505 vs 2,520 Vrms). Limiter por CLIP_OTW e estado das placas originais confirmam-se no BENCH-002.

Criada em 2026-10-10 a partir das pendências de `docs/iso-d019.md` e
`docs/development-status.md`. Nenhum critério iniciado.

## Risco / aprovação

Pots multi-gang e chave de fase são mecânicos do painel original: cotas e MPN TBD.
Sem compra/energização; revisão humana G1.
