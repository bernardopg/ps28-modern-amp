# Fechamento das 190 posições — 2026-10-16

As **190 posições com fabricante ausente ou MPN em texto genérico foram resolvidas**.
A seleção atual cobre as **235 posições de compra** da PCB: fabricante, código
completo, footprint, fonte técnica e notas de seleção. A contagem não representa
235 modelos diferentes: vários componentes usam o mesmo código.

- [Seleção canônica por referência](../bom/system-candidate-selection.csv).
- [Inventário derivado do esquema atual](../bom/system-candidate-inventory.csv).
- [Acessórios de montagem](../bom/system-candidate-accessories.csv): fusível,
  jumper e botão momentâneo externo; separados dos componentes soldados à PCB.
- [Evidência com hashes](../tests/reports/bom-closeout-2026-10-16.json).

O esquema, as propriedades da PCB, o manifesto e o gerador de integração usam os
mesmos dados. O gerador foi exercitado em diretório temporário, sem regenerar o
cobre do produto. Testes conferem todas as referências selecionadas e decodificam
os valores dos resistores de precisão, incluindo a notação correta 6K04/1K5/8K87.

## Escolhas e correções

| Grupo | Resultado |
|---|---|
| Resistores de supervisão/janelas | YAGEO RT, 0,1%, 25 ppm/K, mantendo valores e tamanhos; R320 usa 1206/200 V para PVDD |
| Resistores comuns | Vishay CRCW no tamanho real; 2512/1 W em R601/R603; R301 PR02 4,7 kΩ/2 W com terminais Cu |
| Capacitores | Códigos completos para dielétrico, tensão e tamanho; reaproveitadas seleções já usadas no núcleo quando compatíveis |
| C109 | WIMA MKS2C042201K00JSSD, 2,2 µF/63 V; corpo W7,2 mm e courtyard corrigidos, sem mudar pads, posição ou conexões |
| C301/C302 | Rubycon 63USC4700MEFCSN30X30; descrição corrigida: total de bulk **10.760 µF**, acima do alvo D-031 de 10 mF e abaixo dos 13.600 µF OEM |
| Diodos/transistores/ICs | Removidas descrições do campo MPN; fabricante e sufixos de pedido explícitos; requisitos ficam nas notas |
| L301 | MSS1246T-683MLC: embalagem C atual substitui código B histórico, mantendo a seleção elétrica de 68 µH |
| F301 | O componente na PCB é o porta-fusível Schurter 0031.8201; o Littelfuse 021806.3MXP T6,3 A entra como acessório separado |
| J401/JP701 | Headers Sullins de 2/3 pinos; botão externo e shunt separados; sem autorização para furar o chassis |
| K501 | Mantido o código de fabricante **G6K-2F DC12**, incluindo espaço da tensão de bobina; o auditor rejeita descrições adicionais |

Para C109 foi usada a geometria da biblioteca KiCad correspondente ao corpo real.
Comparação estrutural integral confirmou que **cobre, pads, nets, posições e
rotações foram preservados**. A alteração geométrica intencional limita-se ao
corpo/courtyard/modelo de C109; DRC confirma ausência de novas colisões.

Fontes principais consultadas:
[WIMA MKS2](https://www.wima.de/wp-content/uploads/media/e_WIMA_MKS_2.pdf),
[YAGEO RT](https://www.yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L),
[Vishay CRCW](https://www.vishay.com/docs/20035/dcrcwe3.pdf),
[Vishay PR01/02/03](https://www.vishay.com/docs/28729/pr010203.pdf),
[Schurter OGN](https://www.schurter.com/en/datasheet/OGN),
[Coilcraft MSS1246T](https://www.coilcraft.com/getmedia/dec41de3-f4b7-4c07-b144-cc21921ccfd5/mss1246t.pdf).
Fontes específicas dos demais componentes constam na seleção CSV.

## Verificação e entrega

ERC **0**, DRC **0**, conexões abertas **0**, paridade esquema/PCB **0**.
Continuam **263 componentes no esquema, 269 footprints na PCB**, sem componente
do esquema ausente; H1–H6 são mecânicos. J3/J4/R7/R8 permanecem DNP; pads de teste
não são peças de compra. A seleção de 235 posições exclui esses itens.

`make fab` passa a incluir `purchase-bom.csv` com fabricante/MPN/fontes e
`accessories.csv`, além da BOM nativa, CPL, Gerbers, furos e desenhos existentes.
`purchase-cpl-front.csv`/`purchase-cpl-back.csv` contêm exatamente as mesmas
235 referências, sem repetição; ainda incluem THT para revisão de montagem e não
são declarados como CPL pronto para upload a JLCPCB.
O resumo bloqueia exportação completa se reaparecer MPN/fabricante pendente.
As mídias foram atualizadas para o corpo correto de C109. Relatórios de referência
anteriores permanecem históricos; o ponteiro de evidência atual aponta ao fechamento.

## O que continua fora deste fechamento

Seleção de códigos concluída **não equivale a cotação ou liberação de fabricação**.
Estoque/lifecycle de toda a BOM, catálogo LCSC/JLCPCB, alternativas aprovadas,
rotação/pin1/CPL do montador, DFM global, fit físico e gates humanos seguem nas
respectivas tasks. Não foi afirmado estoque disponível para todos os códigos.

C403 é 2,2 µF/16 V X7R de 0603 usado em EVM TI; antes da liberação de compra,
confirmar capacitância efetiva mínima de 1 µF na saída 3,3 V do LP2985 incluindo
bias, tolerância, temperatura e envelhecimento. C401 e os MLCCs de potência também
exigem conferir capacitância efetiva no ponto de operação. Tolerâncias nominais
não comprovam comportamento dinâmico. Inrush/fusível, ripple, térmica, EMI e tempos
de proteção continuam na bancada. Botão externo de 16 mm exige conferência mecânica;
seus terminais de LED ficam sem ligação. Chicotes, fan e ferragens OEM/auxiliares
exigem conferência de montagem conforme D-032 e documentos mecânicos existentes.

Nenhum software adicional foi necessário. Nenhuma compra, pedido, upload a fábrica,
modificação física ou energização foi realizado. FAB-001 continua aberta para as
qualificações e aprovação G3 que seu critério de aceite exige.
