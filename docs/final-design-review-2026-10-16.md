# Revisão final solicitada — 2026-10-16

**Roteamento completo; desenvolvimento ainda não concluído para fabricação.**
Foi revisada a candidata única `kicad/system-candidate/`, preservando todo o cobre,
placement, contorno, furação e valores elétricos. Snapshot em `build/finalization/snapshot/`.

## Entregas desta revisão

- Blender MCP conectado, Blender 5.2.2 LTS/addon 1.8 compatíveis. Geometria real
  KiCad importada por GLB, sem componentes inventados. Cycles, materiais de máscara,
  metais e polímeros, quatro softboxes, AgX e denoise. Três vistas em
  [pcb-studio](images/pcb-studio/README.md); cena editável em `build/studio/ps28-studio.blend`.
- KCAA conferiu inventário/netlist e corrigiu MPNs; paridade nativa obrigatória após
  sincronização dos campos no esquema e PCB. IPC do KiCad retornou connection refused;
  não se tomou isso como falha de instalação. Nenhuma edição de cobre foi necessária.
- Gerbers, Excellon PTH/NPTH, esquema PDF, CPL/BOM nativos, montagem frente/verso
  (verso espelhado), quatro camadas de cobre, DXF em mm, gabarito e desenho cotado
  1:1 com seis fixações, datum e barra de aferição de 50 mm. `make fab` continua
  gerando rascunhos locais com checksum; o desenho não inventa tolerâncias fabris.
- Auditoria reproduzível `python3 scripts/audit_final_design.py`:
  **263 componentes no esquema, 269 footprints, nenhum componente do esquema
  faltando na PCB**. Seis itens adicionais H1–H6 são de fixação. DNP explícitos:
  J3, J4, R7, R8. Ausência de componente em relação ao esquema não comprova que
  todos os requisitos de circuito foram atendidos.
- Inventário atual completo em [CSV](../bom/system-candidate-inventory.csv), incluindo
  **235 posições de compra e 190 com MPN não normalizado ou fabricante ausente**.
  Essa contagem é mais abrangente que os 82 TBD antigos: texto genérico em MPN
  e falta de fabricante também são identificados. Não são 190 peças ausentes na PCB.

## Correções verificadas

| Referência | Problema | Correção |
|---|---|---|
| C14/C15 | Valor/footprint 680 µF/Ø12,5 mm, MPN antigo 1500 µF/Ø18 mm | Nichicon UHE1J681MHD, preservando a decisão D-031 |
| J5 | Header JST VH, MPN/fabricante do antigo borne Würth | JST B2P-VH(LF)(SN) |
| R101/R102 | Footprint 0805, MPN 0603 | CRCW08051K00FKEA / CRCW0805100KFKEA |
| R310 | Valor 100 kΩ com código Susumu de outro valor | RT0603BRD07100KL, mantendo o valor elétrico |

O integrador aplicava o swap de footprint/valor sem transferir o MPN ao esquema;
corrigido e testado com geração isolada. Geradores do preamp e fonte corrigidos.
MPN, fabricante e campos ocultos não alteram topologia; não se regenerou sobre
o roteamento. C14/C15 continuam totalizando 1360 µF: com C301/C302 são **10,76 mF**,
conforme D-031, sem repetir a alegação antiga de 3000 µF nesses dois capacitores.

Fontes: [Nichicon UHE CAT.8100M](https://www.nichicon.co.jp/english/series_items/catalog_pdf/e-uhe.pdf),
[JST VH](https://www.jst.com/wp-content/uploads/2021/08/eVH-new.pdf),
[Vishay D/CRCW e3 doc.20035](https://www.vishay.com/docs/20035/dcrcwe3.pdf),
[Yageo RT V.17](https://yageogroup.com/content/datasheet/asset/file/PYU-RT_1-TO-0-01_ROHS_L).
Essas fontes qualificam identidade/encapsulamento; não comprovam estoque nem montagem.

## Software instalado e conferências independentes

KiCad 10.0.7, bibliotecas oficiais, ngspice 47, Blender e addon MCP já estavam
disponíveis. Não foi necessária instalação global, atualização do sistema ou
outro plugin de roteamento. O TokenSave não tinha índice neste projeto; a
inspeção foi feita diretamente, sem criar índice incidental.

Instalado **Gerbonara 1.6.3**, Apache-2.0, em `build/validation-venv`, via uv/PyPI.
O ambiente usa Python 3.13 isolado; não modifica o Python do sistema. Reproduzir:

```sh
uv venv build/validation-venv
uv pip install --python build/validation-venv/bin/python -r scripts/validation-requirements.txt
build/validation-venv/bin/python scripts/verify_gerbers.py build/fab/drafts/PASTA
make render-studio
```

O [parser independente](https://gerbolyze.gitlab.io/gerbonara/) reconheceu quatro
camadas de cobre, outline 154,05 × 81,05 mm incluindo traço de 0,05 mm, **591 objetos
PTH e 5 NPTH**. SVGs de frente/verso e relatório ficam junto ao pacote.
Três avisos preservados: G90 após cabeçalho em ambos os Excellon e parâmetros
sobrando na macro `RoundRect`. Não foram tratados como falha elétrica nem ignorados
silenciosamente. A leitura não substitui DFM/inspeção de montagem do fornecedor.

O exportador GLB também registrou autointerferência de fio em uma pequena face,
z=1,585 mm, x=134,278…134,400/y=86,903…87,824 mm. O render é apresentação, não
geometria metrológica liberada. Logs em `build/studio/export.log` e `render.log`
incluem avisos de áudio do Blender e depreciação `use_nodes` para Blender 6.
O KiCad também avisa que a API Python SWIG será removida futuramente; a migração
para IPC fica necessária quando a versão deixar de oferecer essa API, não por
reinstalação das bibliotecas atuais. Um rerender intermediário terminou com sinal
143 antes da última vista, sem evidência de OOM no journal consultado; a galeria
final usa 32 amostras/denoise e staging, com manifesto publicado após as três vistas.

## O que continua necessário para concluir

1. Qualificar e normalizar os 190 registros indicados no CSV, incluindo MPN
   exato, fabricante, ratings, package e seleção de montagem; conferir peças
   hoje descritas em prosa, mesmo quando já mencionam um código candidato.
2. Completar BOM de acessórios (fusível/porta-fusível, housings/crimps, jumpers,
   trança e ferragens), serviço manual/THT, códigos de fornecedor e disponibilidade.
   CPL nativo ainda precisa revisão de centro/face/rotação por encapsulamento.
3. Revisão global de potência/retornos/EMI e G1/G2: DRC não avalia capacidade
   de corrente. PVDD contém ramais de 0,2/0,3/0,6 mm além do ramo de 1,2 mm;
   SPK_P inclui ramal de 0,2 mm. Sem rastrear qual corrente passa em cada ramal,
   essas larguras não são aprovadas nem automaticamente condenadas.
4. Desenho de fabricação com stackup/cobre/tolerâncias/acabamento/vias acordados
   com o fabricante, revisão DFM e pacote liberado por commit/tag após G3.
5. Gabarito físico, folgas/contato térmico e bancada controlada continuam em
   BENCH-002. Não são substituídos por Blender, FreeCAD, KiBot ou outro MCP.

O [roteiro de produção](production-roadmap.md) e os gates humanos permanecem
válidos. Não houve compra, upload, pedido, energização ou aprovação G1/G2/G3.
Evidência atual: `tests/reports/final-design-review-2026-10-16.json`.
