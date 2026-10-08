# Roadmap

## Incremento atual autorizado

[PCB-003](items/PCB-003.md): captura e placement exploratório do core PBTL,
conforme pedido de início da PCB. Não fecha M1/G0 nem libera fabricação;
fonte D-010, magnetics, térmica e dimensões continuam dependentes de evidências.

## Snapshot D-018/D-019 — 2026-10-08

[Mapa de capturas, PCBs e bloqueios](../docs/development-status.md): core B/OEM
preservado; analógico protegido32/80/ERC0 ainda sem PCB; isolamento/pré-carga
D-019 ainda sem implementação. Galeria 3D nativa regenerada mostra só o núcleo,
não integração elétrica nova. Próximo risco: proteção de sinais/power-order,
qualificação de parts/fonte e evidência mecânica antes de roteamento/freeze.
Tasks locais seguem canônicas, WIP2 e todos os gates pendentes; S03 não ativada.

## Now — M0: fundação reproduzível

S01: documentação, skills, ferramentas, GitHub e comandos verificáveis.
Setup não equivale a hardware liberado; fechar M0 após review do proprietário.

## Next — M1: requisitos e viabilidade (G0)

S02: SYS-001/002, MECH-001, PWR-001, ELEC-001, BUY-001 e BENCH-001.
Confirmar woofer/plate/fonte; escolher baseline PBTL e definir aceitação/instrumentos.

## Next — M2: schematic validado (G1)

S03: ELEC-002/003. Front-end real simulado, captura/MPNs e ERC/revisão cruzada.

## Later — M3: layout e produção aprovada (G2/G3)

S04: PCB-001/002, FAB-001. Stackup, loops/térmica/fit, DRC/paridade, BOM/CPL e cotações.

## Later — M4: protótipo e integração (G4/G5)

S05: BENCH-002, ACOU-001. Resistiva primeiro, woofer depois; logs térmicos/acústicos.

## Fora do compromisso

DSP/auto-standby/PFFB/controle remoto só após Rev. A validada e decisão de escopo.
Rev. A é revisão física planejada, não tag de release de setup. Nenhuma data fabril prometida.
