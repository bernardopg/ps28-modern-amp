---
id: ELEC-001
title: Escolher baseline PBTL e matriz de pinos
status: Done
milestone: M1
sprint: S02
depends_on: SYS-001
updated: 2026-10-12
---

# ELEC-001 — Escolher baseline PBTL e matriz de pinos

## Objetivo

Escolher baseline PBTL e matriz de pinos, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [x] Datasheet vs EVM comparados com figuras/revisões
- [x] LC/paralelamento completo e sequência RESET documentados

## Evidência

2026-10-12 (D-030): baseline PBTL SLASEA8A Fig. 31 (D-011) capturada; quatro OUTs paralelos A+C/B+D, M1/M2 e RESET no sequenciador D-020; ERC 0 na placa única.

Pendente. Não marcar critérios sem evidência.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
