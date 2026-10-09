# D-021 — Fonte PVDD não regulada: estudo e captura

Estudo ngspice e captura KiCad isolada. **Não é hardware validado, não libera compra,
fabricação nem energização.** Gates G1–G4 continuam pendentes.

## Entradas

- Medido pelo proprietário (2026-10-09): 34,35 VAC por meia-bobina a vazio com rede
  126,6 VAC; ≈0,2 Ω por meia-bobina (resolução 0,1 Ω). Ver `transformer-reuse.md`.
- Limites TI SLASEA8A Rev A: PVDD 18–53,5 V para RL = 4 Ω (p.6, §7.3). O CI só tem
  UVP de PVDD (14,5 V, §7.5); **não há proteção interna de sobretensão em PVDD**.
- Não medidos, varridos ou genéricos: indutância de dispersão (100 µH e 1 mH por
  metade), resistência do primário/regulação do núcleo (omitidas: queda otimista,
  inrush pessimista), diodo genérico de silício, ESR do banco 20 mΩ, carga em
  corrente constante como média do amplificador.

## Resultado (`make simulate-power`, 54 casos, `tests/reports/power-d021-study.json`)

Rede 108 / 126,6 / 133 VAC × bulk 3 / 10 / 15 mF × carga 0,1 / 2,6 / 3,9 A × dispersão.
2,6 A e 3,9 A aproximam 100 W e 150 W de saída com η 0,88 em ~44 V (hipótese).

| Grandeza | Resultado simulado |
|---|---|
| PVDD máximo (133 V, vazio) | 49,84 V; margem 3,66 V até 53,5 V |
| Vale com 10 mF, 3,9 A, 126,6 V | 38,9–41,8 V; ripple 1,9–2,4 Vpp |
| Vale com 10 mF, 3,9 A, 108 V | 32,4–34,9 V |
| Ripple com 3 mF (bulk atual), 3,9 A | 6,1–7,8 Vpp; insuficiente |
| RMS por meia-bobina, 3,9 A / 2,6 A | 4,3–5,7 A / 3,0–4,0 A |
| Pico de diodo em regime | 12,4–21,3 A |
| Inrush (liga no pico, bulk 0 V) | 45–169 A; I²t ≤ 63,6 A²s nos primeiros 100 ms |
| PIV por diodo (CT full-wave) | ≥ 102,1 V em 133 V |

Leitura: 150 W de pico em 4,4 Ω pedem 36,3 Vp e 100 W pedem 29,7 Vp. O vale com
10 mF atende 100 W mesmo em 108 V e 150 W em rede nominal. O limite de potência é
o woofer/limiter (REQ-002), não a fonte. A placa original operava o mesmo T1 com
2 × 6800 µF; ordem de inrush comparável, mas o circuito de partida original não foi
auditado e não serve de prova.

## Captura `kicad/power-d021/` (ERC 0, sem exclusões, 29 componentes)

`python3 scripts/create_power_d021.py` gera; recusa sobrescrever.

### Retificador e bulk

- J301: T1 1 = vermelho A, 2 = preto CT, 3 = vermelho B. Ordem confirmada por foto
  do chicote (CT no centro); passo ≈ 4 mm (família 3,96 mm), fio 20 AWG UL1015; série do header e rating TBD
  (ver `transformer-reuse.md`).
- F301 no retorno CT, antes do GND: lento, I²t com margem sobre 63,6 A²s, ≥ 63 VDC.
- D301/D302: anodo no vermelho, catodo em PVDD. VRRM ≥ 400 V (2× margem sobre
  102 V), IF(AV) ≥ 6 A, IFSM ≥ 200 A.
- C301/C302: 2 × 4700 µF/63 V, 105 °C. Com C14/C15 do core (2 × 1500 µF) somam
  12,4 mF, entre os casos de 10 e 15 mF. Ripple estimado no banco ≈ 6,7 A RMS a
  3,9 A contínuos; especificar ≥ 3,5 A a 120 Hz por peça e verificar partilha/ESR.
- R301: bleeder 4,7 kΩ; 0,53 W a 50 V; τ ≈ 58 s com 12,4 mF. Peça ≥ 1 W.
- D303: TVS em PVDD com VWM ≥ 51 V e Vc abaixo de 69 V (máximo absoluto) no pulso
  especificado. Cobre transitório rápido; não substitui o OVP sustentado abaixo.
- J302: interface lógica para J1 do core, mesma PCB, não conector novo.

### AUX 12 V — U302 LM5164DDA (capturado)

Fonte: TI LM5164 **SNVSAU4D** (fev/2026), p.3 pinagem, p.5 VREF, p.16–19 Fig 7-1 e
Table 7-1 (VIN 15–100 V, 12 V/1 A, 300 kHz). Valores copiados do exemplo TI, não
otimizados: CIN 2 × 2,2 µF/100 V, CBST 2,2 nF (faixa absoluta 1,5–2,5 nF, p.4),
L 68 µH, RRON 100 kΩ, RFB 453 k/49,9 k, ripple tipo 3 (RA 453 k, CA 3,3 nF,
CB 56 pF), COUT 2 × 22 µF. EN/UVLO ligado em VIN (opção p.14); UV de PVDD fica
no supervisor. PGOOD open-drain em RAILS_OK.

- Calculado: AUX_RAW 11,69 / 12,09 / 12,50 V (VREF mín/típ/máx, RFB 1 %), dentro de
  10,8–13,2 V (SLASEA8A §7.3). VIN abs máx 100 V > Vc do TVS (< 69 V).
- Inconsistência TI: Table 7-1 lista RFB1 = RT0603BRD07**448**KL para 453 kΩ; R311
  fica com MPN TBD até resolver.
- MPNs da Table 7-1 são do exemplo TI; disponibilidade/LCSC não verificada.
- Não simulado: estabilidade COT com C1–C3 do core em AUX_RAW; layout do loop
  de comutação e térmico do HSOP-8 (RθJA 43,4 °C/W, p.5) a revisar.

### Janela de PVDD — U303 TPS3700DDC (capturado)

Fonte: TI TPS3700 **SBVS187G** (fev/2019), p.4 pinagem DDC, p.6 §6.5. Sem símbolo
KiCad oficial: símbolo local `PS28_POWER:TPS3700DDC` com a pinagem da p.4.
Divisor PVDD–R320 931 k–UV–R321 6,04 k–OV–R322 7,32 k–GND, 0,1 %. OUTA (UV) e
OUTB (OV) open-drain unidos a RAILS_OK com PGOOD do buck; baixo = falha.

| Limiar (pior caso: VIT, 0,1 %, corrente de entrada) | mín | típ | máx |
|---|---|---|---|
| OV, PVDD subindo | 50,97 V | 51,60 V | 52,24 V |
| UV, PVDD descendo | 27,28 V | 27,89 V | 28,35 V |

- OV mín 50,97 V > 49,84 V (pior vazio simulado); OV máx 52,24 V < 53,5 V.
- UV máx 28,35 V < vale 32,4 V (10 mF, 108 V, 3,9 A); UV mín > 18 V.
- Histerese interna só 5,5 mV típ (≈ 1,4 %): RAILS_OK pode oscilar perto do
  limiar. Filtrado pelo contrato D-020: queda de rails_valid leva a SAFE, com novo
  hold ≥ 360 ms e nova borda humana; não depende da histerese.
- VDD do TPS3700 vem de AUX_RAW. Sem AUX, OUTA vai baixo abaixo do UVLO e R9
  (4,7 k) já mantém RESET baixo: falha segura por padrão.
- RAILS_OK **não** vai direto ao RESET: o pull-up R323 usa SEQ_LOGIC_VCC
  (≤ 14 V pelo PGOOD) da lógica de sequência, ainda TBD.

### Interfaces lógicas

J302 = PVDD/GND para J1 do core. J303 = AUX_RAW (J2 do core), RAILS_OK,
SEQ_LOGIC_VCC, GND. Mesma PCB, não conectores novos.

Footprints de todos e MPNs dos passivos de potência/divisor estão **TBD**.

## Não capturado — próximo incremento

1. **Inrush:** decidir NTC ou relé de bypass após medir o I²t real do fusível de
   rede T2.5AL e a corrente de partida na bancada.
2. **SEQ_LOGIC_VCC e sequenciador:** a lógica D-020 (TPS3808 em cascata, relé)
   ainda não tem alimentação nem captura.
3. **Integração** de `power-d021` ao `system-candidate` (AUX_RAW, PVDD, RAILS_OK).
4. **Bancada (PWR-001/BENCH-001):** medir regulação sob carga resistiva, ripple e
   temperatura de T1; substituem os parâmetros não medidos deste estudo.

**Segurança:** nunca ligar vermelho–vermelho em ponte (≈97 V, acima do máximo absoluto
do TPA3255). O secundário só sai do chicote original após identificar as cores medidas.
