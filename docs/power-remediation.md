# Potência — alternativas primárias e budgets de remediação

Proposta de engenharia; não sign-off, compra, fabricação ou energização.
A candidata roteada anterior foi preservada. Nova captura:
`kicad/power-researched/power-researched.kicad_pro`.

## Componentes pesquisados

**D301/D302: onsemi RHRP1560**, candidato elétrico em lugar do MUR3040WTG
reprovado. RHRP1560/D Oct-2017 Rev.3, páginas impressas 1–2 (PDF páginas 2–3):
600 V, 15 A com Tc=140 °C, IFSM=200 A para meia onda de 60 Hz. TO-220AC,
flange é catodo: **ligada ao PVDD, nunca tratar como GND/chassi**.
O datasheet contém desenho funcional e máximos, não qualifica automaticamente
footprint, corrente contínua no conjunto ou dissipador. MPN inserido como
candidato; footprint permanece vazio até auditar desenho/numeração/isolação.
IFSM de um pulso não garante sobreviver ao envelope de partida repetitiva.
Lifecycle/estoque/preço não verificados.

**C301/C302: Nichicon LGU2A472MELC**, candidato elétrico com 4700 µF/100 V,
105 °C, ripple 4,14 A RMS a 120 Hz e endurance 3000 h nas condições do catálogo.
Fonte LGU CAT.8100M páginas 1 e 3. Envelope nominal Ø35×50 mm; reservar
conservadoramente Ø36,5×52 mm e courtyard radial de 0,5 mm além do corpo.
Desenho p.1: pitch 10 mm, dois furos Ø2±0,1 mm. Footprint local de estudo
`PS28_POWER:LGU_D35_L50_P10_Study`: pad1 positivo, pad2 negativo, sem modelo 3D
inventado. Em 2026-10-12 o proprietário informou capacitor original de 45 mm
com pouco mais de 30 mm livres até a moldura plástica. Na mesma região/plano
original de montagem, o envelope de 52 mm deixa aproximadamente 23 mm livres:
**altura local deixa de ser bloqueador do estudo**. Evidência e limites em
`../mechanical/owner-clearance-20261012.json` e `../mechanical/oem-harness-sealing.md`.
Isso não comprova ventilação nem encaixe de Ø36,5 mm ou de componentes deslocados.
Não usar essa opção grande como substituição física automática de Ø25/Ø30.

A opção LGU 4700 µF/63 V consultada não fecha o alvo 3,5 A/peça: as variantes
p.3 fornecem 2,83–2,97 A, dependendo das dimensões. A opção 100 V preserva a
capacitância/arquitetura do banco; custo/volume mudam e o fit ainda bloqueia.
Partilha de ripple entre capacitores não foi presumida igual; ESR/tolerâncias,
frequência e temperatura precisam de orçamento e posterior medida.

**J301/F301:** não escolhidos à força. Header precisa casar com o chicote
existente (três vias, CT central), não com um housing de quatro vias. Fotos do
proprietário de 2026-10-12 mostram três vias, trava e vermelho–preto–vermelho;
JST VH continua hipótese visual, não MPN confirmado. Fusível
continua T TBD: exige curva, capacidade de interrupção DC, derating do holder,
coordenação com condutores e corrente/partida no ramo CT.

## Corrente do CT — cálculo sobre simulação, não medida

`python3 scripts/analyze_power_remediation.py` refaz 54 casos ngspice D-021.
`--reuse-waveforms` aceita dados completos apenas com `.cir` idêntico ao gerador
atual; hashes de cada arquivo de dados ficam no relatório. Integração quadrática
linear por trecho, recortada na janela; teste rejeita transiente incompleto.

- `I_CT = I_DA + I_DB`: os diodos conduzem alternadamente, mas F301 conduz o
  retorno total. Usar apenas RMS de uma meia-bobina subestima sua corrente.
- Máximo no envelope: **8,014 A RMS** no CT; **7,000 A RMS** de ripple no banco.
- I²t máximo do CT nos primeiros 100 ms: **63,640 A²s**.
- Não são ratings garantidos do hardware: T1/regulação/dispersão/modelo de diodo
  e ESR continuam hipóteses do estudo. Não escolher 6,3 A ou 10 A apenas por isso.
- A opção 2×4,14 A oferece margem nominal para 7,00 A somente se a partilha for
  suficiente; não comprova distribuição de corrente real com o bulk do core.

Resultados: `tests/reports/power-remediation-budget.json`.

## OVP e inrush — proposta D-028, não capturada como circuito validado

Fonte TI LM5069 SNVS452G Jan-2020: controle de MOSFET série, limitação de corrente
/potência e turn-off por OVLO (p.1/3, §8). É funcionalmente relevante para cortar
PVDD, ao contrário de apenas desabilitar o TPA. Mas **OVLO interno sozinho foi
reprovado** para a janela requerida: p.5 dá threshold 2,4–2,6 V.

Com `Vtrip = ratio × threshold`, mesmo com resistores ideais:

- Para não cortar em 49,84 V: `ratio > 49,84/2,4 = 20,7667`.
- Para cortar até 53,5 V: `ratio <= 53,5/2,6 = 20,5769`.

Intervalo vazio; tolerância/bias/delay pioram. Não adotar divisor típico de
2,5 V como solução fechada. Via a investigar: detector de precisão comandando
desconexão série, alimentado independentemente do rail cortado, com estado
seguro quando sem alimentação. Não foi capturada conexão arbitrária entre
TPS3700 e LM5069 sem revisar corrente, lógica, limiares e sequencing.

Pré-carga controlada exige todos os capacitores cujo inrush se quer limitar
**depois** do elemento série; deixar bulk antes dele não limita a partida do
retificador/T1. Exemplo de escala, não dimensionamento: 12,4 mF a 50 V armazenam
15,5 J. Num modelo de fonte rígida/carga inicialmente nula, limite hipotético
6 A carrega em ~103 ms e inicia com ~300 W no elemento série. Energia e SOA
pulsada/térmica/repetição/falha em curto devem ser verificadas, não apenas RDS(on).
Além disso, limite precisa suportar corrente pulsante do retificador, não só
3,9 A médios do amplificador.

D-027 sem limitador continua hipótese em revisão, não prova de imunidade ao
inrush. D-026 não oferece OVP qualificada enquanto PVDD não for desconectado ou
limitado de modo comprovado. Transientes rápidos, atraso e indutâncias reais
continuam abertos mesmo com detector preciso.

## Evidência e sequência física

Nova captura ERC: **0 violações**; testes: **118 passaram**. Topologia CT,
interfaces e nets preservadas por teste. Footprint do bulk tem regressão de
pitch/drill; isso não equivale a footprint liberado para montagem.

Não foi refeito o placement/roteamento da candidata antiga: os diodos ainda
não têm footprint auditado e a proteção série muda nets/área/loops. Enviar esses
componentes ao autorrouter antes disso repetiria o erro anterior. Próximo gate
físico é decidir o conjunto retificador/dissipação + OVP/SOA + fit dos caps,
seguido de staging da integração; não é revisão cosmética da rota atual.

Referências baixadas diretamente de onsemi/Nichicon/TI, hashes e URLs em
`reference/manifest.json`. Busca web via MCP indisponível por saldo; resultados
acima vieram dos PDFs oficiais, não de anúncios de distribuidor.
