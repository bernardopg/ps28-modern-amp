# Requisitos Rev. B — SYS-002

Baseline de engenharia de 2026-10-17. Os limites abaixo são requisitos de aceitação,
não resultados medidos nem autorização de energização. Aprovação humana G0 em
`docs/sys002-baseline.md`; G4 continua independente. D-010/D-021/D-030/D-032 mantidos.

| ID | Requisito verificável | Aceitação / fronteira |
|---|---|---|
| REQ-001 | Reutilizar gabinete, dutos e woofer `20PR10DAG-FW06-E`, etiqueta `070917`. | DCR corrigido das pontas **4,4 Ω**, medido pelo proprietário; referência OEM 4,4 Ω ±10%. Identificação/integridade SYS-001 concluídas; fit em MECH-001/MECH-002; woofer e gabinete OEM inalterados (D-037). Não transferir dados da variante FW01. |
| REQ-002 | Eletrônica: **100 W / 4 Ω / 50 Hz / 60 min / duty 100% / ambiente 25 ±5 °C**, THD+N ≤1%. | Carga resistiva não indutiva, refrigeração dimensionada, 20 Vrms / 5 Arms. Repetir qualificação a **40 ±2 °C** após aprovação térmica progressiva. Alvo adicional **120–150 W em burst 3 ciclos ON / 20 ciclos totais a 50 Hz**, 15% duty, 60 s; 150 W =24,495 Vrms /6,124 Arms, THD+N ≤1% na janela ON estabilizada. Não declarar 150 W contínuos. |
| REQ-003 | T1 original, retificação CT com **dois diodos**, PVDD não regulado. | Metade do secundário 34,35 VAC medida; operação nominal calculada 42–50 V, bancada permitida inicialmente 24–48 V DC isolados; tensão de trabalho, inclusive ripple/picos, **<53,5 V**. OV/UV de projeto em power-d021; não contornar trips. Ripple PVDD ≤5 Vpp a100 W/60 Hz de rede, sem queda abaixo do UV. Nenhuma autorização de rede/primário por este requisito. |
| REQ-004 | AUX_RAW e ANALOG_12V, VMID, SEQ_3V3 e ±15 V dentro do orçamento. | AUX_RAW **11,69–12,50 V DC**, ripple ≤120 mVpp; envelope de seleção de capacitor **13,2 V**. ANALOG_12V **10,5–12,5 V**, VMID **0,48–0,52 × ANALOG_12V**; ripple VMID ≤10 mVpp. SEQ_3V3 **3,20–3,40 V**, ripple ≤33 mVpp, seleção a3,5 V. P15V/N15V: magnitude **14–16 V**, ripple ≤150 mVpp. Auxiliar requerido ≥0,5 A; fan limitado a0,20 A, TPA0,12 A, lógica0,01 A, relé0,02 A, áudio/monitores0,05 A, reserva0,10 A. Verificar consumo real em BENCH-002. |
| REQ-005 | Reutilizar preamp/limiter OEM D-032, com controles LINE/LFE, volume e fase. | RCA L/R sem curto entre fontes; impedância de entrada >10 kΩ; LINE soma canais; LFE contorna crossover. Fase 0°/180° funcional, ganho entre posições ±1 dB. Máximo de entrada de ensaio2 Vrms, ajustar volume para não ultrapassar potência/excursão. Não reintroduzir LPF nem auto-on novo. |
| REQ-006 | Banda e distorção definidas, preservando o crossover OEM 50–150 Hz /24 dB por oitava. | Eletrônica isolada do crossover:20–150 Hz, ganho ±1 dB a1 W; THD+N ≤0,3% a1 W e≤1% a100 W, frequências20/35/50/100/150 Hz, 5 s/ponto em carga artificial. LINE: Fc nos extremos50/150 Hz ±20%, resposta LR4 −6,02 ±2 dB em Fc, inclinação24 ±4 dB/oitava onde mensurável acima do piso de ruído; LFE sem corte variável. Sistema acústico: resposta OEM 35–150 Hz ±3 dB preservada por reuso de preamp, woofer e gabinete (D-032/D-037). |
| REQ-007 | Proteção e sequência seguras, sem usar proteção térmica como ponto normal. | Offset diferencial SPK+−SPK−: alvo≤10 mV, limite50 mV DC; pop ON/OFF≤100 mV pico, alvo50 mV, medido após filtro áudio22 kHz. RESET seguro e novo comando humano após trip. Hold≥360 ms; relé antes de liberar RESET (12–28 ms); DC_OK2–5 V por12–28 ms antes de AUDIO_EN; timeout de partida≤1,44 s. FAULT/CLIP_OTW, janelas de rails, perda de alimentação e DC devem bloquear áudio conforme D-023/D-024. Sem aprovar woofer somente por ERC/DRC. |
| REQ-008 | Test points e método de medição sem curto de saída PBTL. | Registrar PVDD/AUX/ANALOG_12V/VMID/SEQ_3V3/RESET/FAULT/CLIP_OTW/DIFF/SPK±. Somente sonda diferencial adequada ou aquisição isolada para SPK; nunca garra terra em SPK±. THD+N20 Hz–22 kHz, PWM rejeitado por filtro de medição; registrar largura de banda e ruído do instrumento. |
| REQ-009 | PCB única reparável, stackup de4 camadas, fit e capacitores qualificados. | ERC/DRC/paridade/aberturas=0. Footprints/MPNs/BOM/CPL concordantes, polaridades e rotações conferidas, cobre externo35–70 µm e stackup confirmados pela fábrica antes G3. C401≥1 µF efetivo, C403≥2,2 µF efetivo para LP2985 legado ou novo; regras e orçamento em capacitor-derating.md. Fit físico, dissipador e EMI ainda precisam de validação. |
| REQ-010 | Ambiente, aquecimento, repouso e excursão limitados. | Operação qualificada10–40 °C ambiente; armazenamento−20–70 °C, seco/desenergizado. Alvos de interrupção: Tj calculada≥110 °C, case de capacitor≥70 °C, indutor/PCB≥85 °C ou trip térmico. Perfil OEM deve satisfazer mechanical/thermal-block.md; a15 W perdidos requer perfil≤50,4 °C a40 °C ambiente. Potência de entrada em repouso sem áudio≤15 W, alvo≤12 W (OEM); eficiência da etapa de potência a100 W≥85%, separar auxiliares. Woofer desconectado na primeira energização. Excursão limitada pelo subsônico e limiter OEM reaproveitados (D-032) e potência média ≤100 W, como no produto original (D-037). |

Excursão (D-037): sem medida de Xlin. O woofer original recebe o mesmo sinal
condicionado pelo preamp/limiter/subsônico OEM e potência não superior à do
amplificador original; o ganho da placa nova não deve exceder o OEM.

Origem dos limites: manual PS28 Rev.1 mar/2007 pp.2–3 (100 W, burst3/20, THD,
DC/pop, ruído, térmica e repouso); pp.1/9 (banda/woofer); TI TPA3255 SLASEA8A,
LP2985 SLVS522S e LM5164 SNVSAU4D. Duração60 min, ambiente40 °C, reserva de
corrente, ripple, Xlin80% e temperaturas de interrupção são **margens de engenharia
D-036**, a verificar, não especificações publicadas do woofer.

Fora de escopo: fonte AC integrada, DSP, rádio, app, PFFB customizado e EQ.
Verificação sem bancada (D-037): matriz em [tests/acceptance.md](../tests/acceptance.md).
