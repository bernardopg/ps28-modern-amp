# Fabricação e release — bloqueados até G3

## Especificação da placa (D-039)

| Parâmetro | Valor |
|---|---|
| Camadas / espessura | 4 / 1,6 mm (stackup padrão JLCPCB JLC04161H-7628) |
| Cobre externo / interno | 1 oz (35 µm) / 0,5 oz; confirmar contra correntes em PCB-002 |
| Acabamento | ENIG (planicidade para o HTSSOP-44 0,635 mm e pads largos) |
| Máscara / serigrafia | verde / branca |
| Montagem | SMD pela JLCPCB; THT grandes (C301/C302, D301/D302, conectores) à mão |

Comparar JLCPCB/PCBWay com a mesma stackup, cobre, quantidade e montagem.
Preço/cupom antigo não é orçamento. No TPA3255DDV, PowerPAD é SUPERIOR:
reflow dos 44 leads, dissipador aterrado e interface mecânica/térmica correta,
sem exposed-pad inferior para soldar ou inspecionar por raio-X como premissa;
TH pode ser manual após avaliação de acesso/temperatura/retrabalho.

Pacote por commit/tag: Gerber, drill, BOM/MPN/DNP, CPL, PDF schematic,
stackup/fab notes, assembly drawing, README com checksum e evidências ERC/DRC/paridade.
Conferir outline, pin 1/rotação, polaridade, PowerPAD/pasta, designators BOM↔CPL,
footprints reais e Gerber viewer independente. Gerar em build/, liberar cópia revisada
em manufacturing/releases/ somente com aprovação humana explícita.
Não há target automático de upload/pedido. Não inventar capacidade de fábrica.
