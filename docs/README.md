# Documentação

Tudo aqui descreve a placa atual, `kicad/system-candidate/`.

## Começar

- [Estado do projeto](status.md) — onde estamos e o que falta
- [Segurança e gates](safety.md) — ler antes de qualquer manuseio
- [Requisitos Rev.B](requirements.md) · [baseline G0](sys002-baseline.md) ·
  [matriz de aceitação](../tests/acceptance.md)
- [Decisões D-NNN](decisions.md)

## Projeto elétrico

- [Arquitetura](architecture.md)
- [Esquema](schematic.md) · [SVG do esquema](images/system-candidate/system-candidate.svg)
- [Transformador T1 reaproveitado](transformer-reuse.md)
- [Fonte PVDD não regulada (D-021)](power-d021.md)
- [Sequenciador discreto (D-020)](seq-d020.md) ·
  [contrato RESET/FAULT](reset-supervisor-contract.md)
- [Isolamento da entrada por relé (D-024)](iso-d019.md) ·
  [ordem de energização da entrada](input-power-order-study.md)
- [VMID e rail analógico (D-018)](vmid-protection.md)
- [Derating dos capacitores](capacitor-derating.md)
- [Simulação](simulation.md)

## PCB e mecânica

- [Layout](pcb-layout.md) · [revisão local do TPA3255](tpa-local-layout-review.md)
- [Mecânica e medidas OEM](../mechanical/README.md) ·
  [fit térmico do bloco](../mechanical/thermal-block.md)
- [Renders Blender](images/pcb-studio/README.md) · [renders KiCad](images/kicad-3d/README.md)

## Produção e instalação

- [BOM: fechamento das 235 posições](bom-closeout-2026-10-16.md) · [compras](procurement.md)
- [Fabricação](manufacturing.md) · [revisão final de projeto](final-design-review-2026-10-16.md)
- [Montagem e primeira energização](bringup.md)

## Ferramentas e fluxo

- [Toolchain](toolchain.md) · [GitHub e espelho de tasks](github.md) ·
  [memória Headroom](headroom.md)
- [Referências](references.md) · [assets e licenças](assets.md)
