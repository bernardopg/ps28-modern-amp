---
name: reference-design-guardrails
description: Use ao alterar TPA3255, PBTL, mode pins, bootstrap, OC_ADJ, FREQ_ADJ, rails ou LC; exige evidência oficial antes de mutação.
---
# reference-design-guardrails
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Identificar CI/package e fonte primária com revisão/página.
2. Comparar baseline escolhido contra todas as nets afetadas; distinguir datasheet de EVM.
3. Listar desvio, justificativa, efeitos, riscos e verificações; bloquear se faltar pinagem ou figura.
4. Antes de editar salvar snapshot, confirmar escritor único; depois revisar diff/ERC/DRC pertinentes.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
