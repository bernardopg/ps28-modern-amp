# BOM

Seleção atual do core: `kicad/core-selected/selected-bom.csv` e `core-manifest.json`.
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
