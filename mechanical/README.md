# Mecânica

D-014 mantém gabinete, plate, suportes, chicotes e dissipação OEM. A placa única
se adapta ao conjunto, sem nova furação do plate. Medidas do proprietário já
existem: PCB 154×81 mm, perfil U, fixações e região dos eletrolíticos. Não pedir
novo levantamento completo nem tratar modelos de estudo como medição.

- [Fit térmico atual, desenho e limites](thermal-block.md): bloco/apoios/calços,
  contato superior DDV, cotas OEM corrigidas e orçamento 1D; não é liberação.
- [Parâmetros verificáveis](thermal-fit.json) e
  [evidência](../tests/reports/thermal-fit-review.json).
- [Referência do manual](original-board-reference.md),
  [medidas do perfil](oem-heatsink-measurements.md),
  [chicotes e vedação](oem-harness-sealing.md),
  [conferência física](measurement-request.md).

Restam conferências **locais**: folga no bloco/verso, rosca e calços/TIM na placa
montada; depois ensaio térmico aprovado em BENCH-002. O caminho dissipador→ambiente
não foi medido. Gabarito 1:1 e conferência de montagem precedem fabricação/montagem.
Os modelos nominais preservam referências/limites; não são CAD de fabricante nem
comprovam tolerâncias. Peças mecânicas e TIM ainda exigem BOM/MPN e OK do proprietário.
