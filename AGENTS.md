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

## Objetivo e modo de trabalho (D-030, 2026-10-12)

Objetivo único: **um subwoofer funcionando com uma placa nova** no gabinete PS28,
reaproveitando T1, dissipação, mounting points e chicotes OEM, modernizando o resto
(TPA3255 PBTL). Uma placa só, sem revisões intermediárias. Avançar sempre para a
fabricação; documentação serve ao projeto, não o substitui.

## Política de evidência — pragmática

- Ordem de fontes aceitas: medida do proprietário > manual de serviço PS28
  (`reference/infinity/`) > datasheet/catálogo do fabricante > nota de aplicação/EVM >
  prática consolidada de engenharia. Citar a fonte em uma linha; não exigir PDF arquivado
  para peças comuns (diodos, capacitores, fusíveis, conectores padrão).
- **A placa original é evidência válida:** o que ela fez por anos com o mesmo T1
  (KBL405, 2×6800 µF/50 V, JST VH 3 vias, fusível 2,5 A no primário) define margens
  mínimas razoáveis. Escolher componente igual ou melhor que o OEM com margem.
- Na falta de dado, **decidir com margem conservadora e registrar** a premissa em
  `docs/decisions.md` (uma linha: escolha, motivo, como confirmar). Não bloquear task
  por TBD que se resolve na primeira energização controlada.
- Não inventar pinagem nem resultado de medida. Pinagem vem de datasheet/footprint
  padrão KiCad; resultados só de medição real ou simulação identificada como tal.
- Antes de buscar na internet ou pedir medida, procurar no manual PS28 e em
  `mechanical/`, `docs/`, `tests/reports/`. Pedir ao proprietário só o que falta.

## Regras de segurança — inegociáveis

- Baseline D-010/D-021: T1 original; PVDD não regulado ≈42–50 V por retificação CT
  com dois diodos; auxiliar 12 V; TPA3255 PBTL; sem MCU nem primário AC na PCB nova.
  Nunca ligar vermelho–vermelho de T1 em ponte. Crossover ajustável 50–150 Hz (D-022).
- Modo PBTL: conferir M1/M2, INPUT_C/D e ligação dos quatro OUTs (SLASEA8A Fig. 31).
- SPK+ e SPK- são ativos. Nunca ligar ao GND nem à garra terra do osciloscópio.
- Não usar AVDD/DVDD como alimentação genérica; não improvisar bootstrap/OC_ADJ/FREQ_ADJ.
- Nenhuma compra, fabricação ou energização sem o "ok" explícito do proprietário.
  Primeira energização sempre com Variac ou lâmpada-série no primário e sem woofer.

## Trabalho e segurança digital

Um escritor de EDA por vez. Snapshot antes de mutação; revisar diff e recarregar
GUI após edição externa. **Trabalhar e publicar em `main`**, por determinação do
proprietário em 2026-10-16; não criar branches de trabalho sem pedido explícito.
Fazer snapshot local, validar e revisar o diff antes do commit/push; nunca usar
force-push ou reescrever histórico publicado para contornar conflitos. Não editar simultaneamente buffer GUI e disco. Não executar
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
**Placa única do produto: kicad/system-candidate/** (269 footprints, 3.535 segmentos,
500 vias; ERC/DRC/paridade/aberturas 0 em 2026-10-17). Base gerada por
scripts/integrate_candidate.py e pós-processada/roteada via KCAA/KiCad nativo;
não editar à mão nem regenerar sobre o cobre atual. Revisão local TPA e fit térmico
nominal concluídos; revisão global/G1/G2, fit físico/térmica/EMI e BOM/CPL pendentes.
Preamp/limiter OEM reaproveitado (D-032). Demais pastas kicad/ são histórico/insumo dos geradores. Ler docs/development-status.md
e docs/production-roadmap.md. Núcleo B em kicad/core-selected/ps28-modern.kicad_pro.
47 footprints/142 pads, ainda sem roteamento. Ler docs/selected-core.md.
D-014 fixa montagem/dissipação OEM e os mesmos mounting points por decisão do usuário.
Usar mechanical/original-board-reference.md: manual p.15–16 tem cotas nominais de
plate/carçaça/dissipadores/suportes, p.17–18 tem desenhos da placa original.
Não usar145×95 como contorno OEM nem presumir entrecentros/escala1:1 do PDF.
Reconstruir gabarito e adaptar PCB ao OEM; pedir só cotas locais faltantes, não novo levantamento
completo. Fit/furação final e capacidade térmica permanecem sujeitos a validação.
Terminais 691137710002 são 5,00mm (não5,08); tab HCF2013 é mecânico sem net.
Não sobrescrever documentos GUI abertos; IPC atual indisponível.

## Validação e fechamento de tasks

`make check` antes de commit; `make erc`/`make drc` quando mexer na EDA. Relatórios em
build/ (não versionado); resumos em tests/reports/. Uma task é **Done** quando o
trabalho de projeto dela está feito e verificado (ERC/DRC/teste/medida, o que couber).
Pendências de bancada viram critério da task de bring-up (BENCH-002), não bloqueio.
Fechar a issue GitHub espelho junto com a task. Limites de bancada numéricos e aprovados
pelo proprietário antes de energizar.

## Skills locais

Fonte em skills/<nome>/SKILL.md; .claude/skills e .agents/skills são links para ela.
Leia skills/README.md para catálogo e testes de comportamento. Skills não dão autoridade
de sign-off nem comprovam competência profissional; avaliações iniciais são pendentes.
