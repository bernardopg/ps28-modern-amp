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

Escala 20 kΩ: pinos 1, 3 e 5 sobem continuamente (capacitor em série ou para GND);
pino 2 > 20 kΩ (aberto); pino 4 0,00; pino 6 começa **negativo** e sobe para zero
(capacitor com carga residual negativa: trilho negativo); pino 7 flutua ao toque
(entrada de alta impedância, ex.: base/CMOS de controle).

Hipótese revisada: 4 = GND, 5 = +V, 6 = −V, 1 e 3 = áudio acoplado por capacitor,
2 e 7 = controle/sinal de alta impedância. Ainda 4 = GND, 5 e 6 = alimentações do preamp (provavelmente
±), 1 = áudio. Confirmação depende das tensões ligado.
## Chicote de 7 vias — tensões ligado (2026-10-10)

V DC contra o pino 4, volume no mínimo, sem sinal.

| Pino | Fio | V DC | Função provável |
|---|---|---|---|
| 1 | branco | 0,01–0,02 | áudio (acoplado, 0 V DC) |
| 2 | preto | −12,5 | controle (mute/standby?) ou trilho derivado — a confirmar |
| 3 | preto | −15,8 | **−15 V** do preamp |
| 4 | preto | 0 | **GND** |
| 5 | preto | +15,5 | **+15 V** do preamp |
| 6 | preto | 0,01 | áudio ou retorno de sinal (acoplado) |
| 7 | preto | 0,00 | controle de alta impedância (auto-on/mute?) |

Conclusão: o preamp original é alimentado em **±15 V** pela placa principal. A placa
nova (D-021) só tem PVDD ≈ 42–50 V e AUX 12 V; reaproveitar o preamp exige gerar ±15 V.

### 2ª série ligado — LEVEL mínimo/médio/máximo (escala 200 V DC, sem sinal nas RCA)

Referência no GND da PCB (série 2; a série 1, no terminal preto do woofer, deu os
mesmos valores, então o SPK− original é GND — não vale para a placa nova, D-024).

| Pino | Mín. | Médio | Máx. | Leitura |
|---|---|---|---|---|
| 1 branco | −6,0…−7,8 | −6,9…−7,8 | −10,0…+9,4 | oscila; depende do LEVEL: **saída de áudio do preamp** |
| 2 | −12,6 | −12,6…−12,7 | −12,7 | estável: −12 V auxiliar ou bias de controle |
| 3 | −15,9 | −16,0 | −16,0 | **−15 V** |
| 4 | 0 | 0 | 0 | **GND** |
| 5 | +15,6 | +15,6 | +15,6 | **+15 V** |
| 6 | +0,01 | +0,1 | +0,1 | ≈ 0: retorno/entrada sem uso |
| 7 | 0 | 0 | 0 | ≈ 0: controle inativo |

- Pino 6 = +46,8 V uma vez (série 1, LEVEL médio), não reproduzido: provável ponta
  escorregando para um trilho do amplificador original (≈ ±48 V). Não é função do pino.
- Pino 1 com −6…−8 V "DC" e oscilação crescente com LEVEL, sem sinal: o multímetro
  DC lendo ruído/zumbido de RCA aberta amplificado, ou offset DC real na saída do
  preamp. A primeira medida (0,01 V) não teve esse efeito. **A confirmar** com V AC
  e com as RCA em curto.
### Pino 1 — confirmação (LEVEL médio)

- V AC: flutua de 0 a 30 V.
- V DC com as três RCA em curto: flutua de −13 a +14 V.

Contexto informado depois pelo proprietário: a unidade **já estava queimada**:
Q108 (TO-3P de saída) com o encapsulamento estourado e R112 derretido. As tensões
foram medidas com o estágio de potência danificado ligado ao mesmo nó. Portanto a
oscilação do pino 1 **não isola o defeito no preamp**: pode vir do amplificador
de potência em falha (realimentação/DC) carregando a linha. Estado do preamp
original: **desconhecido**. ELEC-004 (preamp novo) continua sendo o caminho,
porque o preamp exige ±15 V e não pode ser validado isoladamente sem bancada.
**Não energizar mais a placa original**: Q108 em curto pode descarregar os
trilhos ±48 V sem controle.

## Falta medir

1. Qual fio do woofer é o + (marca no terminal do woofer).
2. Woofer: conferir raspagem da bobina (empurrar o cone devagar com as duas mãos).
