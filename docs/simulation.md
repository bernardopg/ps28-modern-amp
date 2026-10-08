# Simulação
`make simulate` executa ngspice sobre `simulation/lr4-ideal.cir` e verifica ganho em
80 Hz. É um modelo Sallen-Key com VCVS ideal e normalização de ganho, não um front-end NE5532 nem o circuito final.

ELEC-002 deve adicionar implementação real, fonte dos modelos/licença, bias VMID,
common-mode/swing, entrada 2 Vrms, gain staging, impedâncias, ruído e estabilidade.
Varrer 10 Hz–10 kHz, fase, degrau, startup/mute e tolerâncias R/C (seed registrada).
Registrar limites, versão de ngspice, netlist/hash e resultados.

LR4 elétrico: duas seções Butterworth de 2ª ordem, Q=0,7071; -6,02 dB em Fc.
Resposta acústica depende do woofer/caixa e integração com satélites; medir depois.
SPICE ideal não valida EMI, PowerPAD, parasitas, saturação HF/térmica nem fabricação.

## Incremento executável — valores físicos LR4, modelo ainda não qualificado
`make simulate` também confere LC diferencial e roda `scripts/simulate_analog.py`.
O incremento usa R/C explícitos, dois buffers SK unitários e gain staging1/2→diferencial:
151 pontos de magnitude/fase,16.384 corners e2048 amostras com seed fixada, mais
contraprova de headroom em modelo comportamental limitado. NÃO é um modelo real
NE5532; CM/swing/VMID/startup/ruído permanecem não qualificados e ELEC-002 bloqueada.
Ver [circuito, fontes, métricas e limites](analog-lr4-study.md).
