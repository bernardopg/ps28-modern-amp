# Estado de desenvolvimento — atualização de 2026-10-08

Snapshot técnico após D-018/D-019, com galeria nativa regenerada.
Planejamento canônico: `.tasks/items/`; este resumo não muda estados ou gates.
Não é release de hardware, montagem completa ou autorização de fabricação.

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
