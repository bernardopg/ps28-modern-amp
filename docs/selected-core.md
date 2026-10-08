# Core B — seleção, placement e revisão

## Estado e arquivos atuais
Abrir `kicad/core-selected/ps28-modern.kicad_pro`. Esta revisão tem **47 componentes,
47 footprints e 142 pads elétricos conferidos**; os dois tabs de estabilidade dos
indutores são pads mecânicos sem número/net. Nenhum footprint crítico ficou vazio.
`selected-bom.csv` e `core-manifest.json` mantêm MPN, fonte e geometria. J6 é feature
GND da PCB, excluída do BOM de componentes; hardware correspondente é conjunto mecânico.

O draft anterior em kicad/ foi preservado: havia pcbnew aberto nele e IPC indisponível;
a tentativa de controle GUI via Orca não teve acesso ao bus de acessibilidade.
Não sobrescrever buffer aberto nem matar processo com possível trabalho não salvo.
`make erc`, `make drc` e `make core-check` agora apontam para core-selected.

## D-012 — Peças selecionadas para validação, não para compra/liberação
Fontes primárias arquivadas em reference/parts, com URLs/hash em reference/manifest.json.
- **L1/L2: Wurth 7443631000**, 10 µH ±15%, Ir 16 A (ΔT50 K), Isat10% 22 A
  **típico**, DCR máximo 8,76 mΩ, corpo máximo 21,8 × 21,5 × 14,5 mm.
  Datasheet rev006.000/2025-07-08 p.1. Footprint local HCF2013 com pads 5×5 mm,
  pitch elétrico 9 mm; tab oposto sem net, exclusivamente estabilidade mecânica.
  A classe D do fixture IEC descrito nesse PDF NÃO certifica uso em amplificador Classe D.
  Core loss/THD/temperatura e curto/OCP continuam exigindo validação. Não usar Ir como
  capacidade demonstrada da nossa PCB nem Isat típico como limite garantido.
- **C22/C23/C26/C27: WIMA MKP2D034701M00JSSD**, polipropileno 470 nF/100 V/5%,
  pitch5 mm, L7,2/W8,5/H14 mm. Catálogo MKP2 03.26 p.38–39, inclui sufixos J/S/SD.
  Mantidos dois 470 nF por ramo da figura31; não misturado com quatro filtros da EVM.
- **C14/C15: Nichicon UHE1J152MHD**, 1500 µF/63 V, D18/P7,5/H40 mm nominal,
  Hmáx42 mm, Zmáx36mΩ a100kHz/20°C, ripple2470mA a100kHz/105°C;
  coeficiente0,8 a120Hz =1976mA por peça. Endurance10000h a105°C para este case/voltage,
  com DC+ripple dentro do rating; UHE CAT.8100M p.1/6. Low-impedance e vida melhores
  que a seleção preliminar NHG ECA1JHG222 (2000h/lifecycle incerto), agora descartada.
  Não alegar ripple2470mA a120Hz nem vida comprovada na caixa. Verificar soma ponderada
  das correntes por frequência, compartilhamento, ESR a quente e tensão do respiro.
  Banco3000µF entra na estabilidade/inrush da fonte D-010; lifecycle/estoque não confirmados.
  Não são C121/C122 originais; os 6800µF/50V originais continuam no estudo da fonte.
- **C1: Wurth 860020575014**, 470 µF/35 V, D10/H16+1,5/P5 mm, hole0,9 mm,
  ripple520mA/120Hz, WCAP-ATG5 rev1.0 p.1. Auxiliar12 V, não PVDD36 V.
- **J1/J5: Wurth 691137710002**, WR-TBL1377, **pitch5,00 mm, não5,08**,
  hole1,3 mm, corpo10×7,5×11,5 mm; 16 A UL/24 A VDE conforme condições do fabricante,
  rev001.003 p.1–2. Footprint local; não substituído por Phoenix5,08 parecido.
- **J6:** ponto GND com holeM3/3,2 mm na própria PCB, para ligação do adaptador/dissipador.
  Conjunto proposto M3×8 ISO4762, arruelasM3 ISO7089, porca/terminal olhal; não são
  coordenadas de furo original. Fixação estrutural da PCB/plate é distinta e pendente.
- **Demais capacitores/headers:** MPNs da tabela8 SLOU441 p.14–16, package compatível.
  C3/C20/C21 são10µF16V X5R0805, C8 é0402, C24/C28 C0G1206, snubbers0603;
  atualizados de verdade no schematic/PCB, não só no CSV. C3 ainda requer verificação de
  capacitância efetiva em12 V e bypass/transientes; MPN selecionado não encerra esse check.
- **Resistores:** Vishay CRCW1%, driver/snubber1206 0,25W; demais0603 0,1W,
  construção de código/ratings no doc20035. Dissipação real dos snubbers pendente.
- **J4 mudou para PEC04DAAN/2×4** da EVM: pinos1=3V3 externo,2=RESET,
  3=FAULT,4=CLIP_OTW,5/6=GND,7/8=NC. Não usar pinagem antiga1×5.

Nenhum preço, estoque, autenticidade/lifecycle ou equivalência de reposição foi inventado.

## Envelope elétrico calculado (não medida)
Dimensionamento resistivo150W/4Ω: Irms=6,124A, pico=8,660A por indutor, não metade.
Com36V, fPWM mínimo430kHz e Lmín8,5µH, ripple triangular máximo aproximado
36/(4×430k×8,5µ)=2,462App; pico estimado9,892A. Margem perante22A típico não
substitui curva a quente/garantias nem análise de curto/OCP. DCR a20°C dá aproximadamente
0,329W por indutor para a fundamental, excluindo core loss/AC/resistência a quente.
LC nominal10µH/940nF por lado: frequência natural≈51,9 kHz; não é crossover LR4.
**Correção dimensional:** o valor anterior1642Hz estava errado. fn=1/(2π√(LC)).
No modelo diferencial balanceado, Ldiff=20µH e Cdiff=470nF; mesma fn e
Q≈0,613 para carga resistiva4Ω, ignorando DCR. `simulation/output-lc-ideal.cir`
confere a resposta linear com DCR20°C; não modela comutação, perdas de núcleo,
impedância do woofer ou estabilidade física do TPA3255.
150W é envelope de dimensionamento, NÃO potência aprovada para woofer/fonte.
Bulk novo armazena aproximadamente1,94J a36V; limites de descarga/inrush permanecem.

## Placement refinado e revisão de regras
Indutores alinhados aos loops de saída, filme próximo ao LC, bulk separado do analógico,
J1 alimentação/J5 saída/J6 bond distintos. L2 girado180° com reversão dos pins1/2
DO INDUTOR NÃO ACOPLADO no schematic também; OUT_B/D e SPK_N não foram trocados.
Corrigidos conflito de silkC20/bulk, courtyard de C1 por tolerância de diâmetro, paridade
BOM de J6 e nome de camada de footprint. `Rescue` não é camada válida: teste captura isso.

ERC bruto: **4 pin_to_pin**, todos revisados/classificados:
1. OUT_A39/40: pads duplicados da mesma saída física, intencionalmente unidos.
2. OUT_D27/28: idem.
3. OUT_C32/OUT_A39: paralelamento PBTL exigido pela figura31.
4. OUT_B35/OUT_D28: paralelamento PBTL exigido pela figura31.
M1=GND/M2=DVDD e INPUT_C/D=GND conferidos contra tabela11. Não alterados tipos dos
outputs nem matriz global para esconder conflitos. As quatro falsas faltas de fonteBST
foram resolvidas com hints PWR_FLAG explícitos da alimentação bootstrap interna, sem
introduzir fonte externa ou parte física. **Nenhuma exclusão dos quatro conflitos aplicada**;
exceções específicas/revisão independente exigidas para freeze, não ERC geral relaxado.

DRC/paridade atual: **zero violações geométricas, zero divergências de paridade,
109 conexões não roteadas**. O aumento85→109 decorre dos 12 footprints que faltavam
agora presentes e do header expandido. Não são defeitos resolvidos por desativar checagem:
**não houve roteamento e DRC global continua reprovado**. Revisão feita, fabricação não.
Logs e exports em build/core-selected, resumo em tests/reports/core-selected-review.json.

## D-013 — Integrar ao gabinete/plate/dissipador originais
Escolhido adaptador de cobre no PowerPAD superior ligado ao dissipador metálico original,
com braço elevado para não tocar SMDs, apoio/fixação reagindo no suporte e GND viaJ6.
Preservar vedação acústica e barreiras do primário. Não confundir caixa com dissipador.
Modelo de envelopes: mechanical/ps28-core-envelope.scad; não é STEP fiel dos componentes.
Modelo paramétrico/dados faltantes: mechanical/ps28-original-integration.json.

Orçamento EXEMPLO: ambiente45°C, Pd25W, alvoTj100°C, Rjc(top)0,36°C/W TI p.6.
Cobrek400, sapata3,8×6,6 e pedestal4,8mm:0,478°C/W; braço20×10/span20mm:0,25°C/W.
TIM25µm/k3 noCI:0,332°C/W; contato400mm² no dissipador:0,021°C/W.
Com dissipador original0,7°C/W, modelo prevê≈98,5°C. **Hipóteses, não temperatura
comprovada nem rating do dissipador original.** Usar a equação para derating se o sink real
não atender; pressão, TIM, span e folgas ainda exigem projeto/medidas reais.

**D-014 / correção da referência:** usar a placa original e os mesmos mounting points
/sistema de dissipação OEM. O manual p.15–16 documenta plate300×200×2,5,
carcaça198×298×102, dissipadores117,5×71,5×25 e65×32×31 e suportes; p.17–18
traz os desenhos da main PCB104-a05064a00-e. A afirmação anterior de que só havia
cotas externas do gabinete estava incompleta. Sem entrecentros/escala1:1 declarados,
reconstruir gabarito com escala verificada, não inventar furação nem modificar o plate.
[Referência original](../mechanical/original-board-reference.md) e
[conferência final](../mechanical/measurement-request.md). Contorno145×95, posição deU1
/J6 e adaptador de cobre são estudos, não interfaces OEM garantidas; adaptar o PCB ao OEM.
Maior peça42mm + respiro proposto5mm exige47mm locais; carcaça102mm não prova essa folga.
G0–G5 permanecem pendentes; não fabricar, comprar ou energizar.
