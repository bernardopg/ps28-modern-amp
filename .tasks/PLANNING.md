# Planejamento
Scrumban solo inspirado no wingdrive: sprints de duas semanas após ativação humana,
WIP máximo 2, backlog ordenado por risco/dependência, roadmap Now/Next/Later.
S01 é preparação: não há compromisso de datas nem capacidade inferida.

Fonte de estado: task .tasks/items/AREA-NNN.md. project-backlog é índice ordenado,
não segunda cópia de status; sprint lista IDs e objetivo, não marca hardware aprovado.
Milestone→epic (prefixo da área)→task; sprint é timebox, não gate.

Frontmatter obrigatório: id, title, status (To Do/In Progress/Blocked/Done),
milestone, sprint (backlog se não alocada), depends_on (IDs ou none), updated.
Ready: evidência de entrada, critérios testáveis, dependências Done, risco conhecido.
Done: todos critérios [x] com evidência, make check e validações pertinentes,
CHANGELOG atualizado, gate humano quando necessário. Não exigir sign-off hardware
para uma task apenas documental; não usar Done documental para aprovar o circuito.

Fim de sessão: atualizar task/log de sprint. Fim do sprint: review/retro e realocar
pendentes. Fim de milestone: evidência explícita e atualizar roadmap. GitHub issues
são espelho/discussão; atualizar task local para evitar divergência.
