# Caminho até produção (JLCPCB)

## Complemento de fechamento — 2026-10-16

[Revisão final](final-design-review-2026-10-16.md): conectividade confirmada,
seis MPNs corrigidos, desenhos de montagem/cobre e gabarito cotado adicionados,
Gerbonara instalado e arquivos fab conferidos com parser independente. As [190 pendências de fabricante/MPN foram resolvidas](bom-closeout-2026-10-16.md).
Faltam qualificar fornecimento/DFM da seleção, revisar CPL e montagem dos acessórios, fechar
revisão global de potência/EMI e gates G1/G2/G3. Render melhorado não fecha esses itens.

## Atualização — 2026-10-16

[Placement local TPA e conectividade concluídos](tpa-local-layout-review.md):
ERC 0, DRC 0, aberturas 0 e paridade 0. Próximo: revisão global de potência,
EMI e fit/G2 → qualificar BOM/CPL JLCPCB → conferir pacote e obter G3.
O [fit térmico nominal/orçamento](../mechanical/thermal-block.md) já foi revisto;
conferências locais e validação térmica medida permanecem em BENCH-002.
As novas faces/rotações dos capacitores devem entrar no CPL. Ainda não liberada.
A [auditoria inicial de 2026-10-15](production-readiness-2026-10-15.md) permanece
como histórico; suas nove aberturas e aviso BST_D foram resolvidos.
D-032 mantém o preamp/limiter OEM.

## Histórico — 2026-10-10

A tabela abaixo registra aquele snapshot; não usar suas contagens como estado atual.

Lista ordenada do que falta entre a candidata atual e um pedido de fabricação.
**Nenhum item autoriza compra, fabricação ou energização**; cada gate é humano.
Estado detalhado em [development-status.md](development-status.md).

## Onde estamos

| Bloco | Situação |
|---|---|
| Núcleo TPA3255 PBTL | Captura e placement B/OEM; 109 conexões sem rota |
| Fonte D-021 (retificador, bulk, LM5164, janela PVDD) | Capturada e simulada; MPNs de potência TBD |
| Sequenciador D-020/D-023 | Capturado, modelo lógico com mutações |
| Interface D-019/D-024/D-024a (relé, mute, janelas, clamp) | Capturada, 1566 casos ngspice |
| Front-end de áudio D-022 (RCA, crossover, LEVEL, fase) | **Não capturado** (ELEC-004) |
| Placement no contorno OEM | **Estudo**: 204 peças no contorno medido 154 × 81, DRC só silkscreen; revisão de layout pendente |
| Roteamento | **Autoroteamento de estudo**: 463/470, sem revisão de loops/pours/EMI |
| BOM/CPL JLCPCB com LCSC | **Não feito** |

## Sequência proposta

| # | Task | Entrega | Bloqueia | Precisa do proprietário |
|---|---|---|---|---|
| 1 | MECH-001 ✓ geometria | Dissipador/perfil U medidos (2026-10-10); faltam distância perfil→PCB, contorno 154 × 81, furos e perfil medidos; falta gabarito 1:1 | 6, 7 | Foto do perfil montado e 3 cotas |
| 2 | ELEC-004 | Front-end D-022 capturado e simulado com tolerâncias | 4, 6 | Fotos/cotas dos pots e chaves do painel |
| 3 | PWR-001 | MPNs de diodos, bulk, TVS, fusível, conector JST VH; decisão de inrush | 4, 8 | — |
| 4 | ELEC-003 | Schematic único completo, ERC sem erros novos, revisão G1 | 6 | **Gate G1** |
| 5 | SYS-001/SYS-002 | Limites de aceitação e do woofer (100 W provisório) | 9 | — |
| 6 | PCB-001 | Stackup 2 ou 4 camadas, placement no contorno OEM, térmica do TPA | 7 | — |
| 7 | PCB-002 | Roteamento (PowerPAD, loops LC, GND estrela, sinal longe do PWM), DRC 0 | 8 | **Gate G2** |
| 8 | FAB-001 | BOM com LCSC/estoque, CPL, Gerbers em `build/`, revisão DFM | 9 | **Gate G3**, orçamento |
| 9 | BENCH-001/002 | Limites de bancada, bring-up com carga resistiva e fonte limitada | 10 | **Gate G4**, bancada |
| 10 | ACOU-001 | Integração ao gabinete e medição | — | **Gate G5** |

Os passos 1, 2 e 3 são independentes e podem andar em paralelo; 6 só começa com
1 e 4 fechados. WIP máximo 2 continua valendo.

## Riscos que seguem abertos até a bancada

- Entrada do TPA desligado/em RESET não publicada pela TI (só modelo RIN).
- Driver do preamp preso em nível alto com relé fechado: pino até 12,5 V até a
  janela OV abrir o relé (~50 ms); corrente limitada por 3,3 kΩ.
- Regulação de T1 sob carga, inrush e indutância de dispersão: só simulados.
- Capacidade térmica do dissipador OEM para o TPA3255 sem medida.

## O que o JLCPCB vai exigir no fim

Gerbers + drill do commit/tag liberado, BOM com código LCSC por linha, CPL com
rotações conferidas, peças THT (relé SMD é ok; bornes, snap-in, fusível, JST VH)
marcadas para montagem manual ou serviço THT, e confirmação de estoque na data.
Gerar só em `build/` e liberar via `manufacturing/` após G3 (ver `manufacturing.md`).
