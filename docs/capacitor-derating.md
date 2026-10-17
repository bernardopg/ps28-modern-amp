# Derating dos capacitores — SYS-002 / D-036

Revisão de projeto2026-10-17,48 posições auditadas em
[bom/system-candidate-capacitor-derating.csv](../bom/system-candidate-capacitor-derating.csv).
**Seleção e orçamento calculados; nenhuma medida de bancada ou aprovação de fabricação.**
Não usar “50% da tensão” como substituto de curva de capacitância, ESR ou ripple.

## C401 e C403: problemas corrigidos

TI LP2985 SLVS522S, Rev.S maio/2025, §5.3 e§7.1.2: chip legado exige
CIN≥1 µF e COUT≥2,2 µF efetivos ao longo da temperatura, capacitância de saída
próxima ao CI e ESR estável. Chip novo permite COUT≥1 µF e ESR0–1 Ω.
`LP2985-33DBVR` pode conter chip legado ou novo; a seleção atende ambos, sem
presumir versão pela string do pedido. As Fig.5-36–38 e texto permitem cerâmica
com ESR a partir de5 mΩ para o legado, dentro da região estável.

| Posição | Antes | Correção / confirmação |
|---|---|---|
| C401 | GRM188R71E105KA12D,1 µF/25 V0603, cerca26 mm do U401; curva dá apenas0,320 µF a12 V e10 mVrms/25 °C. | **GRM21BR61H106KE43L,10 µF/50 V±10%,X5R0805**. Reposicionado para(123,25;72,875) mm, cerca6,41 mm do U401, com ramal AUX local e retorno ao via GND existente. A13,25 V/10 mVrms:2,086/2,398/2,747 µF típicos a−20/25/70 °C. Orçamento conservador **1,3518 µF**, acima de1 µF. |
| C403 | GRM188Z71C225KE43D,2,2 µF/16 V reais, mas Value dizia10 V; cerca1,94 µF típicos a3,52 V/1 Vrms já abaixo dos2,2 µF do legado antes das tolerâncias. | **GRM188R61E106MA73D,10 µF/25 V±20%,X5R0603**; Value e MPN corrigidos em BOM/esquema/PCB/gerador. A3,5 V/10 mVrms:4,317/4,988/4,978 µF típicos a−20/25/70 °C. Orçamento **2,4867 µF**, acima de2,2 µF. Distância geométrica ao U401≈6,85 mm. |

Cálculo de orçamento: menor amostra de temperatura/bias/AC × tolerância inferior
(0,9 C401;0,8 C403) × **0,8 reserva de envelhecimento** × **0,9 reserva de
modelo/dispersão típica**. A temperatura já está na curva: não aplicar novamente
±15% às duas linhas. As reservas são decisões conservadoras de engenharia,
**não limites estatísticos garantidos pelo fabricante nem promessa de vida útil**.
Capacitância de alta constante dielétrica envelhece; reflow pode recuperá-la e
reiniciar o envelhecimento. Conferir lote/curva atual e resposta transitória na bancada.
X5R é especificado até85 °C: este projeto interrompe em70 °C no case, preservando15 K.
SEQ_3V3 tem orçamento contínuo10 mA; perda do LP2985 a12,5 V≈92 mW.
O ensaio transitório até50 mA não autoriza carga contínua de50 mA: conferir
Tj com o encapsulamento/layout e interromper em110 °C.

A ESR típica mínima de C403 isolado é≈3,42 mΩ perto de1 MHz; portanto não seria
correto alegar ≥5 mΩ somente pela peça. O caminho obrigatório na PCB, da ilha de
C403 até o primeiro nó compartilhado em(130,35;68,375), contém≈4,912 mm de trilha
0,20 mm. Mesmo com cobre externo de70 µm e resistividade de cobre a−20 °C,
R≈5,1 mΩ **antes** da ESR do capacitor e do restante do caminho. Com a ESR típica
há margem para o piso de5 mΩ; a100 kHz a peça tem≈10,1 mΩ. O teto1 Ω do chip novo
não é excedido no intervalo de controle relevante pela ESR+conexão calculada.
**Não encurtar esse ramal, engrossar cobre acima70 µm ou substituir o capacitor
sem refazer essa verificação.** Ruído, estabilidade e degraus0–50 mA (≤50 ms,duty≤10%,10 mA contínuos) em toda a
faixa térmica continuam critérios de BENCH-002; modelo típico não substitui teste.

## PVDD: tensão, capacidade e corrente são verificações distintas

Envelope de trabalho **53,5 V incluindo ripple/picos**, limite superior de ensaio
que não pode ser alcançado/ultrapassado. OVP bloqueia áudio, não desconecta o
banco do retificador. TVS não autoriza PVDD sustentado acima desse envelope.

| Grupo | Tensão / utilização | Resultado de seleção e limite de validação |
|---|---|---|
| C301/C302,4700 µF/63 V Rubycon USC | 53,5/63=84,9% | Duas peças30×30 mm,85 °C/3000 h,3,49 Arms/120 Hz por peça no datasheet. Limite de projeto≤80% da corrente nominal: **2,792 Arms/120 Hz por peça**. Não somar correntes nominais sem verificar partilha e espectro. |
| C14/C15,680 µF/63 V Nichicon UHE | 84,9% | 1280 mArms a100 kHz/105 °C; fator120 Hz=0,75 para390–1000 µF, logo **0,960 A nominais/120 Hz**, teto de projeto0,768 Arms. Não tratar1280 mA como especificação120 Hz. |
| C10–C13,1 µF/100 V X7R | 53,5% | Murata:≈0,46076 µF típicos a53,5 V/25 °C/10 mVrms. Orçamento≈0,2538 µF por peça após tolerância/temp/idade/modelo; **≈1,015 µF no conjunto**, distribuído nos pinos PVDD conforme EVM. Não são4 µF efetivos garantidos. |
| C310/C311,2,2 µF/100 V X7R | 53,5% | TDK mostra perda≈60% por bias. Retenção0,38 conservadora lida no gráfico e fatores0,9×0,85×0,8×0,9: **≈0,4605 µF por peça**, par≈0,921 µF. São os nominais do exemplo TI LM5164; funcionalidade conferida pelo cálculo abaixo, não por exigir4,4 µF efetivos. |

Banco nominal total=2×4700+2×680=**10,760 mF**; mínimo de fabricação−20%=8,608 mF;
orçamento após mais20% de perda de capacidade ao fim da vida=**6,8864 mF**.
A100 W, eficiência85% e8 W reservados aos auxiliares/controles, corrente média PVDD
a42 V≈2,992 A.
ΔV≈I/(120C)≈**3,62 Vpp** a60 Hz de rede; a50 Hz≈4,35 Vpp. Isso é estimativa
capacitiva, sem ESR, regulação de T1 nem ângulo de condução; teto de aceitação5 Vpp
precisa ser medido. A simulação histórica de power-d021 com10 mF não prova o
pior caso envelhecido deste banco. 150 W é burst15% duty, não extrapolação contínua.

Ripple do banco depende da impedância de T1, diodos, ESR e tempo de recarga.
Não há medida que confirme a corrente RMS real nesta máquina. Para cada peça,
validar soma espectral `sqrt(sum((I_f/I_rated_f)^2)) ≤0,8`, usando fatores de
frequência do fabricante, e case<70 °C. Essa pendência é ensaio BENCH-002;
**tensão e seleção conferidas não significam vida útil/ripple aprovados**.

## Buck e auxiliares

- LM5164 SNVSAU4D,§7.2.2.4: exemplo12 V/300 kHz/ΔIL≈0,447 A pede COUT>3 µF
  efetivos para60 mV de ripple capacitivo. C315/C316,22 µF/25 V X7R, perdem cerca
  70% a13,2 V; leitura conservadora de28% de retenção dá **3,393 µF por peça**
  com tolerância10%,temperatura15%,idade20%,modelo10%. Par≈6,786 µF, acima dos3 µF.
  ΔV triangular estimado≈27,4 mV a300 kHz; ESR/injeção COT e demais capacitores
  precisam do ensaio, aceitação total AUX≤120 mVpp. A fonte de curva TMK325B7226KM-PR
  é da mesma raiz elétrica do HT selecionado; embalagem/lifecycle ainda são revisão
  de fornecimento, não prova de equivalência automática a qualquer novo código.
- §7.2.2.5/Eq.23: CIN≈IOUT×D×(1−D)/(f×ΔVIN−IOUT×ESR). Com0,5 A,12,5 V,
  VIN42–53,5 V,D0,234–0,298,f mínimo assumido250 kHz e CIN0,921 µF,
  ripple capacitivo máximo≈0,455 Vpp; reservar≤0,6 Vpp local incluindo ESR.
  A frequência mínima e a estabilidade são critérios de bancada; o nominal do
  exemplo é≈300 kHz. **Exceção de engenharia D-036:** TI recomenda tensão nominal
  2×VINmáx por causa do coeficiente de tensão;100 V não é2×53,5 V (seriam107 V).
  Mantêm-se100 V, com46,5 V de margem de tensão, porque a perda de capacitância
  foi contabilizada pela curva e a necessidade funcional foi calculada pela Eq.23.
  Não declarar margem2× nem4,4 µF efetivos. Se a bancada não cumprir250 kHz/0,6 Vpp
  ou o envelope de entrada aumentar, substituir por maior capacitância/tensão e
  refazer curvas/DFM. Não confirmar o buck só porque os MPNs são os do EVM.
- C1/C201/C202,470 µF/35 V:13,2 V=37,7% da tensão; WCAP-ATG5 especifica
  520 mA/120 Hz, limite de projeto416 mArms por peça; mínimo novo376 µF,
  orçamento envelhecido300,8 µF. Espectro/temperatura ainda devem ser medidos.
- C3,10 µF/16 V: utilização82,5% a13,2 V; **não contar10 µF efetivos**.
  Bypass paralelo aC1, sem requisito isolado de10 µF para estabilidade do LP2985;
  C401 agora atende esse requisito local. Troca para código16 V diferente exige
  curva de bias; orçamento funcional do buck usa C315/C316.
- C603,120 µF/63 V, NRAW negativo:53,5 V=84,9%; positivo noGND. UHE408 mA
  a100 kHz×0,70 a120 Hz=285,6 mA nominais; teto228,5 mArms. Orçamento76,8 µF
  com tolerância e envelhecimento. A30 mA de carga assumida, ripple≈3,26 Vpp
  a120 Hz; ainda há headroom para−15 V, a confirmar na carga real do preamp OEM.
- C601/C604,10 µF/25 V em±15 V: envelope16 V=64%, cerâmica não polarizada;
  não alegar10 µF efetivos. São desacopladores de reguladores discretos, sem
  requisito de capacitância mínima de LDO; regularidade/ruído sob carga em BENCH-002.
- Bootstrap C16–C19 vê diferença **BST−OUT≈12 V**, não todo PVDD de modo comum.
  25 V cobre envelope13,2 V. Murata dá≈31,45 nF a12 V/25 °C/1 Vrms, compatível
  com33 nF nominais do EVM. C312 BST−SW vê VCC do buck≈5 V, não53,5 V.
- C6/C7/C9 são desacoplamentos de reguladores internos, nunca fontes genéricas.
  Envelope conservador8,5 V/16 V=53,1% (AVDD típico7,75 V, não7 V);
  perto de8,5 V a peça nominal1 µF dá≈0,469 µF
  típica; não converter requisito nominal do EVM em alegação de1 µF efetivo.
- C22/C23/C26/C27,filme PP470 nF/100 V: tolerância5%, sem perda de capacidade
  DC de MLCC, mas SPK± têm modo comum; usar53,5 V para seleção. C24/C28 C0G
  e C25/C29 de snubber também100 V. Corrente AC/PWM, perdas e temperatura devem
  ser conferidas; tensão nominal DC não é rating ilimitado de ripple/AC.

## Fontes e reprodução

Amostras mínimas, URLs, condições e SHA-256 dos dados de origem em
[tests/fixtures/capacitor-characteristics.json](../tests/fixtures/capacitor-characteristics.json).
Dados brutos/PDFs de terceiros permanecem no cache local `build/sys002-capacitors/sources/`;
nenhum resultado de medição foi atribuído ao fabricante ou ao proprietário.

- [TI LP2985 SLVS522S](https://www.ti.com/lit/ds/symlink/lp2985.pdf),§5.3/7.1.2,Fig.5-36–38.
- [Murata SimSurfing](https://ds.murata.com/simsurfing/mlcc.html),consulta2026-10-17,
  amplitudes/temperaturas identificadas na fixture. [FAQ de bias/AC/temperatura](https://www.murata.com/support/faqs/capacitor/ceramiccapacitor/char/0050)
  e [envelhecimento](https://www.murata.com/en-global/support/faqs/capacitor/ceramiccapacitor/char/0006).
- [TI LM5164 SNVSAU4D](https://www.ti.com/lit/ds/symlink/lm5164.pdf),Rev.D fev/2026,§7.2.2.4/5.
- TDK CGA6N3X7R2A225K230AB,characterization sheet2016-01-04,p.1;
  Taiyo TMK325B7226KM-PR_SS2022-05-24,pp.1–2 (curvas típicas de fabricante).
- [Nichicon UHE CAT8100M](https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhe.pdf),
  tabelas de470–1000 µF/63 V e120 µF/63 V; [Würth860020575014](https://www.we-online.com/components/products/datasheet/860020575014.pdf),rev1.0,p.1.
- Rubycon USC,85 °C3000 h,tabelas63 V4700 µF30×30 e fatores de frequência;
  [PDF do fabricante hospedado pela DigiKey](https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/502/USC.pdf).
