# Captura analógica isolada — estudo, sem PCB

21 componentes/58 pinos físicos; U2/U3 OPA1656ID candidatos, quatro unidades.
ERC nativo0 e14 R/C conferidos contra SPICE; nove casos do modelo oficial TI.
Símbolo local PS28_ANALOG com pinos auditados contra SBOS901C fig.5-3,p.3.

J101 recebe sinal MONO AC já biasado aVMID, NÃO RCA direto.
J102 entrega diferencial analógico, NÃO SPK±.
J103 requer AUX12V/VMID/GND externos; flags indicam interfaces, não fontes reais.

Ainda sem VMID/supervisor/proteção/LINE-LFE/volume/fase completos, sem hierarquia
integrada ou PCB.9 footprints e MPNs passivos/interfaces TBD; nenhum gate aprovado.
Não criar placa extra ou novos mounts OEM por causa deste diretório de estudo.

Ver `docs/analog-capture.md`. `make analog-check` gera ERC/netlist novos;
`make simulate-opa` exige modelo TI local auditado. Gerador recusa sobrescrever.
