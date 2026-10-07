# Layout e mecânica
Prioridade: loops de comutação, desacoplamento, PowerPAD/térmica, LC, retorno e analógico.
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
- Não delegar loops críticos a Freerouting; autorouter só auxilia sinais não críticos.
- Confirmar placa/painel/furos/chicotes, isolamento de ferragens, airflow e vedação acústica.

Netclasses planejadas: ANALOG, LOGIC, PVDD, SWITCH_NODE e SPEAKER.
Valores finais TBD; não relaxar DRC para fazer passar. Coordenadas mm, +Y down.
Freeze exige comparação visual com baseline, DRC/paridade, térmica e fit-check 1:1/3D.
