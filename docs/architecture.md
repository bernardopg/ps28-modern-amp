# Arquitetura proposta
```text
RCA L/R → soma resistiva → buffer → LR4 80 Hz ─┐
RCA LFE → buffer ────────────────────────────┴→ seleção → volume
 → conversor diferencial → fase → TPA3255 PBTL → LC → SPK±
T1 original → retificação/bulk/proteção secundária → conversão regulada 36 V → PVDD
                                              └→ auxiliar 12 V → VDD/front-end/VMID
```
D-010 seleciona reaproveitamento de T1; detalhes da fonte dependem do envelope
VAC/DC medido, ripple, térmica e proteções. Nenhum rail ±Vcc antigo ligado diretamente
ao TPA3255; primário original permanece separado da PCB nova. Saúde dos componentes
informada pelo proprietário, não medida pelo agente. Ver [decisão](transformer-reuse.md).

Planejar terras por retorno de corrente, plano contínuo e placement; não usar uma
regra genérica de estrela para romper os retornos HF. RCA/chassi/ESD exigem decisão.

A interface SE→diferencial é candidata: copiar a referência exige entender bias,
acoplamento, amplitude e impedâncias. NE5532 em 12 V não é rail-to-rail: confirmar
common-mode, swing, estabilidade do buffer VMID e carga capacitiva com datasheet.
Switch de fase pode produzir transientes; definir mute/uso sem sinal antes do painel.

Dois baselines de potência NÃO equivalentes para copiar parcialmente:
1. Datasheet SLASEA8A §10.2.4, fig.31, p.28: aplicação PBTL com dois indutores.
2. EVM SLOU441 §4.2 + SLAR129A/130A: quatro ramos LC e paralelamento de saídas
   no ponto especificado pela EVM.
Escolher um em ELEC-001 e registrar geometria, LC e retornos completos.
