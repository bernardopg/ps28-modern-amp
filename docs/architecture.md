# Arquitetura proposta — capturas parciais, não sistema aprovado

[Estado consolidado](development-status.md): distinguir proposta funcional,
schematic de estudo e componentes efetivamente colocados na PCB.

```text
FUNÇÕES PLANEJADAS (ainda não integradas)
RCA L/R → soma resistiva → buffer → LR4 80 Hz ─┐
RCA LFE → buffer ────────────────────────────┴→ seleção/volume/fase
 → drivers diferenciais → C20/C21 → isolamento/pré-carga D-019 [TBD]
 → INPUT_A/B → TPA3255 PBTL → dois ramos LC → SPK±

FONTE SECUNDÁRIA PLANEJADA D-010
T1 original → retificação/bulk/proteção → conversão regulada 36 V → PVDD
                                    └→ AUX_RAW 12 V → VDD/GVDD TPA

RAMO ANALÓGICO CAPTURADO SEPARADAMENTE D-018 (sem PCB)
AUX_RAW → diodo/15 Ω/2×470 µF → ANALOG_12V → quatro amps OPA1656 candidatos
                                      └→ divisor150/150 Ω +1 µF → VMID
```

O isolamento D-019 fica **no lado TPA dos capacitores**; a cadeia funcional
não substitui schematic/pinagem/controle qualificados. Ver
[contrato e contraprovas](input-power-order-study.md) antes de capturar chaves.
L/R, LINE/LFE, volume/fase, mute/supervisor, limiter/high-pass e proteção DC
permanecem incompletos. Posição/implementação de fase/volume deve cumprir o
envelope de saltos/slew D-019; não autoriza hot-swap do par diferencial.

D-010 seleciona T1 reaproveitado; VAC/DC, VA/corrente, ripple, transientes e
térmica ainda exigem envelope medido. Nenhum ±Vcc antigo ligado diretamente ao
TPA; primário original separado da PCB nova. Saúde informada pelo proprietário
não é medida pelo agente. Fonte externa é bancada/fallback, não nova baseline.
Ver [reaproveitamento](transformer-reuse.md).

D-016 mantém OPA1656ID como candidato reversível. NE5532 em 12 V não foi
qualificado. D-018 substitui a candidata VMID ativa insegura D-017 por bias
passivo com rail protegido; a correção vale **somente sob o envelope declarado**.
ANALOG_12V não alimenta o TPA: seu mínimo calculado pode ficar abaixo de 10,8 V.
Não usar AVDD/DVDD como fonte genérica. [Fonte/VMID](vmid-protection.md).

O pré-amplificador pode sobreviver à alimentação TPA: RESET/mute do TPA não
protege INPUT_A/B. Pré-carga, defaults e isolamento de ambos os terminais de
chaves desenergizadas ainda não estão implementados. J102 permanece separado
do núcleo; RCA ativa durante power-off também não está qualificada.

Planejar GND por retorno, plano contínuo e placement; não romper retornos HF
por regra genérica de estrela. RCA/chassi/ESD e proteção DC diferencial após LC
precisam de decisão/revisão. SPK+ e SPK− são ativos, nunca GND.

## Referência PBTL selecionada — não misturar LC/paralelamento

D-011 selecionou **TI SLASEA8A §10.2.4, Fig.31/tabela11, p.28**: A+C e B+D
paralelados antes dos dois ramos LC. Essa topologia já está no core exploratório.
A **EVM SLOU441 §4.2 + SLAR129A/130A** usa quatro ramos LC e outro ponto de
paralelamento; serve de comparação, não de receita híbrida. Seleção de topologia
não fecha revisão independente, fonte/mecânica/roteamento ou os gates G0–G5.
