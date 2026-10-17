# Matriz de aceitação — SYS-002 / Rev.B

Limites em [requirements](../docs/requirements.md); execução em
[bench-plan](bench-plan.md). Especificar um limite não comprova conformidade.

| Requisito | Tasks / ensaio | Limites / evidência de aceite | Situação |
|---|---|---|---|
| REQ-001 | SYS-001 / MECH-001 / ACOU-001 | Etiqueta/DCR4,4 Ω e inspeção do proprietário; conferir fit e medir T/S/Xlin. | Identificação/integridade concluídas; fit/acústica pendentes. |
| REQ-002 | SYS-002 / BENCH-002 | 100 W/4 Ω/50 Hz/60 min/100% duty;25±5 e40±2 °C; THD+N≤1%;120–150 W burst3/20/50 Hz/60 s. | Limites definidos; bancada pendente. |
| REQ-003 | PWR-001 / BENCH-002 | PVDD<53,5 V incluindo picos; ripple≤5 Vpp a100 W; não cruzar UV/OV; medir inrush/T1 e fusível. | Cálculo/proteção capturados; bancada pendente. |
| REQ-004 | PWR-001 / BENCH-002 | AUX11,69–12,50 V/≤120 mVpp/0,5 A; analog10,5–12,5 V; VMID48–52%/≤10 mVpp;3V3=3,20–3,40 V/≤33 mVpp;±15=14–16 V/≤150 mVpp. | Orçamento e limites definidos; medir corrente/estabilidade. |
| REQ-005/006 | ELEC-002 / BENCH-002 | Entrada>10kΩ;20–150 Hz ±1 dB a1 W;THD+N≤0,3%/1 W e≤1%/100 W;LR4 e LFE/phase conforme Rev.B. | Reuso OEM definido; ensaios de caminho completo pendentes. |
| REQ-007/008 | ELEC-001 / BENCH-001/002 | DC≤50 mV;pop≤100 mVp;hold≥360 ms;RESET/DC dwell12–28 ms;timeout≤1,44 s;trips bloqueiam áudio. | Captura/modelos disponíveis; sequência física pendente. |
| REQ-009 | PCB-001/002 / MECH-001 / FAB-001 | ERC/DRC/paridade/aberturas0;MPN/BOM/CPL;C401≥1 µF/C403≥2,2 µF efetivos;fit/DFM/stackup. | Ver relatórios digitais atuais; sem aprovação G2/G3. |
| REQ-010 | THERM-001 / BENCH-002 / ACOU-001 | Tj<110 °C/caps<70 °C/PCB e L<85 °C;repouso≤15 W;eficiência≥85%;X≤0,8Xlin eP≤100 W;woofer0 W antes Xlin. | Critérios definidos; medição térmica/acústica pendente. |

Ruído adicional OEM: residual≤1,5 mVrms (alvo1 mV), SNR≥85 dBA ou≥80 dB
sem ponderação referido a100 W, e≥60 dB a1 W. Mesmo filtro22 kHz da distorção;
subtrair ruído do instrumento somente se método documentado.

Cada relatório registra instrumento/modelo/série, calibração conhecida, carga real
medida, configuração/filtros, ambiente, commit, duração, limite, resultado e responsável.
Falha térmica/THD não autoriza reduzir silenciosamente a especificação: abrir decisão
com dado medido. G0 da Rev.B e G4 de energização são registros humanos distintos.
