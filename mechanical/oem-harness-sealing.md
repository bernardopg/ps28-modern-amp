# Chicotes e vedação OEM — fotos e respostas do proprietário (2026-10-10)

Dez fotos fora do Git. Leitura visual; passos sem paquímetro ficam como *provável*.

## Conectores da placa principal

| Chicote | Conector | Lado da placa | Situação |
|---|---|---|---|
| T1 secundário (vermelho–preto–vermelho) | 3 vias, passo ≈ 3,96 mm (JST VH provável), 20 AWG | header branco no canto junto do suporte L e do T1, perto dos Y-caps verdes | medido antes (`transformer-reuse.md`) |
| Entre placas (preamp ↔ principal) | 7 vias, fios preto/branco, passo 2,5 mm (JST XH provável) | J101/P101, na borda livre da placa, centro da borda | passo medido; pinagem a medir |
| Woofer (vermelho/preto torcido, termorretrátil) | 2 vias, passo 4 mm (≈ 3,96, JST VH provável), terminais de lâmina | header de 2 pinos ao lado do relé UDH-SS-124D, junto do suporte L | polaridade a medir |

Painel (LEVEL, CROSSOVER, PHASE, RCA) fica na **placa do preamp**, ligada à
principal só pelo chicote de 7 vias. AC e chave POWER não entram na placa principal.

## Vedação e ventilação

- Backplate × gabinete: borracha de 1–2 mm.
- Há fiação passando da carcaça para o volume do woofer.
- Ventilação: apenas a inferior, pelos tubos do gabinete (dutos do reflex).
  Não há fluxo de ar dedicado à eletrônica: o calor sai pelo dissipador externo.

## Implicações para a placa nova

- Reaproveitar os três chicotes sem emenda: T1 (VH 3 vias), woofer (2 vias) e
  7 vias entre placas, nos mesmos cantos da placa: T1 e woofer junto do suporte L.
- O woofer sai pelo relé de proteção original; na placa nova SPK± vão direto do
  filtro LC ao header (ou por relé novo de proteção DC, REQ-007).
- Não abrir furos novos na carcaça nem mexer na vedação (D-014).

## Chicote de 7 vias — resistência para GND (2026-10-10)

Unidade desligada, chicote desconectado, ponta preta no CT de T1, lado da placa
principal (J101), escala 2000 Ω. "1" no display = acima da escala (> 2 kΩ).

| Pino | Fio | Leitura | Interpretação provável |
|---|---|---|---|
| 1 | branco | 755 Ω | sinal (entrada de áudio do amplificador?) |
| 2 | preto | > 2 kΩ | alta impedância: controle ou sinal |
| 3 | preto | 475 Ω | sinal ou alimentação via resistor |
| 4 | preto | 0,5 Ω | **GND** |
| 5 | preto | sobe de ~1900 até > 2 kΩ | capacitor carregando: **trilho de alimentação** com bulk grande |
| 6 | preto | pico de 150 Ω, depois > 2 kΩ | capacitor carregando: trilho com bulk menor |
| 7 | preto | > 2 kΩ | alta impedância: controle ou sinal |

Hipótese, não conclusão: 4 = GND, 5 e 6 = alimentações do preamp (provavelmente
±), 1 = áudio. Confirmação depende das tensões ligado.
## Falta medir

1. Qual fio do woofer é o + (marca no terminal do woofer).
2. Pinagem do chicote de 7 vias (resistência e tensão por pino).
