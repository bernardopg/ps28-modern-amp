# Dissipador, perfil U e backplate — medidas do proprietário (2026-10-10)

Medidas manuais do proprietário na unidade original, em mm. Dados estruturados em
`oem-heatsink-measurements.json`. **Medida**, salvo quando marcado *calculado* ou
*hipótese*. Não libera furação nem fabricação.

## Coordenadas

Referencial do backplate visto **de fora** (lado do dissipador): origem no canto
superior esquerdo, x para a direita, y para baixo. Visto de dentro, x espelha
(x_interno = 200 − x).

| Item | x | y | Origem |
|---|---|---|---|
| Backplate | 0…200 | 0…300 | medida |
| Dissipador externo (118 × 72 × 25, 8 aletas) | 39…111 | 48…166 | medida |
| Furo central superior | 75 *(hipótese)* | 88,0 *(calc.)* / 88,9 *(medida)* | medida + hipótese |
| Furo central inferior | 75 *(hipótese)* | 123 | medida |
| Furos das aletas 2 e 6 | 52,5 / 88,5 *(hipótese)* | 63 / 106 ou 108 / 151 | medida + hipótese |
| Perfil U (comprimento 65 na vertical) | ≈ 75 ± 16,5 *(hipótese)* | 73 (ou 73,9)…138 | calculado |

x dos furos assume aletas igualmente espaçadas (passo 72/8 = 9 mm): o centro da 4ª
ranhura cai em 75, no meio do dissipador. Conferir com régua.

## Conferências

- Dissipador: 39 + 72 + 89 = 200 e 48 + 118 + 134 = 300. Fecha com o backplate.
- Contra o manual (p.16, BOM): dissipador 117,5 × 71,5 × 25 e backplate 300 × 200,
  dentro de 0,5 mm.
- Perfil U medido 65 × 33 × 30 contra BOM 323-AL-00020-0LAE **65 × 32 × 31** (p.15):
  diferença ≤ 1 mm, dentro da resolução de régua.
- Furos centrais: 75 − 40 = 35 no dissipador e 65 − 15 − 15 = 35 no perfil. Coerentes.
- Furo superior: 88,0 calculado contra 88,9 medido do topo do backplate. Diferença de
  0,9 mm; usar o furo do dissipador/perfil como referência, não a borda do backplate.
- Furo intermediário das aletas: 58 mm de uma das bordas, sem saber qual. Com 15 e
  103 nas pontas, o meio exato seria 59; fica 106 ou 108 do topo do backplate.

## Orientação confirmada por fotos (2026-10-10)

Quatro fotos do proprietário, fora do Git: unidade aberta de lado, de cima e
backplate por fora.

- A placa principal fica **em pé**, perpendicular ao backplate, presa por suporte
  em L de alumínio (BOM 362-FE-00013) aparafusado no backplate.
- Há **duas placas**: a principal (potência), junto do perfil U, e a do preamp, do
  outro lado, atrás dos controles LEVEL/CROSSOVER/PHASE e das RCA.
- O perfil U fica deitado no backplate, com pasta térmica: uma perna no backplate e
  a base em pé, **paralela à placa principal**, voltada para ela. A outra perna fica
  paralela ao backplate, a ≈ 33 mm dele.
- Os transistores de potência ficam entre a placa e o perfil, presos ao perfil.

## Placa principal e perfil U — medidas do proprietário (2026-10-10, 2ª rodada)

Referencial da placa principal: em pé, perpendicular ao backplate; "superior" e
"inferior" são as bordas perpendiculares ao backplate (instalado).

| Medida | Valor | Situação |
|---|---|---|
| Base do perfil U | face externa **apoiada na PCB** (lado dos componentes); face interna a 6 mm | coerente: base 6 mm = espessura das pernas |
| Perfil ao longo da placa | 38 mm da borda superior, 55 mm da inferior | ⇒ comprimento da placa **158 mm** (38 + 65 + 55) |
| Furos de fixação da placa | M3, centros a 10 e 53 mm do backplate, 4,5 mm da borda, nas duas bordas (4 furos) | coerente com dois suportes L (BOM 2 × 89 × 9 × 1,6) |
| Furos de ancoragem do perfil | M3 | — |
| "111 mm" | ver abaixo | **ambígua** |

Conferências que fecham:

- Seção do U: 21 + 2 × 6 = 33 (largura externa) e base de 6 mm igual às pernas.
- Posição no backplate: perfil em y 73…138 (furos 88/123 menos 15) ⇒ borda superior
  da placa em y ≈ 35 e inferior em y ≈ 193 (y = 0 no topo do backplate).
- Comprimento 158 mm contra o contorno inferido do `core-oem-refined` (153 mm, a
  partir do desenho da p.17): diferença de 5 mm (3 %). O contorno inferido deve ser
  substituído pelo medido.

### 3ª rodada — contorno e posição da placa

| Medida | Valor |
|---|---|
| Placa principal | **154 × 81 mm** (ao longo do backplate × profundidade), 1 mm de espessura |
| Face dos componentes → borda lateral do backplate | 90 mm de um lado, 109 mm do outro |

Conferências:

- 90 + 1 + 109 = 200 mm: fecha com a largura do backplate.
- Lado dos 90 mm: no referencial de fora, a face dos componentes fica em x = 90. As
  pernas do perfil (30 mm) vão da face até x = 60, e os furos centrais em x = 75
  caem **no meio da perna** (15 mm da face). O outro lado (x = 110) deixaria os furos
  a 35 mm da face, fora da perna de 30 mm. Isso confirma a hipótese x = 75 e mostra
  que os 90 mm são medidos da borda do lado do dissipador (39 mm).
- Profundidade 81 mm: cabe na carcaça traseira de 102 mm (BOM p.16); furos de fixação
  a 10 e 53 mm do backplate ficam dentro. O contorno inferido do desenho (79,1 mm)
  errou por 1,9 mm.
- Comprimento 154 mm contra o inferido 153 mm: 1 mm.
- A medida "111 mm" da rodada anterior fica substituída por estas.

**Única discrepância:** 38 + 65 + 55 = 158 mm, mas a placa tem 154 mm. Faltam 4 mm
nas folgas do perfil até as bordas. Pelos furos do dissipador (perfil em y 73…138),
borda superior a 38 mm do perfil ⇒ placa em y 35…189 e folga inferior 51 mm; ou folga
inferior 55 mm ⇒ placa em y 39…193 e folga superior 34 mm. Conferir qual das duas
folgas (38 ou 55) está certa.

Espessura de 1 mm é incomum (padrão 1,6 mm): a placa nova pode usar 1,6 mm se a
fixação nos suportes L e a altura dos terminais permitirem; conferir na montagem.

## Implicação para o TPA3255 — corrigida

Com a base do perfil **encostada** na PCB, não há folga entre placa e base para o TPA.
Os TO-3P originais ficam deitados sobre a perna externa (a 27…33 mm do backplate),
cuja face fica **perpendicular à PCB**, como no desenho da p.17. A leitura da 1ª
rodada de fotos (base paralela com folga) estava errada.

Consequências para o layout:

- **Keepout** na PCB: faixa de 33 mm a partir do backplate × 65 mm (y 73…138 no
  backplate, 38…103 mm da borda superior da placa), sem componentes no lado de cima.
- Contato térmico do TPA3255 DDV (PowerPAD no topo): TPA logo além da perna externa,
  eixo longo ao longo do perfil, e **bloco de alumínio/cobre** apoiado no PowerPAD com
  uma face lateral prensada na face da perna (onde ficavam os TO-3P). O calor sai pela
  face de cima do TPA e entra na perna pela lateral do bloco: um bloco retangular
  basta, sem dobra, desde que encoste nas duas faces. Fixação pelos furos M3 que
  prendiam os TO-3P (a medir) ou por grampo; folga de terminais ≥ 1 mm da perna.
- Altura da face da perna: 0…30 mm acima da PCB; comprimento útil 65 mm.

## Ainda falta (só cotas locais)

1. Qual folga está certa: 38 mm (borda superior) ou 55 mm (borda inferior).
2. Furos dos TO-3P na perna externa: quantidade, rosca e posição ao longo do perfil.
