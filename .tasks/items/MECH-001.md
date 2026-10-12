---
id: MECH-001
title: Medir plate e modelar envelope
status: Blocked
milestone: M1
sprint: S02
depends_on: SYS-001
updated: 2026-10-12
---

# MECH-001 — Medir plate e modelar envelope

## Objetivo

Medir plate e modelar envelope, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Dimensões/furos/chicotes/vedação documentados
- [ ] CAD/desenho 1:1 e espaço dissipador confirmados

## Evidência
2026-10-12: proprietário informou capacitor de 45 mm + pouco mais de 30 mm
até a moldura plástica. Cerca de 75 mm locais; envelope de 52 mm deixa ~23 mm.
Altura nessa região original resolvida para estudo, sem extrapolar à placa toda
ou liberar fit/térmica. Dez fotos adicionais mostram conector T1 de três vias
vermelho–preto–vermelho e trava; fabricante/MPN ainda não confirmados. Registro:
`mechanical/owner-clearance-20261012.json`, `mechanical/oem-harness-sealing.md`.
Não repetir pedido dessas fotos/folga; critérios restantes continuam abertos.

2026-10-10: medidas do proprietário de backplate, dissipador externo (posição, 8 furos)
e perfil U (65 × 33 × 30, furos a 35 mm) em `mechanical/oem-heatsink-measurements.md`;
somas fecham com 200 × 300 e com a BOM do manual (≤ 1 mm). Placa principal 154 × 81 × 1 mm, face dos componentes a 90 mm da borda lateral
(fecha 200 mm e põe os furos do perfil no meio da perna), 4 furos M3 (10/53 mm do
backplate, 4,5 mm da borda). Base do perfil encostada na PCB: keepout 33 × 65 mm e TPA com bloco
térmico prensado na perna externa. Posição: placa y 35…189 no backplate, perfil 38/51 mm das bordas (fita, ~1 mm).
Furos TO-3P: 2, a 12,7 mm das pontas e 6,35 mm da borda livre da perna
(39,6 mm entre centros; 50,7/90,3 mm da borda superior da placa). Rosca M3. Chicotes/vedação em `mechanical/oem-harness-sealing.md`.
Passos: 7 vias 2,5 mm, woofer 4 mm. Pendente: polaridade do woofer, pinagem
do 7 vias e gabarito 1:1.
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
