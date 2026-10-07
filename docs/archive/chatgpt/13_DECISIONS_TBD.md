# Decisões de projeto e pendências

## Decisões fechadas

- [x] Preservar woofer/gabinete/dutos.
- [x] Não reparar/copiar a arquitetura Classe AB como base da nova placa.
- [x] TPA3255 como power stage.
- [x] PBTL mono.
- [x] Fonte externa 36 VDC na Rev. A.
- [x] KiCad 10.x no Arch Linux.
- [x] Git obrigatório.
- [x] TPA3255EVM como golden reference.

## Pendências antes do schematic freeze

- [ ] Medir DCR real do woofer original.
- [ ] Confirmar que o woofer está mecanicamente saudável.
- [ ] Medir dimensões exatas da plate amp e furos.
- [ ] Selecionar fonte 36 V/5–6 A específica.
- [ ] Selecionar módulo DC/DC 36→12 V específico.
- [ ] Fechar topologia/valores do LPF 80 Hz por SPICE.
- [ ] Decidir se 3.3 V externo é necessário.
- [ ] Selecionar TVS e proteção reversa.
- [ ] Selecionar indutores 10 µH.
- [ ] Selecionar dissipador.

## Pendências antes do layout freeze

- [ ] Capturar EVM como referência visual.
- [ ] Calcular widths/vias de potência.
- [ ] Confirmar stackup da fábrica.
- [ ] Verificar assembly capability para exposed pad.
- [ ] Verificar footprints reais dos componentes TH.
- [ ] Fazer mechanical fit check com modelo 3D.

## Pendências antes de fabricar

- [ ] ERC.
- [ ] DRC.
- [ ] DFM.
- [ ] schematic peer review.
- [ ] layout peer review.
- [ ] BOM availability.
- [ ] Gerber review independente.
- [ ] Bring-up plan fechado.
