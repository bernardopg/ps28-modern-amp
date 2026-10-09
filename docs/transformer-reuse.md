# D-009/D-010 — Transformador original: reaproveitamento selecionado

**Atualização D-021 (2026-10-09):** alvo regulado 36 V substituído por PVDD não
regulado via retificação CT de dois diodos; seções abaixo sobre buck 36 V são históricas.

## Recomendação

D-010: reaproveitar T1 original e projetar fonte nova no domínio secundário,
com alvo PVDD regulado em 36 V e auxiliar 12 V; fonte externa só bancada/fallback.
O proprietário informou transformador e capacitores saudáveis e capacidade técnica
para realizar medições, conexões e testes. Aceitar esse relato como entrada, não como
medição de VAC/VA/ripple. A escolha está feita; componentes e limites dependem dos ensaios.
Não conectar a fonte simétrica original diretamente ao TPA3255. Esta é uma
recomendação de arquitetura, não aprovação de segurança nem circuito fechado.

## Evidência do dispositivo original

Manual entregue pelo proprietário: PS28 SERVICE MANUAL, Rev1 3/2007.
As páginas abaixo são a numeração impressa; o índice físico do PDF é uma página maior.

- p.16: T1, part number 150-e8604107-e, EI-86, 60 Hz, 120 V, TT0869906580.
- p.24, schematic folha 3/3, A/1, 2006-07-27: T1 TT0869906580-E, secundário com
  tomada central, D110 KBL405, rails +Vcc/-Vcc e C121/C122 6800 µF/50 V.
  Primário tem fusível T2.5AL/250 V e chave. Identidade física ainda requer foto/etiqueta.
- p.2: modelo 120 V Classe AB, faixa de rede declarada 108–132 V, 60 Hz;
  carga nominal de ensaio 4 Ω, DCR de referência 4,35 Ω; p.9 pede 4,4 Ω ±10%.
- p.1 anuncia 150 W RMS; p.2 especifica rated output 100 W, THD 0,5%, e
  highest RMS 152 W como referência. Não transformar esses números distintos
  em garantia de 150 W contínuos do transformador ou woofer.
- p.3: consumo 195 W nominal em ensaio de 100 W/4 Ω. Consumo da rede NÃO é
  potência VA do secundário; tamanho EI-86 também não determina capacidade sozinho.
- p.10 e p.22: high-pass e limiter originais. Sua remoção pode aumentar excursão;
  adaptar suas funções deve ser analisado antes de elevar potência disponível.

## Confirmação física pelo proprietário (2026-10-09)

Fotos da unidade (mantidas fora do Git) e relato do proprietário:

- Etiqueta de T1: `TT0869906580-E`, `150-e8604107-e`, TRANSTEC, "BUILT IN THERMAL
  FUSE"; mesma identidade do manual p.16/p.24. O relato digitado "160-…" diverge
  da foto, que mostra "150-…"; vale a foto.
- Primário com 2 fios; secundário com 3 fios (dois vermelhos, um preto),
  consistente com o secundário CT do manual. Que o preto seja a tomada central é
  hipótese até medir continuidade/tensão.
- Painel: rede `120V~60Hz 200 Watts`, fusível `T2.5AL 250V`, chave On/Off e LED POWER.
  Controles do painel: LEVEL, CROSSOVER contínuo 50–150 Hz, PHASE 0°/180° (chave),
  entradas RCA LFE/L/R. Resolvido por D-022: crossover ajustável 50–150 Hz.
- Placa original: bulk 6800 µF/50 V e relé GOODSKY UDH-SS-124D (bobina 24 V).

Medições do proprietário, multímetro de bancada, aparelho desligado (2026-10-09):

- Rede local nominal 127 V (manual p.2 declara faixa 108–132 V para o modelo 120 V).
- Bulk original após desligamento: 0,53 V DC (escala 20 V); abaixo de 1 V para manuseio.
- Secundário desconectado da placa, escala 200 Ω, **sem descontar resistência das pontas**:
  vermelho–vermelho 1,2 Ω; preto–vermelho 0,8 Ω em cada lado.
- Leitura: metades simétricas e preto consistente com CT. Se o preto fosse CT e as
  pontas tivessem resistência zero, vermelho–vermelho deveria dar 1,6 Ω. A diferença
  é coerente com cerca de 0,4 Ω de pontas, ou seja, cerca de 0,4 Ω por meia-bobina.
  Isso é inferência; confirmar medindo as pontas em curto. Resolução de 0,1 Ω limita
  qualquer cálculo de regulação/VA a partir desses valores.
- Pontas em curto medidas depois (mesmo multímetro, 200 Ω): 0,6 Ω. Corrigido:
  ≈0,2 Ω por metade e ≈0,6 Ω total; diferença de 0,2 Ω entre soma e total cabe na
  resolução/contato. Valores baixos demais para estimar regulação com confiança.

Secundário sem carga, desconectado da placa, rede medida 126,6 VAC no mesmo
ensaio, multímetro V AC escala 200 (2026-10-09):

- vermelho–vermelho 69,1–69,3 VAC; preto–vermelho 34,3–34,4 VAC em cada metade.
  Confirma CT no fio preto e metades simétricas (34,35 + 34,35 ≈ 69,2).
- Cálculo (não medição): pico por metade 34,4 × √2 ≈ 48,6 V; com ~0,8–1 V de diodo,
  ≈ 47,7 V DC a vazio. Razão medida 34,35/126,6 = 0,2713 VAC/V; em rede 133 V
  (limite superior adequado ANEEL para 127 V, a confirmar no PRODIST) a metade dá
  ≈ 36,1 VAC e o rail ≈ 50,1 V a vazio: margem ≈ 3,4 V para 53,5 V.
  O rail cai sob carga (resistência ≈0,2 Ω por metade, ripple e regulação do núcleo).
- Retificação full-wave CT com dois diodos gera um rail único positivo ≈ 44–50 V,
  dentro de PVDD 18–53,5 V (SLASEA8A p.6, §7.3), com margem pequena a vazio/rede alta.
- Os 6800 µF/50 V originais não servem nesse rail (pico ≈ 50 V); C14/C15 63 V sim.
- O "34-0-34 VAC" antigo do starter coincide com esta medição; seguia sem fonte até aqui.

Continuam sem medição: VAC por meia-bobina e total, regulação sob carga, VA e
tensão da rede local. Essas evidências não alteram D-010 nem aprovam gate algum.

**O manual não informa tensão VAC do secundário, corrente nominal ou potência VA.**
A afirmação antiga de 34-0-34 VAC no starter não tem comprovação neste documento.

## Compatibilidade elétrica

TI SLASEA8A p.6, §7.3: PVDD 18–53,5 V em carga 4 Ω; VDD/GVDD 10,8–13,2 V.
O máximo absoluto PVDD 69 V, p.5, NÃO é uma tensão de projeto/operação.
O TPA3255 requer PVDD positivo e GND, não alimentação simétrica ±Vcc.
Nunca confundir GND/CT com rail negativo nem aplicar tensão entre +Vcc e -Vcc ao CI.

Estimativa para capacitor após retificação: Vp ≈ VAC por meia-bobina × √2,
menos perdas de diodos; ripple, rede alta e regulação a vazio alteram o envelope.
Exemplo HIPOTÉTICO, não medição do T1: 34-0-34 VAC produz aproximadamente
47–48 V por rail e 95–96 V entre extremos DC, antes das perdas. O último excede
inclusive o máximo absoluto do CI; o primeiro ainda exige análise de rede alta/a vazio.
Capacitores antigos de 50 V não comprovam a tensão de operação nem sua saúde atual.

## Caminho preferido se o transformador passar

T1 existente → retificação full-wave apropriada ao secundário CT → bulk/proteção →
DC/DC de potência regulado 36 V → TPA3255; auxiliar 12 V dimensionado separadamente.
Esse diagrama não especifica ligações, diodos, capacitância, MPN ou layout.
Não usar o secundário completo por conveniência nem reaproveitar só um rail sem
analisar aproveitamento das bobinas, correntes pulsadas e aquecimento.

Um buck só serve se o vale de tensão sob carga superar 36 V mais sua margem de
regulação. Se não superar, reconsiderar rail/arquitetura: não pressupor que buck eleva tensão.
Definir Vin máximo com rede alta, vazio e transientes; analisar falha de pass-through,
ripple/EMI, corrente de partida, dissipação, capacitores, fusíveis e proteção de sobretensão.
Um módulo barato rotulado "300 W" não equivale a 150 W contínuos neste conjunto.

## Gate antes da seleção final (PWR-001/BENCH-001)

- Técnico qualificado verifica isolamento, fiação, proteção/fusível, fixação e estado de T1.
- Documentar tensão por meia-bobina e total, regulação a vazio/sob carga, envelope
  de rede e ripple DC; confirmar capacidade térmica para carga e duração pretendidas.
- Dimensionar transformador pela demanda de DC + perdas de CI/DC-DC + auxiliares,
  fator de utilização e correntes RMS não senoidais do retificador; não só watts de áudio.
- Não ligar primário 120 V em rede 220 V, não aumentar fusível para mascarar falha,
  não remover proteção de isolamento/terra de instrumentos. Sem ensaio energizado
  informal com gabinete aberto; plano/instrumentação e responsável são obrigatórios.
- Comparar custo total da fonte secundária nova com SMPS externa certificada.
  Já possuir T1 não garante economia após retificação, DC/DC, proteção e retrabalho.

**Status:** D-010 seleciona reaproveitamento; não houve medição, compra, ligação
ou energização pelo agente. Ratings dos capacitores de 50 V precisam ser verificados
contra pico/ripple/temperatura do novo uso; saúde não autoriza sobretensão.
Não paralelar/reconfigurar C121/C122 automaticamente. Confirmar topologia e polaridades.
Se o envelope medido inviabilizar regulação buck de 36 V ou potência/térmica alvo,
registrar ajuste de projeto com evidência; não forçar a arquitetura fora dos ratings.
