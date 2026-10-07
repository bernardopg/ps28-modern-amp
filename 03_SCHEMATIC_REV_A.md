# Schematic Rev. A — Especificação de Circuito

> Este documento é a especificação para captura no KiCad. O **núcleo TPA3255, bootstrap, desacoplamento e filtro de saída devem ser conferidos contra o datasheet e TPA3255EVM antes de fabricação**.

## 1. Entrada e soma estéreo

```text
J1 RCA_L ── C1 ── R1 ──┐
                        ├── NODE_SUM ─► U1A buffer
J2 RCA_R ── C2 ── R2 ──┘

J3 RCA_LFE ── C3 ─► U1B buffer
```

Componentes propostos:

- J1/J2/J3: RCA through-hole ou painel com chicote.
- C1/C2/C3: 2.2 µF filme ou bipolar de áudio; se espaço/custo exigirem, usar 2.2 µF X7R com DC bias avaliado.
- R1/R2: 22 kΩ, 1%.
- R3/R4/R5: 47 kΩ para referência/pull-down conforme topologia final.
- U1: NE5532P/D ou equivalente de áudio.

A soma L/R deve ser resistiva; nunca curto direto entre L e R.

## 2. VMID analógico

```text
+12V ── R10 10k ──┬── R11 10k ── GND
                  │
                 C10 47uF
                  │
                 GND
                  │
                  └─► U2A follower ─► VMID ≈ 6 V
```

- R10/R11: 10 kΩ, 1%.
- C10: 47 µF / 25 V.
- C11: 100 nF X7R junto ao op-amp.
- U2A: NE5532.

## 3. Crossover LINE Rev. A

Para reduzir risco, a primeira placa deve usar **80 Hz fixos**. O requisito é resposta de 4ª ordem Linkwitz-Riley (duas seções de 2ª ordem com Q apropriado). Os valores finais **não devem ser congelados sem simulação SPICE**.

Implementação recomendada:

```text
LINE_BUF ─► LPF2_A ─► LPF2_B ─► LINE_LPF
```

- U2B/U3A: NE5532.
- Capacitores: filme 1–5%.
- Resistores: 1%.
- Colocar footprints alternativos/DNP para permitir ajuste de Fc e Q durante bancada.

### Variante futura

Rev. B pode implementar chave 4P4T para 50/80/120/150 Hz. Não liberar a rede com valores aproximados sem simulação.

## 4. Seleção LINE / LFE

```text
LINE_LPF ─┐
          ├─ SW1 SPDT ─► AUDIO_SELECTED
LFE_BUF ──┘
```

- SW1: SPDT de painel ou header para chave externa.

## 5. Volume

```text
AUDIO_SELECTED ─► RV1 50k log ─► AUDIO_VOL
                     |
                   VMID
```

- RV1: 50 kΩ log/audio taper.
- O sinal deve permanecer centrado em VMID no domínio single-supply.

## 6. Conversão single-ended para diferencial

Usar a topologia da TPA3255EVM com NE5532 como referência. Objetivo: produzir dois sinais de mesma amplitude e fases opostas, AC-coupled para o TPA3255.

Componentes preliminares:

- U3B/U4A: NE5532.
- R20/R21/R22/R23: 10 kΩ, 0.1–1%.
- C20/C21: 22 pF C0G em feedback se adotado o mesmo compensation da EVM.
- C22/C23: 10 µF X7R, conforme prática da EVM, para acoplamento às entradas do power stage.

## 7. Phase 0/180

Preferência: inverter os dois sinais diferenciais com uma DPDT após o conversor, sem criar novo estágio de ganho.

```text
PHASE 0:   DIFF_A → IN_A ; DIFF_B → IN_B
PHASE 180: DIFF_A → IN_B ; DIFF_B → IN_A
```

- SW2: DPDT.

## 8. TPA3255 power stage

- U5: TPA3255DDV, HTSSOP-44 PowerPAD.
- Configurar em PBTL conforme tabela/figura oficial do datasheet.
- Não inventar níveis de M1/M2/M3: capturar exatamente a configuração PBTL publicada pela TI.
- RESET, FAULT e CLIP_OTW expostos em test points.

### Desacoplamento

Usar o arranjo da EVM como baseline:

- PVDD local: 100 nF / 100 V + 1 µF / 100 V por grupo de alimentação, extremamente próximos aos pinos.
- Bulk local: 1500 µF / 63 V por banco de potência é uma referência razoável baseada na EVM.
- VDD/AVDD/DVDD/GVDD: seguir valores exatos do datasheet/EVM.
- Bootstrap: 33 nF X7R conforme EVM/datasheet.

## 9. Entrada 36 VDC

```text
J4 +36V ─► F1 ─► proteção reversa ─► PVDD
                    │
                    └► TVS para GND
```

Proposta:

- F1: 7.5 A slow-blow ou automotivo/PCB apropriado; valor final após medição de inrush.
- D1: TVS unidirecional com standoff compatível com 36 V nominal; selecionar após tolerância máxima da fonte.
- C30: 4700 µF / 63 V low-ESR próximo à entrada.
- C31: 1 µF / 100 V.
- C32: 100 nF / 100 V.

## 10. DC/DC auxiliar

Para Rev. A, usar módulo pronto de baixa tensão em vez de buck discreto.

- U6: DC/DC 36 V → 12 V, ≥0.5 A, entrada com margem para pelo menos 42 V.
- Preferência por módulo encapsulado de fabricante conhecido.
- Adicionar C_IN/C_OUT conforme datasheet do módulo escolhido.

## 11. 3.3 V opcional

Somente se necessário para LEDs/supervisor/controle.

- U7: LDO 12 V → 3.3 V com dissipação avaliada, ou pequeno buck se carga subir.
- Não usar AVDD/DVDD internos do TPA3255 como fonte genérica para cargas externas sem autorização explícita do datasheet.

## 12. Filtro LC PBTL

Baseline da aplicação TI para 2–4 Ω:

- L1/L2: 10 µH, baixa DCR, corrente de saturação com margem.
- C_OUT1/C_OUT2: 1 µF filme, ≥100 V; 250 V é comum na EVM.
- Snubber/EMI: copiar valores e topologia da EVM; não improvisar.

```text
OUT_P ─► L1 ─► SPK+
              │
             C1F
              │
             GND

OUT_N ─► L2 ─► SPK-
              │
             C2F
              │
             GND

SPK+ ───────── Woofer 4 Ω ───────── SPK-
```

## 13. Test points obrigatórios

- TP1 PVDD.
- TP2 +12V.
- TP3 3V3 (se usado).
- TP4 VMID.
- TP5 LINE_BUF.
- TP6 LINE_LPF.
- TP7 LFE_BUF.
- TP8 DIFF_A.
- TP9 DIFF_B.
- TP10 RESET.
- TP11 FAULT.
- TP12 CLIP_OTW.
- TP13 SPK+.
- TP14 SPK-.

## 14. Componentes DNP úteis

Adicionar footprints opcionais para:

- snubber alternativo;
- capacitor de feedback alternativo no LPF;
- resistores de ganho alternativos;
- ferrite/0 Ω em rails auxiliares;
- RC de mute/RESET;
- rede Zobel se indicada pela validação.
