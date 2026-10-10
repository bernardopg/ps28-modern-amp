# Core + D-018 + D-021 + D-020 — candidata de revisão INCOMPLETA

Abrir `system-candidate.kicad_pro`. **Não energizar/fabricar.** Não é substituta
aprovada de B/OEM. `system-manifest.json` registra 204 componentes/footprints (+4 furos M3 board-only),
580 pinos elétricos casados netlist↔PCB, sem footprints vazios nessa candidata.

- PCB-001 (2026-10-10): contorno OEM medido 154 × 81, furos M3 e área do perfil U;
  placement de estudo de todos os componentes; DRC só silkscreen; 470 sem rota.
- D-024/D-024a: banco `iso` (relé K501, série 3,3k + clamp BAT54, mute U503, janelas DC/AUX). Ponte
  DIFF_POS/NEG→DIFF_P/N **fechada só via K501**: C20/C21.2 = INA_ISO/INB_ISO (COM),
  U1.5/6 no NO. J3 DNP. Ver `docs/iso-d019.md`.

- D-023 (2026-10-09): bancos `power` (retificador T1, bulk, LM5164, TPS3700) e
  `seq` (sequenciador discreto) à direita do contorno, sem placement/fit.
  `PVDD_36V` agora é `PVDD`; J4/R7/R8 DNP. Ver `docs/seq-d020.md` e
  `docs/power-d021.md`. Itens abaixo descrevem a base D-020.

- Núcleo OEM refinado + 29 componentes analógicos/alimentação, GND e AUX_RAW
  compartilhados; todos os amps em ANALOG_12V, VMID passivo. Schematics anteriores
  permanecem intactos. J101/J102/J103 eram interfaces lógicas de estudos separados:
  removidos, não transformados em três novos conectores na placa OEM.
- (Base D-020, superado por D-024) **Ponte de sinal aberta:** DIFF_POS/NEG NÃO ligam DIFF_P/N do TPA. Falta proteção,
  mute físico, supervisor, RCA/soma/LINE-LFE/volume/fase/limiter/DC/fonte integrada.
  MONO_BIASED é porto de entrada de estudo, não RCA direta protegida.
- Os 29 footprints novos estão em **banco de importação fora do contorno**,
  separados entre si; não é placement concluído nem prova de caber no OEM.
  Mounts/reservas/contorno originais não alterados; nada foi roteado.
- R9 candidata4,7k1% (CRCW06034K70FKEA) substitui10k só nesta revisão: análise de
  fuga100µA TPA +10µA driver dá0,52217V <VIL0,8V. Isso não qualifica rampas,
  backfeed ou controlador externo arbitrário. Ver D-020.
- C101–106: MKP2D031001F00JSSD; C203: MKP2C041001N00JSSD, filmePP.
  Footprints nominais compatíveis; tolerâncias de corpo/courtyard/fit pendentes.
- R201: AC03000001509JAC00, axial15Ω5%, candidato de triagem: pulso repetitivo,
  conformação dos leads e tolerância total NÃO qualificados sob D-018.
- R202/203: TNPW12061K00BEEA/TNPW12062K20BEEA, footprint local derivado da
  recomendação Vishay28950; derating/térmica/drift devem fechar envelope.
- CADs oficiais CC Würth para C1/L1/L2/C201/C202; pads preservados e tabHCF semnet.
  J1/J5 STEP direto baixado localmente, mas registroXYZ/redistribuição pendentes.
  U1 DDV44 disponível por gateway autorizado TI/UltraLibrarian, não baixado.
  J6 pad/trança não tem corpo CAD de peça comprada. Demais modelos são genéricos.

Gerador `scripts/integrate_candidate.py --output <novo-diretório>` recusa overwrite
antes de qualquer mutação; staging é promovido só após captura/importação completas.
Não instalar libs/configs globais. Um escritor EDA; preservar buffers/histórico.

Fontes/achados/sequência: [D-020](../../docs/integration-protection-review.md).
G0–G5 continuam pendentes. ERC/DRC/simulação/IA não aprovam hardware.
