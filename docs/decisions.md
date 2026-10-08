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
Não confundir decisão de arquitetura com liberação de fabricação/energização.
