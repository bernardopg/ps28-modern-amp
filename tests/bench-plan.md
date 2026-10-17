# Plano de bancada — Rev.B / execução depende de G4

Critérios fechados por SYS-002 em docs/requirements.md e tests/acceptance.md.
Nenhum ensaio físico executado nesta revisão. BENCH-001 registra instrumentos e
aprovação do proprietário antes de energizar; não inferir aprovação da definição dos limites.

## Instrumentação e preparação

Fonte DC isolada ajustável até48 V/≥5 A com limitador; DMM; osciloscópio com
sonda diferencial adequada ao PWM/common-mode; gerador/analisador com filtro áudio
22 kHz; carga4 Ω não indutiva≥300 W com ventilação e medição da resistência quente;
termopares/câmera e ambiente controlado para40 °C; parada de emergência e ESD.
Inventário real/modelos/séries/calibração: **a registrar em BENCH-001 pelo operador**.
Para T1/rede: Variac ou lâmpada-série no primário preservando fusível OEM2,5 AT;
conexões de rede somente por operador habilitado. Nenhum woofer nesta sequência.

## Sequência e interrupções

1. Desenergizado: polaridade, resistências entre rails/GND, fixture/dissipador,
   torque/isolação, fonte limitada e fixture diferencial. Confirmar gates G1–G4.
2. Fonte24 V, RESET imposto baixo, limite0,10 A; elevar limite somente se tensões
   e consumo coerentes. Não tentar liberar áudio abaixo do UV de PVDD. Aumentar
   até42 V mantendo RESET; parar se tensão de rail sair de REQ-004, corrente de
   entrada DC em repouso exceder0,25 A ou houver aquecimento anormal.
3. A42 V testar hold/START/FAULT/DC/CLIP_OTW e ciclos ON/OFF com carga artificial.
   Registrar oscilações do LP2985 e LM5164 a vazio e degraus auxiliares0–0,5 A;
   para SEQ_3V3 usar0–10 mA contínuos e degraus até50 mA por≤50 ms
   com duty≤10%, extremos de alimentação e temperatura. Ripple e
   DC/pop conforme matriz; aumento sustentado de oscilação ou trip inesperado reprova.
4. A42–48 V, limite inicial1 A,1 W/50 Hz/5 min; aumentar para3 A para10/25/50 W,
   2 min cada; para100 W usar limite5 A e monitorar a potência real de entrada.
   Limite é proteção da fonte, não confirmação de consumo normal. Fazer THD/banda
   20/35/50/100/150 Hz por5 s/ponto a1 W e100 W; reduzir imediatamente se clipping.
5. 100 W/50 Hz/60 min/25±5 °C e depois40±2 °C,100% duty. Interromper por Tj
   calculada≥110 °C, capacitor≥70 °C,PCB/indutor≥85 °C, rail fora da faixa,
   DC>50 mV,THD+N>1%,trip ou comportamento anormal. Tj exige perda medida e
   impedância térmica do caminho documentado; temperatura do dissipador não é Tj.
6. Burst120 e150 W:3 ciclos ON/20 totais a50 Hz,60 s,15% duty, medir THD+N na
   janela estabilizada e primeiros4 picos para comparação OEM. Não substituir por
   seno contínuo nem interpretar o RMS de todo o trem como potência do burst.
7. Somente depois da qualificação isolada, testar T1 CT2 diodos na janela de rede
  108–132 VAC/60 Hz do modelo120 V, com limitação inicial, carga e temperaturas
   controladas. O topo da janela é ensaio condicional: parar antes de PVDD53,5 V.
   Medir regulação/inrush/ripple/corrente RMS nos capacitores e perdas; não usar o
   TVS como regulador nem forçar rede alta se a tensão sem carga já for excessiva.
8. ACOU-001 mede T/S/Xlin e verifica subsônico antes de ensaio com woofer; aplicar
   X≤80%Xlin e média≤100 W, o menor limite, nunca iniciar por potência máxima.

Aprovação G4: responsável/data/commit e inventário real a registrar pelo proprietário.
O restante são instruções de projeto prontas, sem simular uma execução física.
