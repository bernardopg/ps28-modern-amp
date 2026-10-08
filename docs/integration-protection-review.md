# D-020 — integração de revisão, CAD e sequência executável

## Entrega e limite

Três subagentes investigaram CAD/parts, isolamento e sequenciamento; um escritor
fez captura/importação. Pesquisas ficaram em `build/integration-agents/` (local).
Conferência primária, novo projeto e regressões, **não conclusão do amplificador**.

`kicad/system-candidate/`: 76 componentes/212 pads, core OEM+29 analógicos no
mesmo schematic/PCB de estudo. GND/AUX_RAW compartilhados; amps em ANALOG_12V.
Removidas interfaces lógicas J101–103, não novos conectores físicos. Footprints
candidatos atribuídos; analógico em banco externo ao contorno, sem placement/fit.
**Ponte DIFF_POS/NEG→TPA aberta**, proteção/mute/supervisor não implementados.
RCA/LINE-LFE/volume/fase/high-pass/limiter/DC e conversão T1 não completos.
B/OEM/capturas D-016/D-018 anteriores preservados; não sobrescrever buffers.

## Assets efetivamente encontrados

- CAD Würth WCAP-ATG5/WE-HCF rev26c baixados de fabricante e registrados na
  candidata para C1/C201/C202/L1/L2. STEP inalterados, licença CC BY-SA4.0 e
  exceção de designs conferidas; atribuição/avisos em `kicad/models/vendor-wurth/`.
  Geometria nominal simplificada, não tolerância/fit/capacidade térmica garantida.
- J1/J5 691137710002 STEP rev1 baixado, mas licença de redistribuição/registroXYZ
  não presumidos. Fonte direta: <https://www.we-online.com/components/products/download/691137710002%20%28rev1%29.stp> . Local somente nesta etapa.
- U1 TPA3255DDVR: gateway oficial <https://vendor.ultralibrarian.com/TI/embedded/?gpn=TPA3255&package=DDV&pin=44> . Download autorizado/termos ainda necessários;
  não usar modelo bottom-pad/DAP38. Package DDV0044D no apêndice TI p44–46.
- J6 OEM é land de trança, não peça com corpo CAD. WIMA STEP oficial não
  localizado; modelos genéricos identificados não se tornam CAD do fabricante.

## Footprints/MPNs candidatos, não qualificação concluída

C101–106 MKP2D031001F00JSSD (100nF100V5%); C203 MKP2C041001N00JSSD
(1µF63V5%). WIMA MKP2 **03.26 p37–38**, ordering/dimensões/PP/tanδ;
<https://www.wima.de/wp-content/uploads/media/e_WIMA_MKP_2.pdf> . Pitch5mm,
lead0,5; footprints nominais conservadores, tolerâncias máximas de corpo TBD.
C203+6×100n máximos iniciais somam1,68µF; cálculo de budget, não dinâmica exata.
ESR C203≤0,0838Ω calculada de tanδ máximo só a1kHz/20°C, não todo envelopeD-018.

R202/203 TNPW12061K00BEEA/TNPW12062K20BEEA (0,1%/25ppmK). Vishay28758
rev10-Apr-2026 p1–4/15, <https://www.vishay.com/docs/28758/tnpw_e3.pdf> . Land IPC
reflow Vishay28950 rev12-Jul-2022 p1: pads1,15×1,80,centros±1,45mm;
<https://www.vishay.com/docs/28950/recsoldpaddims-drabeyresfus.pdf> . Derating/drift
não fechados; não assumir variação total igual à tolerância inicial.

R201 AC03000001509JAC00 é o exemplo15Ω5% do fabricante, Vishay28730
rev05-Dec-2024 p2/10, <https://www.vishay.com/docs/28730/ac_ac-at_ac-ni.pdf> .
Body≤13×4,8,lead0,8±0,03mm; footprint conservador exige conformação de leads.
Cálculo com1128µF/13,2V/Rmin14,25Ω: I0≈0,926A,P0≈12,23W,E≈0,09827J,
τ≈16,07ms. Curvas/ensaio de sobrecarga não qualificam qualquer repetição/quente;
5%inicial+TCR/drift pode ultrapassar envelope total5%. **Continua bloqueador**.

## Achados de controle — corrigir antes de energia

TI TPA3255 **SLASEA8A RevA out2016 §11.2 p30** recomenda RESET baixo≥250ms
apósPVDD ligar. Fig32 pré-carga≈200ms não é timeout máximo garantido.
**§7.5 p8**: RESET VILmáx0,8V/fugamáx100µA. R9 legado10k1% pode produzir
1,01V com essa fuga, sem sequer somar driver. Candidata4,7k1% com110µA dá
0,52217V; nenhum resultado de power-off/controle externo medido.
FAULT/CLIP_OTW têm pull-ups internos20…32k aDVDD: R7/R8 externos podem
realimentar controle morto; não unir nova3V3 ao J4 automaticamente.

TPS3808 **SBVS050N RevN ago2026 p7**: CTaberto12/20/28ms; CTfixo aVDD por
resistor40…200k180/300/420ms. Uma etapa “300ms” permite180ms (<250); duas
cascatas dão mínimo360ms. Datasheet: <https://www.ti.com/lit/ds/symlink/tps3808.pdf> .
Candidato temporal, não circuito pronto; propagação MR/SENSE só típica, captura
FAULT/POR/partial-power/backfeed ainda requer prova física.

## Sequência definida como especificação executável — NÃO firmware

`scripts/sequence_contract.py`, regressões `tests/unit/test_sequence_contract.py`:

- SAFE→QUALIFY: rails reais/ref/VMID válidos, áudio0/isolamento aberto.
- Hold mínimo360ms desde qualificação; nova borda humana, não botão mantido.
- WAIT_DRIVERS: retirar descarga; observar drivers quietos e erro de ambas
  placas≤10mV e confirmação de descargaOFF antes de comandar conexão.
- CONNECT_QUIET: confirmar fechamento físico antes de liberarRESET.
- START_AVDD: observar FAULTbaixo inicial e depois alto; alto mascarado porRESET
  não arma RUN. Timeout proposto, não startupTPA garantido.
- PRECHARGE: **ambos DCs** válidos contínuos12ms, quietude eFAULT armado antesáudio.
- RUN: falhaPG/ref/VMID/DC/FAULT/fase-volume abre/muta/RESETbaixo; descarga somente
  depois de isolamento físico confirmado. FAULT voltaralto não autorrearma.
- Rearme≥12ms depois de latch/eventoFAULT, nova ação humana; sem restart por
  brownout, FAULTmascarado ou botão antecipado. Ausência de observação falha segura.

Observações são sinais de **circuitos ainda faltantes**, não GPIOs existentes.
Modelo de ordem/timers, não simula tensão, injeção, bounce real, pinosoff ou
saída do TPA. `latency_qualified()` rejeita máximos desconhecidos/meros típicos.
Não há prova física de abertura≤100µs nem circuito de supervisor/mute concluído.

## Proteção pesquisada — não trocar requisitos por marketing

- ADG4612/4613: triagem de texto ADI Rev0 out2010 tables5/6 p8–9: faixa de
  isolamento−5,5…16V/span16V, não±16V; absoluto negativo−7V. Rejeitadas.
- ADG5412**BF**BRUZ: candidata bidirecional±55V/span80V (ADI RevB jan2016
  table6 p12). **F semB protege sóS.** Q≈−340pC eCoff≈15–16pF são típicos
  (+12V), sem teto; condições de floating/partial/fault não fecham D-019.
  PDFs ADI diretos falharam; extração porrelay daURL oficial foi só triagem,
  não inspeção gráfica/pinagem autorizada para implementar.
- TI TMUX4827 **SCDS457B jul2024 §5.1 p4/§5.8 p8–9**: ±12V/span15V e
  tTRANmáx220/490µs, não±16V/100µs. Rejeitada para contrato atual;
  <https://www.ti.com/lit/ds/symlink/tmux4827.pdf> .
- Relé NO pode isolar ambos lados, mas3ms não atende100µs. Exige outro projeto
  de reserva/slew/tempos com decisão explícita, não relaxamento silencioso.

**Nenhuma chave pesquisada demonstrou todos os limites.** Não prova inexistência.
Próximo trabalho: obter PDF primário ADG5412BF/alternativas, redesenhar e analisar
budget completo incluindo C_SD (CoffaoGND não é capacitância mútua), sensores,
RCA ativa, partial-power e parasitas. Não colocar chave genérica/DNP ponte fechada
para aparentar conclusão. Todos gates pendentes; sem compra/energização.

## Evidência desta candidata

76 regressões offline passaram; `make simulate` preservou contraprovas obrigatórias,
ambas capturas históricas passaram checks nativos. Candidata: ERC4 conflitos de
saída +1 avisoMONO_BIASED isolado, **sem exclusão**; DRC0 geometria/0 paridade/
163 conexões ausentes. Banco externo ao contorno continua não colocado/roteado.
Revisor independente identificou e regressões corrigiram dwell reutilizado,
perda de fechamento/quiet/match/isolamento, feedback contraditório, UUIDs
multiunit e corrida de overwrite. Sem sign-off físico.
[Ledger de hashes e fatos](../tests/reports/system-candidate-review.json),
[mídia nativa e escopo](images/system-candidate/README.md). Atribuição/registroCAD
não são qualificação dimensional. Original e local WCAP pads(0,0)/(5,0) coincidem;
HCF CCW90° mapeia−X para+Y da biblioteca local; tab mecânico continua semnet.
