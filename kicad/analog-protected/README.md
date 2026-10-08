# Front-end com VMID/rail protegido — candidata D-018
Abrir `analog-protected.kicad_pro`. Captura integrada:32 componentes/80 pinos,
ERC0 nativo,14 R/C LR4 +10 passivos/polaridade de diodo conferidos independentemente.
[Projeto, prova, hipóteses e bloqueios](../../docs/vmid-protection.md).

J103:1=AUX_RAW regulado10,8–13,2V,2=VMID para monitoramento (não fonte),3=GND.
Os quatro opamps são alimentados por ANALOG_12V, NÃO por AUX_RAW; mínima modelada
≈8,03V. J101 não é RCA direto e J102 não é saída de alto-falante.

13 footprints e vários MPNs pendentes; ESR/temperatura/pulso/correntes precisam
qualificação. Proteção de todos os sinais externos e power-order do TPA ainda
bloqueados. Não fabricar/energizar; layout na mesma PCB/mounts OEM ainda pendente.
Captura anterior `../analog-front-end/` e PCBs preservadas.

Gerador `scripts/create_vmid_protection.py --integrated` é atômico e recusa
sobrescrita. Fonte canônica do bloco: `simulation/analog/vmid-protected.cir`.
`make analog-protected-check` invalida evidências anteriores antes da validação.
PDF/SVG nativos: `docs/images/analog-protected/`.
