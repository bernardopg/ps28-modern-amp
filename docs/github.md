# GitHub e espelho do planejamento
Repositório privado: https://github.com/bernardopg/ps28-modern-amp
Main contém o starter original no primeiro commit e setup separado.

18 tasks publicadas como issues (16 abertas, duas de infraestrutura concluídas),
cinco milestones M0–M4; relações em `.tasks/github-mirror.json`.
Sprints/dependências/estado oficial continuam em `.tasks/`, não no título remoto.
Não foi criado GitHub Projects board; issues/milestones e backlog local atendem
planejamento sem exigir token com permissão adicional de Projects.

```bash
python3 scripts/publish_backlog.py          # dry-run, sem mutação remota
python3 scripts/publish_backlog.py --apply  # criar faltantes, aprovação explícita
```
O script nunca sobrescreve/reabre issues existentes. Mudanças de estado futuras
precisam ser reconciliadas manualmente; não é sincronização bidirecional.
CI valida docs/tasks/skills e modelo ideal, não ERC/DRC de hardware real.
Primeiro run aprovado: https://github.com/bernardopg/ps28-modern-amp/actions/runs/37654550846
Checkout fixado em SHA da v7.0.1/node24 para evitar runtime depreciado.
Revisão do proprietário do setup/arquitetura continua pendente.
