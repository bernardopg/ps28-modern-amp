# Skills do projeto
Fonte única skills/<nome>/SKILL.md; links .claude/skills e .agents/skills apontam aqui.
Pi descobre `.agents/skills/` no projeto; executar `/reload` após mudanças, ou usar
`/skill:hardware-researcher` (e demais nomes) para forçar carregamento.
Nesta sessão, carregar SKILL.md explicitamente se o catálogo ainda estiver desatualizado.
Não instalar globalmente: evita aplicar regras de amplificador a outros projetos.

- reference-design-guardrails: mudança no core/LC ou comparação com TI.
- schematic-review: revisão pin-a-pin, rails e front-end.
- class-d-layout-review: switching, PowerPAD, retornos e mecânica.
- bom-dfm-review: MPN, package, CPL e release readiness.
- bringup-review: checkpoints, instrumentação e gates físicos.
- hardware-debugger: hipótese→teste seguro→medida→causa, sem tentativa perigosa.
- hardware-researcher: fontes primárias, revisão/hash e conflito de evidências.
- parts-procurement: preço landed/autenticidade/disponibilidade sem compra automática.
- hardware-system-engineer: requisitos, trade-offs, budgets e gates multidisciplinares.

Cinco skills originais foram preservadas e reescritas; quatro novas complementam o fluxo.
Prompts e critérios em evals.json por skill; estrutura testada automaticamente.
Avaliações comportamentais/baseline independentes ainda NÃO executadas; estas skills
são playbooks iniciais, não credenciais profissionais nem validação de engenharia.
