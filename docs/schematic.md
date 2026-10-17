# Captura elétrica integrada — G1 ainda não aprovado

## Estado atual — 2026-10-16

Abrir `kicad/system-candidate/system-candidate.kicad_pro`: captura de potência,
áudio/bias/isolamento, sequenciamento e supervisão integrada à PCB única.
**ERC 0, paridade 0, DRC 0 e nenhuma conexão aberta.** A ligação acidental
TP127/R506 foi corrigida; placement local/bootstrap revisto. Revisão independente,
auditoria MPN/footprint e G1 seguem pendentes em ELEC-003.

D-032 mantém o preamp/limiter OEM (RCA, crossover, volume/fase), ligado à interface
da placa nova por J7. D-018/D-019/D-024 e o front-end novo anterior são referências
de evolução, não outras placas de produto ou indicação de que a candidata atual
esteja sem integração. Ver [arquitetura](architecture.md),
[revisão local](tpa-local-layout-review.md) e [estado](status.md).

[SVG atual](images/system-candidate/system-candidate.svg).
U2/U3p8 usam ANALOG_12V, não AUX_RAW; VMID é referência, não fonte externa.

## Golden reference

SLASEA8A §10.2.4, tabela 11: M2=H, M1=L, INPUT_C/D aterrados.
D-011: SLASEA8A Fig.31/tabela11 p.28, A+C/B+D antes dos dois ramos LC.
SLOU441 §4.2 é comparação com a EVM de quatro filtros; não misturar topologias.
Não curto-circuitar nós PWM por analogia; conferir ponto do paralelamento e figura original.
D-011 seleciona figura31 para o primeiro core exploratório: captura inicial já existe,
sem fonte/front-end e sem freeze. Ver incremento. SYS/PWR ainda
bloqueiam integração e fechamento do schematic, não a análise isolada do core.

## Organização da captura

A captura integrada atual é plana, em folha User 1400 × 841 mm. Os blocos
históricos que a originaram ficam em outras pastas KiCad. Não regenerar por cima
da candidata roteada sem snapshot e revisão; nomes de nets/tipos elétricos e
paridade devem continuar coerentes.

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

A BOM atual deve ser extraída da candidata, não desta lista de revisão ou das
capturas históricas. MPNs/DNP e disponibilidade ainda precisam qualificação; DC/DC
com Vin 42 V sozinho não prova tolerância a transientes. Exigir revisão cruzada,
checklist de desvio da referência e G1 antes de freeze.
