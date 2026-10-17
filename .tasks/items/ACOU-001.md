---
id: ACOU-001
title: Integrar woofer e medir resposta
status: To Do
milestone: M4
sprint: S05
depends_on: BENCH-002
updated: 2026-10-17
---

# ACOU-001 — Integrar woofer e medir resposta

## Objetivo

Integrar woofer e medir resposta, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Excursão/vedação/fase/crossover e resposta medidos
- [ ] Uso real sem falhas e G5 humano registrado

## Evidência

Pendente. Não marcar critérios sem evidência.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.

## Critério de excursão fechado por SYS-002 (Rev.B2026-10-17)

Medir Xlin por compressão10% do deslocamento versus tensão, nos dois sentidos
e frequências relevantes; usar menor Xlin, limite operacional0,8Xlin, média
≤100W e ausência de clipping. Antes da caracterização, woofer0W; abaixo35Hz
nenhum ensaio energizado sem verificar subsônico/excursão. Não inventar Xmax
nem atribuir potência térmica do amplificador ao transdutor OEM.
