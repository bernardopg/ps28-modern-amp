# GitHub e espelho do planejamento

Repositório: <https://github.com/bernardopg/ps28-modern-amp>.
Cada task aberta de `.tasks/items/` tem uma issue espelho; o mapa está em
[github-mirror.json](../.tasks/github-mirror.json). O backlog local é canônico.

## Publicação

**Commit e push direto em `main`** (proprietário, 2026-10-16). Sem branches de
trabalho sem pedido. Snapshot local, `make check` e revisão do diff antes do push;
nunca force-push nem reescrita de histórico publicado.

## Issues e gates

- Issue espelha título, estado e critérios da task; fechar junto com a task.
- Done é trabalho de projeto concluído, não aprovação de gate.
- G1–G4 são registros humanos; nenhuma issue fecha só por ERC/DRC ou render.
- Milestones M0–M4 agrupam as issues; não há Projects board.

```sh
python3 scripts/publish_backlog.py          # dry-run: issues faltantes
python3 scripts/publish_backlog.py --apply  # criar faltantes (com autorização)
```

O script não reabre nem sobrescreve issues existentes; reconciliações são explícitas.

## CI

`.github/workflows/validate.yml` roda `make check` e as simulações ngspice
(incluindo o macromodelo oficial OPA1656 em container efêmero). Actions fixadas
por SHA, Ubuntu 24.04. ERC/DRC nativos e revisão de hardware são locais.
**Nenhum push autoriza fabricar, comprar ou energizar.**
