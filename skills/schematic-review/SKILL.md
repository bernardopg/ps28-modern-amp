---
name: schematic-review
description: Use ao revisar schematic, pinagem, bias/VMID, NE5532, LPF, proteção e power sequencing; produzir achados rastreáveis.
---
# schematic-review
## Entrada
Ler AGENTS.md, task atual e documento técnico pertinente. Pedir artefatos reais
e limites ausentes; não transformar TBD em fato.
## Método
1. Ler requirements/schematic e extrair netlist real; container vazio significa não revisável.
2. Auditar pin-a-pin rails/mode/control/boot/LC, RESET e pull-ups open drain.
3. Verificar soma L/R, bias/acoplamento, headroom e estabilidade VMID/op-amps; não confiar em valores legados.
4. Rodar ERC e separar falsos positivos justificados de riscos que ERC não cobre.
## Saída
Objetivo; evidências e referências (documento/revisão/página); achados por severidade
com componente/net; hipótese/cálculo/simulação/medida; ações, testes e bloqueadores;
gates pendentes e atualização da task. Sem sign-off, fabricação ou compra automática.
## Avaliação
Usar evals.json; avaliação estrutural não comprova comportamento nem expertise.
