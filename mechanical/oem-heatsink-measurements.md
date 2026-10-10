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

## Implicação para o TPA3255 — achado

No desenho de componentes da placa original (manual p.17), Q107/Q108 (TO-3P) aparecem
de perfil, em pé, numa fila de ≈ 65 mm: **a face do perfil U onde eles encostam é
perpendicular à PCB**. O TPA3255 DDV tem o PowerPAD **no topo do encapsulamento**, que
fica paralelo à PCB. Ele **não encosta direto** no perfil U com a placa na orientação
original. Isso é inferência do desenho e da descrição, a confirmar por foto.

Isso é compatível com D-013 (adaptador de cobre no PowerPAD superior), mas o
adaptador precisa **virar 90°**: uma face plana sobre o TPA, paralela à PCB, e outra
parafusada na face do perfil U, perpendicular à PCB. Não muda backplate nem
dissipador (D-014). Alternativa, se o adaptador em L não couber: placa-filha
vertical só com o TPA e seu desacoplamento, PowerPAD direto no perfil.

## Ainda falta (só cotas locais)

- Foto do perfil U montado com a placa original, mostrando qual face toca os TO-3P
  e qual perna toca o backplate.
- Distância da face do perfil (onde estão os TO-3P) até a superfície da PCB e a
  borda da PCB mais próxima do backplate.
- Contorno e furos de fixação da placa original (suportes L 89 × 9 × 1,6 e suporte
  11,75 × 8,5 × 12,5 da BOM): posição em relação ao perfil U.
- Rosca/diâmetro dos dois furos de ancoragem do perfil (M3 ou M4).
