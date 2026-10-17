# SYS-002 — baseline e revisão G0

Data:2026-10-17. Baseline: D-010/D-021/D-030/D-032 + requisitos Rev.B.
Documentos de aceitação: [requirements.md](requirements.md),
[matriz](../tests/acceptance.md), [plano](../tests/bench-plan.md) e
[derating](capacitor-derating.md). Fontes e cálculos identificam o que é medido,
extraído do fabricante ou premissa conservadora.

## Baseline aprovada

- Uma PCB TPA3255 PBTL, T1 CT de dois diodos, controles/limiter OEM, montagem OEM.
- 100 W contínuos é meta de qualificação **da eletrônica em carga artificial**;
  120–150 W apenas burst3/20 a50 Hz. Nenhuma promessa de150 W contínuos no woofer.
- Operação10–40 °C; ensaio inicial25 ±5 °C, depois40 ±2 °C, limites térmicos
  explícitos. Perfil OEM e T1 ainda não foram medidos sob essa carga.
- Excursão≤80% do Xlin medido e≤100 W médios. Enquanto Xlin for desconhecido,
  não energizar woofer: finalizar elétrica com carga artificial e medir em ACOU-001.
- C401 e C403 selecionados por capacitância efetiva; a validação de estabilidade,
  ripple, temperatura e excursão é execução BENCH-002/ACOU-001, não evidência inventada.

## Registro G0

Estado: **G0 da Rev.B aprovado explicitamente pelo proprietário em2026-10-17**.
Registro da resposta: “Aprovo o G0 da Rev.B”.
Não reutilizar D-030 como aprovação de limites que foram definidos depois.
Responsável: proprietário do projeto (bitter). Data:2026-10-17.
Commit da baseline aprovada: [`6cf2260da231`](https://github.com/bernardopg/ps28-modern-amp/commit/6cf2260da231e5125bdf267e938a8d7b2d3235dc).
[Registro G0 com hashes dos arquivos aprovados](../tests/reports/g0-revb-approval-2026-10-17.json). Aprovar G0 não autoriza compra, fabricação, energização nem substitui G1–G5.

Regra aplicável: SYS-002 exige “Baseline e G0 aprovados pelo proprietário”; docs/safety.md
exige “IA recomenda, humano aprova”. O aceite explícito foi recebido; ensaios físicos e demais gates permanecem
independentes.
