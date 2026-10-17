---
id: MECH-002
title: Conferir gabarito 1:1 na unidade OEM
status: To Do
milestone: M3
sprint: S04
depends_on: MECH-001
updated: 2026-10-17
---
# MECH-002 — Conferir gabarito 1:1 na unidade OEM

## Objetivo

Única verificação física antes do pedido (D-037): imprimir o gabarito cotado 1:1
gerado por `make fab` e conferi-lo sobre a placa/suportes originais.

## Critérios de aceite

- [ ] Escala conferida com régua no próprio impresso (cota de 154 mm)
- [ ] Quatro furos de fixação coincidem com os suportes OEM (±0,5 mm)
- [ ] Perfil U assenta na região reservada; furos laterais do bloco alinhados aos M3 OEM
- [ ] Chicotes T1 (JST VH 3 vias), woofer e preamp (7 vias) alcançam seus conectores
- [ ] Altura livre sobre C301/C302 confirmada contra a moldura

## Evidência

Gabarito: `build/fab/drafts/<commit>/` (rascunho, não liberado). Medidas OEM em
[mechanical/](../../mechanical/README.md).
