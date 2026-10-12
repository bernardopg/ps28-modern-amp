# Changelog

Mudanças de infraestrutura/documentação separadas da revisão física Rev. A.

## [Unreleased]

### Medidas OEM — 2026-10-12
- Registrada altura de capacitor 45 mm + folga superior pouco maior que 30 mm,
  informada pelo proprietário: envelope 52 mm deixa ~23 mm na região original.
  Resolve altura local do estudo, não fit global/térmica.
- Inventariadas dez fotos locais por hash; conector T1 de três vias e trava,
  hipótese JST VH sem atribuir fabricante/MPN pela aparência. Originais fora do Git.

### Pesquisa e remediação D-028 (proposta)
- Captura isolada `kicad/power-researched`: candidatos RHRP1560 e LGU2A472MELC
  por fonte primária, footprint de estudo do bulk; ERC 0, não integra PCB.
- Reanálise de 54 transientes D-021: corrente CT pela soma dos diodos, máximo
  8,014 A RMS e 63,640 A²s/100ms. Contraprova reprova OVLO interno LM5069 para
  janela 49,84–53,5 V. Scripts e sete testes novos; 118 testes totais OK.
- Fontes oficiais e limites em `docs/power-remediation.md`; fit/OVP/SOA/ratings
  ainda bloqueiam placement e fabricação. Candidata roteada preservada.

### Captura de revisão de potência
- Criada `kicad/power-package-review/` e gerador sem sobrescrita: remove seleções
  falsas/incompatíveis mantendo nets D-021. ERC 0; 111 testes de infraestrutura.
- Fonte primária onsemi MUR3020WT/D Rev.7 p.2 reprova MUR3040WTG: IFSM é 150 A,
  não 200 A. Seleção D-025 bloqueada independentemente do footprint.
- PCB roteada preservada; captura nova não possui placement, não libera produção.

### Revisão de prontidão da candidata
- Adicionado `make pcb-readiness`: auditoria parcial bloqueante de inventário e
  DRC nativo com paridade/refill, sem salvar a PCB; quatro testes de regressão.
- Corrigida interpretação do ratsnest: há 18 itens desconectados, inclusive
  potência; revisão rastreável em `docs/pcb-readiness-review.md` registra também
  incompatibilidades MPN/footprint, inrush e OVP não qualificados. Não libera fab.

### Added
- PWR-001 fechado por fonte primária com decisões formais **D-025/D-026/D-027**:
  diodos **MUR3040WTG** (VRRM 400 V, IF(AV) 15 A, IFSM 200 A; STTH8L06 rejeitado por
  IFSM 120 A); bulk **Rubycon 63USC4700MEFCSN30X30** 2× (4700 µF/63 V, 3,49 A rms
  @120 Hz, LCSC C1498587 — única família que entrega 4700 µF/63 V com ripple ≈3,5 A);
  conector **JST VH SVH-41T-P1.1** (20 AWG). Datasheets arquivados em `reference/parts/`
  com SHA256; relatório `tests/reports/power-pwr001-parts.json`.
- D-026: proteção de sobretensão de PVDD **por arquitetura** — o requisito "TVS Vc<69 V"
  é inviável com TVS passivo de 51 V (SMCJ51A grampeia 82,4 V > 69 V abs max do TPA3255,
  SLASEA8A p.5 §7.1). Proteção sustentada pelo OV do TPS3700 (50,97–52,24 V); SMCJ51A
  apenas absorve transiente rápido.
- D-027: inrush do bulk tratado pelo **fusível time-lag** (rating por corrente de
  operação), sem NTC/relé de bypass — replicando a abordagem da placa original.
  I²t exato/ampere a confirmar em BENCH-001.

### Changed
- `power-d021` e `system-candidate` regenerados com os MPNs D-025 (D301/D302=MUR3040WTG,
  C301/C302=Rubycon 63USC, D303=SMCJ51A, F301=T time-lag, J301=JST VH). ERC power-d021
  0 erro (2 warnings de interface). Conectividade inalterada; NTC/relé de pré-carga
  (N301/K301) **não** implementados (D-027).
- PCB-002: autoroteamento de estudo **retomado da sessão interrompida** — import do
  `system.ses` (2.348 trilhas/208 vias) + 2ª passada Freerouting `--resume`
  (2.430 trilhas/212 vias). 6 pares abertos em 4 nets (AUDIO_EN, C_START, caudas de
  FAULT, 3 pads de VMID), bloqueados pelo fanout do TPA3255 + keepout do perfil U;
  fechamento fica para a revisão manual com pours. DRC kicad-cli: 0 erros elétricos
  (clearance/curto/furo), 105 avisos de silkscreen, 4 stubs dangling. Tentativa de
  rota manual de FAULT via PNS violou keepout/curto e foi revertida por rip-up.
- `integrate_candidate.py`: corrigido `.kicad_pro` gerado que herdava
  `top_level_sheets` da fonte (apontava `ps28-modern.kicad_sch`).
- Renders 3D da galeria regenerados com a candidata roteada (`make render-3d`).

### Removed
- `kicad/jlcpcb/`: Gerber/BOM/CPL obsoletos do draft A (`A-core-draft`, sem
  roteamento, sem LCSC), removidos para evitar pedido acidental. Release futuro
  segue `docs/manufacturing.md` (gerar em `build/`, liberar só após G3).

### Fixed
- `analog-protected.svg` restaurado ao export nativo KiCad registrado no manifesto;
  o commit de lint o havia reformatado e quebrado `make check`. Marcado `binary`
  em `.gitattributes` como `system-candidate.svg`.

### Added
- `.gitignore`: ignora `.history/` (backups do KiCad) e remove do índice o gitlink
  órfão `kicad/.history` (repo aninhado, ausente de `.gitmodules`). Resolve marcadores
  de conflito de merge/stash commitados em 3412f04, mantendo a variante comentada
  (Upstream) para não ignorar `.claude`/`.codex` por inteiro e preservar os symlinks
  versionados `.claude/skills`, `.agents/skills` e `CLAUDE.md`.

- README reescrito como índice/wiki visual: hero com o render 3D da candidata de
  sistema (D-023), faixa de estado, renders funcionais (schematics nativos KiCad
  embedados) e tabelas de navegação recolhíveis por área; detalhamento textual
  movido para `<details>`. Sem novos assets — apenas links aos exports existentes.
- `make route-system`: autoroteamento Freerouting da candidata (463/470 conexões, plano
  GND em In1, DRC sem clearance/curto) e modelos 3D de envelope (TPA3255 DDV, JST VH,
  WR-TBL, parafuso M3) a partir dos datasheets; render 3D sem corpos faltando exceto J6.
- PCB-001: candidata usa o contorno OEM medido 154 × 81 mm, 4 furos M3 e área
  proibida do perfil U (65 × 33 mm) no lugar do contorno inferido 153 × 79,1;
  placement de estudo de todos os 204 componentes (topo/fundo), DRC só com silkscreen;
  README mostra o render 3D mais recente.
- MECH-001: medidas do proprietário de backplate, dissipador externo e perfil U em
  `mechanical/oem-heatsink-measurements.{md,json}`, conferidas contra a BOM do manual;
  placa principal 154 × 81 × 1 mm com 4 furos M3, base do perfil apoiada na PCB (keepout 33 × 65 mm, bloco térmico do TPA na perna externa).
- `docs/production-roadmap.md`, ELEC-004 (front-end D-022, issue #20), estado do
  projeto reescrito para a candidata de sistema; auditoria dos footprints DGK0008A e
  G6K-2F contra os desenhos de fabricante.
- D-024a: clamp BAT54 + 3,3 kΩ série nos pinos de entrada do TPA (falha simples para
  GND ≈ −5,9 V → ≤ −0,351 V no VF máximo), casos de falha simples na simulação,
  footprint TI DGK0008A para o TMUX6219 e tabela de tratamento dos riscos D-019.
- D-024: interface D-019 em `kicad/iso-d019/` — relé Omron G6K-2F Form C após
  C20/C21 (NO no pino, NC descarga), mute TMUX6219, janelas DC dos pinos e de AUX
  (TPS3700); lógica de RESET pós-conexão, dwell DC e latch de áudio no sequenciador.
  `make simulate-d019`: 1350 casos ngspice, pino −0,262…6,61 V. Ponte de sinal
  fechada só via relé na candidata (200 footprints, DRC 0).
- D-023: sequenciador discreto D-020 (subconjunto sem D-019) em `kicad/seq-d020/`:
  LP2985 3,3 V, 2× TPS3808 (hold ≥360 ms), latches 74LVC2G74 para partida humana e
  arme/latch de FAULT, timeout 0,62–1,44 s, janelas TPS3700 de ANALOG_12V/VMID.
  Modelo lógico da netlist capturada com testes de mutação.
- `system-candidate` integra D-021 e D-020: 150 footprints, `PVDD_36V` vira `PVDD`,
  J4/R7/R8 DNP; ERC igual à base, DRC 0 violações. Galeria 3D inclui a candidata.
- D-021: AUX 12 V (LM5164, exemplo TI SNVSAU4D Fig 7-1) e janela de PVDD
  (TPS3700, OV 50,97–52,24 V, UV 27,3–28,4 V pior caso) capturados em
  `kicad/power-d021/`; saída RAILS_OK open-drain para rails_valid D-020, não
  direto no RESET. ERC 0; footprints e parte dos MPNs TBD.
- Conector do chicote de T1 documentado por foto: 3 vias vermelho–preto–vermelho,
  CT no centro, coincide com J301; passo ≈ 4 mm (família 3,96 mm), fio 20 AWG UL1015; série/rating TBD, com risco de corrente
  registrado em `docs/transformer-reuse.md`.
- D-021: `make simulate-power` (54 casos ngspice com T1 medido) e captura isolada
  `kicad/power-d021/` (retificador CT, fusível, bulk, bleeder, TVS; ERC0, MPNs TBD).
  TPA3255 não tem OVP de PVDD: supervisor externo especificado, não capturado.
- Woofer `20PR10DAG-FW06-E` sem T/S públicos; limiter provisório 100 W e
  limites de DC/transitório do manual como piso de REQ-007.
- Woofer Re medido 4,4 Ω (pontas 0,6 Ω descontadas), dentro do manual; correção
  da resistência das meias-bobinas de T1 para ≈0,2 Ω.
- D-021: PVDD não regulado ≈42–50 V por retificação CT de dois diodos de T1
  (34,35 VAC/metade medido), substituindo o buck 36 V de D-010. D-022: crossover
  ajustável 50–150 Hz no controle original. Requisitos, README e AGENTS atualizados.
- Confirmação física de T1 e do painel original em `docs/transformer-reuse.md`
  (etiqueta, secundário de 3 fios, fusível, controles); sem medição de VAC/VA.
- Headroom MCP por projeto para Claude Code, Codex, Pi e Hermes, com banco
  compartilhado `.headroom/memory.db`, configurações locais fora do Git e
  instruções de acesso independentes do provedor em `docs/headroom.md`.
- D-020: candidata separada core+analógico76 componentes/212 pads, passivos/
footprints candidatos e CAD oficial Würth CC com atribuição; ponte de sinal aberta,
analógico fora do contorno em banco de importação, sem fit/proteção física completos.
- Especificação executável de sequência semMCU: hold≥250ms TI (candidata360ms),
FAULTmemorizado, pré-carga observada de ambos ramos, confirmação de isolamento,
novo dwell/rearme e rejeição de atrasos típicos como máximos. Não é firmware.
- Contraprova R9legado10k versus fuga100µA/VIL0,8V; candidata4,7k separada.
Gerador no-overwrite/no-replace, identidade multiunit auditada e regressões de
feedback contraditório. Pesquisa por três subagentes+revisão independente;
nenhuma fabricação/compra/energização/gate aprovado.
- Estado consolidado D-018/D-019: arquitetura, mapa das capturas/PCBs, riscos/
pendências e tasks/sprint/roadmap sincronizados, sem mudança de status/gates.
- `make render-3d`: galeria KiCad regenerada (6 PNGs/2 GIFs,16 câmeras/GIF),
contexto/hash dos estudos/captura e aviso de núcleo sem integração analógica.
Staging verifica todos os assets antes de promover manifesto; notas manuais e
revisões preservadas, sem modificar PCB/mounts ou inventar modelos ausentes.
- Relatório consolidado de checks/mídia/tasks,60 testes;19 tasks agora com
espelhos GitHub únicos, incluindo PCB-003 que estava sem issue. Rechecagem
nativa B/OEM mantém ERC4/109 não roteadas, geometria/paridade0; sem sign-off.
- D-019: 288 hipóteses RC/196 violações e quatro comparações ngspice para
C20/C21 e power-order TPA, mais duas redes com a alimentação D-018 intacta;
VMID protegido não qualifica entrada TPA. Capacitor/resistor série/chave upstream e conexão
com áudio preservados como contraprovas. Contrato de isolamento/pré-carga
condicional, sem MPN escolhido ou proteção física aprovada; fontes TI auditadas.
- `make simulate-input-order`, dez regressões offline, hashes de circuito/código/
capturas, logs de CI e integração ao `make simulate`; PCBs/schematics intactos.
- Teste de geração/refusal/retrocompatibilidade usa cache real de símbolos
  incorporados às capturas, permitindo CI sem bibliotecas globais KiCad;
  nenhum teste/critério/modelo suprimido. ERC nativo permanece validação separada.
- D-018 corrige o VMID D-017 sob envelope: divisor passivo/rail isolado/reserva,
  sem buffer indefinido no desligamento; prova RC com ESR/carga/fuga,33 cenários
  de rede e9 casos oficiais LR4. Critérios/contraprovas mantidos; sem sign-off.
- Captura integrada `kicad/analog-protected/`:32 componentes/80 pinos/ERC0,
  dois audits independentes e SVG/PDF nativos. Bloco lógico13/27 separado para
  revisão, não outra PCB. Originais/PCBs/galeria3D preservados.
- Gerador genérico retrocompatível, atômico/sem sobrescrita; auditoria da ligação
  dos opamps ao rail protegido rejeita até mutação consistente de XML/manifesto.
- Estudo de VMID físico D-017 com modelo TI íntegro:32 casos de return ratio,
  PM mínimo60,67°, contraprova sem isolamento/PM negativo, carga±1mA, ripple,
  referência inicialmente descarregada com AUX já válido e LR4 acoplado.
- Bloqueio de power-down pela análise RC independente: REF retida acima do
  rating de entrada sem clamp/descarga/backfeed qualificados. Sem captura
  insegura, MPN freeze, alterações às PCBs ou aprovação de gates.
- `make simulate-vmid`, relatórios/hashes/regressões e CI; runner PSA isolado
  compartilhado, sem modificar modelo do fabricante ou configurações globais.
- Estudo TI exige ngspice>=47 após falha real de convergência no42 do Ubuntu;
  CI usa job isolado Arch Linux/pacotes assinados, sem alterar modelo/critérios.
  Versão registrada, regressão de rejeição de runtime legado e invalidação de
  relatório mesmo quando falha preflight. Sem instalações no host do usuário.
- Diagnóstico de simulação TI preservado como artifact CI sem incluir modelo
  proprietário; HOME/PSA isolados no subprocesso para builds ngspice legados.
- Captura analógica KiCad isolada de21 componentes/58 pinos, candidato OPA1656ID,
  símbolo local auditado, ERC0 e14R/C comparados com netlist SPICE independente.
- Modelo TI SBOMAW6C/Final1.3 auditado sem redistribuir/vendor scripts;9 casos de
  supplies/temperatura no ngspice PSA local, com warnings/fallbacks explícitos.
- Exportações nativas PDF/SVG, fixtures/hashes e regressões;9 footprints, VMID e
  front-end completo permanecem pendentes; nenhuma PCB/mount/gate alterados.
- Contrato preparatório do supervisor contra TI: assinatura normal de FAULT baixo
  na partida, RESET baixo apaga FAULT, rearme≥4ms e latch sem oscilação automática;
  temporizações/circuito ainda TBD, sem MCU ou mudança no core.
- Estudo executável de front-end LINE LR4 com R/C explícitos, ganho unitário por
  seção e divisor1/2→diferencial;151 pontos de magnitude/fase,16.384 corners e
  2048 amostras. Modelo de headroom comportamental, NÃO NE5532 qualificado.
- Fontes TI SLOA024B/SLOS075K revisadas com hashes; explicitada ausência de garantia
  CM/swing em10,8–13,2V totais. ELEC-002 permanece bloqueada, sem alterar as PCBs.
- Galeria versionada do renderizador3D nativo KiCad:6 PNGs e2 GIFs com16 frames
  independentes cada, faixas de estudo não roteado, auditoria de modelos ausentes
  e SHA256/commit/comandos; reprodução por `scripts/render_kicad_gallery.py`.
- Candidata OEM refinada separada: contorno conservador153×79,1mm inferido,
  24 reservas nas quatro camadas, sem nova furação;47 footprints/142 pads,
  DRC0 geometria/0 paridade/109 não roteadas e ERC4 conflitos não excluídos.
- Revisão de operacionalidade com bloqueios de fonte, controle, entrada, proteção,
  dissipação e roteamento; nenhum gate físico aprovado.
- Modelo LC diferencial ngspice com201 pontos conferidos analiticamente; corrigido
  erro dimensional da frequência natural:51,9kHz, não1642Hz.
- Geração OEM atômica, validação por diretório explícito e cinco regressões novas.

- Projeto Git, containers KiCad 4 camadas vazios, CLI/CI e testes de infraestrutura.
- AGENTS único com links CLAUDE/skills; backlog, roadmap, S01–S05 e tasks rastreáveis.
- Auditoria toolchain, fontes TI com proveniência e skills engenharia/research/compras.
- Modelo LR4 ideal ngspice com verificação automática, sem alegação de hardware validado.

### Changed

- Starter truncado arquivado intacto; documentação reescrita com propostas/TBD/gates.
- PBTL M1/M2, diferenças LC datasheet/EVM e riscos de alimentação/medição esclarecidos.
- Manual PS28 Rev1 3/2007 recebido: D-009 recomenda qualificar o transformador original antes de comprar fonte; nenhuma tensão VAC/VA presumida nem alimentação simétrica ligada diretamente ao TPA3255.
- Manifesto de referências preserva documentos locais não TI em futuros downloads.
- D-010 seleciona reaproveitamento do T1 original com fonte secundária nova 36 V/12 V;
  fonte externa passa a bancada/fallback. Saúde dos componentes aceita conforme relato
  do proprietário; medições de ratings/envelope e gates permanecem pendentes.

### Referência mecânica OEM fixa
- D-014: mesmos mounting points e sistema de dissipação original, sem novos furos
  no plate; PCB nova se adapta à main PCB104-a05064a00-e.
- Conferidos desenhos p.17–18 e BOM mecânica p.15–16: cotas documentadas do plate,
  carcaça, dois dissipadores e suportes. Corrigida afirmação de que só havia cotas
  externas do gabinete. Entrecentros/escala1:1 ainda não declarados; gabarito a conferir.
- Substituído pedido de levantamento completo por conferência local do gabarito OEM.

### Core B selecionado
- 47 footprints/142 pads, MPNs e fontes; HCF2013, filme WIMA, bulk63V e terminais
  WR-TBL5,00mm com land patterns corretos. Modelo fixture/tab mecânico não é GND.
- Placement, silk/courtyard/paridade corrigidos. Quatro ERC classificados ainda
  sem exclusão; 109 conexões não roteadas mantidas no DRC.
- Integração ao gabinete/plate/dissipador originais por adaptador de cobre;
  furação/fit dependem de medidas reais, não dimensions externas do manual.
- Revisão anterior preservada (GUI aberta/IPC e acessibilidade indisponíveis).
- Checker rejeita camada Rescue e EDA elimina reports antigos ao falhar parsing/input.

### Hardware draft
- Primeiro core TPA3255/PBTL capturado: 47 componentes, 35 footprints e nets reais,
  sem roteamento; 12 footprints críticos ainda não selecionados.
- D-011 seleciona SLASEA8A figura31. Correção DDV: PowerPAD superior, footprint
  TopEP com 44 pads, não bottom-EP/vias/pasta central.
- Verificação independente de 116 pads e 11 testes aprovados; ERC 8 erros a revisar,
  DRC 85 não roteadas/12 footprints ausentes, sem liberação fabril.

### Pending

- G0–G5; circuito físico, ERC/DRC de projeto real, bancada, licença e fabricação.

### Infrastructure verification

- Repositório privado bernardopg/ps28-modern-amp publicado; CI inicial aprovado.
- 18 issues e cinco milestones espelham tasks; script dry-run/idempotente de criação.
- Warnings PROPERTY_ENUM de KiCad 10.0.7 registrados em TOOL-001; IPC sem conexão.
- Checkout CI atualizado para SHA da v7.0.1/node24 após aviso do runtime antigo.
