# Arquitetura — PS28 Modern Amp Rev. A

## Diagrama de blocos

```text
 RCA L ─┐
        ├── SUM L/R ──► BUFFER ──► LPF 80 Hz / 24 dB-oct ──┐
 RCA R ─┘                                                   │
                                                            ├─► SOURCE SELECT ─► VOLUME
 RCA LFE ───────────────► BUFFER ────────────────────────────┘                      │
                                                                                   ▼
                                                                   SE → diferencial / fase
                                                                                   │
                                                                                   ▼
                                                                            TPA3255 PBTL
                                                                                   │
                                                                                   ▼
                                                                             filtro LC
                                                                                   │
                                                                                   ▼
                                                                       Woofer Infinity 4 Ω

 36 VDC externo ─► fusível/TVS ─► PVDD TPA3255
                         │
                         └─► DC/DC 12 V ─► front-end + VDD
                                      └─► 3.3 V opcional para lógica/LED
```

## Filosofia de projeto

### Domínio de potência

O TPA3255 opera em PBTL mono. O objetivo não é obter a potência máxima anunciada pelo CI; é fornecer margem limpa para o woofer do PS28 em 4 Ω. A escolha de 36 V reduz a potência disponível em relação a 48–53 V e, portanto, ajuda a manter o projeto próximo da faixa útil do transdutor original.

### Domínio analógico

O front-end opera em fonte simples de 12 V com referência virtual VMID em aproximadamente 6 V. Entradas RCA são AC-coupled e condicionadas por op-amps de áudio.

### Domínio de controle

A Rev. A usa controle por hardware. RESET/MUTE, FAULT e CLIP_OTW ficam acessíveis em header/test points. Não há MCU.

## Interfaces

### Entrada DC

- J_PWR: 36 VDC e GND.
- Fusível substituível.
- TVS dimensionado para a rail escolhida.
- Proteção contra polaridade reversa deve ser considerada antes do layout final; MOSFET ideal é preferível a diodo série de alta perda.

### Áudio

- J_RCA_L, J_RCA_R, J_RCA_LFE.
- Ground de RCA retorna ao domínio analógico e encontra o power ground em ponto controlado conforme estratégia de grounding.

### Woofer

- J_SPK: SPK+ / SPK-.
- **Nenhum terminal é GND.**

### Painel

- RV_VOL 50 kΩ log.
- SW_SOURCE LINE/LFE.
- SW_PHASE 0/180.
- LED_POWER, LED_FAULT, LED_CLIP_OTW.

## Rev. A versus Rev. B

A Rev. A deve priorizar validação. O crossover pode ser fixado em 80 Hz. Após confirmação acústica, a Rev. B pode implementar seleção 50/80/120/150 Hz ou controle contínuo, desde que os componentes de filtro sejam recalculados e simulados.
