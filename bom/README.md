# BOM

## Inventário atual — 2026-10-16

Fonte atual: `system-candidate-inventory.csv`, extraído do esquema único por
`python3 scripts/audit_final_design.py`. Contém 263 referências, DNP e itens sem
compra separados; **235 posições de compra, zero com fabricante/MPN pendentes**.
As 190 pendências anteriores foram resolvidas na seleção canônica
`system-candidate-selection.csv`, sincronizada com esquema/PCB/gerador.
Acessórios estão em `system-candidate-accessories.csv`. Não é compra aprovada
nem CPL qualificado. Fechamento: [relatório](../docs/bom-closeout-2026-10-16.md).
Correções de MPN, fontes e pendências em
[`docs/final-design-review-2026-10-16.md`](../docs/final-design-review-2026-10-16.md).

## Histórico do núcleo e seleção inicial

Seleção atual: `system-candidate-selection.csv` (235 posições de compra).
MPNs, fontes e footprints incluídos; **seleção para validação, não compra/liberação**.
J6 é feature GND da PCB, não item de compra; hardware em mechanical/.
Disponibilidade/lifecycle, capacitância efetiva, ripple/temperatura e DFM não fechados.
Detalhes e limites em docs/selected-core.md. Rev. A — candidatos, não comprar

TPA3255DDV/DDVR package a confirmar; NE5532 ou alternativa validada;
DC/DC 36→12 V, fonte 36 V, proteção reversa/TVS/fusível, LC, bulk e dissipador TBD.
Contagem dos indutores depende do baseline escolhido. BOM original permanece no arquivo.
BOM final deve vir do KiCad e conter Reference, Quantity, Value, Footprint,
Manufacturer, MPN, Supplier, Supplier_PN, DNP, lifecycle e referência de aprovação.
Preços em cotação separada, não no valor elétrico. Ver docs/procurement.md.
