# Layout e mecânica

Prioridade: loops de comutação, desacoplamento, PowerPAD/térmica, LC, retorno e analógico.

## Placement visível versus integração pendente

B/OEM refinada: 47 footprints/142 pads, zero geometria/paridade no último DRC,
quatro ERC não excluídos e **109 conexões não roteadas**. OEM usa contorno inferido
153×79,1 mm e 24 reservas nas quatro camadas para seis features não identificadas;
não transformar essas reservas em furação. B permanece padrão de validação.
[Galeria nativa regenerada](images/kicad-3d/README.md) mostra **só o núcleo**:
D-018/D-019 não têm PCB integrada. Não existem novos placements de preamp/
isoladores/supervisor nesses renders; nenhum footprint/modelo fictício adicionado.
Sete modelos ausentes continuam explícitos, inclusive U1; 3D não comprova fit.
[Estado/bloqueios](development-status.md). Layout físico não foi alterado.

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
- Não delegar loops críticos a Freerouting; autorouter só auxilia sinais não críticos.
- Confirmar placa/painel/furos/chicotes, isolamento de ferragens, airflow e vedação acústica.

Netclasses planejadas: ANALOG, LOGIC, PVDD, SWITCH_NODE e SPEAKER.
Valores finais TBD; não relaxar DRC para fazer passar. Coordenadas mm, +Y down.
Freeze exige comparação visual com baseline, DRC/paridade, térmica e fit-check 1:1/3D.
