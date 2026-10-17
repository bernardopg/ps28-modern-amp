# D-024 — Interface D-019: isolamento por relé, mute e observação DC

Captura `kicad/iso-d019/` (ERC 0), lógica em `kicad/seq-d020/` e integração em
`kicad/system-candidate/`. **Estudo; não é hardware validado, não libera compra,
fabricação nem energização.** A ponte DIFF_POS/NEG → C20/C21 agora existe, mas
**só alcança o TPA através do relé K501**.

## Por que relé, e não chave de estado sólido

A triagem anterior (`input-power-order-study.md`) rejeitou chaves CMOS por limites de
tensão com o lado desligado e rejeitou relé porque 3 ms não cumpre "detecção +
abertura ≤ 100 µs". Esse requisito supunha que os drivers do preamp poderiam
mudar antes da abertura. D-024 troca o requisito pela grandeza que ele protegia,
**a tensão no pino INPUT_x (−0,3…7 V, SLASEA8A §7.1 p.5)**, e mostra que:

1. Todo gatilho de desligamento (RAILS_OK: PVDD, AUX, ANALOG_12V, VMID, FAULT,
   timeout, DC) dispara com os trilhos do preamp ainda dentro das janelas, porque os
   limiares ficam acima do piso operacional e os bancos seguram os trilhos.
2. Depois do gatilho, o relé abre em ≤ 3 ms (Omron K106-E1-11 p.3) e os drivers
   mudam devagar: ANALOG_12V cai ≤ 126 V/s (95 mA em 2×470 µF −20 %), VMID ≤ 63 V/s.
3. Com o pino em 1,94…5,06 V de DC (janela observada) e áudio ≤ 1,556 V de pico,
   o pino fica entre −0,3 e 7 V durante essa abertura (simulado abaixo).

Um contato metálico também resolve o que as chaves CMOS não resolviam: isolação
≥ 1000 MΩ, ausência de backfeed e de injeção de carga, independentemente da
alimentação. Classe de contato P (10 µA a 10 mV DC) serve para sinal de baixo nível.

## Topologia (por ramo; B idêntico)

| Elemento | Nets | Função |
|---|---|---|
| C20 (núcleo, 10 µF) | DIFF_P → INA_ISO | acoplamento; placa direita passa a ser INA_ISO |
| K501 COM 3 | INA_ISO | placa isolada |
| K501 NO 4 | INA_NO → R517 3,3 kΩ → INPUT_A_AC (U1.5) | conecta só com bobina energizada |
| D503 BAT54 | K = INPUT_A_AC, A = GND | clamp negativo de falha simples (D-024a) |
| K501 NC 2 | INA_DIS → R503 1 kΩ → GND | descarga só com a placa **desconectada** |
| C503 4,7 nF C0G | INPUT_A_AC → GND | capacitância definida no pino (≥ 4 nF) |
| R505–R507 787k/115k/78,7k | INPUT_A_AC → GND | janela DC e retorno do pino (~0,98 MΩ) |
| C509/C510 330n/680n | taps | média do DC, τ ≈ 50 ms |
| U501 TPS3700 | DC_OK (wired-AND) | baixo fora de 2…5 V |

Form C garante *break-before-make* físico: NC e NO nunca fecham juntos. Relé sem
bobina = isolado e descarregando. Pinagem: G6K-2F vista de cima, bobina 1(+)/8(−),
COM 3/6, NC 2/7, NO 4/5 (K106-E1-11 p.6), igual ao símbolo KiCad `Relay:G6K-2`.

**Driver da bobina:** RUN → R501 2,2 kΩ → Q501 MMBT3904 (Diodes DS30036: VCEsat
≤ 0,2 V a 10 mA/1 mA; VCEO 40 V). Bobina DC12 1315 Ω, 9,1 mA, operação ≥ 9,6 V
(80 %) contra AUX ≥ 11,69 V. Flyback 1N4148W + BZT52C15 (13,8–15,6 V): pico de coletor
≤ 12,5 + 15,6 + 1 ≈ 29 V, abaixo de 40 V, e soltura mais rápida que só diodo.

**Mute:** U503 TMUX6219 (TI SCDS420E) alimentado por ANALOG_12V. EN alto (pull-up
interno de 4 MΩ + R511 100 kΩ) e SEL em GND ligam D–S1, curto-circuitando DIVIDED
(entrada do buffer U2) a VMID com RON ≤ 7,5 Ω (p.10) contra 5 kΩ de fonte: ≥ 56 dB.
O preamp inteiro fica quieto em VMID. AUDIO_EN → Q502 puxa EN para baixo (VIL 0,8 V)
e desmuta. Sem lógica, Q502 corta e fica mutado. S2 vai a GND, como manda
§7.4 p.32 para caminho sem uso.

**Janela de AUX_RAW:** U504 (357k/1,5k/11,5k) entra em RAILS_OK: UV 10,98–11,42 V,
acima do mínimo de VDD do TPA (10,8 V, §7.3) e abaixo do AUX mínimo (11,69 V); OV
12,71–13,03 V. Não depende do PGOOD do LM5164, cujo estado é indefinido com o CI morto.

## Sequência (lógica em `seq-d020`, modelo da netlist capturada)

1. Hold ≥ 360 ms com rails válidos; borda humana com CLIP_OTW alto → RUN.
2. RUN energiza K501 (fecha ≤ 3 ms). Placa isolada ≈ 0 V (NC) e pino ≈ 0 V (TPA
   em RESET); casamento antes do fechamento por projeto, não observado.
3. U414 (TPS3808, CT aberto) libera RESET **12–28 ms** depois de RUN: conexão antes
   de START_AVDD. O TPA faz a pré-carga dos capacitores (Fig.32).
4. FAULT sobe → ARMED. Com ARMED e DC_OK (janela nos dois pinos), U416 conta
   12–28 ms contínuos e U417 trava AUDIO_EN → desmuta.
5. Em RUN: DC_OK cai → U418/U419 derrubam RAILS_OK → latch de falha. Qualquer
   gatilho zera RUN: RESET baixo e mute imediatos, relé abre ≤ 3 ms, NC descarrega.
6. Timeout de partida (U404, 0,62–1,44 s) cobre arme + pré-carga + dwell.

## Simulação (script removido em D-038; histórico Git), 1350 casos + 216 de falha simples, `tests/reports/d019-interface-study.json`)

Modelo: driver ideal (VMID + áudio), C20 8/10/12 µF, Form C com BBM, TPA = RIN
10/20/40 kΩ para viés ideal, série 3,3 kΩ e BAT54 no **VF máximo** de catálogo; no defeito o viés vai a **0 instantaneamente** (pior
caso). Varredura: viés nas bordas da janela 1,937/3,875/5,057 V, VMID 4,36/6,25 V,
áudio de 20 Hz com 1,556 V de pico (contrato + 10 % de overshoot do degrau de mute)
em 8 fases.

| Cenário | Pino mín. | Pino máx. |
|---|---|---|
| Partida (fecha 3 ms, RESET 12 ms, desmuta no 1º cruzamento da janela) | 0,0 V | ≤ 6,47 V |
| Defeito com trilhos mantidos, abertura 3 ms | 0,0 V | ≤ 6,47 V |
| Defeito com ANALOG_12V caindo 126 V/s, abertura 3 ms | 0,0 V | ≤ 6,47 V |
| Mesmo, abertura **10 ms** (3,3× o máximo de catálogo) | −0,158 V | ≤ 6,47 V |
| **Falha simples**: driver em curto para GND, relé fechado | **−0,351 V** | — |
| **Falha simples**: driver preso em ANALOG_12V, relé fechado | — | **12,5 V** |

Placa isolada ≤ 6,61 V (contrato ≤ 16 V; contato 60 VDC). Margem do pior caso
sem falha: 142 mV acima de −0,3 V. Média DC em 20 Hz deixa ripple de 0,24 V.
Aritmética de janela: 1,937 − 1,556 − 0,24 = 0,14 V ≥ −0,3; 5,057 + 1,556 + 0,24 =
6,85 V ≤ 7 V.

## Tratamento dos riscos (D-024a, 2026-10-10)

| Risco | Situação | Como |
|---|---|---|
| Falha simples, driver para GND | **Mitigado, não eliminado** | R517/R518 3,3 kΩ + BAT54 no pino: sem clamp ≈ −5,9 V; com clamp ≤ −0,351 V no VF **máximo** de catálogo (DS11005 p.2: ≤ 240 mV a 0,1 mA, ≤ 320 mV a 1 mA). Ainda 51 mV além de −0,3 V nesse canto; o clamp interno do TPA só divide corrente (não modelado). Fechar exigiria ≥ 12 kΩ em série (−5 dB). |
| Falha simples, driver preso alto | **Aberto** | Pino até 12,5 V até a janela OV (filtro ~50 ms) abrir o relé; corrente limitada por 3,3 kΩ. Clamp superior exigiria trilho entre 6,5 e 6,7 V com tolerância que não existe na placa. |
| Entrada real do TPA desligado/em RESET | **Não resolvível por projeto** | TI não publica o circuito; só RIN para viés ideal. Aceito por projeto: relé isola a entrada até RESET liberado (D-037). |
| Bounce do contato | **Resolvido por projeto** | Fecha com placa e pino ≈ 0 V, RESET baixo e mute ativo; RESET só sai 12–28 ms depois (bounce ≪ 3 ms de operação). Na abertura, bounce só reconecta brevemente o estado anterior. |
| Contato colado | **Aberto, baixa probabilidade** | Sinal sem corrente (µA): solda de contato improvável. Sem contato auxiliar para detectar. |
| Áudio < 20 Hz | **Falha segura** | Dispara a janela DC → mute e desligamento travado, não excursão do pino. Passa-altas subsônico registrado em ELEC-002 para evitar desligamento incômodo. |
| Footprint TMUX6219 | **Resolvido** | `PS28_ANALOG:TI_DGK0008A` conforme exemplo TI SCDS420E p.50 (1,4 × 0,45 mm, passo 0,65, centros 4,4 mm). |
| Footprints G6K-2F, SOT-23 | Candidatos KiCad | G6K-2F conferido só em pinagem; ver K106-E1-11 p.6 antes de G3. |

Custos: série 3,3 kΩ reduz o ganho em −2,48/−1,33/−0,69 dB com RIN 10/20/40 kΩ;
compensar no ganho do front-end. Fuga do BAT54 (≤ 2 µA a 25 V) desloca o DC do pino
≤ 40 mV com RIN 20 kΩ a 25 °C; quente é maior.

- RCA ativa com o OPA desligado e eventos de fase/volume do painel continuam
  requisitos do front-end, não desta interface.

## Fontes

Omron G6K Cat. No. K106-E1-11 (p.3 ratings/características, p.6 terminais); TI
TMUX6219 SCDS420E (p.3, p.10, §7.4 p.32, p.39); TI TPS3700 SBVS187G; TI TPS3808
SBVS050N; Diodes MMBT3904 DS30036 Rev.27, 1N4148W DS30086 Rev.31, BZT52 DS18004
Rev.38; TI SLASEA8A Rev A. PDFs locais em `reference/`, hashes no manifesto.
