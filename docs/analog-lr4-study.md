# Front-end — incremento LR4 e budget de headroom

## Objetivo e limite

Preparação verificável de ELEC-002, não conclusão da task nem esquema integrado.
Fonte/supervisor, somador L/R, seleção LFE, potenciômetro, VMID físico, ESD,
proteção/limitação e montagem continuam ausentes do core. Não altera as PCBs
renderizadas nem libera roteamento/fabricação. D-015 é proposta reversível de estudo.

## Fontes primárias e achado de risco

- TI **SLOA024B**, jul.1999/rev.set.2002, figura5/equação9,p.4 e caso K=1,p.5.
  Sua C1 é capacitor para referência; C2 é capacitor de feedback. Neste projeto
  usamos nomes **CG/CFB** para não trocar as posições.
- TI **SLOS075K**, rev.dez.2025, p.3: alimentação recomendada ±5 a ±15 V,
  referenciada ao ponto médio; p.4: características medidas em **±15 V**.
  VICR mínimo ±12 V e GBW típico12 MHz nessa condição. Figura5-3,p.5 usa±10 V.
  **Não se pode transformar isso em limites garantidos de common-mode/swing em
  alimentação total10,8–13,2 V.** VCC=±10 V da figura significa20 V totais, não10 V.
  Modelo/licença/compatibilidade NE5532 reais ainda não qualificados.

PDFs locais e URLs/revisões/hashes: `reference/manifest.json`. Nenhum script de
fabricante executado; modelos comportamentais abaixo foram escritos no projeto.

## Circuito R/C explícito

`simulation/analog/lr4-rc.cir` contém esta cadeia de estudo:

```text
MONO AC já referido a VMID → divisor10k/10k → buffer → SK1 → SK2
                                                      ├→ POS
                                                      └→ inversor10k/10k → NEG
```

Cada Sallen-Key tem ganho unitário e:

- R1=R2=14,0 kΩ;
- CFB=2×100 nF em paralelo, do nó entre resistores até a saída;
- CG=100 nF, da entrada não inversora para VMID;
- fn=1/(2π√(R1R2 CFB CG))=**80,3854 Hz**;
- Q=√(R1R2 CFB CG)/(CG(R1+R2))=**0,707107**.

Duas seções produzem−6,0206 dB em sua fn; com esses valores,−5,9375 dB em80 Hz.
Isso elimina ganho de1,586 por seção e compensações que um SK de C iguais exige.
R±1%/C±5% são requisitos candidatos; **MPNs, dielétrico, tolerância térmica,
matching e footprints ainda TBD**. Esses valores não foram inseridos na PCB.

O divisor reduz2 Vrms a1 Vrms por perna; a diferença POS−NEG recupera ganho
unitário em baixa frequência em relação ao MONO. Os resistores do inversor
controlam equilíbrio; devem ser revisados por tolerância/offset/ganho real.
Inversão de fase0°/180° pode ser feita trocando POS/NEG, mas chave/transientes
não foram implementados ou validados. Não confundir180° relativo entre pernas
com fase absoluta do LR4, que varia com frequência.

## Contratos ainda não fechados

- MONO representa sinal **AC acoplado/biasado em VMID**, máximo candidato2 Vrms;
  fonte ideal no modelo. Somador L/R deve evitar ganho2 com entradas correlacionadas.
  Corrente/impedância do divisor e fonte RCA reais precisam de verificação.
- **LFE não passa pelo LR4**. Seu bypass precisa do mesmo gain staging candidato
  antes do conversor diferencial para não dobrar nível/clipping. Não foi simulado.
- Volume50 kΩ log permanece proposta. Se o sinal é biasado, o terminal inferior
  deve preservar VMID, não impor0 V ao wiper; a solução física depende da cadeia
  final e do budget de corrente/estabilidade de VMID. Não é conexão capturada.
- POS/NEG aqui são saídas analógicas, **não SPK±**. O core já tem acoplamentos de
  entrada; carga10 kΩ do estudo é hipótese conservadora de interface, não medição
  nem substituição da especificação da entrada do TPA3255.
- VMID é fonte ideal. NÃO há validação de sua impedância, estabilidade, ruído,
  sink/source, tolerância de referência, partida ou comportamento sem alimentação.

## Simulações executadas

`make simulate` agora também executa `scripts/simulate_analog.py`:

1. **151 pontos10 Hz–10 kHz**, magnitude **e fase** do circuito R/C com VCVS
   conferidas contra equação independente, incluindo divisor e inversor diferencial.
2. Modelo próprio de um polo: Aol=100000/GBW=12 MHz/Rout=50Ω, saída limitada
   por hipótese a3 V de cada rail. Não é macromodelo NE5532, não modela slew,
   correntes, ruído, offset/bias, tolerância térmica ou comportamento de falha.
   Efeito de ganho no sweep≤0,00778 dB nesta hipótese.
3. **16.384 combinações extremas** de14 componentes independentes:10 do LR4,
   dois do divisor e dois do inversor; resposta diferencial em80 Hz entre
   **−7,182 e−4,703 dB**. fn de cada seção entre75,800 e85,471 Hz;
   Q entre0,67256 e0,74339. Extremos discretos não provam extremo contínuo global.
4. **2048 amostras uniformes**, seed20261008; não é distribuição de fábrica nem
   yield. A janela−8 a−4 dB é critério interno **proposto para estudo**, não aprovação
   de REQ-006. Uma exigência mais estreita requer componentes/matching melhores.
5. Transiente20 Hz, entrada2 Vrms, rail10,8 V e VMID5,4 V: com divisor, pico do
   buffer≈1,4142 V relativo aVMID e0 amostras de clipping na janela final100 ms;
   bypassando divisor,≈39,9% das amostras atingem limite no modelo. Isso demonstra
   o risco da hipótese; **não prevê clipping/THD do NE5532 real**.

## Próximos fechamentos de ELEC-002

Modelo autorizado/compatível ou ensaio qualificado para headroom em rail mínimo,
VMID real e carga; incluir bias/offset, impedâncias, ganho/ruído, degrau e power-up/down.
Depois capturar somador/LINE/LFE/volume/fase com MPN/pinagem/footprint auditados,
e integrar somente após revisão de proteção e supervisor. Não marcar G1 nem Done
com base no estudo comportamental. Medidas de T1 e fit OEM continuam necessárias.

Evidência versionada: [relatório](../tests/reports/analog-lr4-study.json).
Decks/logs/vetores completos em `build/analog/`; nenhum dado de bancada inventado.
