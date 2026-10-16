# Relatórios persistentes
Só versionar resultados reais/resumos; logs brutos grandes ficam externos ou build/.
Separar testes de infraestrutura (não hardware), simulação ideal e medidas de bancada.
Template: objetivo, task/REQ, commit, instrumentos/modelos, setup, limites, resultados,
anomalias, conclusão, responsável e links/checksums dos anexos.

## Índice do estado atual — 2026-10-16

- [TPA/layout e fontes atuais](tpa-local-layout-review.json): conectividade/local;
  não aprovação global ou fabril. Mantém hashes históricos separados dos atuais.
- [Fit térmico](thermal-fit-review.json): CAD, malha e cálculo concentrado;
  não montagem real, FEM ou ensaio térmico.
- [CI/simulação](simulation-ci-2026-10-16.json): reexecução verificada do commit
  4346009, comparada a OPA1656/VMID/VMID protegido; não um novo modelo elétrico.
- [Issues/main](main-sync-2026-10-16.json): reconciliação de 21 tasks/issues;
  [primeira publicação](publication-sync-2026-10-16.json) é histórico do branch anterior.

Estudos elétricos: [OPA1656](opa1656-model-study.json),
[VMID](vmid-buffer-study.json), [VMID protegido](vmid-protection-study.json),
[fonte CT](power-d021-study.json), [D-019](d019-interface-study.json).
[Escopo, limites e comandos](../../docs/simulation.md).

`production-readiness-2026-10-15.*` e relatórios de núcleo/capturas anteriores
são snapshots históricos. Não substituir seus números/hashes pelos do PCB atual.
Logs brutos, macromodelos TI e pacotes de CI ficam em build/; PDFs baixados em
reference/ são cache ignorado pelo Git. Esses caches não são necessários para
abrir o projeto ou executar os testes de repositório offline.
