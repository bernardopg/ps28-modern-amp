# Registro de decisões

Usar D-NNN: problema, opções, fonte, consequência, responsável, status/data e tasks.

- D-001 — Proposta herdada: TPA3255 PBTL/36 V externo/12 V/sem MCU.
  Origem da alimentação supersedida por D-010; demais requisitos ainda sujeitos a G0.
- D-002 — Aceita para infraestrutura: KiCad + ngspice + Git/CLI; um escritor de EDA.
- D-003 — Aceita para documentação: AGENTS único, CLAUDE symlink, skills locais,
  Scrumban .tasks; originais preservados no arquivo e no commit inicial.
- D-004 — Proposta: LR4 LINE 80 Hz e LFE bypass; fechar após ELEC-002.
- D-005 — Proposta: 4 camadas; stackup/cobre e custo pendentes PCB-001.
- D-006 — Pendente: baseline LC datasheet vs EVM; ELEC-001 bloqueia captura.
- D-007 — Pendente: licença do projeto; não importar licença wingdrive automaticamente.
- D-008 — Aceita por precaução de setup: GitHub privado; publicação só por solicitação.
- D-009 — Recomendada após leitura do manual: qualificar o T1 original antes de
  comprar fonte; fonte secundária regulada 36 V/auxiliar 12 V como caminho preferido
  se aprovado, externa como fallback. Nenhuma ligação direta de ±Vcc ao TPA3255.
  Ver [análise e gate](transformer-reuse.md); PWR-001/BENCH-001 pendentes.
- D-010 — Selecionada nesta sessão por delegação do proprietário: reaproveitar T1
  e desenvolver fonte secundária nova, alvo PVDD regulado 36 V e auxiliar 12 V.
  Fonte externa apenas bancada/fallback. Proprietário informou T1/capacitores saudáveis
  e capacidade técnica para medir/conectar/testar. Isso não comprova VAC/VA, corrente
  disponível ou ratings do conjunto novo. Detalhes elétricos e gates continuam pendentes.
  D-010 substitui a escolha de fonte externa de D-001 e a espera de escolha de D-009.
- D-011 — Baseline de core selecionado para início exploratório: SLASEA8A p.28
  figura31, dois indutores e paralelamento A+C/B+D antes do LC. Symbol local 44 pinos,
  footprint TopEP (PowerPAD superior), sem pad inferior 45. Captura/placement não
  incluem fonte/front-end nem fecham gates. Ver incremento, PCB-003.
- D-012 — Seleção do core B para validação: HCF2013 7443631000, filme WIMA MKP2,
  bulk local Nichicon UHE1500µF/63V e terminais WR-TBL1377 5,00mm; todos footprints
  críticos preenchidos. Não mistura paralelamento/filtro com EVM; sourcing e bancada pendentes.
- D-013 — Reusar gabinete/plate/dissipador originais, por adaptador de cobre no
  PowerPAD superior e bond GND próximo de U1. Furação/fit/contato dependem de medidas
  reais ausentes; não deduzidos do tamanho externo do gabinete. Ver selected-core.md.
- D-014 — Interfaces mecânicas OEM fixas por decisão do proprietário: reutilizar sistema
  de dissipação e mounting points da placa original PS28; sem nova furação no plate.
  Usar main PCB104-a05064a00-e, desenhos p.17–18 e BOM mecânica p.15–16 como master.
  Corrigida afirmação anterior de que o manual só cotava gabinete externo: plate,
  carcaça, dissipadores e suportes têm dimensões nominais documentadas. Entrecentros
  /escala1:1 da PCB não são declarados; reconstruir/conferir gabarito antes de fabricação.
  PCB/adaptador atuais se adaptam ao OEM, nunca o contrário; não solicitar novo
  levantamento completo do gabinete como pré-requisito para avançar.
- D-015 — Proposta reversível de front-end LINE para estudo: duas SK de ganho
  unitário14k/CFB200nF/CG100nF, divisor de entrada1/2 e inversor diferencial unitário.
  Mantém LR4≈80Hz, LFE bypass e rail auxiliar12V sem MCU. Não congela NE5532,
  MPNs ou pinagem; modelo comportamental não garante CM/swing/VMID a10,8–13,2V.
  Fontes TI SLOA024B p.4–5 e SLOS075K p.3–4; riscos: clipping/bias/partida, ruído
  e tolerâncias. Não altera PCB, gates ou topologia de potência. ELEC-002 continua
  bloqueada; ver `analog-lr4-study.md` e relatório de simulação,2026-10-08.
- D-016 — OPA1656ID candidato para captura analógica isolada, em vez de presumir
  NE5532 qualificado a12V. TI SBOS901C fig.5-3 p.3/p.4–7 e modelo SBOMAW6C
  Final1.3 auditados;9 casos de rail/temperatura passaram no modelo oficial.
  U2/U3 duals, 21 componentes/58 pinos; ERC0,14 R/C comparados com SPICE.
  Mantém fonte12V/front-end sem MCU; não acrescenta placa física à arquitetura.
  Símbolo local e SOIC8 candidatos;9 footprints e MPNs passivos ainda TBD.
  VMID/fonte/supervisor/ruído/startup/fábrica não qualificados. Objetivo: sair de
  VCVS genérica para candidato real; risco: simulação não garantir extremos reais.
  Evidência `analog-capture.md`,2026-10-08; ELEC-002/003 não concluídas.
- D-017 — Estudo de VMID físico com divisor 4,7 kΩ/4,7 kΩ, CREF 22 µF,
  buffer OPA1656 e isolamento 25/50 Ω para reservatório 22/47 µF; NÃO adotar
  nem capturar como fonte pronta. Modelo TI: 32 casos, PM mínimo 60,67°;
  sem isolamento PM negativo. Análise RC independente mostra REF acima do
  limite de entrada em power-down sem clamp qualificado (SBOS901C §6.1 p.4).
  Exigir descarga/clamp/corrente/backfeed e sequenciamento antes de integração;
  RESET não protege os pinos analógicos. MPNs/ESR/fuga e fonte reais TBD.
  Objetivo: quantificar carga/estabilidade e evitar captura insegura. Risco:
  extrapolar macro/curvas típicas para startup/clamps/hardware. Evidência em
  `vmid-buffer-study.md` e relatório,2026-10-08; gates/tasks não concluídos.
- D-018 — Substituir a candidata VMID D-017 por divisor passivo150/150Ω
  (quatro75Ω) e1µF, todos os opamps no rail ANALOG_12V isolado de AUX_RAW,
  filtro15Ω/reserva2×470µF/bleeds1k e2,2k. Remover buffer/REF22µF, sem
  depender de clamp interno/estado do opamp desligado. Limites de armazenamento,
  ESR, carga e fuga explícitos; invariância RC resolve a causa D-017 sob esse
  envelope. Captura integrada32componentes/80pinos/ERC0 e9 casos TI; não
  relaxar critérios anteriores nem alegar hardware aprovado. Custo/risco:
  consumo/térmica/divisor, queda de rail, pulso, ESR/temperatura e power-order
  TPA/sinais externos ainda requerem qualificação. Não outra PCB/mounts/MCU.
  Ver `vmid-protection.md` e relatórios; decisão reversível,2026-10-08.
- D-019 — Bloquear integração energizável da saída analógica até proteção de
  INPUT_A/B e pré-carga qualificada. Adotar contrato **preparatório**, não um
  circuito/MPN aprovado: isolamento depois de C20/C21, controle da placa isolada,
  mute analógico e observação de DC antes de áudio; auditar ambos os terminais
  quando a chave estiver sem alimentação. Contraprovas RC mostram que capacitor,
  resistor série, chave upstream ou reconexão com áudio não demonstram segurança.
  Não tratar RIN/bias típicos como garantia de CI desligado nem usar 1 mA como permissão
  para violar −0,3…7 V. Objetivo: impedir fechamento falso de ELEC-002/003;
  risco: limites de chave/slew/pré-carga ainda TBD. Ver
  `input-power-order-study.md`, relatório e regressões; 2026-10-08.
- D-020 — Integrar core + analógico em **candidata de revisão separada**, sem
  fechar ponte de sinal D-019 e sem mover baselines. Nets de alimentação compartilhadas,
  76 componentes/212 pads; analógico em banco externo ao contorno, não fit concluído.
  Objetivo: avançar captura, candidatos de passivos, assets CAD oficiais com licença
  confirmada e especificação executável de sequência (não firmware/MCU). R9 candidata
  4,7 kΩ substitui10 kΩ diante de fuga100 µA/VIL0,8 V; holdRESET≥250 ms TI, proposta
  mínimo360 ms. Risco: pulse/ESR/drift/backfeed/isolamento/sensores/mute/latências reais
  não qualificados. Nenhum switch pesquisado fechou D-019. Validação: revisão
  independente, regressões com contraprovas, ERC/DRC nativos e ledger de nets/UUIDs.
  Ver `integration-protection-review.md` e `system-candidate-review.json`; reversível,
  2026-10-08. G0–G5, tasks, WIP e S03 inalterados.
  Não confundir decisão de arquitetura com liberação de fabricação/energização.
- D-021 — Substitui o alvo "PVDD regulado 36 V" de D-010; mantém reuso de T1.
  PVDD **não regulado** por retificação full-wave CT com dois diodos: cada fio
  vermelho via diodo para +PVDD, fio preto (CT) para GND. Evidência do proprietário
  2026-10-09: 34,35 VAC por metade e 69,2 VAC total a vazio com rede 126,6 VAC;
  CT confirmado por resistência e tensão (`transformer-reuse.md`). Calculado, não
  medido: ≈47,7 V a vazio em 126,6 V, ≈50,1 V a vazio em 133 V, ≈42–46 V sob carga
  conforme bulk. Dentro de PVDD 18–53,5 V (SLASEA8A p.6 §7.3), margem ≈3,4 V.
  Proibido ligar vermelho–vermelho em ponte (≈97 V). Consequências obrigatórias:
  bulk ≥63 V redimensionado por ripple de 120 Hz (estimativa 10–15 mF; 6800 µF/50 V
  originais não reutilizáveis nesse rail), proteção de sobretensão/TVS abaixo de
  53,5 V, inrush, fusível no secundário, buck 48→12 V para auxiliar e limiter/teto
  de ganho porque a potência disponível excede o woofer original. Objetivo: eliminar
  o buck 36 V/5–6 A. Risco: margem pequena em rede alta/vazio, ripple e regulação
  sob carga não medidos. Validação: PWR-001/BENCH-001 com carga resistiva. Aprovada
  pelo proprietário em 2026-10-09; não libera fabricação nem energização.
- D-022 — Crossover LINE ajustável contínuo 50–150 Hz no furo CROSSOVER original,
  substituindo LR4 fixo 80 Hz de D-004/REQ-006. Fase 0°/180° por chave, LEVEL e RCA
  LFE/L/R mantêm a interface do painel. Estudo LR4 80 Hz vira ponto da faixa,
  não projeto final; topologia de sintonia (potenciômetro multi-gang/state-variable)
  e tracking entre seções ficam TBD em ELEC-002. Aprovada pelo proprietário em
  2026-10-09.
- D-023 — Implementar em lógica discreta (sem MCU) o subconjunto de D-020 que não
  depende de D-019: hold ≥360 ms por dois TPS3808, partida por borda humana com
  CLIP_OTW alto, arme por borda de FAULT, latch com rearme humano, timeout
  0,62–1,44 s e janelas TPS3700 de PVDD, ANALOG_12V e VMID em RAILS_OK
  (open-drain). Integrar `power-d021` e `seq-d020` ao `system-candidate` como
  bancos fora do contorno; `PVDD_36V` vira `PVDD`; J4/R7/R8 ficam DNP para não
  realimentar 3V3 externa. Objetivo: tirar RESET/FAULT do controle externo.
  Risco: footprints não auditados, latências/níveis reais e UX do botão não
  validados; isolamento/mute D-019 continuam abertos. Validação: ERC/DRC nativos,
  modelo lógico da netlist capturada com mutações, `make check`. Ver
  `seq-d020.md`; 2026-10-09. Não libera fabricação nem energização.
- D-024 — Concluir a interface D-019 com **relé de sinal Form C** (Omron G6K-2F DC12)
  depois de C20/C21: COM na placa isolada, NO no pino do TPA, NC em descarga de 1 kΩ.
  Mute analógico real por TMUX6219 em DIVIDED→VMID, janelas DC 2…5 V nos dois pinos
  (TPS3700, média τ≈50 ms), janela de AUX_RAW e lógica discreta: RESET 12–28 ms
  depois do fechamento, dwell DC 12–28 ms antes de desmutar, trip por perda de DC.
  Substitui o requisito proposto "detecção + abertura ≤ 100 µs" pela grandeza que
  ele protegia: pino em −0,3…7 V. A troca vale porque todo gatilho dispara com os
  trilhos do preamp ainda válidos e o relé abre em ≤ 3 ms (catálogo). Simulação
  ngspice com 1350 casos: pino ≥ 0 V com 3 ms e ≥ −0,262 V com 10 ms pessimista.
  Ponte DIFF_POS/NEG→DIFF_P/N fechada só através do relé; J3 DNP. Objetivo:
  remover o bloqueio de integração do sinal. Risco: falha simples (curto de
  ANALOG_12V/driver) não coberta, entrada real do TPA desligado não caracterizada,
  bounce/contato colado, conteúdo < 20 Hz exige passa-altas no front-end. Validação:
  ERC/DRC, modelo lógico da netlist com mutações, simulação, `make check`. Ver
  `iso-d019.md`; 2026-10-09. Proposta do agente sob autorização do proprietário,
  pendente de revisão G1. Não libera fabricação nem energização.
- D-024a — Mitigação de falha simples na interface D-019: R 3,3 kΩ em série após o
  NO do relé e BAT54 (catodo no pino, anodo em GND). Driver em curto para GND com
  relé fechado: ≈ −5,9 V sem clamp → ≤ −0,351 V no VF máximo de catálogo (ainda
  51 mV além de −0,3 V). Custo −1,33 dB típico. Driver preso alto continua aberto.
  Footprint TI DGK0008A local para o TMUX6219. Validação: simulação de 216 casos de
  falha simples, ERC/DRC. 2026-10-10; pendente de revisão G1.
> **Revisão 2026-10-11 — D-025/D-026/D-027 não qualificadas:** a tabela
> onsemi MUR3020WT/D Rev.7 p.2 especifica **150 A** para MUR3040WTG;
> 200 A pertence ao MUR3020WTG. A seleção MUR3040WTG abaixo está **reprovada
> contra o requisito IFSM≥200 A**, não apenas aguardando footprint.
> RAILS_OK/RESET não desconectam PVDD; fusível time-lag não limita inrush por si.
> Captura corrigida de revisão: `kicad/power-package-review/`, sem substituir a
> candidata roteada. Não constitui nova aprovação de arquitetura/MPN.

- D-025 — Fechar os MPNs de potência do retificador CT D-021 por fonte primária.
  Diodos D301/D302: **onsemi MUR3040WTG** (MUR3020WT/D Rev.7): VRRM 400 V (≈3,9× o
  PIV 102,1 V a 133 VAC), IF(AV) 15 A @145 °C, IFSM 200 A, TJ −65…+175 °C — atende
  folgado a todos os requisitos; STTH8L06 foi **rejeitado** (IFSM 120 A < 200 A).
  Bulk C301/C302: **Rubycon 63USC4700MEFCSN30X30** (LCSC C1498587): 4700 µF/63 V,
  3,49 A rms @120 Hz, Ø30×30, 3000 h @85 °C — a única família que entrega 4700 µF a
  63 V com ripple próximo de 3,5 A; Nichicon UHE e Panasonic NHG-A **não têm**
  4700 µF/63 V (máx. 1500/2200 µF). J301/J302: terminais **JST VH SVH-41T-P1.1**
  (20–16 AWG, 10 A) em housing VHR (pitch 3,96 mm), casa com o fio 20 AWG do chicote.
  Datasheets arquivados em `reference/parts/` com SHA256 no manifesto. Footprints
  ainda candidatos (snap-in Ø30, TO-247, relé) a auditar antes de G3. LCSC/estoque/
  preço não verificados. 2026-10-11; pendente de revisão G1. Não libera fabricação.
- D-026 — Proteção de sobretensão de PVDD por **arquitetura**, não por clamp de TVS.
  O requisito anterior "TVS com Vc < 69 V" é **inviável** com TVS passivo de 51 V:
  SMCJ51A confirma VWM 51,0 V mas Vc 82,4 V @IPP 18,2 A (PPP 1500 W, 10/1000 µs),
  acima do máximo absoluto do TPA3255 (PVDD 69 V, SLASEA8A p.5 §7.1; operação
  ≤53,5 V §7.3). Como todo TVS grampeia ≈1,6× VWM, nenhum passivo de 51 V protege o
  CI. Decisão: (1) proteção **sustentada** fica no supervisor **TPS3700** — janela OV
  50,97–52,24 V já capturada, que desarma RAILS_OK antes de qualquer dano; (2) o
  **TVS SMCJ51A** fica como **absorvedor de energia de transiente rápido** (não como
  clamp primário), compondo com o bulk de 12,4 mF, que por Xc já suprima transientes
  de alta frequência. Objetivo: parar de buscar clamp passivo inexistente e ancorar a
  proteção no OV sustentado + absorção. Risco: transiente mais rápido que a resposta
  do supervisor ainda vê até ~82 V no nodo — mitigado pelo bulk e pela natureza CT do
  secundário (sem comutação). Validação: ERC/DRC, janela OV do TPS3700, `make check`;
  caracterização de transiente real fica para a bancada. 2026-10-11; pendente de G1.
- D-028 — **Proposta em revisão, não aprovada:** RHRP1560 e LGU2A472MELC como
  alternativas elétricas por fonte primária; estudar desconexão série/pré-carga
  com detector OVP preciso. LM5069 com OVLO interno apenas foi reprovado por
  tolerância (2,4–2,6 V não cabe em 49,84–53,5 V). CT recalculado até 8,014 A RMS,
  não usar RMS de meia-bobina para F301. Evidência, riscos/SOA/fit e pendências:
  `docs/power-remediation.md`. Captura separada `kicad/power-researched`, ERC 0,
  não integrada à PCB roteada. 2026-10-11; G1/G2/G3 pendentes.

- D-027 — Inrush do bulk tratado pelo **fusível time-lag**, sem NTC nem relé de
  bypass. A alternativa NTC+relé (bypass por G5LE-1) foi avaliada e **descartada**:
  (a) um NTC dimensionado para o pico de partida (45–169 A, D-021) dissipa I²R
  relevante em regime a 3,9 A contínuos e varia com a temperatura; (b) o relé de
  bypass Ø17×23 mm não cabe no placement de estudo do contorno OEM sem rearranjo, e
  exigiria mais um driver do sequenciador. A solução escolhida replica o que a placa
  original já fazia (D-021: "a placa original operava o mesmo T1 com 2 × 6800 µF;
  ordem de inrush comparável") — um **fusível time-lag T** absorve o I²t de partida
  por definição, e o bulk de 12,4 mF + o secundário CT (sem comutação) limitam o
  pico. F301: time-lag (T) 5×20 mm, ≥63 VDC; rating pela corrente de operação
  (≈4,3–5,7 A rms por meia-bobina, D-021) com margem, **não** pelo inrush. O I²t
  exato de fusão e a corrente de partida seguem a medir na bancada (BENCH-001) antes
  de travar o ampere rating; a família (Littelfuse 218/892) e a lógica estão fixadas.
  Objetivo: eliminar 2 componentes e a complexidade de controle sem perder proteção.
  Risco: pico de partida real não medido — se a bancada mostrar I²t acima do fusível
  escolhido, reavaliar NTC (aí sim, com o espaço já conhecido). 2026-10-11; pendente
  de G1. Não libera fabricação nem energização.

- D-029 — **REVOGADA em 2026-10-12 por D-030** (proprietário: uma placa só).
  Texto original: Rev A = placa de bring-up de bancada; retificador T1 adiado para Rev B.
  Selecionada em 2026-10-12 por delegação do proprietário ("tomar as melhores
  decisões"); G1 pendente. Motivo: J301/F301/D301/D302/C301/C302 são os únicos
  itens do estágio de potência sem MPN/footprint qualificados
  (`docs/pcb-readiness-review.md`), e D-027 já exige medir inrush/I²t de T1 na
  bancada (BENCH-001) antes de fixar fusível e retificador. O desenho mecânico do
  TO-220AC do RHRP1560 não está no datasheet arquivado e o download onsemi foi
  negado; não se inventa land pattern. Rev A mantém todo o resto da candidata
  (core PBTL, bulk C14/C15 UHE 3000 µF/63 V, buck LM5164, TPS3700, sequenciador,
  D-019/D-024, R301, D303) e recebe PVDD pelo terminal auditado J1 (WR-TBL
  691137710002) a partir de fonte de bancada com limite de corrente/tensão. A
  janela OV do TPS3700 continua só desabilitando áudio; na Rev A a proteção
  sustentada de sobretensão é o limite da fonte de bancada, ajustado ≤ janela
  aprovada em BENCH-001. Não muda a baseline D-010/D-021 do produto final: a Rev B
  reintegra o retificador CT com dados medidos, mesmo contorno/fixação D-014.
  Gerador `scripts/create_rev_a_bench.py` → `kicad/rev-a-bench/` (placement de
  estudo, sem rota). Risco: Rev A não valida T1/inrush/retificador, só o restante.
  Não libera fabricação, compra nem energização.

- D-030 — **Uma placa só e política de evidência pragmática.** Aprovada pelo
  proprietário em 2026-10-12. Revoga D-029; substitui as escolhas de potência de
  D-025/D-027/D-028 e as pendências da revisão de prontidão. Objetivo: subwoofer
  funcionando com a placa nova; regras de trabalho em `AGENTS.md`.
  Escolhas, com a placa original como referência (manual PS28 p.14):
  - J301: JST **B3P-VH(LF)(SN)**, 3 vias 3,96 mm — o manual lista "3 PIN
    PITCH=3.96mm JST-VH" (175-1d03v01-e); casa com o chicote vermelho–preto–vermelho.
  - D301/D302: **P600J** axial R-6 (600 V, 6 A, IFSM 400 A). OEM usava KBL405
    (4 A/500 V, IFSM 200 A) para a mesma corrente de T1; P600J tem mais margem e
    mantém o footprint D_P600 já no projeto. Corrente média por diodo ≤ ~2 A em potência
    contínua máxima; dissipação ~2 W cada, no ar, com terminais longos.
  - C301/C302: **Rubycon 63USC4700MEFCSN30X30** em footprint correto D30 snap-in.
    Com C14/C15 (2×1500 µF/63 V): 12,4 mF a 63 V, contra 13,6 mF a 50 V no OEM; PVDD
    máximo simulado 49,84 V, margem de tensão maior que a do OEM.
  - F301: **Littelfuse 02186.3MXP** (T 6,3 A 5×20) em suporte Schurter 0031.8201,
    no retorno CT. Confirmar na primeira energização (Variac/lâmpada-série); trocar por
    8 A se abrir só na partida. Fusível original de 2,5 A no primário permanece no gabinete.
  - Sobretensão: rede 127 V nominal + T1 medido dão ≤ 49,84 V no pior caso simulado,
    abaixo de 53,5 V de operação do TPA3255; TPS3700 desarma o áudio na janela
    50,97–52,24 V e SMCJ51A absorve transientes. Sem limitador série (D-028 arquivada).
  - R201 passa a DIN0617 vertical (mesmo resistor, ocupa menos placa).
  - ERC: pinos PBTL paralelos marcados passive e TP101 MONO_IN (da branch
    `fix/pcb-route-drc-erc`). Resultado: ERC 0, DRC 0, paridade 0; 471 conexões a rotear.
  - Autoroute de estudo descartado; rota manual com planos (PCB-002).
  Capturas `kicad/power-package-review/` e `kicad/power-researched/` ficam como
  histórico. Risco aceito: margens baseadas na placa original e em simulação, confirmadas
  na energização controlada (BENCH-002), não em ensaio prévio de inrush.

- D-031 — **Bloco térmico do TPA3255, aterramento e conectores OEM.** 2026-10-12,
  com medidas do proprietário (6ª rodada). Bloco de alumínio sobre o PowerPAD de U1,
  apoiado na face da perna do perfil U e parafusado nos dois furos M3 roscados dos
  TO-3P (x 70,7/110,3); alívio de 3 mm por baixo, exceto no pedestal do PowerPAD.
  Pasta térmica (SLASEA8A §7.4 usa 0,7 W/m·K, 2 mil); sem o filme isolante. Perfil é
  flutuante hoje; SLASEA8A pede heat sink aterrado → trança de J6 liga bloco/perfil
  ao GND. Keepout na PCB x 64–117, y 52–68 (top): só SMD baixo (R/C/D/U).
  Para caber: C14/C15 passam a Nichicon UHE1J681MHD (680 µF/63 V, D12,5×40,
  0,071 Ω; CAT.8100M) → bulk PVDD 10,76 mF (≥10 mF D-021). J5 passa a JST
  B2P-VH: chicote do woofer é 2 vias VH (P102 no manual p.14), pluga sem emenda;
  vermelho = SPK_P (+), preto = SPK_N.
  **Revisão de engenharia 2026-10-16, sem liberação fabril:** modelo e fit nominal em
  `mechanical/thermal-fit.json`/`thermal-block.md`. Corrigida altura dos furos OEM
  para 23,65 mm e transformação WRL; corpo com alívio nominal 3,3 mm/topo 30 mm,
  pedestal 6×3 mm dentro do pad mínimo, apoios metálicos/calços independentes do CI.
  TIM superior fino com gap calibrado e calço lateral sólido; J6 continua obrigatório.
  Não usar o encapsulamento como batente nem supor perfil a 50 °C. Orçamento 1D
  usa Rjc(top)=0,36, hipóteses declaradas e caminho OEM→ambiente não medido;
  confirmar folgas/roscas/calços na montagem e perdas/térmica em BENCH-002.

- D-032 — **Front-end = placas originais de preamp e limiter reaproveitadas.**
  2026-10-12, ELEC-004, por delegação do proprietário ("aproveitar o que faz sentido").
  As placas originais já entregam RCA L/R e LFE, LR4 24 dB/oit. 50–150 Hz contínuo
  (VR202), LEVEL, PHASE, subsônico, limiter e auto-on nos furos originais do painel
  (manual p.22–23), ligadas à principal só pelo chicote de 7 vias. A placa nova
  substitui o lado P101 (manual p.24):
  - J7 JST B7B-XH-A (2,5 mm), ordem do manual: 1 LIMIT, 2 STB, 3 −15 V, 4 GND,
    5 +15 V, 6 PTC, 7 IN. Confere com as leituras de 2026-10-10 (pino 4 = GND,
    5 = trilho com bulk, 7 = alta impedância).
  - ±15 V: seguidores discretos como Q117/Q119 originais — BCP56/BCP53 com zener
    BZT52C16; +15 V do PVDD, −15 V de semiciclos negativos de T1 (S1M + 120 µF/63 V).
  - Áudio: IN → C109 2,2 µF filme → divisor 1k/100k em VMID → U2A ganho 1,887 →
    U3 driver diferencial → K501 (D-019/D-024). Com a sensibilidade original
    (0,670 Vrms em plena potência, ganho 1+56k/1,5k da p.24), chegam 2,505 Vrms
    diferenciais contra 2,520 Vrms necessários (TPA 21,5 dB, −1,33 dB da série 3,3 kΩ).
  - LIMIT: BSS138 com gate no CLIP_OTW; em clip/OTW o LIMIT sobe a +15 V (R605) e
    sai da janela ±7 V do comparador U301 original. Hipótese funcional, confirmar na
    bancada. STB e PTC ficam em pads de teste (auto-on e LED de proteção sem uso).
  - O LR4 onboard (R103–R106, C101–C106) sai: o crossover é o original.
  Risco: placas originais com 19 anos (eletrolíticos C2xx/C3xx); se falharem, ELEC-004
  volta com front-end novo. Gerador `scripts/create_pre_interface.py`.

- D-034 — **Placement afrouxado para rota.** 2026-10-13, pedido do proprietário.
  Anel livre de 3 mm em volta do U1 nas duas faces (só capacitores do núcleo);
  grupos iso → esquerda/fundo, seq → lado do T1/fundo, dbg → direita/topo. Folga entre
  courtyards fica 0,5 mm (≥0,6 mm não cabe com as âncoras de potência). Conexões
  abertas caíram de 58 para 6.

- D-035 — **Saídas PWM do TPA3255 desenhadas à mão.** 2026-10-13. O Freerouting
  levava PWM_AC/BD com trilhas finas e via única. Agora: escape 0,25 mm de cada
  pino entre as vias de PVDD/GND (único ponto fino, ~4 mm), barramento por ponte
  (AC 1,0 mm F.Cu; BD 0,6 mm B.Cu com via por pino) e 1,5 mm até L1/L2. C8 (C_START)
  vai para B.Cu sob o corpo do U1. Risco: aquecimento do escape a plena potência;
  medir com termopar no BENCH-002.



2026-10-16 — Fechamento BOM: selecionar códigos exatos nas 235 posições; usar RT 0,1%/25 ppm nas janelas, CRCW comuns no tamanho real, WIMA C109 W7,2 mm com pads P5 preservados; separar porta-fusível/fusível e acessórios; confirmar derating MLCC, fornecimento e montagem nos gates de compra/DFM e bancada. Evidência: `docs/bom-closeout-2026-10-16.md`.

- D-036 — **SYS-002 Rev.B e derating**,2026-10-17: qualificar100 W contínuos em
  carga artificial e120–150 W burst3/20; ambiente10–40 °C; woofer0 W até Xlin
  medido, depois≤80%Xlin e≤100 W médios. C401 passa a10u50V0805 próximo do U401;
  C40310u25V0603 para≥2,2uF efetivos e versões legado/nova do LP2985, com ESR
  incluindo cobre. C310/C311100V mantidos apesar da recomendação2×VINmáx
  (107V): C efetiva e ripple calculados pela curva/Eq.23; exceção explícita no
  relatório, a confirmar em bancada. Curvas típicas, tolerância/idade/modelo e48 capacitores revistos
  em docs/capacitor-derating.md; limites são requisitos, não medidas. G0 Rev.B
  aprovado pelo proprietário em2026-10-17 (“Aprovo o G0 da Rev.B”); BENCH-002 verifica estabilidade/ripple/
  térmica, ACOU-001 mede excursão. Sem compra/fabricação/energização automática.

- D-037 — **Verificação sem bancada; único passo físico antes do pedido é dimensional.**
  2026-10-17, pedido do proprietário. Requisitos Rev.B passam a ser verificados por
  análise, simulação, ERC/DRC e revisão CAD; ensaios de bancada (THD, 60 min térmico,
  burst, carga resistiva, termopar em escapes PWM, T/S do woofer) saem do plano.
  Premissas: (1) o caminho perfil U→backplate→dissipador OEM serviu por anos a um
  classe AB de perdas muito maiores que as 5–20 W calculadas do TPA3255 (cenários em
  `tests/reports/thermal-fit-review.json`); OTW/OTSD do TPA protegem o restante;
  (2) preamp/limiter OEM e woofer não mudam (D-032), então a resposta acústica é a
  original; (3) limites elétricos ficam garantidos por projeto com derating
  (`docs/capacitor-derating.md`). Física restante: gabarito impresso 1:1 contra a
  unidade OEM (MECH-002) e, na instalação, conferência de folgas/TIM e primeira
  energização com lâmpada-série sem woofer (BENCH-002). Como confirmar: se OTW/clip
  aparecer em uso normal ou rails saírem da faixa na primeira energização, abrir decisão
  com o dado observado. Regras de segurança de `docs/safety.md` continuam inegociáveis.
- D-038 — **Repositório só com a placa atual.** 2026-10-17, pedido do proprietário.
  Núcleos `core-*`, capturas parciais (`analog-*`, `power-*`, `seq-d020`, `iso-d019`,
  `vmid-protected`), geradores, estudos superados e `docs/archive/` removidos; continuam
  no histórico Git. A candidata `kicad/system-candidate/` não depende deles (bibliotecas
  locais e `kicad/models/`). Decisões acima que citam essas pastas descrevem a origem.
- D-039 — **Especificação de fabricação: 4 camadas 1,6 mm, ENIG, máscara verde.**
  2026-10-17, decisão delegada pelo proprietário ("decida tudo por conta própria").
  ENIG pela planicidade no TPA3255DDV (passo 0,635 mm) e nos pads de potência; HASL
  sem chumbo deixa relevo irregular. Máscara verde: a placa fica dentro do gabinete,
  verde dá melhor contraste para inspeção e retrabalho de uma unidade única, é o
  padrão de AOI/prazo da JLCPCB. Como confirmar: cotação FAB-001 com esses parâmetros.
- D-040 — **Emenda Rev.B1 dos requisitos aprovada por delegação.** 2026-10-17. A
  verificação sem bancada (D-037) substitui a medida de Xlin por limiter/subsônico
  OEM e ≤100 W médios e troca ensaios por análise. O proprietário delegou a decisão
  ("Resolva todas essas pendências, decida tudo por conta própria pelo melhor
  resultado do projeto"); registrado em `docs/sys002-baseline.md`. G4 continua humano.
