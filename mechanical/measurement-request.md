# Conferência final da interface OEM — não novo levantamento do gabinete

O proprietário definiu usar o mesmo sistema de dissipação e os mesmos mounting points.
A fonte principal é a [documentação da placa original](original-board-reference.md):
manual p.8/15–18, plate300×200×2,5, carcaça198×298×102, dissipadores e suportes OEM.
Não pedir todas essas dimensões novamente nem criar uma montagem independente.

## Quando houver gabarito reconstruído
- Conferir na placa/suportes originais que contorno, recortes e todos os mounting points
  coincidem. O desenho do PDF não declara escala1:1; impressão100% não prova a escala.
- Verificar somente as folgas locais afetadas pela placa nova: capacitores, indutores,
  chicotes e contato superior do TPA3255. A seleção atual de bulk tem corpo máximo42mm;
  com respiro proposto5mm exige47mm no lado dos componentes, NÃO um dado OEM garantido.
- Se algum entrecentro/altura de contato não puder ser recuperado com escala consistente
  da documentação, pedir apenas essa cota local ou usar a placa original como gabarito.
- Preservar furação, suportes, vedação e barreiras do primário. Adaptar PCB/contato térmico
  ao OEM em vez de modificar plate/dissipação originais.

Unidade desconectada, capacitores descarregados e ausência de tensão verificada para
conferência física. Nenhuma medição energizada da rede é necessária para essa etapa.
J6 do draft é ponto GND interno, não um furo original; não copiar sua posição para o plate.
Mecânica não liberada para fabricação até a conferência do gabarito/contato/folgas.
