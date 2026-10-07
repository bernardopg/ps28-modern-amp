---
name: hardware-debugger
description: Use para FAULT, clipping, hum, pop, sobreaquecimento, rails ou amplificador que falha; diagnosticar por evidência e testes seguros.
---
# hardware-debugger
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Registrar sintomas, commit/revisão, condições, medidas, instrumentos e eventos da falha.
2. Construir hipóteses ordenadas por risco/probabilidade e uma variável por teste.
3. Começar desligado/descarga/inspeção, depois medidas de baixa energia autorizadas.
4. Conferir source/sequence/RESET/FAULT/shorts/bias/LC/térmica; separar causa de consequência.
5. Reproduzir correção e regressão com limites; nunca aumentar current limit para esconder FAULT.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
