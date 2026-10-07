---
name: bom-dfm-review
description: Use para BOM/MPN/footprints/CPL/DNP, montagem exposta e checklist de fabricação, sem liberar pedido.
---
# bom-dfm-review
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Derivar refs/quantidades do schematic congelado; conferir manufacturer/MPN/package/ratings.
2. Comparar BOM↔CPL↔PCB, DNP/pin1/rotação/polaridades, PowerPAD/paste e TH acessível.
3. Verificar lifecycle/estoque com timestamp e alternativas eletricamente equivalentes.
4. Conferir fab capability, pacote/tag/checksum e assinaturas G2/G3; recomendar bloqueio se faltar.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
