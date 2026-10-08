# Plano de captura elétrica — não é schematic aprovado
## Estado após D-018/D-019
Core B/OEM permanece com 47 componentes/142 pads; D-018 é captura **separada**
com 32 componentes/80 pinos/ERC0, ainda sem PCB. D-019 é contrato não implementado
para isolamento pós-C20/C21, mute analógico e pré-carga observada. J102 não foi
conectado ao core. Há 13 footprints analógicos pendentes, além de fonte/control/
LINE-LFE/volume/fase/limiter/DC incompletos. [Mapa atual](development-status.md).
U2/U3p8 usam ANALOG_12V, não AUX_RAW; VMID é monitor/referência, não fonte externa.
Ver [D-018](vmid-protection.md) e [D-019](input-power-order-study.md).

## Golden reference
SLASEA8A §10.2.4, tabela 11: M2=H, M1=L, INPUT_C/D aterrados.
D-011: SLASEA8A Fig.31/tabela11 p.28, A+C/B+D antes dos dois ramos LC.
SLOU441 §4.2 é comparação com a EVM de quatro filtros; não misturar topologias.
Não curto-circuitar nós PWM por analogia; conferir ponto do paralelamento e figura original.
D-011 seleciona figura31 para o primeiro core exploratório: captura inicial já existe,
sem fonte/front-end e sem freeze. Ver [incremento](core-draft.md). SYS/PWR ainda
bloqueiam integração e fechamento do schematic, não a análise isolada do core.

## Folhas planejadas
Power input/auxiliary; analog inputs/VMID; LINE filter/control; power core/output LC.
Hierarquia deve ter nomes de nets inequívocos e pins/tipos elétricos coerentes.

## Revisão por bloco
- RCA: acoplamento, impedância, soma L/R, RF/ESD e retorno sem corrente de potência.
- VMID: ruído, corrente, estabilidade, startup e carga do volume/op-amps.
- LPF: topologia explícita; duas seções Butterworth Q=1/√2 para LR4; valores de R/C
  calculados, ganho total e tolerâncias. Modelo ideal não escolhe R/C físicos.
- Diferencial: igualdade de amplitude, fase, bias e AC coupling conforme TI.
- TPA: tabela pin-a-pin M1/M2, RESET/FAULT/CLIP_OTW, OC_ADJ/FREQ_ADJ,
  C_START, GVDD, AVDD/DVDD/VBG, bootstrap e PVDD. Citar cada valor crítico.
- Potência: inrush, fusível DC (capacidade de interrupção), TVS (VRWM/VBR/VC),
  proteção reversa, margem de Vin DC/DC, bulk/ripple e energia armazenada.
- LC: MPN, DCR, Isat e Irms em temperatura; perdas HF; tolerância e filtro sob carga.
- PowerPAD SUPERIOR do DDV: footprint TopEP com 44 pads, dissipador aterrado e
  interface/fixação térmica; não inventar pad inferior 45 nem paste/vias centrais.

Valores antigos (7,5 A, 4700/1500 µF, 10 µH, 1 µF, NE5532 e 22 pF) são candidatos,
não lista de compra. DC/DC com Vin 42 V sozinho não prova tolerância a transientes.
Exigir ERC, revisão cruzada e checklist de desvio da referência antes de freeze.
