---
id: MECH-001
title: Medir plate e modelar envelope
status: Blocked
milestone: M1
sprint: S02
depends_on: SYS-001
updated: 2026-10-07
---

# MECH-001 — Medir plate e modelar envelope

## Objetivo

Medir plate e modelar envelope, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Dimensões/furos/chicotes/vedação documentados
- [ ] CAD/desenho 1:1 e espaço dissipador confirmados

## Evidência

Pendente. Não marcar critérios sem evidência.

## Incremento de integração original
D-013 seleciona gabinete/plate/dissipador originais com adaptador de cobre superior.
Modelo de envelopes e orçamento térmico em mechanical/ e docs/selected-core.md.
D-014 fixa sistema de dissipação e mounting points OEM por decisão do proprietário.
Correção: manual p.15–16 dimensiona plate/carçaça/dissipadores/suportes; p.17–18
contém main PCB104-a05064a00-e. Referência em mechanical/original-board-reference.md.
Pendência para fechamento: reconstruir gabarito com escala verificada e entrecentros
conferidos na placa original; pedir somente cotas locais não recuperáveis do documento.
Não bloquear desenvolvimento por um levantamento novo de todo o gabinete.
Contorno145×95, posição deU1/J6 e sapata atuais são propostas, não interfaces OEM.
Não usinar/perfurar/fabricar por esse modelo; todos critérios físicos continuam pendentes.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
