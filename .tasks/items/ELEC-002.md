---
id: ELEC-002
title: Simular front-end físico e tolerâncias
status: Blocked
milestone: M2
sprint: S03
depends_on: ELEC-001, PWR-001
updated: 2026-10-08
---

# ELEC-002 — Simular front-end físico e tolerâncias

## Objetivo

Simular front-end físico e tolerâncias, atendendo docs/requirements.md e gates docs/safety.md.

## Critérios de aceite

- [ ] Modelo do op-amp selecionado/VMID real com licença e compatibilidade (D-016: OPA1656 candidato)
- [ ] LR4/ganho/headroom/impedância/startup/fase e tolerâncias verificados

## Evidência

Preparação de estudo realizada, sem fechar os critérios acima:
- Circuito SPICE com R/C explícitos: duas SK unitárias14k/200nF feedback/100nF referência,
  divisor10k/10k e inversor diferencial10k/10k; fn80,385Hz/Q0,7071.
-151 pontos de magnitude/fase conferidos contra equação independente;16.384
  combinações extremas e2048 amostras com seed20261008.
- Transiente com2Vrms/10,8V avaliado SOMENTE em modelo comportamental próprio.
- Datasheets TI SLOA024B/SLOS075K arquivados localmente com hashes; CM/swing
  de NE5532 a±15V não extrapolados para10,8–13,2V totais.
Ver `docs/analog-lr4-study.md` e `tests/reports/analog-lr4-study.json`.
Bloqueada pelas dependências ELEC-001/PWR-001 e por modelo/validação real de
NE5532/VMID, MPNs, impedâncias, ruído, bias/offset, startup e integração completos.
Nenhuma captura na PCB, Done ou gate de hardware aprovado.

Incremento D-016: OPA1656ID candidato, modelo oficial TI SBOMAW6C/Final1.3
inteiro auditado e pin order conferido;9 casos10,8/12/13,2V ×0/27/70°C passaram.
Modelo permanece local, sem redistribuição; ngspice PSA configurado isoladamente.
Warnings/fallbacks de convergência estão no relatório. VMID continua ideal, logo
critério completo acima NÃO fechado. Captura independente21 componentes/58pinos,
ERC0 e14R/C comparados com SPICE;9 footprints pendentes.
Ver `docs/analog-capture.md` e `tests/reports/opa1656-model-study.json`.

D-017: VMID físico avaliado no modelo TI (divisor, CREF, buffer, isolamento/ESR).
32 casos de return ratio, PM mínimo60,67°; carga±1mA/ripple e carga inicial de
referência com AUX já válido conferidos contra equações independentes. Contraprova
sem isolamento: PM−2,96°. LR4 acoplado ao VMID físico≈1,99237Vrms/20Hz.
**Bloqueio adicional de segurança:** power-down passivo sem clamp deixa REF acima
V++0,5V; descarga, corrente/backfeed e os outros pinos analógicos devem ser
qualificados antes de captura. Não usar RESET como proteção desses pinos.
Ver `docs/vmid-buffer-study.md` e `tests/reports/vmid-buffer-study.json`.
Sem captura/PCB/MPNs/fabricação/energização; estudo não conclui o critério VMID.

D-018 corrige a causa D-017 sob envelope: rail analógico isolado/reserva,
VMID passivo150/150Ω,1µF, sem buffer/REF22µF. Prova RC com ESR e cargas;
30 quedas+3 casos de partida/brownout/fonte desconectada;9 casos LR4/TI.
Captura integrada32 componentes/80 pinos/ERC0; preserve contraprova sem isolamento.
`docs/vmid-protection.md` e `tests/reports/vmid-protection-study.json`.
Ainda Blocked: confirmar ESR/aging/temperatura/Vf/pulso/MPNs/correntes, proteger
sinais externos/TPA power-order, supervisor/fonte; nenhuma qualificação de hardware.

D-019: 288 hipóteses RC (196 violações neste equivalente), quatro comparações
ngspice, duas redes acopladas D-018 e regressões de desligamento/conexão fria;
capacitor/resistor série
não demonstram proteção. Mute/pré-carga observada e isolamento pós-C20/C21
permanecem contrato condicional sem parts/circuito. Bias/impedância desligados
TPA não caracterizados; nenhuma captura promovida. Ver
`docs/input-power-order-study.md` e `tests/reports/input-power-order-study.json`.

Docs/3Ds/tasks atualizados após D-019: os renders continuam somente core,
sem integração de 32 componentes/13 footprints analógicos pendentes ou chaves/
supervisor. `docs/development-status.md` centraliza distinções e próximos bloqueios;
nenhum limite/modelo/caso foi relaxado, status Blocked/dependências preservados.

D-020: três subagentes pesquisaram CAD/parts/proteção/controle e reviewer
independente encontrou bugs corrigidos nas regressões de sequência/identidade EDA.
R9 legado10k pode exceder VIL0,8V com fuga100µA; candidata4,7k separada.
HoldRESET≥250ms TI, contrato executável360ms mínimo; latência física100µs não
provada. Nenhuma chave demonstrou todos budgetsD019; ADG461x não é±16V.
`docs/integration-protection-review.md`; proteção/mute/supervisor físicos pendentes.
Status Blocked preservado, nenhuma energização/relaxamento de critérios.

## Risco / aprovação

Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
