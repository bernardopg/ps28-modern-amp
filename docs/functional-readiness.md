# Operacionalidade — revisão do núcleo e bloqueios do produto

## Estado verificável
A candidata separada `kicad/core-oem-refined/` preserva B e C, sem modificar buffers
antigos. É estudo de integração OEM, **não produto operacional nem PCB fabricável**.
`core-selected` permanece o padrão dos comandos existentes; conferir a candidata com
`python3 scripts/check_core.py --design-dir kicad/core-oem-refined`.

Nesta revisão:47 componentes/47 footprints/142 pads conferidos pelo checker; DRC
nativo com paridade:0 violações geométricas,0 divergências e109 conexões não roteadas.
ERC nativo:4 conflitos `pin_to_pin`, ainda sem exclusões. G0–G5 continuam pendentes.
O checker é revisão automatizada, não substitui revisão elétrica independente.

## Achados que afetam funcionamento
- **Bloqueador — fonte:** J1/PVDD e J2/AUX_12V são interfaces, não conversores.
  T1 original não pode ser ligado diretamente ao core, muito menos seus rails
  simétricos. Faltam qualificação VAC/VA/ripple e captura da retificação, fusível,
  inrush, conversão36V/12V, transientes e descarga. D-010 permanece; o regulador
  deve ser escolhido pelo envelope medido, não por34-0-34VAC presumidos.
- **Bloqueador — controle:** J4 requer3V3 externa e supervisor de RESET/FAULT.
  R9 garante RESET baixo sem controle; não basta aplicar PVDD para obter áudio.
  Faltam captura e validação de partida/desligamento/brownout, remoção de RESET
  antes de rails fora de faixa e resposta a FAULT. Não derivar controle de AVDD/DVDD.
  [Contrato preparatório](reset-supervisor-contract.md): não usar AND combinacional
  FAULT/RESET; startup produz FAULT baixo e RESET baixo força FAULT alto (TI).
- **Bloqueador — entrada:** J3 espera sinal diferencial adequado ao TPA3255.
  Soma L/R, LINE/LFE, volume, fase, VMID, diferencial e LR4 físico não existem
  nesta candidata. O modelo LR4 ideal não valida op-amps, estabilidade ou headroom.
  [Incremento LR4 com R/C explícitos](analog-lr4-study.md) está simulado como estudo,
  mas VMID/integração continuam não qualificados. D-016 acrescenta
  [captura isolada e modelo oficial OPA1656](analog-capture.md):21 partes/58 pinos,
  ERC0, nove casos de modelo. Não é o somador/LINE/LFE/volume completo nem PCB.
  [VMID físico D-017](vmid-buffer-study.md):32 casos/PM mínimo60,67°, carga±1mA
  e LR4 acoplado; candidata bloqueada por REF armazenada no desligamento sem
  clamp/descarga/backfeed qualificados. RESET não protege esses pinos analógicos.
- **Bloqueador — woofer:** ainda não há limitador, high-pass qualificado nem
  proteção DC diferencial. Proteções internas do CI não garantem proteção de
  cone/bobina. Projetar detecção após LC entre SPK+ e SPK−, rejeitando PWM sem
  mascarar DC; não comparar apenas uma saída ativa com GND. Estados de falha,
  limiares/tempos e meio de desligamento exigem análise antes da seleção de peças.
- **Bloqueador — caminho térmico:** PowerPAD superior do DDV precisa do contato
  mecânico proposto e dissipadores/suportes OEM. Temperatura calculada com°C/W
  assumido não é evidência de capacidade. Não apoiar pressão de fixação nos leads.
- **Bloqueador — PCB:** não há cobre roteado. DRC limpo de geometria não verifica
  loops de comutação, retorno, largura de cobre, EMI ou integridade de potência.

## Correção técnica do LC
Foi corrigido erro dimensional em `selected-core.md`:10µH e940nF por lado dão
**fn=51,9106kHz**, não1642Hz. Referência de topologia:TI SLASEA8A Rev.A,
§10.2.4/figura31,p.28; A+C/B+D antes das duas pernas LC, não quatro filtros EVM.
Para excitação balanceada: Ldiff=20µH, Cdiff=470nF e Q=0,613 para4Ω sem DCR.
`simulation/output-lc-ideal.cir` usa DCRmáx20°C=8,76mΩ por bobina, da documentação
Würth7443631000 arquivada em `reference/parts/`.201 pontos ngspice10Hz–1MHz
conferidos contra equação independente; sem comutação, perdas HF ou woofer real.
Essa correção não altera componentes nem demonstra estabilidade física.

## Budget de potência — cálculo, não rating do conjunto
Para REQ-002/carga **resistiva**4Ω:
-120W:21,91Vrms,30,98Vp,5,48Arms;
-150W:24,49Vrms,34,64Vp,6,12Arms.
Em36V,150W deixa apenas1,36V entre pico ideal e rail: perdas, ripple e headroom
reduzem essa margem. Portanto120–150W segue alvo, não promessa. Só a perda DC das
duas bobinas em20°C seria0,526W/0,657W respectivamente; não inclui aquecimento,
núcleo, ripple PWM ou perdas do CI. DCR do woofer não é impedância nominal/frequencial.

## Sequência de fechamento técnico
1. Revisar pin-a-pin o core e resolver/classificar os quatro ERC individualmente,
   sem enfraquecer regras globais. Confirmar PBTL, rails e controle contra TI.
2. Qualificar secundário de T1 e contato térmico OEM; obter só cotas locais
   irreconstituíveis. Capturar fonte/supervisor com tolerâncias e falhas explicitadas.
3. Capturar front-end e proteção; simular modelos não ideais, extremos de carga,
   tolerância e partida. Associar ensaios a REQ-001–009 e tasks existentes.
4. Integrar placement e então rotear loops PVDD/GND/PWM/LC prioritários. Conferir
   todos os planos/retornos e reservas. Rodar ERC/DRC/paridade novamente.
5. Só com gates humanos: placa montada, inspeção, carga artificial e limites
   numéricos aprovados antes de energia; woofer somente após proteção/offset/clip
   verificados. SPK± sempre ativos/flutuantes; nenhuma garra terra neles.

## Evidência
Relatório versionado: `tests/reports/core-oem-refined-review.json`.
Logs nativos/exportações/modelos: `build/mechanical-reference/` e `build/`.
Sem compra, pedido fabril, alteração de rede primária ou energização nesta revisão.
