# D-009/D-010 — Transformador original: reaproveitamento selecionado

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
