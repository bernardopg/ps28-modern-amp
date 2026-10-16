# Arquitetura da candidata integrada

Estado em **2026-10-16**: uma placa principal roteada em
`kicad/system-candidate/`; estudos em outras pastas são referências históricas.
ERC/DRC/conectividade/paridade zerados não substituem G1/G2 ou ensaios.
[Estado e evidências](development-status.md).

## Baseline atual — D-010/D-021/D-032

```text
T1 original, secundário CT → dois diodos + bulk/proteção → PVDD ≈42–50 V
                                                      ├→ TPA3255 PBTL
                                                      ├→ auxiliar 12 V
                                                      └→ alimentação do preamp OEM

Preamp/limiter OEM (RCA L/R/LFE, crossover 50–150 Hz, volume, fase)
  → chicote OEM J7 → interface de áudio/bias/isolamento/mute
  → INPUT_A/B → TPA3255 PBTL → dois ramos LC → SPK±

Supervisão de rails/DC/falhas + sequenciador discreto → RESET/mute/isolamento
```

PVDD é **não regulado**; a antiga proposta de conversor principal 36 V foi
substituída por D-021. Não há MCU nem primário AC na PCB nova. Nunca usar uma
ponte vermelho–vermelho em T1. [Fonte](power-d021.md) · [T1](transformer-reuse.md).

D-032 reaproveita as placas originais de preamp/limiter e o chicote de sete vias
(manual PS28 p.22–24), em vez de fabricar o front-end de controle anterior.
Pinagem, interface e premissas estão em [decisions.md](decisions.md).
O front-end novo D-022/ELEC-004 e as capturas isoladas anteriores continuam como
histórico de projeto, não como outra PCB de produto.

## Pontos críticos da revisão

- **PBTL:** TI SLASEA8A §10.2.4/Fig.31/tabela11: M2 alto, M1 baixo,
  INPUT_C/D ao GND, A+C e B+D paralelados antes dos dois ramos LC. Não misturar
  com o ponto de paralelamento/filtro da EVM SLOU441.
- **Áudio e power-order:** a proteção é após os capacitores de acoplamento;
  RESET sozinho não protege INPUT_A/B. Qualificar sinais externos, falha única,
  polarização, pré-carga e comportamento desenergizado contra os envelopes
  de [D-019](input-power-order-study.md) e [D-024](iso-d019.md).
- **Sequenciamento:** partida, hold, latch e timeout discretos; não usar AND
  combinacional ingênuo entre FAULT e RESET. [Sequenciador](seq-d020.md).
- **Alimentação:** AUX/rail analógico têm funções distintas; AVDD/DVDD não são
  fontes genéricas. Ripple, regulação e transientes de T1 ainda exigem ensaio.
- **Retornos/EMI:** revisão global de corrente e laços de comutação pendente;
  DRC não prova indutância, capacidade de corrente nem emissão.
- **Térmica:** PowerPAD superior → TIM → bloco/alívio com batentes → calço/TIM →
  perfil OEM. Bond J6→perfil obrigatório; GND não é PE. Fit calculado nominal,
  montagem/roscas/folgas e dissipação ao ambiente ainda precisam validação.

## Limites de evidência

O alvo 120–150 W não é rating contínuo garantido. A placa atual tem 269 footprints,
3.531 segmentos e 499 vias; conectividade fechada e revisão local não encerram a
revisão elétrica independente/global nem qualificam BOM/CPL ou montagem.

[Revisão local](tpa-local-layout-review.md) ·
[Fit térmico](../mechanical/thermal-block.md) ·
[Roadmap](production-roadmap.md) · [Segurança e gates](safety.md).
SPK+ e SPK− são ativos/flutuantes: nunca GND ou garra terra do osciloscópio.
