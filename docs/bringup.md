# Bring-up seguro

Pré-requisito BENCH-001: preencher limites numéricos em tests/bench-plan.md e obter
aprovação. Fonte ajustável limitada em corrente, DMM, sonda diferencial/scope,
gerador/analisador, carga 4 Ω não indutiva com potência/cooling suficientes,
termopar/termômetro, ESD e extintor apropriado. Inventário físico ainda desconhecido.

1. Sem alimentação/woofer: inspeção óptica, polaridade, resistência PVDD-GND,
   44 leads do DDV, PowerPAD superior/dissipador aterrado e interface térmica,
   fixação, descarga, instrumentação. Não presumir solda/pad térmico inferior.
2. RESET assertado: sequência conforme TI e Vin mínimo do DC/DC; não usar uma
   rampa indiscriminada que deixe o auxiliar fora da faixa. Medir rails/VMID/RESET.
3. PVDD: current limit definido, registrar repouso e temperaturas; confirmar FAULT.
4. Sinal baixo: L/R/LFE, ganho/filtro, conversor diferencial e fase/mute.
5. Saída: técnica diferencial segura, DC diferencial e comportamento sem carga
   conforme referência; sem interpretar PWM bruto como tensão útil de áudio.
6. Carga resistiva: 1→10→25→50→100 W→alvo apenas com checkpoints aprovados.
   Registrar Vrms/I/P, clipping/THD+N, duração, ambiente, CI/LC/PCB/dissipador.
7. Woofer somente após G4; volume mínimo, ensaio progressivo e excursão/ruído.
   Não aplicar seno de alta potência sem limites do transdutor, especialmente abaixo da sintonia.

Parar por corrente/temperatura/DC acima dos limites, FAULT, cheiro, oscilação ou
ringing anormal. Desligar, medir descarga e diagnosticar; não continuar por tentativa.
