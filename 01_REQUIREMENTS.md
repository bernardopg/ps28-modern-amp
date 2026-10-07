# Requisitos de Sistema — PS28 Modern Amp Rev. A

## 1. Requisitos elétricos

| Item | Meta Rev. A |
|---|---|
| Woofer | Infinity PS28 original, 4 Ω nominal |
| Potência contínua útil | 120–150 W RMS alvo |
| Arquitetura | Classe D, TPA3255 PBTL mono |
| PVDD | 36 VDC nominal |
| Fonte externa | 36 V, 5–6 A, isolada |
| Alimentação auxiliar | 12 V, ≥300 mA |
| Entrada | RCA L, RCA R, RCA LFE |
| Crossover LINE | 24 dB/oitava alvo; 80 Hz na Rev. A inicial |
| LFE | bypass do LPF interno |
| Volume | 50 kΩ log |
| Fase | 0° / 180° |
| Proteções | short/OC/OT/UV internas + fusível de entrada DC |

## 2. Requisitos acústicos

- Preservar gabinete, volume interno, woofer e dutos originais.
- Não alterar comprimento/diâmetro dos ports sem medição eletroacústica.
- A nova chapa traseira deve permanecer hermética ao gabinete, exceto pelos dutos originais.
- Evitar ruído audível, hiss e hum perceptível a 1 m em ambiente silencioso.
- Ganho máximo deve ser limitado para não exceder desnecessariamente a capacidade térmica/mecânica do woofer.

## 3. Requisitos de PCB

- KiCad 10.x.
- Preferência por 4 camadas na placa integrada; 2 camadas/2 oz é aceitável apenas se o layout permanecer muito próximo da EVM da TI.
- Cobre externo 2 oz recomendado na região de potência.
- Thermal pad do TPA3255 com matriz de vias térmicas conforme datasheet/EVM.
- Separação física clara entre:
  - entradas analógicas;
  - conversão single-ended/differential;
  - TPA3255;
  - nós de switching;
  - filtro LC;
  - entrada DC.

## 4. Requisitos de manutenção

- Test points para: PVDD, +12V, 3V3, RESET, FAULT, CLIP_OTW, sinal analógico antes/depois do filtro, SPK+ e SPK-.
- Componentes críticos identificáveis por serigrafia.
- Indutores, eletrolíticos e conectores devem poder ser substituídos sem remover o TPA3255.
- Firmware não é requisito para Rev. A.

## 5. Critérios de aceitação antes de conectar o woofer

- ERC sem erros não justificados.
- DRC sem violações não justificadas.
- Sem curto PVDD-GND.
- Consumo em repouso compatível com a aplicação de referência.
- Rails corretos e estáveis.
- Sem DC diferencial anormal na saída.
- Forma de onda e filtro de saída validados em carga resistiva de 4 Ω apropriada.
- FAULT/CLIP funcionando.
- Dissipador e PCB sem runaway térmico em ensaio progressivo.

## 6. Fora de escopo na Rev. A

- Fonte AC universal 127/220 V integrada.
- DSP, Bluetooth, Wi‑Fi ou microcontrolador.
- EQ paramétrico.
- Auto-calibração de sala.
- PFFB customizado.
- Controle remoto.

Esses itens podem ser considerados após a validação da Rev. A.
