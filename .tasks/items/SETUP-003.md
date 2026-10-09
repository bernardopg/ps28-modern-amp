---
id: SETUP-003
title: GitHub e revisão do setup
status: In Progress
milestone: M0
sprint: S01
depends_on: SETUP-002
updated: 2026-10-09
---

# SETUP-003 — GitHub e revisão do setup

## Objetivo

GitHub e revisão do setup, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [x] Repositório privado e main enviados
- [x] Workflow remoto confirmado
- [x] Headroom local compartilhado entre Claude Code, Codex, Pi e Hermes
- [ ] Proprietário revisou escopo, backlog e pendências

## Evidência

GitHub privado: <https://github.com/bernardopg/ps28-modern-amp>.
CI inicial aprovado: <https://github.com/bernardopg/ps28-modern-amp/actions/runs/37654550846>
Review do proprietário ainda pendente; task permanece In Progress.

Atualização de 2026-10-08: D-019 publicado em main (`e26f61f`), CI completo
aprovado: <https://github.com/bernardopg/ps28-modern-amp/actions/runs/37784991096>.
Docs/tasks e galeria nativa regenerada com separação explícita entre core e
capturas/contrato analógicos ainda sem PCB. Histórico/revisões preservados;
nenhum review humano inferido desse pedido de atualização. WIP permanece2,
S03 planejada e gates G0–G5 pendentes. Ver `docs/development-status.md`.

Atualização de 2026-10-09: acesso MCP dos quatro harnesses configurado para o
mesmo banco `.headroom/memory.db`, independente do provedor de modelo.
Carregadores nativos e consultas de memória validados; configuração privada
fora do Git. Ver [relatório Headroom](../../tests/reports/headroom-harnesses.md)
e [instruções de uso](../../docs/headroom.md). Review do proprietário e gates
de hardware continuam pendentes; nenhuma task adicional entrou em WIP.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
