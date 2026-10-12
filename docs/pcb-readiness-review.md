# Revisão de prontidão da candidata — 2026-10-11

Escopo: auditoria de fabricação da candidata existente, sem modificar EDA,
sem selecionar substitutos e sem liberar fabricação, compra ou energização.
Task: FAB-001/PWR-001/PCB-002. Branch `fix/pcb-readiness-audit`.

## Evidência reproduzível

`make pcb-readiness` executa DRC nativo com `--schematic-parity --refill-zones`
(sem `--save-board`) e verifica contradições no inventário gerado. Retorna
**não zero enquanto bloqueado**, inclusive quando a auditoria falha. Não é um
comando de exportação nem certificação automática. Relatórios completos:
`build/readiness/pcb-readiness.json` e `build/readiness/native-drc.json`.
Resumo persistido: `tests/reports/pcb-readiness-review.json`.

Nesta rodada: 109 warnings (105 silkscreen, 4 trilhas pendentes), **18 itens
não conectados**, zero registros de divergência schematic↔PCB no DRC nativo.
`make check`: 109 testes OK. Paridade não verifica se o MPN corresponde ao
símbolo/footprint: ambos podem carregar o mesmo erro.

## Correção da conclusão anterior

Os seis pares retornados pelo ratsnest aproximado **não** representam a
conectividade completa. O DRC encontra aberturas em AUX_RAW, GVDD_AB, PWM_AC,
PWM_BD, FAULT, VMID, INPUT_A_AC, C_START, AUDIO_EN, MUTE_BASE, INA_UV, DC_OK,
INB_OV e DIVIDED. Logo, não é correto declarar as nets de potência fechadas.
A causa de cada abertura precisa ser inspecionada; falha do autorrouter não
prova, por si, que todas sejam causadas pelo keepout/densidade.

## Bloqueios antes de novo roteamento

- **D301/D302:** inventário atribui MUR3040WTG ao símbolo `Device:D` e footprint
  axial `D_P600_R-6_P12.70mm_Horizontal`. D-025 descreve outro encapsulamento.
  Auditar datasheet onsemi MUR3020WT/D Rev.7, circuito interno, pinagem, tab,
  corrente por junção, montagem e dissipação. Não trocar apenas o nome do
  footprint nem inventar equivalência de pads.
- **C301/C302:** MPN declarado D30×L30 com footprint D25.0 mm. Revisar desenho,
  pinagem/polaridade, courtyard e placement. A pesquisa registrada também
  declara 85 °C/3,49 A frente ao requisito anterior 105 °C/≥3,5 A; não tratar
  como qualificado sem rever o requisito e derating com evidência primária.
- **J301:** texto VHR-4N contra header 1×03. O terminal SVH-41T-P1.1 não é
  o MPN do header; confirmar o conjunto que casa com o chicote OEM.
- **F301:** valor T6.3A sem MPN/corrente/I²t qualificados. Fusível time-lag
  tolera um envelope de partida especificado; **não limita inrush por si**.
  Não dimensionar a partir de uma corrente por meia-bobina sem verificar a
  corrente efetiva no ramo CT onde F301 está instalado.
- **PVDD/D-026:** desabilitar RESET/RAILS_OK não desconecta o PVDD do CI.
  Um supervisor que apenas desabilita áudio não comprova proteção do máximo
  absoluto da alimentação. A própria D-026 registra clamp 82,4 V frente ao
  limite 69 V: segue bloqueio de transientes/OVP, não uma margem validada.
  Não assumir que bulk ideal suprima todos os transientes reais (ESR/ESL).
- **Layout:** revisar PowerPAD, bootstrap/decoupling junto ao TPA, loops do
  buck, LC/PVDD, retornos e térmica contra referência TI antes de pours/rotas.
  Conectividade sozinha não qualifica Classe D. Preservar contorno e fixação OEM.
- **Sistema:** front-end D-022 (50–150 Hz/controles) ainda falta na captura;
  BOM, CPL, estoque, fit-check e gates humanos continuam pendentes.

O verificador aponta também 91 linhas de inventário sem MPN/qualificação
completos pelo critério textual (vazio/TBD/not audited). Isso é triagem,
não lista de compras nem auditoria exaustiva; DNP requer disposição explícita.

## Ordem do próximo incremento físico

1. Auditar fontes primárias e corrigir símbolo/MPN/footprint de potência nos
   geradores, com regressão pin↔net e revisão de OVP/inrush.
2. Integrar D-022; produzir candidata nova em staging sem apagar esta rota.
3. Refazer placement crítico/fit e fanout; rotear potência e sinal nessa ordem.
4. DRC **com paridade e desconexões**, ERC, revisão elétrica/térmica/DFM;
   só então pacote por commit/tag e autorização humana G2/G3.

Esta revisão qualifica o backlog, não conclui PWR-001 nem PCB-002/FAB-001.
