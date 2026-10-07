# BOM preliminar — PS28 Modern Amp Rev. A

> **Não é uma BOM de fabricação final.** Part numbers de passivos e do DC/DC devem ser fechados depois do schematic e da checagem de disponibilidade JLCPCB/LCSC.

## Semicondutores e módulos

| Ref | Qtde | Componente | Requisito | Observação |
|---|---:|---|---|---|
| U5 | 1 | TPA3255DDV | TI, HTSSOP-44 PowerPAD | power stage PBTL |
| U1–U4 | 4 | NE5532 | dual audio op-amp | front-end/filtro/differential |
| U6 | 1 | DC/DC 36→12 V | Vin com margem ≥42 V, 12 V ≥0.5 A | módulo encapsulado preferido |
| U7 | 0/1 | LDO/buck 3.3 V | somente se necessário | DNP até fechar controle |
| U8 | 0/1 | supervisor reset | opcional | usar se melhorar power-up/reset |
| D_TVS | 1 | TVS | compatível com 36 V rail | fechar após fonte escolhida |

## Potência

| Ref | Qtde | Valor/Tipo | Requisito |
|---|---:|---|---|
| L1,L2 | 2 | 10 µH | Isat ≥8 A desejável, baixa DCR, áudio Classe D |
| C_OUT1,C_OUT2 | 2 | 1 µF filme | ≥100 V; 250 V preferível |
| C_BULK1,C_BULK2 | 2 | 1500 µF | 63 V, low ESR, 105 °C |
| C_IN_BULK | 1 | 4700 µF | 63 V, low ESR, 105 °C |
| C_PVDD_1..n | conforme EVM | 100 nF / 1 µF | 100 V X7R, próximos aos pinos |
| C_BOOT_* | 4 | 33 nF | X7R, valor conforme datasheet/EVM |
| F1 | 1 | 7.5 A preliminar | ajustar após inrush/consumo |

## Front-end analógico

| Grupo | Componentes | Requisito |
|---|---|---|
| Soma L/R | 2 × 22 kΩ | 1% |
| Bias/pull-down | 47 kΩ / 100 kΩ conforme captura | 1% |
| VMID | 2 × 10 kΩ | 1% |
| VMID bulk | 47 µF / 25 V | 105 °C preferível |
| VMID bypass | 100 nF | X7R/C0G conforme função |
| Differential amp | 4 × 10 kΩ | 0.1–1%, matched se possível |
| Feedback HF | 2 × 22 pF | C0G/NP0 |
| Input coupling | 2.2 µF | filme ou solução validada |
| TPA input coupling | 10 µF | X7R conforme EVM |

## Crossover

A rede exata de R/C deve ser gerada após a escolha formal da topologia e simulação. Para Rev. A:

- alvo: Linkwitz-Riley 4ª ordem em 80 Hz;
- resistores: 1%;
- capacitores: filme 1–5%;
- footprints permitem ajuste em bancada.

Não comprar lote completo antes de congelar os valores.

## Controles e conectores

| Ref | Qtde | Item |
|---|---:|---|
| J1/J2/J3 | 3 | RCA L/R/LFE |
| J4 | 1 | entrada DC 36 V |
| J5 | 1 | saída woofer 2 vias |
| RV1 | 1 | 50 kΩ log |
| SW1 | 1 | LINE/LFE SPDT |
| SW2 | 1 | PHASE DPDT |
| SW3 | 0/1 | RESET/MUTE |
| LED1 | 1 | POWER |
| LED2 | 1 | FAULT |
| LED3 | 1 | CLIP/OTW |

## PCB e mecânica

- PCB FR-4 1.6 mm.
- 4 camadas recomendado.
- Outer copper 2 oz desejável.
- Dissipador dimensionado após ensaio térmico; prever interface térmica e fixação mecânica independente da PCB.
- Standoffs e parafusos não devem transferir esforço ao encapsulamento do TPA3255.

## Estratégia JLCPCB

Antes de congelar a BOM:

1. procurar cada componente no catálogo LCSC/JLCPCB;
2. priorizar Basic parts apenas quando não prejudicar especificação;
3. usar Extended para os componentes críticos sem sacrificar qualidade;
4. deixar indutores grandes, conectores, potenciômetros e eletrolíticos TH para montagem manual se isso reduzir custo;
5. verificar estoque no dia do pedido.
