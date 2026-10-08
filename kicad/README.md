# KiCad — núcleo PBTL

## Revisão atual B
Abrir **core-selected/ps28-modern.kicad_pro**: 47 footprints completos e 142 pads
conferidos. Seleção/placement/revisão em ../docs/selected-core.md; sem roteamento,
fit medido ou fabricação. Make erc/drc/core-check usam esta revisão.
A revisão abaixo é histórica; não sobrescrevê-la a partir de buffers GUI antigos.

## Captura analógica isolada D-016
`analog-front-end/analog-front-end.kicad_pro`: 21 componentes/58 pinos, dois
OPA1656ID candidatos/quatro amplificadores; ERC0 e14R/C comparados com SPICE.
Sem PCB/fonte/VMID/supervisor completos; não acrescenta placa física à arquitetura.
Ver [captura e modelo oficial](../docs/analog-capture.md);9 footprints pendentes.

## Primeiro draft A (preservado)
Abrir `ps28-modern.kicad_pro`. Captura com 47 componentes e PCB com 35 footprints
em placement, ainda sem roteamento. Quatro camadas e contorno 145 × 95 mm provisórios.

U1: TPA3255DDV com PowerPAD **superior**, footprint oficial TopEP e 44 pads;
ligação/folga/dissipador ainda precisam de desenho mecânico. Não usar bottom exposed-pad.

Leia [estado e limitações](../docs/core-draft.md). ERC/DRC têm pendências explícitas;
nenhuma fabricação/energização aprovada. Fonte/analógico ficam fora deste incremento.
MPNs e 12 footprints críticos continuam TBD no core-manifest.json.
`make check` verifica consistência, não aprovação elétrica/térmica.

Biblioteca local `libraries/PS28.kicad_sym` registrada com ${KIPRJMOD}; passivos e
footprints usam bibliotecas oficiais KiCad. Geradores não devem sobrescrever edições futuras.
