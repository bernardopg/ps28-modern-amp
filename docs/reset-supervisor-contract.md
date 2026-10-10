# Contrato RESET/FAULT — preparação do supervisor, não circuito implementado

## Achado crítico

**Não conectar RESET como simples AND de power-good e FAULT.**
TI SLASEA8A Rev.A (out.2016), §9.4.1.8,p.21: RESET baixo força FAULT alto,
apagando a informação externa de falha. §11.2/figura32,p.30: após liberar RESET,
FAULT normalmente fica baixo enquanto AVDD sobe; depois ocorre pré-carga dos
capacitores de entrada e ramp-up. A lógica combinacional ingênua pode oscilar
na partida ou tentar rearme repetido de uma falha real.

O mesmo §9.4.1.8 exige que a borda de subida de RESET ocorra **não antes de4 ms**
após a borda de descida de FAULT. Isso não é tempo máximo garantido de startup,
nem duração suficiente para resfriar o conjunto. §9.4.1.7,p.20 recomenda não
liberar RESET em sobretemperatura; conferir CLIP_OTW alto antes de rearme.
§11.3,p.31 recomenda RESET baixo no power-down para minimizar artefatos.

## Estados propostos, sem MCU

A futura implementação deve usar supervisão, memória de falha e temporização
analógica/lógica discreta. Estes nomes especificam comportamento, não firmware
ou componentes escolhidos:

- **SAFE:** RESET baixo por padrão, inclusive sem3V3 de controle. R9 legado10 kΩ **não** garante VIL≤0,8 V com fuga100 µA (§7.5p8).
  D-020 usa4,7 kΩ só na candidata; driver/backfeed/rampas seguem pendentes. Não inferir rail válido só pela existência de tensão.
- **STARTING:** somente liberar RESET após rails/VMID estáveis e autorização;
  permitir a assinatura normal de FAULT baixo inicial, por janela derivada do
  startup real. Timeout ou perda de rail levam a estado seguro. A janela é TBD.
- **RUN:** alimentação e bias válidos, startup concluído; FAULT baixo de operação
  causa latch e RESET baixo. Ruído/debounce deverão ser dimensionados sem
  ocultar proteção real. CLIP_OTW é combinado clipping/aviso térmico: não tratá-lo
  como identificação exclusiva de temperatura nem desligar por qualquer clip.
- **FAULT_LATCHED:** manter RESET baixo mesmo que FAULT volte alto por ação do
  próprio RESET. Sem repetição automática. Rearme humano/controlado somente com
  rails/VMID válidos, CLIP_OTW alto e intervalo≥4 ms desde último FAULT descendente.
  Falhas persistentes exigem diagnóstico; não aumentar limite de corrente.

## Bloqueios de captura e ensaio

- Limiares/histerese, tolerância, ripple e velocidade de perda de PVDD/12V/3V3/VMID:
  TBD; dimensionar conforme fontes reais e thresholds TI, não escolher por estética.
- Janela de blanking/timeout baseada em C_START, AVDD, pré-carga e ramp-up:
  TBD; verificar extremos e waveform antes de definir números.
- Memória de falha retida durante RESET; comportamento de brownout/unplug/replug,
  descarga de bulk, contato de volume/fase e retorno do controle: ainda não capturados.
- Não usar AVDD/DVDD como fonte genérica do supervisor, nem realimentar rails por
  pull-ups quando CI/fonte estão desligados.3V3 externa no J4 permanece interface.
- Não há simulação real do supervisor, ERC desse bloco ou sign-off de proteção DC.

## VMID e proteção dos pinos — D-017

[Estudo físico de VMID](vmid-buffer-study.md): o RC de referência pode manter
REF acima de V++0,5 V quando AUX cai. RESET baixo não evita injeção nos pinos
analógicos nem backfeed pelo driver/VMID. Qualificar descarga/clamp/corrente e
fonte ausente antes de integrar. Assentamento calculado/modelado com AUX já
válido≈0,33 s NÃO define timeout do supervisor nem comprova power-on real.
Fonte, tolerâncias e comportamento de todas as entradas no power-down continuam
bloqueios; não assumir diodos internos como proteção de sistema.

D-018 substitui o buffer por bias passivo/rail protegido ([estudo](vmid-protection.md)).
Supervisor deve verificar AUX_RAW E ANALOG_12V/VMID; não assumir que a reserva
elimina pop ou protege INPUT_A/B do TPA enquanto o preamp ainda está vivo.
J102 não pode ser ligado ao núcleo energizável antes da revisão de todos os
pinos/coupling e power-order. Não reutilizar timeout≈0,33s da candidata anterior.

## Interface de saída — contrato preparatório D-019

[Contraprovas e requisitos](input-power-order-study.md): INPUT_X tem limite
absoluto −0,3…7 V relativo a GND, diferente do OPA1656. A pré-carga da Fig.32
não pode ser substituída por reconectar capacitores com áudio já ativo.
Supervisor precisa comandar isolamento **depois** de C20/C21 e mute analógico
real, controlar a placa isolada sem aterrar o pino TPA conectado e observar DC
válido dos dois ramos antes de áudio. Implementação/MPNs/defaults/latências TBD.
Os 100 µs e janela DC 2…5 V do contrato são requisitos propostos, não resultados
de bancada ou garantias TI. Os 145,19 ms do equivalente de partida NÃO são
timeout de produto; FAULT alto não comprova pré-carga concluída. O input RIN
20 kΩ típico não garante retorno quando desligado. Nenhuma integração liberada.

## Incremento D-020 — especificação, não circuito

TI §11.2p30 recomenda RESET baixo≥250 ms apósPVDD. Timer300 ms típico com
mínimo180 ms não atende; contrato executável usa mínimo360 ms e observações
explícitas. FAULT/CLIP_OTW têm pull-ups internos20…32 kΩ aDVDD (§7.5p8):
R7/R8 podem realimentar controle morto. Não unir nova3V3 automaticamente.
Supervisor/mute/proteção físicos ainda não capturados; latência100 µs não provada.
Ver [sequência e pesquisa](integration-protection-review.md).

## Incremento D-023 — subconjunto capturado

Hold, partida humana, arme/latch de FAULT, timeout e janelas de rails estão
capturados em `kicad/seq-d020/` e integrados na candidata. Detalhes, limites e o
que continua aberto: [seq-d020.md](seq-d020.md). Os itens de D-019 acima seguem
como bloqueio.

## Testes futuros obrigatórios

Fonte faltante/em ordem invertida; VMID fora de faixa; FAULT inicial normal;
FAULT persistente; FAULT seguido de RESET baixo sem autorrearme; OTW ativo ao
rearmar; brownout breve/lento; power-down; chaveamento de fase/volume; falha da
própria3V3. Conferir SPK diferencial/pop em carga artificial com limites aprovados.
Esses testes não foram executados nesta etapa. G0–G5 continuam pendentes.
