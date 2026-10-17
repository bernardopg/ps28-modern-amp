---
id: BENCH-002
title: Bring-up e carga resistiva
status: To Do
milestone: M4
sprint: S05
depends_on: FAB-001
updated: 2026-10-17
---

# BENCH-002 — Bring-up e carga resistiva

## Objetivo

Bring-up e carga resistiva, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Rails/DC/repouso/FAULT e potência progressiva registrados
- [ ] Térmica/THD dentro dos limites e G4 humano
- [ ] Antes de energizar, com conjunto seguro e descarga verificada: gabarito local
  do bloco, folga útil ≥32 mm acima e ≥5 mm sob H5/H6; rosca OEM útil/engate dos
  parafusos; pilhas de apoios iguais e gap superior real 0,05…0,10 mm preenchido por
  TIM qualificado. Não usar encapsulamento/leads como batente nem forçar a PCB.
- [ ] Verificar vínculo GND eletrônico J6→bloco→perfil (não é PE), ausência de
  contato em leads/passivos e shim lateral sólido ajustado. Não presumir continuidade
  por tinta/pasta; revisar consequências para backplate/chicotes antes de ligar.
- [ ] Sob carga resistiva e limites humanos aprovados: registrar perdas, temperatura
  ambiente, perfil, bloco e ponto do corpo; obter caminho OEM→ambiente efetivo e
  confrontar cenários em `tests/reports/thermal-fit-review.json`. Não tratar 110 °C
  calculados de junção como limite medido/autorizado, nem usar OTW/OTSD como alvo.
- [ ] Medir com termopar os escapes PWM de 0,25 mm dos pinos de saída de U1, na potência máxima aprovada em carga resistiva; registrar ponto, potência, duração, temperatura ambiente, temperatura estabilizada e ΔT. Limites numéricos/tempo de ensaio aprovados antes de energizar.
- [ ] Termopar eletricamente isolado e instrumentação com isolamento apropriado: não aterrar PWM/SPK± nem deixar a junção condutora unir pinos/trilhas. Aquecer progressivamente; interromper ao atingir limites aprovados. Ensaio ainda não realizado.
- [ ] D-030: primeira energização com Variac/lâmpada-série, sem woofer; medir PVDD em vazio/carga, temperatura de D301/D302 e confirmar F301 6,3 A

## Evidência

Pendente. Não marcar critérios sem evidência.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.

## Critérios transferidos de SYS-002 (Rev.B2026-10-17)

Executar tests/bench-plan.md e tests/acceptance.md. Medir estabilidade de
LP2985 a0–10mA contínuos e até50mA por≤50ms/duty≤10% e LM5164 a0–0,5A, extremos de alimentação/temperatura;
capacitância efetiva de lote se necessário, ripple espectral/partilha nos
48 capacitores, case<70C, rails/DC/pop/THD/potência/térmica conforme Rev.B.
Registrar instrumentos e dados reais; não converter curvas típicas em medidas.
