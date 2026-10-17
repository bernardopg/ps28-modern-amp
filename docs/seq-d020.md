# D-020 — Subconjunto discreto do sequenciador (sem MCU)

Atualização2026-10-17: [SYS-002 Rev.B](sys002-baseline.md) e
[derating atual](capacitor-derating.md) prevalecem para limites/capacitância
efetiva; C40110u50V0805 próximo do LP2985 e C40310u25V0603.

Captura `kicad/seq-d020/` (ERC 0) e integração em `kicad/system-candidate/`.
**Estudo; não é hardware validado, não libera compra, fabricação nem energização.**
D-024 acrescentou a lógica da interface D-019 (RESET depois do relé, dwell DC,
latch de áudio, trip por DC) e o relé/mute/janelas em `kicad/iso-d019/`; ver
[iso-d019.md](iso-d019.md). A seção abaixo descreve o subconjunto D-023 original.

## Fontes primárias

| Peça | Documento | Uso |
|---|---|---|
| TPA3255 | SLASEA8A Rev A, p.6 (RESET/FAULT abs. máx. 4,2 V), p.8 §7.5 (VIH 1,9 V, VIL 0,8 V, FAULT VOH 3–3,6 V), §9.4.1.8 p.21, §11.2 p.30 | interface |
| TPS3808G33 | SBVS050N (ago/2026), p.4 pinagem DBV, p.6 §6.5, p.7 §6.6 td | hold e timeout |
| TPS3700 | SBVS187G (fev/2019), p.4, p.6 | janelas ANALOG_12V e VMID |
| LP2985-33 | SLVS522S (mai/2025), Table 4-1, p.33 orderable | SEQ_3V3 |
| SN74LVC2G74 | SCES203Q (set/2021), Table 5-1 | latches RUN e ARMED |
| SN74LVC1G14/1G32/1G08/1G07/1G06 | SCES218AA, SCES219W, SCES217AA, SCES296AG, SCES295AB | portas |

PDFs em `reference/ti/` (fora do Git), hashes em `reference/manifest.json`.

## Topologia

1. **SEQ_3V3:** LP2985-33 a partir de AUX_RAW (11,69–12,50 V calculado; VIN máx.
   16 V). 3,3 V porque RESET do TPA tem máximo absoluto de 4,2 V.
2. **RAILS_OK (wired-AND open-drain, baixo = inválido):** PGOOD do LM5164, janela
   TPS3700 de PVDD, janelas TPS3700 de ANALOG_12V e de VMID, e as duas saídas de
   *trip* abaixo. Pull-up R323 para SEQ_3V3.
3. **Hold:** U402 → U403, dois TPS3808G33 com CT ao VDD por 100 kΩ (180/300/420 ms
   cada). RAILS_QUAL sobe ≥ 360 ms depois de RAILS_OK, igual a `BOOT_HOLD_US`.
4. **Partida humana:** botão (J401) com debounce RC (10 ms aperto, ~110 ms
   soltura) e Schmitt inversor U405. A borda de aperto registra CLIP_OTW em U406
   (RUN). Botão mantido não gera borda: não enfileira partida. Borda com
   RAILS_QUAL baixo é ignorada (CLR assíncrono).
5. **RESET:** (D-024: RUN → U414, 12–28 ms → RESET_GO) → R408 1 kΩ → RESET; com R9 4,7 kΩ dá ≥ 2,6 V (VIH 1,9 V) e
   ≤ 3,35 V (< 4,2 V).
6. **Arme de FAULT:** U407 registra RUN na borda de subida de FAULT depois da
   liberação de RESET (assinatura de startup §11.2). Antes disso, FAULT baixo é
   mascarado, como em START_AVDD.
7. **Latch de falha:** U408 = NOT_ARMED OR FAULT; baixo (armado e FAULT baixo)
   aciona U409 open-drain em RAILS_OK. O hold reinicia, RUN cai, RESET cai e o
   pulso se autoencerra quando ARMED zera. Rearme exige novo hold ≥ 360 ms
   (> 4 ms de §9.4.1.8 e > 12 ms de `REARM_US`) e nova borda humana.
8. **Timeout de partida:** U410 = RUN AND NOT_AUDIO (D-024; antes NOT_ARMED) no MR de U404 (CT 180 nF,
   0,62–1,44 s). Sem arme dentro da janela, U411 open-drain derruba RAILS_OK.
   Máximo 1,44 s = `START_TIMEOUT_US`.

## Janelas analógicas (calculado, VIT pior caso e divisores 0,1 %)

| Janela | mín | típ | máx | Faixa esperada |
|---|---|---|---|---|
| ANALOG_12V UV (descendo) | 8,71 V | 8,90 V | 9,04 V | piso D-018 ≈ 8,03 V |
| ANALOG_12V OV (subindo) | 13,53 V | 13,69 V | 13,85 V | AUX máx. 12,50 V |
| VMID UV | 3,86 V | 3,95 V | 4,01 V | ANALOG UV mín. / 2 = 4,36 V |
| VMID OV | 6,49 V | 6,56 V | 6,64 V | 12,50 V / 2 = 6,25 V |

O UV analógico dispara antes do piso de 8,03 V do estudo D-018, mas a queda real
de D201/R201 sob carga não foi medida: margem de partida em rede baixa a confirmar.

## Verificação executável

`scripts/seq_d020_logic.py` simula **a netlist capturada** (peças lidas de
`create_seq_d020.parts()`), em tempo discreto de 1 ms, nos cantos mín./máx. de td.
`tests/unit/test_seq_d020.py` cobre: hold ≥ 360 ms e botão antecipado ignorado;
botão mantido; OTW baixo; FAULT após arme com latch, rearme bloqueado no novo hold
e nova borda; timeout; perda de rail derruba RESET. Mutação: remover U403, U409 ou
U411 derruba os testes correspondentes.

Não modelado: atrasos de propagação, níveis analógicos, VDD abaixo de VPOR,
bounce real, comportamento interno do TPA (substituído por estímulo), ruído em
RAILS_OK perto dos limiares (histerese do TPS3700 de só 5,5 mV típ.).

## Integração `system-candidate`

- Bancos D-021 (power) e D-020 (seq) fora do contorno OEM, sem placement nem
  fit, como o banco analógico. 150 footprints; 421 pinos casados entre netlist
  nativa e PCB.
- `PVDD_36V` do núcleo renomeado para `PVDD` (D-021). Retificador → PVDD do U1;
  LM5164 → AUX_RAW (C1); R408 → RESET; FAULT/CLIP_OTW → latches.
- J4 (controle externo), R7 e R8 (pull-ups a VIO externo) marcados **DNP**: o
  sequenciador comanda RESET e os pull-ups internos de FAULT/CLIP_OTW bastam
  (fanout 30, §7.5). Evita realimentação de 3V3 externa.
- J302, J303 e J402 eram interfaces lógicas e foram removidas.
- J1 (borne PVDD) segue como entrada de bancada; não usar junto com T1.
- ERC: 4 erros OUT_x em paralelo PBTL + 1 aviso MONO_BIASED, os mesmos da base.
  DRC: 0 violações, 0 erros de footprint, 338 conexões sem roteamento.

## Pendências

- D-019 resolvido como estudo por D-024 ([iso-d019.md](iso-d019.md)); confirmação
  de aberto/fechado e casamento prévio são por projeto/tempo, não observados.
- Footprints candidatos não auditados contra desenhos dos MPNs; layout, placement
  OEM e roteamento.
- Localização mecânica do botão de partida (J401) no painel original; UX de
  pressionar após ligar a rede.
- Bancada: brownout lento, falha da própria SEQ_3V3, FAULT persistente, OTW ativo
  no rearme e forma de onda real de FAULT no startup.
