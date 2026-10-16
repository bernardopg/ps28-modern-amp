# GitHub e espelho do planejamento

Repositório: <https://github.com/bernardopg/ps28-modern-amp>.
21 tasks/21 issues espelhadas: **12 concluídas e 9 abertas**. PCB-002 é a única
In Progress; as outras oito abertas estão To Do. Estados e dependências em
`.tasks/items/`; relações em [github-mirror.json](../.tasks/github-mirror.json).

## Política de publicação — 2026-10-16

**Trabalhar, fazer commit e publicar diretamente em `main`**, por determinação
explícita do proprietário. Não criar branches/PRs de trabalho sem novo pedido.
Preservar segurança com snapshot local, revisão de diff e validações, não com
branches permanentes. Não usar force-push nem reescrever histórico publicado.

A consolidação `4346009`, inicialmente publicada em um branch temporário, foi
integrada por **fast-forward**, sem descartar commits. O branch temporário é
removido após confirmação do push em `main`. Links ativos nas issues apontam para
`blob/main`; nomes de branches nos relatórios de snapshots antigos são históricos.

## Issues e gates

As issues espelham corpo/estado/evidência da task local; o backlog é canônico.
Done refere-se ao trabalho da task, não a montagem/ensaio ou aprovação de gates.
G1/G2/G3 permanecem humanos: nenhuma issue fecha só por ERC/DRC ou render.

```sh
python3 scripts/publish_backlog.py          # dry-run do publicador inicial
python3 scripts/publish_backlog.py --apply  # criar faltantes, com autorização
```

Esse script não sobrescreve/reabre issues existentes e não sincroniza em duas
vias. Reconciliações são explícitas. Não há Projects board; milestones/issues e
backlog local atendem ao planejamento.

- [Primeira consolidação](../tests/reports/publication-sync-2026-10-16.json):
  snapshot histórico ainda no branch temporário.
- [Reconciliação em main](../tests/reports/main-sync-2026-10-16.json): estado atual
  das 21 issues e destino dos links.

## CI e organização

[Run 38930461712](https://github.com/bernardopg/ps28-modern-amp/actions/runs/38930461712)
**aprovado nos dois jobs**, sobre `4346009`. Resultado e escopo das simulações em
[simulation.md](simulation.md); não confundir reexecução com ampliação do modelo.
Cada novo push em `main` dispara sua própria CI; não herda o status do commit anterior.

Galeria atual em `docs/images/kicad-3d/`; renders parciais preservados em
`docs/archive/render-staging-2026-10-13/`. Staging/logs/cache ficam fora do Git.
Validações nativas de ERC/DRC e revisão de hardware continuam separadas da CI.
**Nenhum push autoriza fabricar, comprar ou energizar.**
