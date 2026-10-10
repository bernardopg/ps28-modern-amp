# Documentação técnica

Começar pelo [estado consolidado D-018/D-019 e mapa das capturas/PCBs](development-status.md)
e pela [galeria 3D nativa atual](images/kicad-3d/README.md). Estudos analógicos não
foram integrados à PCB; planejamento/gates não avançam por aparência do render.

Ordem: [requisitos](requirements.md) → [arquitetura](architecture.md) →
[captura elétrica](schematic.md) → [layout](pcb-layout.md) →
[simulação](simulation.md) → [fabricação](manufacturing.md) → [bring-up](bringup.md).

Transversais: [segurança](safety.md), [decisões](decisions.md), [referências](references.md),
[toolchain](toolchain.md), [auditoria de origem](source-review.md),
[Headroom por projeto e harnesses](headroom.md),
[compras/BOM](procurement.md), [assets](assets.md), [GitHub/CI](github.md), [transformador original](transformer-reuse.md), [primeiro núcleo PCB](core-draft.md), [seleção/placement atual B](selected-core.md), [operacionalidade e candidata OEM refinada](functional-readiness.md),
[front-end LR4 e headroom em estudo](analog-lr4-study.md),
[captura KiCad e modelo oficial OPA1656](analog-capture.md),
[VMID físico e bloqueio de desligamento](vmid-buffer-study.md),
[correção D-018 — rail protegido/VMID passivo](vmid-protection.md),
[interface TPA: desligamento/pré-carga e contrato D-019](input-power-order-study.md).
[D-021 — fonte PVDD não regulada: simulação e captura](power-d021.md),

[D-023 — sequenciador discreto D-020](seq-d020.md),

[D-024 — isolamento D-019 por relé, mute e DC](iso-d019.md),

[caminho até produção](production-roadmap.md).
[D-020 — integração candidata, CAD e sequência executável](integration-protection-review.md):
76 componentes importados, proteção física ainda aberta; não hardware completo.

Planejamento vive somente em `.tasks/`; instruções de agentes somente em `AGENTS.md`.
