# D-018 — Correção da fonte VMID e rail analógico protegido

## O que foi corrigido
A candidata D-017 foi **substituída**, não remendada com um diodo interno presumido.
Removemos o buffer de VMID e seu capacitor REF de 22 µF; os quatro opamps passam
a receber **ANALOG_12V**, derivado de AUX_RAW por diodo isolador, resistor e reserva
local. VMID é agora divisor passivo de baixa impedância. Nenhum buffer indefinido
sem alimentação pode ligar a energia armazenada de REF a um pino desprotegido.

A causa específica do bloqueio anterior está resolvida **no projeto/modelo, sob o
envelope abaixo**. Isso não equivale a proteção garantida de todo o amplificador,
BOM congelada, medição ou autorização de fabricação/energização. D-017 e suas
contraprovas foram preservados para detectar regressões.

## Circuito capturado
- AUX_RAW → anodo D201 → catodo ISO_FEED → R201 **15 Ω** → ANALOG_12V.
- C201/C202: duas candidatas Würth **860020575014**, 470 µF/35 V em paralelo.
- R202: **1 kΩ** de AUX_RAW a GND, limita alimentação fantasma por fuga reversa.
- R203: **2,2 kΩ** de ANALOG_12V a GND, descarga definida mesmo sem consumo ativo.
- Divisor: R204+R205 e R206+R207, **75+75 Ω** em cada braço, tolerância alvo 1%.
  Candidatas CRCW120675R0FKEA/1206; carga térmica deve ser revisada no layout.
- C203: **1 µF** VMID–GND; capacitância efetiva TOTAL ligada ao bias deve ficar
  ≤2 µF, incluindo distribuição/front-end. MPN/footprint TBD.
- **Sem U4/buffer/feedback/compensação de VMID.** Impedância DC nominal=75 Ω;
  corrente do divisor≈40 mA a 12 V ideal, em troca da eliminação do estado ativo
  indefinido. Consumo/térmica adicionais entram no budget da fonte/PCB.

D201 candidato **1N4007-E3/54**: família Vishay doc88503, rev.29-Apr-2020,
p.1 DO-41/catodo marcado, p.2 tabela elétrica e padrão de pedido54. VF máximo
**1,1 V a 1 A/25 °C**; fuga máxima **5 µA/25 °C e 50 µA/125 °C** à tensão de
bloqueio nominal. Rating 1 A/75 °C usa leads de 9,5 mm: não transpor essa
condição ao footprint mais curto como garantia térmica. **VF≤1,5 V e fuga≤50 µA
no envelope de uso são hipóteses conservadoras a verificar**, não especificação
inventada para todas as temperaturas. PDF local/hash em `reference/manifest.json`.

## Envelope explícito, não gate de bancada aprovado
`simulation/analog/vmid-protection.json` é a fonte dos limites:
- AUX_RAW regulado 10,8–13,2 V; amplitude máxima 13,2 V; sem overshoot não analisado.
- R201±5%; divisor/bleed analógico±1%; R202 variação TOTAL≤5%.
- Reserva analógica **≥752 µF**, ESR combinada **≤0,5 Ω**.
- Carga ativa + fuga dos bulks **≤50 mA**, além do divisor/bleed.
- VMID: carga total bidirecional **≤1 mA**, capacitância efetiva **≤2 µF**, ESR≤2 Ω.
- Cargas absorventes tornam-se passivas ao atingir zero; fonte de backfeed de
  +1 mA em VMID foi mantida mesmo após desligamento. Não assumir cargas ideais
  alimentadas externamente capazes de forçar tensão negativa ilimitada.
- Modelo RC concentrado: ESL, layout, spikes/EMI e todos os drivers externos
  ainda exigem revisão física. Não há prova para curto interno em ANALOG_12V.

ESR/leakage/aging ao longo da temperatura, Vf real, MPNs/footprints restantes e
pulso de R201 NÃO estão qualificados. Duas peças±20% dão a capacitância mínima
aritmética; isso não substitui avaliação de aging/temperatura de peças reais.

## Por que funciona sem macromodelo abaixo de 4,5 V
A reserva do rail sustenta os opamps enquanto o divisor descarrega VMID.
A prova usa tensões de armazenamento dos dois capacitores e campo vetorial RC,
não a saída de um opamp desligado. Na fronteira VMID_storage=ANA_storage+0,4 V:
- maior decaimento permitido de ANA_storage≈**77,2 V/s**;
- decaimento mínimo de VMID_storage≈**432,4 V/s**;
- campo aponta para dentro com margem≈**355,2 V/s**.

A queda instantânea de terminal causada por ESR também está limitada: excesso
máximo conservador do bias sobre V+≈**0,47250 V**, abaixo de **0,5 V** do TI
OPA1656 **SBOS901C §6.1 p.4**. Existe fronteira inferior dirigida para dentro.
Um teste independente resolve os dois nós por matriz e verifica o campo nas
fronteiras/corners; não replica somente o resultado da função de prova.

Diodo limita condução de retorno; **fuga não é zero**. Com bleed de AUX_RAW,
alimentação fantasma conservadora≤**52,5 mV**, incluindo tolerância de R202. Não realimentar outros rails por
conectores: essa garantia se refere ao caminho D201/R202.

## Evidência executada
[Relatório](../tests/reports/vmid-protection-study.json), com hashes de código,
configuração, topologia canônica e modelo TI original:
- **30 quedas**: duas entradas ×cinco tempos (1 µs,100 µs,2 ms,20 ms,100 ms)
  ×três cargas VMID. Todas dentro dos limites absolutos de entrada.
- **3 casos adicionais**: partida descarregada/brownout/rearme em duas cargas e
  fonte realmente desconectada com backfeed. Esses testes usam rede passiva
  adversarial, NÃO comprovam startup dos opamps ou supervisor.
- Contraprova: retirar isolamento/hold-up reproduz violação; deve continuar falhando.
- Bounds incluem queda abrupta, sem impor um tempo mínimo conveniente à fonte.
- **9 casos TI LR4**: entradas10,8/12/13,2 V ×0/27/70 °C, alimentando o modelo
  com o rail protegido mínimo calculado. Diferencial≈1,99237 Vrms/20 Hz;
  corrente ativa e headroom modelados passam, sem VMID ideal.
- O rail mínimo no estudo é≈**8,03 V**, não 12 V garantidos. Características
  CM/swing de SBOS901C §6.6 são caracterizadas a±18 V: margem no modelo NÃO
  garante extremos de produção a8 V. Qualificação funcional permanece pendente.

Estabilidade do antigo buffer capacitivo deixou de ser problema porque o buffer
foi removido. Isso não dispensa revisão da estabilidade/ruído dos opamps LR4 nem
da interação com fonte/regulador e EMI Classe D.

## Captura e integração lógica reais
[Revisão integrada](../kicad/analog-protected/README.md): **32 componentes/80 pinos**,
ERC nativo **zero, sem exclusões**. Dez passivos +polaridade de D201 conferidos
contra `simulation/analog/vmid-protected.cir`;14 R/C e pinagem dos quatro amps
conferidos separadamente contra LR4/TI. Alterar o manifesto juntamente com uma
ligação errada de V+ a AUX_RAW ainda falha a auditoria independente.

U2/U3 p.8 recebem ANALOG_12V; p.4 GND. J103:1=AUX_RAW,2=VMID **monitoramento,
nunca fonte externa**,3=GND. J101 continua MONO previamente acoplado/biasado,
**não RCA direto**; J102 é sinal diferencial, **não SPK±**.
Há13 footprints não atribuídos e MPNs ainda TBD; não gerar produção desta captura.

`kicad/vmid-protected/` é desenho lógico auxiliar do mesmo bloco, **não outra
PCB nem novos conectores físicos adicionais**. Captura D-016 original e todas
as PCBs/galerias3D foram preservadas. Geradores recusam diretórios existentes.

## Limitações que continuam bloqueando o sistema
- Entrada externa ainda presente com opamps sem alimentação: proteção de TODOS
  os pinos/RCA e capacitores de sinal não está qualificada por este estudo.
- OPA pode ficar vivo depois de AUX_RAW/TPA cair: conferir INPUT_A/B/coupling e
  power-order do TPA antes de conectar J102 ao núcleo. **RESET/mute não prova
  proteção dos pinos analógicos.** Não integrar ao núcleo energizável sem revisão.
- Supervisor, pop/DC diferencial/limiter/LINE-LFE/volume e fonte T1 não concluídos.
- Curto interno no rail protegido, falha do diodo, overshoot e layout não são
  cobertos pela hipótese de caminho isolado/limites; exigem análise de falhas.
- Pico teórico de entrada≤0,927 A; energia do bulk máximo≈0,0983 J@13,2 V.
  R201 necessita verificação de curva de pulso, repetição, temperatura e derating;
  o texto TBD não é aprovação de um resistor de sinal comum.

ELEC-002/003 e gates G0–G5 continuam pendentes. **O bloqueio específico D-017
foi removido por mudança de topologia sob envelope, não por mudar tolerâncias,
silenciar contraprovas ou declarar o sistema aprovado.**

## Reprodução
```bash
make simulate-vmid-protected  # modelo TI local auditado; ngspice>=47
make analog-protected-check  # KiCad native ERC/netlist, dois audits independentes
make check
```
Circuitos/dados/logs em `build/analog/vmid-protection/`; modelo do fabricante
permanece local, nunca incluído nos commits/artifacts. Imagens PDF/SVG são
exportações nativas do KiCad em `docs/images/analog-protected/`.
