# Layout e mecânica

Prioridade: loops de comutação, desacoplamento, PowerPAD/térmica, LC, retorno e analógico.

## Placa única — placement e cobre (D-031/D-033, 2026-10-12)

Placa: `kicad/system-candidate/` (contorno OEM medido 154×81 mm, 4 camadas).
Geradores: `scripts/place_system_candidate.py` (zonas fixas abaixo) e
`scripts/route_system_candidate.py` (planos, fanout e trilhas).

| Zona | Peças | Motivo |
|---|---|---|
| Centro, junto da perna do perfil | U1 TPA3255, bloco térmico (x 64–117, y 54–67) | PowerPAD encosta no bloco; só SMD baixo sob o bloco |
| Logo acima da fileira de saídas do U1 | L1/L2 HCF2013, filmes C22/C23/C26/C27 | Laço PWM→LC de ~10 mm (antes ~40 mm) |
| Borda livre, centro | J7 (chicote de 7 vias do preamp) | Posição do P101 original |
| Extremo esquerdo do U1 | C14/C15 680 µF, C1, K501, ±15 V (Q601/Q602) | Bulk local PVDD/GVDD, relé de entrada perto de INPUT_A/B |
| Esquerda | J5 woofer, trilho analógico C201/C202, OPA1656 (fundo) | Lado do relé OEM; analógico longe do retificador |
| Direita | J301 T1, F301, D301/D302, C301/C302, L301 + LM5164 (fundo) | Lado do transformador; laço do buck sob L301 |

Cobre:
- In1.Cu: plano GND contínuo. In2.Cu: plano PVDD na faixa do U1 + região do
  retificador/bulk; resto livre para sinais. F.Cu/B.Cu: preenchimento GND.
- U1: fileiras de PVDD/GND unidas com tira de 0,3 mm e duas vias por fileira até os
  planos; cada pad SMD de GND tem via própria para In1.
- Larguras: SPK±/T1 1,5 mm; PVDD/BUCK_SW/AUX 0,6 mm; PWM_AC/BD 0,4 mm (pad do U1);
  sinais 0,2 mm. Trilhas restantes traçadas pelo Freerouting dentro dessas restrições
  (planos e fanout já fixos); revisar no KiCad antes do pedido.

## Regras de revisão

4 camadas são hipótese de integração; EVM 2 camadas não equivale ao stackup fabricável.
Confirmar cobre/dielétrico/vias com fábrica antes de finalizar regras.

- Placement: entrada DC → bulk/local decoupling → CI → LC → conector SPK.
- Capacitores PVDD próximos aos pinos, vias curtas; bulk não substitui cerâmicos.
- Reduzir área de switch nodes; não rotear analógico sob eles/indutores.
- Plano GND contínuo com caminhos de retorno controlados; não cortar sob sinais HF.
- TPA3255DDV tem PowerPAD SUPERIOR (SLASEA8A p.3–4/DDV0044D): footprint TopEP,
  44 leads, sem pad inferior 45. Dissipador aterrado, contato térmico e fixação independentes.
  Não aplicar receita bottom-EP com pasta/vias centrais. Verificar altura/relief do
  dissipador sobre capacitores; a reserva Dwgs.User do draft não é keepout aprovado.
- Cobre e vias calculados para corrente, perdas e ΔT; 0,25 mm não é regra de potência.
- Loops críticos (PVDD/GND do TPA, LC) definidos por placement/planos/fanout fixos;
  o Freerouting só liga o que resta, com largura por classe.
- Confirmar placa/painel/furos/chicotes, isolamento de ferragens, airflow e vedação acústica.

Netclasses planejadas: ANALOG, LOGIC, PVDD, SWITCH_NODE e SPEAKER.
Valores finais TBD; não relaxar DRC para fazer passar. Coordenadas mm, +Y down.
Freeze exige comparação visual com baseline, DRC/paridade, térmica e fit-check 1:1/3D.
