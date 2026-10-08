# KiCad — núcleo PBTL

## Revisão atual B
Abrir **core-selected/ps28-modern.kicad_pro**: 47 footprints completos e 142 pads
conferidos. Seleção/placement/revisão em ../docs/selected-core.md; sem roteamento,
fit medido ou fabricação. Make erc/drc/core-check usam esta revisão.
A revisão abaixo é histórica; não sobrescrevê-la a partir de buffers GUI antigos.

## Integração candidata D-020 — INCOMPLETA
`system-candidate/system-candidate.kicad_pro`: coreOEM+29 analógicos,76 footprints/
212 pads. Potência/GND integrados; saída de sinal **aberta** até proteção qualificada.
Novos footprints em banco fora do contorno; sem fit/placement/roteamento completos.
MPNs/passivos candidatos, CAD Würth licenciado, R9 candidata4,7k; não fabricar/energizar.
Ver [D-020](../docs/integration-protection-review.md); baselines preservados.

## Captura analógica protegida D-018 — sem PCB
`analog-protected/analog-protected.kicad_pro`: 32 componentes/80 pinos, ERC0 e
13 footprints pendentes. Fonte+VMID passivos integrados **ao estudo analógico**,
não ao core. U2/U3p8 em ANALOG_12V; J103p2 VMID monitor, nunca fonte externa.
`vmid-protected/` é captura lógica auxiliar de revisão, não outra placa física.
D-019 define isolamento/pré-carga ainda sem circuito/MPNs; J102 fica separado.
Ver [mapa e bloqueios](../docs/development-status.md). Nenhuma captura integrada
à PCB e nenhuma autorização de fabricação/energização.

## Candidata OEM refinada — estudo mecânico
`core-oem-refined/ps28-modern.kicad_pro`: 47 footprints/142 pads, contorno inferido
153×79,1 mm e reservas nas quatro camadas sem furos presumidos. J6 é pad de trança
GND; mounts/fit/contacto térmico requerem verificação. Não substitui B por default.
[3Ds atuais](../docs/images/kicad-3d/README.md) mostram somente B/OEM, sem blocos
D-018/D-019 inseridos no layout. Drafts/GUI antigos permanecem preservados.

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
