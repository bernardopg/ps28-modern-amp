# Requisitos Rev. A — rascunho verificável

Status: baseline herdada do starter, pendente de confirmação física e do proprietário.

- REQ-001: preservar gabinete/dutos/woofer; confirmar modelo, impedância nominal,
  DCR, integridade, dimensões e dados do fabricante (task SYS-001).
  Medido pelo proprietário 2026-10-09: Re = 5,0 − 0,6 (pontas) = 4,4 Ω, igual ao
  4,4 Ω ±10% do manual p.9. Etiqueta (foto do proprietário): `20PR10DAG-FW06-E`,
  código `070917`. Família 8" Harman/Infinity; parts list do manual não traz o woofer.
  Busca pública (eBay/Encompass, fonte fraca) não achou Xmax, Fs, Qts, Vas nem
  potência térmica; variante FW01 é outra impedância e não serve de referência.
  Sem dados: limiter provisório 100 W contínuos (rated output do manual p.2) até
  medir T/S em ACOU-001. Manual p.2–3: DC offset ≤10 mV (máx. 50), transitórios
  liga/desliga ≤50 mV pico (máx. 100) e proteção DC por relé/crowbar; usar como
  piso de REQ-007, não como garantia do projeto novo.
- REQ-002: alvo 120–150 W em carga nominal 4 Ω, não compromisso de potência.
  Definir frequência, duração, THD+N, duty cycle e temperatura ambiente em SYS-002.
  P=V_RMS²/R: 150 W requerem 24,49 Vrms, 34,64 Vp e 6,12 Arms.
  Com Re 4,4 Ω, 150 W pedem 25,7 Vrms/36,3 Vp; PVDD D-021 ≈42–46 V sob carga
  deixa margem de swing, então o limite passa a ser limiter/woofer, não a fonte.
- REQ-003 (D-010/D-021): reaproveitar T1 original com retificação full-wave CT
  dois diodos, PVDD não regulado ≈42–50 V calculado (34,35 VAC por metade medido);
  sobretensão abaixo de 53,5 V, bulk ≥63 V e limiter obrigatórios;
  fonte externa isolada somente bancada/fallback; VA e regulação sob carga não medidos;
  especificar tolerância, ripple, transient, inrush, proteções e conector em PWR-001.
- REQ-004: rail auxiliar 12 V; orçamento candidato ≥0,5 A a calcular; VMID ~6 V.
- REQ-005: RCA L/R sem curto entre fontes; LFE independente com bypass do LPF,
  seleção LINE/LFE, volume 50 kΩ log candidato e fase 0°/180° sem MCU.
- REQ-006 (D-022): LINE LR4 ajustável 50–150 Hz no controle CROSSOVER original, -6,02 dB em Fc; tolerâncias, ganho e headroom
  com entrada 2 Vrms a aprovar após SPICE e bancada; LFE não atravessa LPF.
- REQ-007: RESET seguro na partida/desligamento; indicadores FAULT/CLIP_OTW;
  fusível, polaridade reversa, transientes, térmica e proteção DC analisados.
- REQ-008: test points PVDD/12 V/VMID/RESET/FAULT/CLIP_OTW/LINE/LFE/DIFF/SPK±;
  3V3 somente se justificado; potência/referência de cada TP documentadas.
- REQ-009: PCB reparável com footprint/PowerPAD e dissipador revisados; número de
  camadas/cobre aprovados com fábrica, não escolhidos apenas por estética.

Fora de escopo: fonte AC integrada, DSP, rádio, app, PFFB customizado e EQ.
Matriz requisito→task→ensaio em tests/acceptance.md. Limites TBD bloqueiam aprovação.
