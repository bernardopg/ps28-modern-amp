# Changelog

Mudanças de infraestrutura/documentação separadas da revisão física Rev. A.

## [Unreleased]

### Added
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
