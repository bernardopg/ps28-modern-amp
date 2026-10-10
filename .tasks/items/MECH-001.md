---
id: MECH-001
title: Medir plate e modelar envelope
status: Blocked
milestone: M1
sprint: S02
depends_on: SYS-001
updated: 2026-10-10
---

# MECH-001 — Medir plate e modelar envelope

## Objetivo

Medir plate e modelar envelope, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Dimensões/furos/chicotes/vedação documentados
- [ ] CAD/desenho 1:1 e espaço dissipador confirmados

## Evidência

2026-10-10: medidas do proprietário de backplate, dissipador externo (posição, 8 furos)
e perfil U (65 × 33 × 30, furos a 35 mm) em `mechanical/oem-heatsink-measurements.md`;
somas fecham com 200 × 300 e com a BOM do manual (≤ 1 mm). Fotos confirmam placa
principal em pé e base do perfil U paralela a ela: adaptador D-013 pode ser bloco reto.
Duas placas no OEM (potência e preamp). Faltam distância PCB→base, altura da borda
inferior da placa, posição do perfil ao longo da placa, rosca e contorno/furos.
Critérios seguem abertos.

## Incremento de integração original
D-013 seleciona gabinete/plate/dissipador originais com adaptador de cobre superior.
Modelo de envelopes e orçamento térmico em mechanical/ e docs/selected-core.md.
D-014 fixa sistema de dissipação e mounting points OEM por decisão do proprietário.
Correção: manual p.15–16 dimensiona plate/carçaça/dissipadores/suportes; p.17–18
contém main PCB104-a05064a00-e. Referência em mechanical/original-board-reference.md.
Pendência para fechamento: reconstruir gabarito com escala verificada e entrecentros
conferidos na placa original; pedir somente cotas locais não recuperáveis do documento.
Não bloquear desenvolvimento por um levantamento novo de todo o gabinete.
Contorno145×95 pertence ao draft/B preservado, não a uma validação de interfaces OEM.
A candidata `core-oem-refined/` usa contorno **inferido**153×79,1mm, J6 pad de
trança GND e seis features reservadas em quatro camadas, sem furos inventados.
Galeria 3D nativa atualizada em `docs/images/kicad-3d/`; nenhum mount/layout alterado
nesta atualização. U1 segue sem modelo disponível, impedindo confirmar por imagem
altura/folga do contato PowerPAD/dissipador; fit/térmica/cotas locais continuam TBD.
Ver `docs/development-status.md`. Status Blocked e critérios físicos preservados.
Não usinar/perfurar/fabricar por esse modelo; todos critérios físicos continuam pendentes.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
