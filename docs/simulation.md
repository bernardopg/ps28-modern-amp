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
