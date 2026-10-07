# Plano de captura elétrica — não é schematic aprovado
## Golden reference
SLASEA8A §10.2.4, tabela 11: M2=H, M1=L, INPUT_C/D aterrados.
SLOU441 §4.2: OUTA+OUTC e OUTB+OUTD conforme conexões da EVM.
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
