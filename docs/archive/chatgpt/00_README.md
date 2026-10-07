# Infinity Primus PS28 — Modern Amplifier Rev. A

Starter pack de engenharia para substituir o plate amplifier original do Infinity Primus PS28 por uma eletrônica Classe D moderna baseada no **Texas Instruments TPA3255**, preservando o woofer MMD de 8", o gabinete e os dutos originais.

> **Status:** projeto preliminar / Rev. A. Não fabricar nem conectar o woofer antes de concluir ERC, DRC, revisão do datasheet/EVM, validação em carga resistiva e o plano de bring-up.

## Objetivo

- Woofer original: 4 Ω nominal.
- Potência alvo: aproximadamente 120–150 W RMS úteis.
- Amplificador: TPA3255 em PBTL mono.
- Alimentação principal: **36 VDC externa, 5–6 A**, isolada e certificada.
- Alimentação auxiliar: 12 V para TPA3255/front-end via módulo DC/DC.
- Entradas: L/R somadas + LFE dedicado.
- Crossover: Rev. A com **LFE bypass** e caminho LINE com LPF ativo; começar com 80 Hz e tornar selecionável após simulação/validação.
- Fase: 0°/180°.
- Volume: 50 kΩ log.
- Proteções: usar as proteções internas do TPA3255 e manter sinais FAULT/CLIP acessíveis.

## Estratégia do projeto

A Rev. A não replica o circuito Classe AB original. O núcleo de potência deve ser derivado diretamente da documentação oficial da TI para o TPA3255/TPA3255EVM. A fonte de rede não fará parte da primeira PCB: uma fonte externa 36 VDC reduz radicalmente risco, EMI, complexidade e custo de protótipo.

## Estrutura deste pacote

- `01_REQUIREMENTS.md` — requisitos e critérios de aceitação.
- `02_ARCHITECTURE.md` — arquitetura funcional e interfaces.
- `03_SCHEMATIC_REV_A.md` — esquema funcional e componentes propostos.
- `04_BOM_REV_A.md` — BOM preliminar.
- `05_KICAD_ARCH_SETUP.md` — setup no Arch Linux.
- `06_AI_MCP_WORKFLOW.md` — KiCad + IA + MCP.
- `07_PCB_LAYOUT_RULES.md` — regras de layout Classe D.
- `08_SIMULATION_VALIDATION.md` — simulação e validação elétrica.
- `09_MANUFACTURING_JLCPCB.md` — fabricação/PCBA e estratégia de custo.
- `10_BRINGUP_TEST_PLAN.md` — energização e testes.
- `11_SAFETY_RISKS.md` — riscos e limites do projeto.
- `12_REFERENCES.md` — referências oficiais.
- `13_DECISIONS_TBD.md` — decisões fechadas e pendências.
- `skills/` — instruções em Markdown para agentes de IA.

## Regras de ouro

1. **TPA3255 + desacoplamento + filtro LC**: copiar a topologia da TI antes de otimizar.
2. Não usar o antigo transformador 34-0-34 VAC na Rev. A; ele produziria trilhos incompatíveis com a arquitetura proposta sem nova conversão.
3. Nenhum terminal do woofer deve ser ligado ao GND em PBTL/BTL.
4. Não liberar Gerber/PCBA apenas porque ERC/DRC passaram; revisar também térmica, loops de comutação, retorno de corrente, clearance e BOM.
5. Toda alteração em valores da aplicação de referência deve ter justificativa documentada.

## Meta de custo

Para uma única unidade, módulos prontos continuam sendo mais baratos. A PCB customizada vale a pena como projeto de engenharia e integração. Meta inicial: **US$ 50–120** de PCBA/peças para a primeira revisão, excluindo fonte externa, frete e eventuais retrabalhos. O custo real só deve ser estimado após BOM/CPL completos.
