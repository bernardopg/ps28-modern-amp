# Primeiro incremento EDA — núcleo PBTL

**Histórico A:** a revisão atual B está em [selected-core.md](selected-core.md),
`kicad/core-selected/`. Contagens/pendências abaixo são o snapshot anterior, não o estado atual.

## Conteúdo real

`kicad/ps28-modern.kicad_sch`: 47 componentes; U1 com 44 pinos, modo e bypasses,
bootstrap, LC/snubber da figura 31 e interfaces de alimentação/áudio/controle/woofer.
`kicad/ps28-modern.kicad_pcb`: 35 footprints em placement preliminar, quatro camadas,
sem trilhas, vias ou pours. Contorno 145 × 95 mm é somente envelope de estudo,
não deriva de medições do plate. 12 footprints deliberadamente não selecionados:
C1/C14/C15 (bulk), C22/C23/C26/C27 (filtro/dielétrico), L1/L2, J1/J5/J6.
Não converter reservas em footprints de fabricação por aproximação.

## D-011 — Baseline selecionado para estudo

TI SLASEA8A §10.2.4, figura31/tabela11, p.28; p.3–4 pinout/tabela de modos.

- M1=GND, M2=DVDD interno; INPUT_C/D=GND; OSC_IOM/IOP sem conexão no master.
- OUT_A(39,40)+OUT_C(32) → PWM_AC → L1 → SPK_P.
- OUT_B(35)+OUT_D(27,28) → PWM_BD → L2 → SPK_N.
- Dois indutores 10 µH; por lado dois 470 nF, 1 nF e 10 nF/3,3 Ω conforme figura.
- OC_ADJ=22 kΩ/FREQ_ADJ=30 kΩ conforme figura; revisar limitação corrente/frequência
  para carga real antes de freeze. Bulk 470 µF da figura é ponto de partida, não aprovação.
- Pin2 VDD: acrescentado 10 µF além dos bypasses da figura, conforme requisito p.4.
- Pull-ups FAULT/CLIP_OTW em 3V3 externo; RESET com pull-down 10 kΩ, default ativo.
  Sequenciamento/mute e geração de 3V3 externos ainda faltam; header não é controlador.
- Áudio diferencial entra por J3 com AC coupling de 10 µF; front-end/fase/LR4 ainda faltam.

O core recebe PVDD (36 V regulado no draft; D-021 passou a ≈42–50 V não regulado) e 12 V, nunca AC ou ±Vcc original. D-010 da fonte
permanece válida, mas seu circuito não está nesta PCB. Estudo modular permite desenvolver
núcleo sem inventar tensão/VA do transformador. Nenhum alvo de potência foi demonstrado.

## Correção crítica de encapsulamento

SLASEA8A p.3–4 e desenho DDV0044D: **PowerPAD superior** deve tocar dissipador
aterrado. Footprint oficial escolhido: `Package_SO:HTSSOP-44_6.1x14mm_P0.635mm_TopEP4.14x7.01mm`.
São 44 pads de solda; não há pad inferior 45. Não usar footprints bottom-EP nem matriz
de vias/pasta central como receita térmica desse CI. J6 representa ligação GND do
conjunto dissipador, ainda sem fixação/pad físico aprovado.
A reserva desenhada em Dwgs.User NÃO é um keepout DRC nem um dissipador final.
Capacitores próximos/sob dissipador exigem altura/relief/isolamento/folga reais: capacitores
1206 altos podem interferir no contato ou tocar metal. Rever antes de roteamento/fabricação.

## Verificação executada

- Netlist XML exportado de schematic real e usado para atribuir nets dos pads.
- `python3 scripts/check_core.py`: conectividade de 47 componentes e 116 pads
  dos 35 footprints confere; verifica PBTL, speaker flutuante, modo e TopEP.
- `make check`: 11 testes; inclui regressão que detecta SPK_N aterrado e footprint errado.
- ERC: **8 erros não suprimidos** — quatro fontes bootstrap não inferíveis pelo ERC
  e quatro conflitos entre outputs unidos intencionalmente pelo PBTL. Sem warnings off-grid.
  Não relaxado globalmente; justificar/excluir pontualmente somente após revisão independente.
- DRC/paridade: zero violações geométricas reportadas no placement atual, **85 conexões
  não roteadas e 12 footprints ausentes**. Nenhum erro escondido; DRC NÃO aprovado.
  IDs de biblioteca e campos schematic↔PCB sincronizados para os 35 footprints existentes.
- SVG/PDF/imagens e logs em `build/core-draft/`; ERC/DRC completos em `build/`.
- Warnings internos PROPERTY_ENUM da instalação KiCad continuam conhecidos (TOOL-001).

## Próximo trabalho

Selecionar magnetics/filtro/bulk/conectores por ratings e MPN, fazer fit e dissipador,
refinar placement, revisar circuito/gates, então rotear loops/PVDD/GND/LC. Front-end,
fonte D-010, proteção de DC/limiter/high-pass e sequencing precisam de tarefas próprias.

Geradores `create_core_draft.py`/`place_core_draft.py` são ferramentas de inicialização:
`--apply` recusa arquivos EDA não vazios. Saída default em build/ não sobrescreve
trabalho roteado. Continuar alterações no KiCad; não regenerar por cima de edições manuais.
Gate G1/G2 e fabricação permanecem PENDENTES.
