# Regras de PCB — Classe D / TPA3255

## Prioridades

A qualidade do layout importa mais do que aumentar a contagem de camadas sem critério. A TPA3255EVM da TI usa 2 camadas com cobre de 2 oz e serve como referência geométrica. Para uma placa integrada com front-end analógico, 4 camadas facilitam segregação e retorno de corrente.

## Stackup recomendado

```text
L1 — componentes, sinais críticos, PVDD local, switching e filtro LC
L2 — plano GND contínuo
L3 — power distribution: PVDD / 12V / 3V3
L4 — analógico de baixa amplitude e controles
```

## Placement obrigatório

```text
[PVDD connector]
      ↓
[bulk + local decoupling]
      ↓
[TPA3255]
      ↓
[LC filter]
      ↓
[speaker connector]
```

Esse caminho deve ser curto e direto.

RCA e front-end devem ficar no extremo oposto do power stage.

## Regras de desacoplamento

- 100 nF/1 µF de PVDD imediatamente junto aos pinos relevantes.
- Via direta e curta para plano GND.
- Não colocar vias desnecessárias entre capacitor e pino.
- Bulk não substitui ceramic decoupling local.

## PowerPAD

- copper pour sob o exposed pad;
- matriz de vias térmicas conforme recomendação TI;
- vias preferencialmente preenchidas/tented de acordo com capacidade da fábrica;
- plano térmico amplo;
- dissipador/thermal interface avaliado no conjunto final.

## Switching nodes

- área de cobre mínima necessária;
- não passar sinais analógicos abaixo ou próximos;
- não criar grandes antenas de cobre;
- afastar de borda de PCB e RCA;
- manter loops half-bridge → LC → return compactos.

## Grounding

- L2 deve permanecer o mais contínuo possível.
- Não "fatiar" GND sem uma razão suportada pela referência.
- Controle de retorno é feito por placement/roteamento, não por criar ilhas arbitrárias.
- Entrada analógica deve retornar localmente sem compartilhar trechos estreitos com corrente do woofer.

## Trilhas/cobre

Os valores finais devem ser calculados conforme espessura, temperatura e corrente. Como ponto de partida:

- sinal: 0.20–0.30 mm;
- 12 V: ≥0.5 mm conforme corrente;
- PVDD e speaker: preferir pours/polígonos largos;
- vias de potência em paralelo.

Não tratar esses números como sign-off térmico.

## Filtro LC

- indutores imediatamente depois do TPA3255;
- capacitores de filtro próximos;
- afastar magneticamente os indutores entre si quando recomendado pelo fabricante;
- verificar orientação e campo do indutor;
- selecionar componente com Isat e Irms adequados.

## Analógico

- pares diferenciais simétricos no trecho final para o TPA3255;
- manter impedâncias e comprimentos semelhantes onde prático;
- 22 pF/C0G e feedback colados ao op-amp;
- VMID roteado como referência analógica limpa, não como power ground.

## Mecânica

- prever furos de montagem sem copper clearance inadequado;
- não depender dos terminais do TPA3255 para suportar dissipador;
- validar altura dos eletrolíticos/indutores contra o gabinete;
- manter chapa traseira vedada.

## DRC adicional

Criar regras explícitas para:

- `SWITCH_NODE`;
- `PVDD`;
- `SPEAKER`;
- clearance de montagem do dissipador;
- keepout sob hardware metálico.
