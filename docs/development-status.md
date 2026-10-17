# Estado de desenvolvimento

## SYS-002 e capacitores —2026-10-17

[Requisitos Rev.B / G0](sys002-baseline.md) preparados com potência, duração,
duty, THD, banda, ambiente, térmica e excursão verificáveis.
[48 capacitores revistos](capacitor-derating.md); C40110u50V0805 aproximado
do LP2985 e C40310u25V0603 para capacitância efetiva legado/novo. PCB269
footprints,3.535 segmentos/500 vias; verificação nativa ERC/DRC/paridade/aberturas0.
G0 Rev.B aprovado pelo proprietário em2026-10-17; ripple/estabilidade/térmica reais pertencem
a BENCH-002, excursão a ACOU-001. Nenhuma liberação fabril/energização.


## Complemento final — 2026-10-16

[Revisão final, BOM e blueprints](final-design-review-2026-10-16.md): seis MPNs
incompatíveis corrigidos no esquema/PCB/geradores; cobre e placement preservados.
Nenhum dos 263 componentes do esquema falta na PCB. [Fechamento da BOM](bom-closeout-2026-10-16.md): as 190 pendências de
fabricante/MPN foram resolvidas; 235 posições selecionadas e sincronizadas. Novos renders
Cycles e desenhos de montagem/cobre/DXF/gabarito cotado disponíveis. Desenvolvimento
não concluído para fabricação; revisão global, BOM/CPL e gates continuam pendentes.

## Revisão atual — 2026-10-16

Abrir `kicad/system-candidate/system-candidate.kicad_pro`: única PCB de produto,
com preamp/limiter OEM reaproveitado conforme D-032. 143 testes aprovados;
cartuchos históricos das capturas não definem o estado de liberação.
[Revisão local TPA e conectividade](tpa-local-layout-review.md): 269 footprints,
3.531 segmentos/499 vias. **ERC 0, DRC 0, aberturas 0, paridade 0**. Bootstrap,
VBG e desacoplamentos aproximados; GND local revisto; ramo PVDD esquerdo
restabelecido com 1,2 mm. [Fit térmico nominal e orçamento](../mechanical/thermal-block.md)
revistos: cotas/malha corrigidas, batentes positivos e R junção→perfil 2,25…3,97 °C/W.
Continuam revisão global/G2, validação física/térmica/EMI e BOM/CPL antes de G3. Não liberada para fabricação. Galeria nativa atualizada.

## Histórico — revisão de 2026-10-15

Ver [auditoria de produção](production-readiness-2026-10-15.md): 269 footprints,
ERC 0 e paridade 0 após correção TP127/R506 pelo KCAA; 9 conexões abertas e
1 aviso BST_D. BOM/CPL JLCPCB, placement crítico e documentação de release ainda
não concluídos. D-032 reutiliza preamp/limiter OEM. Não liberada para fabricação.

## Histórico — atualização de 2026-10-10

Os números e pendências abaixo pertencem ao snapshot histórico, não à candidata atual.

Planejamento canônico: `.tasks/items/`; este resumo não muda estados ou gates.
Não é release de hardware, montagem completa ou autorização de fabricação.
Próximos passos até produção: [production-roadmap.md](production-roadmap.md).

### Candidata de sistema naquele snapshot (2026-10-10)

Abrir **`kicad/system-candidate/system-candidate.kicad_pro`**. Contém núcleo OEM +
analógico D-018 + fonte D-021 + sequenciador D-020/D-023 + interface D-019/D-024:
**204 footprints, 580 pinos** casados netlist↔PCB. ERC: os 4 conflitos PBTL OUT_x
e 1 aviso MONO_BIASED da base, nada novo. DRC: 0 violações, 0 erro de footprint,
470 conexões sem roteamento. 118 footprints estão em bancos **fora do contorno**.

| Decisão | Bloco | Documento | Evidência |
|---|---|---|---|
| D-021 | Retificador CT de T1, bulk 2×4700 µF, LM5164 12 V, janela PVDD TPS3700 | [power-d021.md](power-d021.md) | 54 casos ngspice, PVDD máx. 49,84 V |
| D-022 | Crossover ajustável 50–150 Hz | [decisions.md](decisions.md) | não capturado (ELEC-004) |
| D-023 | Sequenciador discreto: hold ≥ 360 ms, partida humana, latch de FAULT, timeout | [seq-d020.md](seq-d020.md) | modelo lógico da netlist, testes de mutação |
| D-024 | Relé G6K-2F Form C após C20/C21, mute TMUX6219, janelas DC/AUX | [iso-d019.md](iso-d019.md) | 1350 casos, pino −0,158…6,47 V |
| D-024a | Série 3,3 kΩ + BAT54 contra falha simples | [iso-d019.md](iso-d019.md) | 216 casos, ≤ −0,351 V no VF máximo |

Footprints auditados contra fabricante nesta rodada: TI DGK0008A (TMUX6219,
SCDS420E p.50) e Omron G6K-2F (K106-E1-11 p.6). Os demais blocos novos usam
footprints candidatos KiCad, a auditar quando os MPNs de potência forem fechados.

Galeria 3D com a vista `system-*` (núcleo + bancos), regenerada nesta data:
[images/kicad-3d](images/kicad-3d/README.md). Os bancos aparecem soltos ao lado da
placa porque **não há placement**; não é prova de encaixe.

Riscos abertos: entrada do TPA desligado não publicada pela TI; driver do preamp
preso em nível alto com relé fechado; regulação/inrush de T1 só simulados; térmica
do dissipador OEM sem medida. Detalhes em `iso-d019.md` e `power-d021.md`.

## Histórico — snapshot de 2026-10-08 (D-018/D-019)

As seções abaixo descrevem o estado antes de D-021…D-024a e são mantidas para
rastreabilidade; números e "não implementado" se referem àquela data.

## Incremento posterior D-020 — candidata incompleta

[Core + analógico e pesquisa de proteção](integration-protection-review.md):
`kicad/system-candidate/system-candidate.kicad_pro` contém76 componentes/212 pads,
sem footprints vazios nessa candidata. Analógico em banco **fora do contorno**,
ponte de sinal aberta e proteção/mute/supervisor físicos NÃO implementados.
CAD Würth licenciado incorporado; R9 candidata4,7k após contraprova de fuga.
B/OEM/capturas anteriores e seus números abaixo permanecem históricos intactos.
Não confundir importação de footprints com placement ou schematic completo.

## O que existe e onde abrir

- **Core B**, `kicad/core-selected/ps28-modern.kicad_pro`: captura/placement
  de potência, 47 componentes/footprints e 142 pads. Referência D-011, Fig.31
  TI, dois ramos LC; padrão de `make core-check`/ERC/DRC. Sem roteamento.
- **Core OEM refinado**, `kicad/core-oem-refined/ps28-modern.kicad_pro`:
  candidata mecânica separada com 47 footprints/142 pads e contorno inferido
  153×79,1 mm. Seis features ambíguas reservadas em quatro camadas (24 áreas),
  sem furos inventados; J6 é pad de trança GND. Fit/contacto térmico não medidos.
- **Front-end protegido D-018**, `kicad/analog-protected/analog-protected.kicad_pro`:
  schematic de estudo com 32 componentes/80 pinos, 14 passivos LR4 e 10 passivos
  de alimentação/polaridade D201 auditados, ERC0 sem exclusões. Integra LR4 e
  alimentação/VMID **nesse schematic**, não ao core; **não tem PCB**.
- **VMID protegido auxiliar**, `kicad/vmid-protected/`: captura lógica para
  revisão, não outra placa física ou novos conectores de produção.
- D-016, drafts A/B/C e estudos rejeitados D-017 continuam preservados para
  rastreabilidade; não usar um buffer GUI antigo para sobrescrever revisões.

## Mudanças elétricas já documentadas

**D-018:** retirar o VMID ativo com referência retida; divisor passivo
150 Ω/150 Ω com 1 µF. Todos os quatro amps candidatos OPA1656 usam
**ANALOG_12V**, isolado de **AUX_RAW** por diodo/15 Ω/2×470 µF e bleeds.
TPA mantém sua alimentação auxiliar própria; não alimentar TPA com o rail
protegido que pode operar abaixo de 10,8 V. J103.2 e J102.3 são referência/
monitor VMID, não fontes externas nem retorno do par diferencial.

A causa D-017 foi corrigida **sob o envelope explícito D-018**, com 30 quedas,
três cenários de partida/brownout/desconexão e nove casos TI LR4. Não equivale
a qualificação de ESR, aging, Vf/fuga, pulso, térmica ou funcionamento real.
Detalhes/fontes: [D-018](vmid-protection.md).

**D-019:** documentar contraprovas de entrada TPA e contrato não implementado
de isolamento **depois** de C20/C21, controle da placa isolada, mute analógico
real e pré-carga observada antes do áudio. 288 hipóteses RC, quatro comparações
ngspice e duas redes com a alimentação passiva D-018 intacta. No equivalente
com bias TPA já zero, a entrada chega a −2,09 V com rail analógico ainda ≥4,5 V.
Bias/impedância desligados e driver são hipóteses, **não medições ou garantias**.
Não ligar J102 ao núcleo energizável. [D-019](input-power-order-study.md).

## O que os 3Ds atuais mostram — e o que não mostram

[Seis PNGs e dois GIFs de 16 câmeras KiCad](images/kicad-3d/README.md), regenerados
com `kicad-cli pcb render`. As faixas agora explicitam **“núcleo apenas;
D-018/D-019 sem PCB integrada”**. O manifesto inclui hashes das PCBs, capturas,
configs dos estudos, gerador e mídia; o commit-fonte é o snapshot anterior à
publicação dos assets. Pillow só acrescenta faixas e codifica GIFs.

A geometria das PCBs **não mudou** com D-018/D-019. Por isso não há 32 componentes
analógicos, chave protetora, supervisor, roteamento ou adaptador térmico novo
nesses renders. Não inserir placeholders visuais para aparentar integração.
Os 40 footprints visualizados usam modelos genéricos KiCad, não CAD qualificado
de fabricantes. Faltam modelos de **C1/J1/J5/J6/L1/L2/U1**; o corpo U1 ausente
não confirma altura/folga do dissipador. Reservas inferidas não são furação aprovada.

## Próximos trabalhos — por risco/dependência

1. Qualificar parts/envelope D-018 e selecionar proteção/mute/supervisor que
   atendam o contrato D-019, incluindo power-off de ambos os terminais, defaults,
   pré-carga, injeção/fuga/feedthrough e eventos de fase/volume. Proteger também
   RCA ativa com opamp desligado; ausência de evidência segue TBD.
2. Concluir L/R, LINE/LFE, volume/fase, high-pass/limiter e proteção DC diferencial;
   integrar e auditar schematic completo antes de integrar ao layout.
3. Resolver os **13 footprints** analógicos pendentes: C101–C106, J101–J103,
   R201–R203 e C203. MPN/land pattern devem ser auditados; sem compra automática.
4. Obter envelope medido de T1/fonte e cotas locais OEM/contacto térmico;
   dimensionar conversão/inrush/fusíveis/transientes/térmica pela evidência.
5. Revisão independente do core, roteamento crítico e stackup/planos; fit e
   DRC/paridade finais. B/OEM continuam com **quatro ERC não excluídos e 109
   conexões não roteadas**; zero geometria/paridade não significa board completa.

ELEC-002 e MECH-001 continuam Blocked; ELEC-003/PWR-001 seguem To Do.
PCB-003/SETUP-003 são os dois itens In Progress; review do proprietário ainda
pendente. S03 permanece planejada, não ativa. **G0–G5 pendentes**.

## Verificações e reprodução

```bash
make check
make simulate                  # estudos, inclusive contraprovas obrigatórias D-019
make analog-protected-check    # capture/80 pinos/ERC nativos do estudo D-018
make analog-check              # regressão da captura histórica D-016
make render-3d                  # KiCad/Pillow/modelos/fontes locais; não instala nada
python3 scripts/check_core.py --design-dir kicad/core-oem-refined
```

Regeneração prepara/verifica todos os assets antes de promovê-los; manifesto é
publicado por último e README/manual notes são preservados. Logs/frames brutos
ficam em `build/`; evidências versionadas em `tests/reports/` e no manifesto da
galeria. `tests/reports/documentation-media-refresh.json` registra checks nativos,
hashes e snapshot das tasks: **60 testes locais passaram**, incluindo proteção
contra publicação de render incompleto/hash inválido e preservação do README.
B/OEM ERC4 e DRC109 não roteadas foram rechecados, sem novos problemas de
geometria/paridade; não são resultados de hardware aprovado.
Dados simulados não substituem revisão humana, medições ou gates.
SPK± ativos: nunca GND/garra de scope; nenhuma energização ou compra autorizada.
