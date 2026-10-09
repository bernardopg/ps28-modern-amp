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

## Captura `kicad/power-d021/` (ERC 0, sem exclusões)

`python3 scripts/create_power_d021.py` gera; recusa sobrescrever.

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

Todos os MPNs e footprints estão **TBD**. Nenhum valor acima é rating de peça escolhida.

## Não capturado — próximo incremento

1. **Buck AUX 12 V:** Vin ≥ 65 V (preferível ≥ 70 V), saída 12 V dentro de
   10,8–13,2 V (SLASEA8A §7.3), Iout ≥ 0,5 A. Orçamento: VDD 30 mA + GVDD
   2 × 24 mA (SLASEA8A §7.5) + analógico ≤ 50 mA (D-018) + relé/supervisor TBD.
2. **OVP/brownout de PVDD:** comparador com referência, disparo ≈ 52 V com
   histerese, que segura RESET baixo e abre o relé de saída. Integra com o contrato
   de sequência D-019/D-020, sem MCU. Tolerância da referência e do divisor entra
   no cálculo para nunca disparar abaixo de 49,8 V nem passar de 53,5 V.
3. **Inrush:** decidir NTC ou relé de bypass após medir o I²t real do fusível de
   rede T2.5AL e a corrente de partida na bancada.
4. **Bancada (PWR-001/BENCH-001):** medir regulação sob carga resistiva, ripple e
   temperatura de T1; substituem os parâmetros não medidos deste estudo.

**Segurança:** nunca ligar vermelho–vermelho em ponte (≈97 V, acima do máximo absoluto
do TPA3255). O secundário só sai do chicote original após identificar as cores medidas.
