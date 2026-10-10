---
id: ELEC-004
title: Capturar front-end completo D-022 e fechar a interface de áudio
status: To Do
milestone: M2
sprint: S03
depends_on: ELEC-002
updated: 2026-10-10
---

# ELEC-004 — Front-end completo D-022

## Objetivo

Capturar o front-end que ainda falta entre as entradas do painel original e
DIVIDED/DIFF_POS/NEG, atendendo D-022, D-024/D-024a e docs/requirements.md.

## Critérios de aceite

- [ ] RCA L/R somadas e LFE/LINE selecionável, com proteção de entrada e OPA desligado
- [ ] LR4 ajustável 50–150 Hz no controle original, tracking entre seções verificado
- [ ] Passa-altas subsônico que impeça disparo da janela DC (<20 Hz) e LEVEL/fase sem degrau DC
- [ ] Ganho compensando −0,69…−2,48 dB da série 3,3 kΩ (D-024a) e limiter provisório 100 W
- [ ] Captura integrada à candidata com ERC sem erros novos e simulação de tolerâncias

## Evidência

Criada em 2026-10-10 a partir das pendências de `docs/iso-d019.md` e
`docs/development-status.md`. Nenhum critério iniciado.

## Risco / aprovação

Pots multi-gang e chave de fase são mecânicos do painel original: cotas e MPN TBD.
Sem compra/energização; revisão humana G1.
