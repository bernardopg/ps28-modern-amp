# Bloco térmico do TPA3255 (D-031)

Peça única de alumínio (6061/6063 ou barra comercial equivalente) que leva o calor do
PowerPAD superior do U1 até a perna do perfil U original. Modelo: `thermal-block.stl`
(gerado por `scripts/blender_thermal_block.py`); vistas em
`../docs/images/thermal-block.png` e `thermal-block-bottom.png`.

## Cotas (referencial da PCB, mm)

x ao longo da placa, y em direção à perna do perfil (face da perna em y = 68),
z a partir da face superior da PCB.

| Elemento | Cota |
|---|---|
| Corpo | 53 × 13 × 10: x 64–117, y 54–67, z 3–13 |
| Pedestal (encosta no PowerPAD) | 8 × 5,2: x 86,5–94,5, y 57,9–63,1, de z 1,25 até o corpo |
| Furos de fixação na PCB | 2 × M3 roscado por baixo, prof. 8 (broca 2,5): x 79 e 102, y 60,5 |
| Furos laterais para a perna | 2 × oblongo 3,4 × 6,4 (±1,5 em z), passante em y: x 70,7 e 110,3, z 6,35 |
| Rebaixo dos laterais | Ø6,5 × 3 na face y = 54 (cabeça M3 Allen) |

Alívio de 3 mm sob o corpo: só SMD baixo (R/C/D/U, até ~2 mm) fica embaixo. O
pedestal é o único contato com a placa. O TPA3255 DDV tem 1,2 mm máx. (SLASEA8A,
desenho DDV), por isso o pedestal fica em z 1,25.

## Montagem

1. Pasta térmica fina no PowerPAD (SLASEA8A §7.4 caracteriza 0,7 W/m·K, 2 mil).
2. Bloco sobre o U1; dois parafusos **M3×12** por baixo da PCB (H5/H6, furos
   metalizados em GND) com arruela de pressão; apertar alternado e leve até o
   pedestal assentar. Sem espaçador: quem define a altura é o pedestal.
3. Gap pad térmico isolante de 1,0 mm (≥3 W/m·K) entre a face y = 67 do bloco e a
   perna do perfil (folga nominal 1 mm, absorve a tolerância da montagem).
4. Dois parafusos **M3×16** pelos oblongos até os furos roscados originais dos TO-3P;
   apertar só até comprimir o gap pad. Não usar o filme isolante antigo dos TO-3P.

O bloco fica em GND pelos parafusos de fixação (SLASEA8A: "PowerPad — Ground,
connect to grounded heat sink"). O perfil continua flutuante atrás do gap pad; a
trança em J6 é opcional para aterrá-lo (EMI).

## Estimativa térmica (cálculo, não medida)

Perda do TPA3255 em 150 W contínuos ≈ 15 W; música real fica perto de 1/8 da
potência (≈ 4–5 W). Cadeia junção → perfil: 2,4 °C/W (SLASEA8A §7.4, com
dissipador e pasta) + bloco ≈ 0,3 + gap pad ≈ 0,5 = 3,2 °C/W. Com o perfil a
50 °C (ele já dissipava a classe AB original, bem mais que 15 W): Tj ≈ 50 + 15 × 3,2
≈ 98 °C em seno contínuo de potência máxima, abaixo do aviso OTW. Confirmar na bancada (BENCH-002) com termopar no bloco.
