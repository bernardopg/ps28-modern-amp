# Fabricação e release — bloqueados até G3
Comparar JLCPCB/PCBWay com a mesma stackup, cobre, quantidade e montagem.
Preço/cupom antigo não é orçamento. Exposed pad montado por processo adequado;
TH pode ser manual após avaliação de acesso/temperatura/retrabalho.

Pacote por commit/tag: Gerber, drill, BOM/MPN/DNP, CPL, PDF schematic,
stackup/fab notes, assembly drawing, README com checksum e evidências ERC/DRC/paridade.
Conferir outline, pin 1/rotação, polaridade, PowerPAD/pasta, designators BOM↔CPL,
footprints reais e Gerber viewer independente. Gerar em build/, liberar cópia revisada
em manufacturing/releases/ somente com aprovação humana explícita.
Não há target automático de upload/pedido. Não inventar capacidade de fábrica.
