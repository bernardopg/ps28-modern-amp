---
name: parts-procurement
description: Use para procurar peças/fontes/módulos e comparar preço, qualidade, estoque, frete/impostos e alternativas sem realizar compra.
---
# parts-procurement
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Solicitar MPN/spec/quantidade/destino/orçamento/prazo; não publicar endereço pessoal.
2. Filtrar qualidade/autenticidade/lifecycle e fornecedores antes do preço.
3. Comparar fontes equivalentes com timestamp, moeda/MOQ/estoque/lead time e landed cost.
4. Anotar frete/impostos/câmbio desconhecidos e validade; não simular estoque confirmado.
5. Alternativas precisam revisão de ratings/footprint/thermal; retornar shortlist e recomendação condicional.
6. Não pagar, enviar pedido nem preencher dados pessoais sem autorização específica.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
