# Fabricação e PCBA — estratégia JLCPCB/PCBWay

## JLCPCB

Em setembro de 2026 a JLCPCB informa, para Economic PCBA, setup de aproximadamente US$8.18 e stencil de aproximadamente US$1.53, além de montagem e componentes. Componentes classificados como Extended podem adicionar custos de feeder/setup; confirme no quote atual.

## Estratégia para a Rev. A

1. PCB pequena o suficiente para minimizar custo, sem sacrificar layout.
2. SMD preferencialmente em um único lado.
3. TPA3255 montado pela fábrica por causa do PowerPAD.
4. Componentes TH grandes podem ser soldados manualmente:
   - eletrolíticos bulk;
   - indutores;
   - RCA;
   - potenciômetro;
   - conectores;
   - fusível.
5. Não trocar componente crítico por Basic part inferior apenas para economizar centavos.

## Arquivos necessários

- Gerber.
- Drill.
- BOM CSV.
- CPL / Pick-and-place.
- Drawing/assembly notes.
- PDF do schematic congelado.
- versão/tag Git correspondente.

## Checklist antes do upload

- [ ] Board outline fechado.
- [ ] footprints conferidos fisicamente.
- [ ] orientation pin 1 conferida.
- [ ] TPA3255 footprint e exposed pad revisados.
- [ ] polarity de eletrolíticos/diodos conferida.
- [ ] BOM designators batem com CPL.
- [ ] nenhum componente DNP enviado como populated.
- [ ] revisão e data impressas na silkscreen.

## Cupons

A JLCPCB publica pacotes de cupons para novos clientes, mas valores e elegibilidade podem variar por país, endereço e método de pagamento. Em setembro de 2026 a página de boas-vindas citava pacote nominal de até US$123, incluindo cupons específicos para PCB, SMT e frete. Trate isso como desconto eventual, não como premissa de orçamento.

## PCBWay

Use como segunda cotação, principalmente se:

- JLC não tiver componente crítico;
- montagem especial ficar mais barata;
- houver exigência mecânica/material específica.

## Budget de protótipo

Não usar uma estimativa única antes do quote. Para uma Rev. A montada em baixa quantidade, reserve margem para:

- 5 PCBs;
- 2–3 PCBA;
- componentes TH extras;
- frete/impostos;
- eventual Rev. B.
