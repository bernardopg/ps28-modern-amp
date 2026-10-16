# GitHub e espelho do planejamento

Repositório: <https://github.com/bernardopg/ps28-modern-amp>.
Estado reconciliado em **2026-10-16**: 21 tasks/21 issues espelhadas,
**12 concluídas e 9 abertas**. PCB-002 é a única In Progress; as outras oito
abertas estão To Do. Estados oficiais e dependências em `.tasks/items/`;
relações em [github-mirror.json](../.tasks/github-mirror.json).

As issues recebem o corpo da task local, estado e evidência. Uma task de projeto
Done não aprova bancada; G1/G2/G3 permanecem humanos e explícitos. Nenhuma issue
foi fechada só por ERC/DRC zerado ou por um render.

## Publicação desta consolidação

Branch: `fix/production-readiness-20261015`, com mudanças de placa, modelos,
documentação, renders, testes e planejamento. O conteúdo da branch não se torna
`main` por push; uma integração posterior exige revisão. Links relativos nos
corpos das issues apontam para esta branch, não silenciosamente para `main` antigo.

```sh
python3 scripts/publish_backlog.py          # dry-run: listar faltantes
python3 scripts/publish_backlog.py --apply  # criar faltantes, com autorização
```

Esse script não sobrescreve/reabre issues existentes e não é sincronização
bidirecional. A reconciliação desta sessão é explícita, não mudança de ferramenta.
Não há Projects board; milestones/issues e backlog local atendem ao planejamento.
[Registro da sincronização](../tests/reports/publication-sync-2026-10-16.json):
21 corpos/estados conferidos sem fechar ou reabrir issues por inferência.

CI executa validações/testes da configuração versionada; conferir o resultado do
run do commit antes de afirmar CI remoto aprovado. Validação nativa local de
ERC/DRC e revisão de hardware continuam separadas. Nenhum push autoriza fabricar,
comprar ou energizar a PCB.
