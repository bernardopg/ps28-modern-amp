# VMID físico — estudo D-017, desligamento bloqueado

## Objetivo e estado
Substituir a fonte VMID ideal do estudo por divisor, buffer e carga capacitiva
explícitos, **antes** de integrar o front-end à PCB. Resultado: comportamento
estacionário promissor no modelo TI; **candidata NÃO aprovada para captura/integração**
porque a referência armazenada exige proteção no desligamento. Nenhuma PCB,
mount OEM, esquema KiCad existente ou gate foi alterado.

## Fontes primárias
TI OPA1656 **SBOS901C**, rev. setembro/2022:
- §6.1, p.4: entrada entre V−−0,5 V e V++0,5 V; corrente de entrada ±10 mA.
  São limites absolutos, **não metas de projeto nem autorização para exceder tensão**.
- §6.3, p.4: alimentação recomendada de 4,5–36 V single.
- §6.6, p.6: caracterização com VS=±18 V; não garantir extremos reais a 12 V.
- Figuras 6-35/6-36, p.13: estabilidade/carga capacitiva, resistores de isolamento
  de 25/50 Ω em curvas típicas. As curvas usam **pF**, não qualificam nossos µF.

Modelo TI SBOMAW6C/Final1.3 original, hash/auditoria/licença descritos em
[estudo OPA1656](analog-capture.md). Ngspice >=47, configuração isolada;
nenhuma alteração no modelo TI nem relaxamento de convergência. Dados e estudos
não são medições de bancada ou garantia de componentes/produção.

## Proposta avaliada, sem seleção de BOM
Divisor AUX_12V → 4,7 kΩ → REF → 4,7 kΩ → GND; CREF=22 µF de REF a GND.
Buffer OPA1656 seguidor: feedback no **driver, antes** de RISO.
Driver → RISO → VMID; capacitor de VMID a GND com ESR explícita.
Segundo canal do dual terminado como seguidor de REF, não flutuante;
isso não congela um novo U4 nem substitui futuras funções do front-end.

RISO=25/50 Ω; reservatório=22/47 µF; ESR assumida=0,05/2 Ω.
Resistores do divisor ±1%; fuga de CREF entre 0 e 10 µA **assumida**, não rating
verificado de um MPN. MPNs, tolerâncias/derating de C, ESR, fuga, footprints e
comportamento de clamp/backfeed ainda TBD. 25 Ω é referência de estudo, não
promessa de estoque nem resistor escolhido para fabricação.

## Cálculos independentes
- Rth do divisor nominal: 2,35 kΩ; τREF=51,7 ms; polo≈3,08 Hz.
- Com RISO=25 Ω e 47 µF, τVMID≈1,175 ms (ESR pequena à parte).
- Corners divisor/fuga a 13,2 V: REF entre 6,51050 e 6,66600 V.
  Somando queda de 50 Ω com carga ±1 mA: erro máximo assumido≈139,50 mV.
  Janela interna proposta: ±150 mV. Não inclui todos extremos do opamp/produção.
- Critérios internos de estudo: margem de fase ≥45°; assentamento em ±10 mV.
  Não são requisitos de bancada aprovados nem timeout escolhido do supervisor.

## Simulações executadas
Relatório: [JSON versionado](../tests/reports/vmid-buffer-study.json).
- **32 casos de return ratio**: 10,8/13,2 V ×0/70 °C ×25/50 Ω ×22/47 µF ×duas ESRs.
  Fonte de injeção em série no feedback, DC=0; cálculo de −Vdriver/Vfeedback.
  721 pontos de 1 Hz a 1 GHz; um cruzamento unitário por caso, mínimo de
  **60,67°** de margem modelada. Banda de varredura não é banda útil garantida.
- **Contraprova sem isolamento**: 1 mΩ representa conexão direta; 12 V/27 °C,
  47 µF/0,05 Ω. Margem modelada **−2,96°**: capacitor direto não é solução aceita.
- Carga imposta de +1/−1 mA em três supplies: desvio máximo≈25,48 mV do meio
  do rail com RISO=25 Ω; níveis estacionários conferidos pela lei de Ohm.
- Ripple auxiliar de 100 mV pico/100 Hz: VMID≈1,237 mV pico, conferido contra
  transferência RC independente. Não é ensaio de PSRR/ruído do amplificador completo.
- Três cargas de CREF inicialmente zero, **AUX já válido antes do teste**:
  janela de ±10 mV alcançada no modelo em≈324–334 ms; equação RC ideal prevê
  ≈326–337 ms. Corrente do driver durante carga também registrada: o degrau
  estacionário ±1 mA não é envelope de partida. Não simula o power-on do CI,
  subida real de AUX ou partida do TPA.
- LR4 anterior com VMID físico no lugar da fonte ideal: três supplies,
  20 Hz/2 Vrms; diferencial≈1,99237 Vrms, integração ponderada no tempo;
  maior erro de VMID≈3,52 mV no conjunto nominal. **A entrada biasada acompanha
  VMID neste teste**: não usar os ≈37 µA de pico do driver como envelope do futuro
  somador/RCA/LFE. Carga ±1 mA é teste independente, não consumo medido do sistema.

Warnings de gmin/source stepping e fallback ficam no JSON/logs; falha não gera
relatório de sucesso. Curvas típicas, phase margin modelada e fontes ideais não
comprovam estabilidade física, EMI, layout ou ruído. O teste de return ratio foi
checado também contra função de transferência analítica conhecida.

## Bloqueio crítico: power-down
Não simulamos o macro abaixo da alimentação recomendada para inventar proteção.
Analisamos o RC passivo, **sem clamp qualificado**, partindo de 12 V/REF=6 V,
com rampas de AUX até zero em 0,1/2/20/100 ms. Ao fim das rampas, REF permanece
respectivamente≈5,994/5,885/4,976/2,654 V. O modelo passivo foi comparado com
integração numérica independente da EDO.

Com AUX=0, o limite superior de entrada é 0,5 V: **a ligação direta de REF à
entrada não pode ser aceita sem proteção qualificada**. Diodos internos podem
alterar essas tensões, mas corrente/injeção/backfeed e confiabilidade não estão
qualificados; não assumimos que eles resolvam o sistema. CREF armazena só
0,396 mJ a 6 V: energia pequena não elimina violação de rating.
O reservatório VMID também pode realimentar o driver e os outros opamps quando
AUX cai. Isso não foi qualificado pelo modelo nem por hardware.

**RESET baixo não protege esses pinos.** Capturar esta candidata como fonte
pronta esconderia um risco real. Próximo requisito: descarga/clamp controlados,
limites de corrente e prevenção/limitação de backfeed de AUX, incluindo os
outros pinos do front-end e o caso de fonte ausente. O envelope real da fonte
continua pendente em PWR-001; não impor tempo mínimo de queda sem evidência.

## Reprodução e critérios de publicação

```bash
python3 scripts/simulate_opa1656.py --fetch-model  # TI local, auditado, não republicado
make simulate-vmid                              # ngspice >=47
make check
```

`simulation/analog/vmid-study.json` contém todas hipóteses; circuitos, dados e logs
em `build/analog/vmid/`. CI usa job isolado Arch Linux com pacote assinado.
Relatório guarda hashes de configuração, scripts e modelo; fonte alterada exige
nova evidência. Nenhum script de fabricante executado/configuração global alterada.

**Exit code 0 significa que o estudo reproduziu inclusive os bloqueios esperados,
não que VMID seja seguro.** Critérios ELEC-002/003, G0–G5 e liberação de bancada,
compra/fabricação continuam pendentes. Sem captura ou energização automática.
