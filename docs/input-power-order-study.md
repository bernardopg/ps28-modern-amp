# D-019 — interface analógica: desligamento e pré-carga

## Resultado e escopo

**Não ligar J102 ao núcleo energizável ainda.** D-018 protege seu VMID sob
um envelope, mas não qualifica INPUT_A/B do TPA3255 nem sinais externos.
Esta revisão acrescenta contraprovas RC e requisitos verificáveis para a
interface; **não implementa nem aprova uma proteção física**.
Não houve mudança de schematic, PCB, mounts OEM ou arquivos de produção.
ELEC-002 continua Blocked; ELEC-003 e os gates não foram concluídos.

Interfaces conferidas nos manifestos, com hashes dos schematics preservados:

- `kicad/analog-protected/`: J102.1 DIFF_POS, .2 DIFF_NEG, .3 VMID, .4 GND.
  VMID é referência/monitor, não retorno da entrada diferencial do TPA.
- `kicad/core-selected/`: C20 de DIFF_P a INPUT_A_AC; C21 de DIFF_N a
  INPUT_B_AC, ambos 10 µF nominais. O mapeamento POS→P/NEG→N é **somente
  proposta de integração**, não uma conexão já realizada.
- Esta conferência é de manifestos; não substitui os audits KiCad nativos.
  As quatro ocorrências ERC e as 109 conexões não roteadas do core permanecem.

## Evidência primária — não misturar ratings

TI **SLASEA8A**, Rev. A, outubro de 2016:

- §7.1, p.5: INPUT_X admite **−0,3…7 V em relação a GND** como limite
  absoluto. Não é VDD+0,5 V nem a faixa de entrada do OPA1656.
- §7.5, p.6: RIN **20 kΩ típico**, AVDD **7,75 V típico** e corrente de
  entrada máxima **1 mA**, sob as condições energizadas da tabela.
  **1 mA não é autorização de corrente por clamp interno durante power-off**
  nem dispensa o limite de tensão. A tabela não fornece o equivalente de
  entrada desligada. AVDD/2=3,875 V abaixo é uma hipótese, não bias garantido.
- §11.2, Fig.32, p.30: RESET liberado habilita AVDD; existe fase de pré-carga
  dos capacitores de entrada antes da rampa de saída. A indicação de 200 ms
  da figura não fornece um máximo qualificado para esta nova interface.
  Não inferir daí o circuito/impedância de entrada em RESET ou desligado.
- §11.3, p.31: RESET baixo no desligamento reduz artefatos; não promete
  proteção dos pinos analógicos. A ausência de sequência obrigatória entre
  supplies do CI não libera qualquer sequência de um pré-amplificador externo.

OPA1656: TI **SBOS901C**, setembro de 2022, §6.3 p.4: supply recomendado
mínimo 4,5 V. O proxy não é um macro autorizado, e a janela energizada não
qualifica operação/headroom do componente nos extremos de produção.

URLs/hashes das fontes estão em `simulation/analog/input-power-order.json`,
`reference/manifest.json` e no relatório. PDFs de terceiros permanecem locais,
sem redistribuição. Falharam uma tentativa de URL TI inexistente e uma consulta
ADI por timeout; nenhuma especificação foi deduzida desses acessos.

## Hipóteses RC executáveis e contraprovas

Equivalente explícito de **um** ramo: driver ideal → C de acoplamento →
R série opcional → entrada com retorno resistivo a um bias hipotético.
Não contém macro de OPA/TPA, clamp interno, bootstrap, proteção DC, PWM,
capacitância parasita nem indutância de layout. Não prediz corrente real de
injeção, dano efetivo ou pop no woofer. A mesma vulnerabilidade de modo comum
pode existir nos dois ramos; isso não prova uma resposta diferencial na saída.

Com `τ=(RIN+RS)C` e `k=RIN/(RIN+RS)`, o equivalente obedece:

```text
dv/dt + v/τ = k·d(driver)/dt + (1−k)·d(bias)/dt + bias/τ
```

Após a queda do bias para zero, `v0=k·bias_inicial·exp(−delay/τ)`.
Para uma queda linear de driver durante T:

```text
v(T) = v0·exp(−T/τ) + k·Δdriver·τ/T·(1−exp(−T/τ))
```

As **288 combinações analíticas** variam C de 1/10/12 µF, retorno de
10/20/40 kΩ, RS de 0/1 kΩ, bias inicial de 0/3,875 V, atraso de 0/100 ms e
queda de 1 µs/2/20/100 ms. **196 violam o limite de tensão neste equivalente**.
Esses valores são hipóteses de sensibilidade, não envelopes garantidos de
MPNs ou do TPA desligado. O driver cai de 5 a 2,25 V: interpretado como
VMID de uma alimentação de 10 a 4,5 V, nunca extrapola operação energizada
abaixo de 4,5 V. Ainda assim, isso **não caracteriza** a saída real do OPA.

Contraprovas obrigatórias:

- C=10 µF/RIN=20 kΩ, bias 3,875 V perdido 100 ms antes e driver caindo
  5→2,25 V em 30 ms: **−0,53076 V** na entrada, abaixo de −0,3 V.
- Adicionar RS=1 kΩ, bias já zero e queda em 20 ms: **−2,49820 V**.
  Reduzir corrente com resistor não equivale a manter a tensão admissível.
- Uma chave **antes** do capacitor, sem garantir o estado da sua placa
  esquerda quando desenergizada, não resolve: se essa placa for forçada de
  5 V a GND com a entrada inicialmente em zero, o equivalente recebe **−5 V**.
  É hipótese de clamp da chave, não previsão de um componente escolhido.
- Mesmo com chave ideal **depois** do capacitor e sua placa direita antes
  descarregada a GND, reconectar com áudio ativo no pico pode falhar durante
  a pré-carga: **−2,22354 V** no equivalente de partida.
- Manter o driver sem áudio até uma **observação ideal** de DC≥2 V evita
  essa contraprova: 0…4,88275 V. Nesse caso específico a observação ocorre em
  **145,19 ms**, não constitui timeout de produto, garantia TI ou medida.

Quatro redes passivas ngspice independentes da solução analítica verificam
175.022 pontos cada; maior divergência **<1 µV**, com critério numérico de
2 mV preservado. `simulation/analog/input-coupling.cir` é uma contraprova
passiva, **não modelo autorizado de comportamento desligado do TPA**.
Duas redes adicionais reutilizam **sem alterar** a alimentação passiva D-018
(12 V raw/queda em 100 µs, carga envelopada), com driver proxy seguindo VMID
e o mesmo retorno TPA **hipotético**. Cada uma verifica 45.025 pontos contra
integração independente. Avaliar a entrada somente com ANALOG_12V≥4,5 V:

- bias de entrada já zero: mínimo **−2,09043 V**, com rail analógico ainda
  em **4,50045 V**; o próprio VMID continua dentro de −0,5…VANA+0,5 V;
- bias inicial 3,875 V perdido 100 ms antes: mínimo **−0,22950 V** nessa
  janela, sem violação nela. Não esconder esse caso menos severo nem inferir
  segurança fora da janela/hipótese.

Essa comparação liga a contraprova ao armazenamento D-018 sem inventar um
macro de amplificador desligado: seguir VMID ainda é comportamento proposto,
não caracterização real. Dados do proxy com VANA<4,5 V não são usados como
previsão de saída OPA. Ausência de caracterização impede declarar segurança;
esses números não são medição de dano na placa atual.

## Contrato proposto de isolamento — ainda sem componentes

Arquitetura em estudo, na mesma PCB OEM:

1. Uma interrupção de cada ramo **no lado TPA do capacitor**; chave precisa
   tolerar os estados energizado/desenergizado de **ambos** os terminais,
   sem backfeed. Exigir especificações de fuga e feedthrough, não apenas RON.
2. Descarga/controle da placa direita do capacitor **no lado isolado**,
   nunca curto dessa placa a GND enquanto a entrada TPA estiver conectada.
   Intertravamento/break-before-make e defaults seguros precisam ser físicos.
3. Retorno externo definido e pequena capacitância no **lado do pino TPA**
   para limitar fuga, feedthrough e injeção da chave. Valores/MPNs e o efeito
   na impedância, bias, headroom, áudio e pré-carga ainda não qualificados.
   Não usar o RIN típico desligado como garantia desse retorno.
4. Mute **analógico real do pré-amplificador**, mantendo os drivers quietos
   no bias durante conexão/pré-carga. RESET/mute do TPA não faz isso.
5. Observar a pré-carga de ambas as entradas antes de liberar áudio; não
   presumir pronto apenas porque FAULT subiu ou um timer de 200 ms venceu.

**Requisitos numéricos propostos, não medidos nem especificações de parts:**

- detecção + abertura ≤100 µs; durante esse intervalo, salto do driver ≤0,1 V
  e slew ≤1000 V/s, incluindo brownout, ESR e ações de fase/volume;
- injeção de chave ≤20 pC, capacitância off ≤5 pF, fuga ≤100 nA;
- capacitância efetiva adicionada no pino ≥4 nF e retorno externo ≤50 kΩ;
- excursão da placa isolada ≤16 V e erro antes da conexão ≤10 mV;
- com fonte ainda sem áudio, janela DC de partida proposta de **2…5 V**,
  para sinal por ramo ≤1,41421 V pico; verificar essa janela com bias real.

A soma conservadora é 0,1+0,1+0,005+0,020+0,005+0,010 = **0,240 V**.
Partindo de zero na condição de isolamento, restam **60 mV** para o limite
inferior de −0,3 V, atendendo o requisito proposto de margem ≥50 mV.
Isso é **aritmética condicional**, não uma simulação de circuito protegido.
Regressões rejeitam maior latência/fuga/feedthrough, capacitância insuficiente,
erro de pré-carga maior e relaxamento da margem/ratings. Saltos não limitados,
falha de chave, overshoot, ausência desse retorno e fonte de sinal externa
fora do envelope invalidam o contrato. Não há promessa de proteção contra
falha simples de componente nem liberação de energização.

### Triagem de chaves por fonte primária

- **TMUX721x**, TI SCDS416D, julho de 2024, §6.1 p.5/§6.4 p.6:
  S/D com ratings VSS−0,5…VDD+0,5 V e operação dentro dos rails.
  Seleção lógica/desligamento do canal não confere tolerância power-off
  independente da alimentação; **rejeitada para esse papel**.
- **TMUX7462F**, TI SCDS394B, junho de 2023, §6.1 p.4:
  source S suporta ±65 V absolutos, mas drain D tem limites
  VFN−0,7…VFP+0,7 V. Não transferir a proteção de S para D.
  A detecção com VT=0,7 V **típico**, §6.5 p.5, tampouco comprova clamp
  de entrada TPA acima de −0,3 V. **Não selecionada**; inverter S/D sem
  auditar a placa de acoplamento/rails não é solução demonstrada.

Chave, descarga, mute e comparadores/supervisor: **MPNs e footprints TBD**.
Nenhum estoque, preço ou desempenho foi inventado. Não capturar uma chave
somente porque seu nome contém “fault protected” ou “power-off”.

## Integração com supervisor e próximos bloqueios

Estados necessários ainda não implementados: isolado/descarregando → drivers
quietos/rails válidos → conexão com pré-carga → observação da janela DC dos
dois pinos → áudio. Qualquer perda de validade deve comandar isolamento e
mute analógico; memória de falha e RESET seguem o contrato já documentado.
A ordem e latência de sinais devem ser demonstradas sob abrupto desligamento,
RESET independente, FAULT mascarado, chaves de fase/volume e reconexão.
Não depender de software/MCU, AVDD como fonte externa ou contatos humanos
para atender os 100 µs propostos.

Para promover isso a proteção física: selecionar parts com limites garantidos
no envelope de temperatura/tensão, incluir defaults/inrush/backfeed e falhas,
caracterizar bias/impedância/pré-carga TPA, montar modelo completo com parasitas,
capturar/auditar o circuito e obter revisão humana G1. RCA ativa com OPA sem
alimentação é **outro bloqueio**, não resolvido por essa interface de saída.
Nenhuma compra, fabricação ou bancada energizada foi realizada/autorizada.

## Reprodução

`make simulate-input-order` ou `make simulate` executa a análise e as quatro
redes RC e duas redes acopladas D-018; requer ngspice, sem download/modelos de fabricante. `make check`
executa regressões offline. Relatório reproduzido em
`build/analog/input-power-order/result.json`; evidência revisada em
`tests/reports/input-power-order-study.json`. Logs ficam em `build/`, com
artefato de CI, sem PDFs/modelos de terceiros. Fonte primária presente é
verificada por hash; ausência local é registrada, não vira nova revisão de PDF.

## Atualização D-024 (2026-10-09)

O contrato acima foi implementado com relé Form C, mute e observação DC, e o
requisito de 100 µs foi substituído pelo limite do pino. Detalhes, simulação e o
que continua sem cobertura em [iso-d019.md](iso-d019.md). As contraprovas desta
página seguem válidas como casos que a topologia precisa evitar.
