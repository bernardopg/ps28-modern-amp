# Requisitos Rev. A — rascunho verificável
Status: baseline herdada do starter, pendente de confirmação física e do proprietário.

- REQ-001: preservar gabinete/dutos/woofer; confirmar modelo, impedância nominal,
  DCR, integridade, dimensões e dados do fabricante (task SYS-001).
- REQ-002: alvo 120–150 W em carga nominal 4 Ω, não compromisso de potência.
  Definir frequência, duração, THD+N, duty cycle e temperatura ambiente em SYS-002.
  P=V_RMS²/R: 150 W requerem 24,49 Vrms, 34,64 Vp e 6,12 Arms.
  Em 36 V, margem real de perdas/clipping é pequena; não prometer esse resultado.
- REQ-003: entrada DC externa isolada/certificada 36 V, capacidade candidata 5–6 A;
  especificar tolerância, ripple, transient, inrush, proteções e conector em PWR-001.
- REQ-004: rail auxiliar 12 V; orçamento candidato ≥0,5 A a calcular; VMID ~6 V.
- REQ-005: RCA L/R sem curto entre fontes; LFE independente com bypass do LPF,
  seleção LINE/LFE, volume 50 kΩ log candidato e fase 0°/180° sem MCU.
- REQ-006: LINE LR4 80 Hz candidato, -6,02 dB em Fc; tolerâncias, ganho e headroom
  com entrada 2 Vrms a aprovar após SPICE e bancada; LFE não atravessa LPF.
- REQ-007: RESET seguro na partida/desligamento; indicadores FAULT/CLIP_OTW;
  fusível, polaridade reversa, transientes, térmica e proteção DC analisados.
- REQ-008: test points PVDD/12 V/VMID/RESET/FAULT/CLIP_OTW/LINE/LFE/DIFF/SPK±;
  3V3 somente se justificado; potência/referência de cada TP documentadas.
- REQ-009: PCB reparável com footprint/PowerPAD e dissipador revisados; número de
  camadas/cobre aprovados com fábrica, não escolhidos apenas por estética.

Fora de escopo: fonte AC integrada, DSP, rádio, app, PFFB customizado e EQ.
Matriz requisito→task→ensaio em tests/acceptance.md. Limites TBD bloqueiam aprovação.
