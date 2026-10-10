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

## Implicação para o TPA3255

A base do perfil é **paralela à PCB e voltada para o lado dos componentes**, igual ao
PowerPAD superior do TPA3255 DDV. O adaptador D-013 pode ser um **bloco reto** (cobre
ou alumínio) entre o PowerPAD e a base, sem dobra em L, desde que o TPA fique na
faixa da PCB em frente à base (65 mm ao longo do perfil × até 33 mm a partir do
backplate). A espessura do bloco é a distância PCB→base menos a altura do
encapsulamento DDV e a camada de interface térmica.

Correção: a versão anterior deste arquivo, baseada só no desenho da p.17, concluía
que a face do perfil era perpendicular à PCB e pedia adaptador em L. As fotos
mostram a base paralela à PCB.

## Ainda falta (só cotas locais)

1. Distância da superfície da placa principal (lado dos componentes) até a face
   externa da base do perfil U.
2. Altura da borda inferior da placa principal acima da face interna do backplate.
3. Posição do perfil ao longo da placa: distância de uma borda da placa até uma
   ponta do perfil.
4. Rosca dos dois furos de ancoragem (M3 ou M4) e contorno/furos da placa principal.
