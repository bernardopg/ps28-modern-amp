# Revisão local TPA3255 e fechamento de conectividade — 2026-10-16

**Escopo concluído em CAD:** reposicionamento/revisão dos desacoplamentos locais e
fechamento das conexões. **Não é liberação de fabricação nem sign-off G2.**
Placa: `kicad/system-candidate/system-candidate.kicad_pcb`.
Evidência com hashes, coordenadas e métricas: `tests/reports/tpa-local-layout-review.json`.

## Alterações e referência

Referência: TI TPA3255 **SLASEA8A §12.1 e Fig.40, p.33/36**, conferidas no texto e
na figura de `reference/ti/tpa3255.pdf`. Preservados valores, footprints, nets de
todos os pads, quatro OUTs PBTL, modos, INPUT_C/D, contorno e fixações OEM.
Não foi criado pad térmico inferior: o PowerPAD do DDV continua superior.

- KCAA: reposicionados C16–C19 e C2/C4–C10/C13; C8 ajustado. Os 13 componentes
  locais estão em B.Cu, sob a região do núcleo, fora das furações/suportes.
- Distância planar pad BST→pino: **C16 2,61 mm; C17 1,75 mm; C18 1,86 mm;
  C19 2,32 mm**, contra 21,10/45,44/30,80/56,88 mm anteriores. C9/VBG: **2,21 mm**,
  contra 28,15 mm. Distância planar não equivale à indutância do laço.
- Cada net BST tem uma via e 1,09–3,13 mm de trilhas em F/B. O retorno de cada
  capacitor até seu OUT correspondente foi conferido por conectividade nativa;
  limites superiores CAD, contando 1,6 mm por via: **5,63–6,48 mm**.
- C10 e C13 ficaram junto aos dois bancos PVDD. C11/C12 e os reservatórios foram
  mantidos. A montagem no verso com vias é um desvio da geometria de referência;
  aproxima os laços sem alterar a topologia, mas EMI/transientes ainda exigem ensaio.
- Acrescentados retornos GND explícitos em C4 e C10, trilha 0,4 mm e via
  Ø0,6/0,3 mm. Não foram forçadas vias onde havia conflito. Os demais retornos
  continuam pelas pours e vias GND existentes; distância planar pad GND→via
  próxima de **0,68 a 4,89 mm**. Isso não prova o percurso HF efetivo nem substitui
  a revisão global/ensaio de ruído. In1 permanece plano GND, sem trilhas de sinal.

## Rotas e alimentação

Fechadas as nove aberturas iniciais e as desconexões temporárias necessárias à
reorganização. Removidos os ramos obsoletos e o `track_dangling` BST_D.
LED_RUN_K, CLIP_OTW, FAULT, bootstrap, VBG, snubber e VMID estão conectados.
AUDIO_EN também foi fechado; sua passagem em In2 exigiu restabelecer o ramo PVDD
para o reservatório esquerdo C14/C15/J1/auxiliares.

Essa reconexão usa **1,2 mm**, aproximadamente **74 mm de trilhas** distribuídas
em F/B/In2 e quatro vias Ø0,6/0,3 mm, não um jumper fino. O grupo principal de
retificação/bulk à direita e os bancos de alimentação do TPA já permaneciam
conectados entre si. Queda, compartilhamento de ripple e aquecimento desse ramo
esquerdo devem ser verificados na revisão global/bring-up; especialmente se J1
for usado como entrada de bancada. Não se declara capacidade de corrente só
pela largura nem se autoriza ensaio com carga por este registro.

## Integridade e validação

- **269 footprints, 3.531 segmentos, 499 vias.**
- **`make erc`: 0. `make drc`: 0 violações, 0 aberturas, 0 divergências de paridade.**
- **`make check`: 131 testes aprovados**, incluindo regressões de placement,
  despacho dos checks, Fab, galeria e rastreabilidade da evidência atual.
- Regras/exclusões preservadas; nenhuma regra relaxada para obter o resultado.
- Novas furações de vias conferidas contra terras SMD: nenhuma via-in-pad nova.
- Todos os componentes fora do grupo local mantiveram posição, face e pads;
  todos os valores e nets dos pads foram preservados, incluindo U1.1–44.
- Referências Fab reorganizadas após o placement, sem modificar cobre.
- `make erc/drc` agora verifica a candidata de sistema por padrão, não o núcleo
  histórico. `--design` permite selecionar uma referência explicitamente.
- Cartucho atualizado para `ROUTED ENGINEERING CANDIDATE - NOT RELEASED FOR FABRICATION`.
- Galeria nativa atualizada junto com a evidência; o relatório histórico de
  2026-10-08 foi preservado e aponta para a evidência atual de mídia.

O KCAA foi usado para placement/remoções e recarga da PCB. O roteador MCP não
conseguiu fechar todos os caminhos; houve fallback nativo KiCad em cópia isolada,
com aceitação somente após DRC/paridade completos. Foram corrigidos courtyards
que o flip do MCP havia deixado na face errada. Tentativas com curto, perda de
continuidade do plano ou via em pad não foram promovidas.

**Ainda pendentes:** revisão global de potência/EMI/térmica e fit/G2, seleção e
qualificação da BOM, CPL JLCPCB com as novas faces/rotações, revisão dos arquivos
fabris e G3 do proprietário. Nenhuma compra, pedido ou energização realizada.
