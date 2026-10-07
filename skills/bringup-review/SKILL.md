---
name: bringup-review
description: Use antes ou durante energização/ensaio de amplificador; checar segurança de saída BTL, limites e checkpoints humanos.
---
# bringup-review
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Ler safety/bringup e bench-plan; sem limites/inventário/aprovação não energizar.
2. Confirmar woofer desconectado, sonda diferencial/carga/cooling/RESET/source limits adequados.
3. Acompanhar sequência rails→repouso→sinal baixo→resistiva com registro de medidas.
4. Parar por anomalia; ligar woofer somente após G4, com limites acústicos/excursão.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
