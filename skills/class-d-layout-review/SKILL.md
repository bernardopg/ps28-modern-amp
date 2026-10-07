---
name: class-d-layout-review
description: Use em placement/roteamento Classe D, PowerPAD, LC, GND, térmica e fit-check do amplificador.
---
# class-d-layout-review
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Obter PCB, stackup e geometria da referência; revisar com nets/pads reais.
2. Inspecionar PowerPAD→decoupling→switching loops→LC→speaker→GND→analógico→mecânica.
3. Avaliar cobre/vias por corrente/temperatura, retorno HF e montagem das vias térmicas.
4. Executar DRC/paridade e registrar imagens/coordenadas e limites ainda não calculados.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
