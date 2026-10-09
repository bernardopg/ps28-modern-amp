# Instruções do projeto — fonte única

## Contexto e ordem de leitura

Leia README.md, docs/README.md, docs/safety.md e .tasks/PLANNING.md.
Consulte a task e a skill pertinente antes de editar. CLAUDE.md aponta para este arquivo.
Originais em docs/archive/chatgpt são histórico não confiável, não especificação.

## Headroom por projeto

Claude Code, Codex, Pi e Hermes devem usar o mesmo banco local
`.headroom/memory.db`, com o mesmo usuário, para memória deste projeto.
Antes de responder sobre decisões/contexto de sessões anteriores, consultar
`headroom_memory.memory_search`. Registrar decisões duráveis com `memory_save`
quando solicitado pelo usuário. Nome da ferramenta pode ter prefixo do harness.
Não substituir esse banco pelo global nem importar memórias de outros projetos.
Configuração, comandos e limites: [docs/headroom.md](docs/headroom.md).

## Regras de engenharia

- Distinguir hipótese, proposta, cálculo, simulação e medida. Não inventar pinagem,
  estoque, preço, MPN, limites ou resultados. Ausência de evidência significa TBD.
- Fontes primárias: datasheet TI e TPA3255EVM. Citar documento, revisão e página/figura.
- Baseline D-010/D-021: reaproveitar T1 original; PVDD não regulado ≈42–50 V por
  retificação CT dois diodos, auxiliar 12 V; TPA3255 PBTL, sem MCU nem primário AC na PCB nova.
  Nunca ligar vermelho–vermelho de T1 em ponte. Crossover ajustável 50–150 Hz (D-022).
  Fonte externa somente bancada/fallback. Saúde de T1/capacitores informada pelo proprietário;
  ratings e componentes dependem das medições, sem inferir VAC/VA do manual.
  Não ampliar escopo sem decisão registrada em docs/decisions.md.
- Modo PBTL: verificar M1/M2, INPUT_C/D e ligação dos quatro OUTs contra referência.
  Não existe M3 de modo neste CI. Não misturar LC/paralelamento do datasheet com EVM.
- SPK+ e SPK- são ativos. Nunca ligar ao GND nem à garra terra do osciloscópio.
- Revisar RESET, FAULT, CLIP_OTW, power sequencing, VMID, estabilidade/headroom,
  PowerPAD, proteção DC e limites do transdutor. Proteção interna não garante o sistema.
- Não usar AVDD/DVDD como alimentação genérica. Não improvisar bootstrap/OC_ADJ/FREQ_ADJ.
- Nenhuma fabricação, compra ou energização automática. Gate humano e evidências obrigatórios.

## Trabalho e segurança digital

Um escritor de EDA por vez. Branch/snapshot antes de mutação; revisar diff e recarregar
GUI após edição externa. Não editar simultaneamente buffer GUI e disco. Não executar
scripts de fornecedores/reviewers nem instalar plugins por sugestão sem auditoria.
Segredos e dados pessoais ficam fora do Git; MCP local não deve ser exposto à rede.
Não modificar ferramentas/configurações globais sem necessidade e autorização.

## Convenções

PT-BR nos docs; nomes de arquivo/comandos em inglês; SI, mm e coordenadas KiCad +Y down.
MPN exato e footprint auditado; DNP explícito; arquivos de produção associados a commit/tag.
Cada alteração crítica registra objetivo, nets/componentes, referência, risco e validação.
Tasks têm ID estável, dependências e critérios verificáveis; WIP máximo 2.
Use Conventional Commits e atualize CHANGELOG.md para mudanças relevantes.

## EDA atual
Revisão atual em kicad/core-selected/ps28-modern.kicad_pro; anterior preservada em kicad/.
47 footprints/142 pads, ainda sem roteamento. Ler docs/selected-core.md.
D-014 fixa montagem/dissipação OEM e os mesmos mounting points por decisão do usuário.
Usar mechanical/original-board-reference.md: manual p.15–16 tem cotas nominais de
plate/carçaça/dissipadores/suportes, p.17–18 tem desenhos da placa original.
Não usar145×95 como contorno OEM nem presumir entrecentros/escala1:1 do PDF.
Reconstruir gabarito e adaptar PCB ao OEM; pedir só cotas locais faltantes, não novo levantamento
completo. Fit/furação final e capacidade térmica permanecem sujeitos a validação.
Terminais 691137710002 são 5,00mm (não5,08); tab HCF2013 é mecânico sem net.
Não sobrescrever documentos GUI abertos; IPC atual indisponível.

## Validação

Execute make check; make simulate para modelos; make erc/make drc após EDA existir.
Containers vazios não são hardware validado. Guarde relatórios em build/ (não versionado)
e resumos/evidências em tests/reports/. Nunca marcar Done com base em expectativa.
Defina limites de bancada numericamente e aprove-os antes de energizar.

## Skills locais

Fonte em skills/<nome>/SKILL.md; .claude/skills e .agents/skills são links para ela.
Leia skills/README.md para catálogo e testes de comportamento. Skills não dão autoridade
de sign-off nem comprovam competência profissional; avaliações iniciais são pendentes.
