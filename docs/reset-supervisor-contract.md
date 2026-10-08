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
- **SAFE:** RESET baixo por padrão, inclusive sem3V3 de controle. R9 do core já
  garante safe-low. Não inferir rail válido só pela existência de tensão.
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

## Testes futuros obrigatórios
Fonte faltante/em ordem invertida; VMID fora de faixa; FAULT inicial normal;
FAULT persistente; FAULT seguido de RESET baixo sem autorrearme; OTW ativo ao
rearmar; brownout breve/lento; power-down; chaveamento de fase/volume; falha da
própria3V3. Conferir SPK diferencial/pop em carga artificial com limites aprovados.
Esses testes não foram executados nesta etapa. G0–G5 continuam pendentes.
