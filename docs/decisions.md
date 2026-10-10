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
  incluem fonte/front-end nem fecham gates. Ver [incremento](core-draft.md), PCB-003.
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
