# Simulação e validação antes da PCB

## 1. O que simular

### Front-end

- ganho de soma L/R;
- impedância de entrada;
- headroom com 2 Vrms de entrada;
- VMID e margem dos NE5532;
- resposta LINE/LFE.

### Crossover

Objetivo inicial:

- LPF Linkwitz-Riley de 4ª ordem;
- Fc = 80 Hz para Rev. A;
- -6 dB no ponto de crossover;
- soma acústica depende também da caixa/woofer e deve ser medida posteriormente.

Executar:

- AC sweep 10 Hz–10 kHz;
- Monte Carlo com tolerâncias de R/C;
- análise de fase;
- step response.

## 2. O que não confiar ao SPICE simples

- EMI radiada/conduzida do Classe D;
- comportamento real de layout;
- saturação térmica do indutor;
- ringing de switching sem modelos parasíticos adequados;
- desempenho térmico do PowerPAD.

## 3. Golden reference

Compare sempre:

1. datasheet TPA3255;
2. schematic TPA3255EVM;
3. BOM TPA3255EVM;
4. PCB TPA3255EVM.

## 4. Checklist antes de congelar schematic

- [ ] Modo PBTL confere com datasheet.
- [ ] VDD/PVDD/AVDD/DVDD/GVDD corretos.
- [ ] Bootstrap conforme referência.
- [ ] FAULT/CLIP/RESET corretamente polarizados.
- [ ] TPA input AC coupling correto.
- [ ] Nenhum terminal SPK aterrado.
- [ ] LPF simulado.
- [ ] Headroom do NE5532 em 12 V validado.
- [ ] Fonte auxiliar tem margem térmica/corrente.

## 5. Validação pós-layout

- ERC.
- DRC.
- revisão visual contra EVM.
- revisão dos loops de corrente.
- revisão térmica.
- revisar Gerber e drill em visualizador independente.
- comparar BOM/CPL com schematic e PCB.
