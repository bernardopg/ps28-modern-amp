# Relatórios

Resumos versionados de verificações reais (CAD, simulação, revisão). Logs brutos
ficam em `build/`. Relatórios datados registram o estado daquela data; não
reescrever seus hashes com os da placa atual.

- Layout e térmica: [revisão local TPA](tpa-local-layout-review.json),
  [fit térmico](thermal-fit-review.json), [prontidão PCB](pcb-readiness-review.json),
  [integração da candidata](system-candidate-review.json)
- Revisão e BOM: [revisão final](final-design-review-2026-10-16.json),
  [fechamento BOM](bom-closeout-2026-10-16.json),
  [capacitores SYS-002](sys002-capacitors-2026-10-17.json),
  [G0 Rev.B](g0-revb-approval-2026-10-17.json), [peças PWR-001](power-pwr001-parts.json)
- Simulação: [CI](simulation-ci-2026-10-16.json), [OPA1656](opa1656-model-study.json),
  [VMID](vmid-buffer-study.json), [VMID protegido](vmid-protection-study.json),
  [fonte CT](power-d021-study.json), [ordem de entrada](input-power-order-study.json)
- Ferramentas: [setup](setup.md), [Headroom](headroom-harnesses.md)

Escopo e comandos das simulações: [simulation.md](../../docs/simulation.md).
