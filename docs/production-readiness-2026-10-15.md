# Revisão de prontidão para produção — 2026-10-15

**Resultado: NÃO LIBERADA.** Revisão do working tree, não de um release aprovado.
Base Git `b2d01f67cdc5b77168b9b159e23abbed9689223d`, com alterações locais prévias
preservadas. Branch `fix/production-readiness-20261015`. Hashes e resultados em
`tests/reports/production-readiness-2026-10-15.json`; logs em `build/production-audit/`.
Este documento prevalece sobre números históricos dos resumos de desenvolvimento.
Não representa revisão completa pin-a-pin, aprovação de layout ou validação física.

## Correções realizadas e verificadas

1. **Esquema, TP127/R506:** o trecho do test point sobrepunha o divisor e juntava
   `INPUT_A_AC` a `INA_UV`; TP127.1 e R506.1 apareciam desconectados no ERC nativo.
   KCAA removeu o trecho/rótulo incorreto, deslocou TP127 para (1371,6; 109,22) mm
   e restaurou R506.1–INA_UV. Correção feita em cópia, validada e promovida sem
   mudar a PCB. Intenção elétrica conferida em `scripts/create_iso_d019.py`
   (divisor R505/R506/R507) e `scripts/create_debug_io.py` (TP127 = INPUT_A_AC).
   Gerador corrigido e dois testes de regressão adicionados. A captura regenerada
   isoladamente também apresentou ERC 0 com bibliotecas/configuração do projeto.
   Risco: alterar o monitor DC por conexão acidental; validação: ERC nativo e
   paridade PCB, ambos zerados. Não foram adicionadas exclusões de regra.
2. **Exportador de fabricação:** `make fab` agora cria diretório de rascunho único,
   registra commit completo, working tree sujo e hashes de entrada, não reutiliza
   pasta identificada apenas por commit. Erro 5 só é tolerado nos checks ERC/DRC,
   não nas exportações. `summary.json` entra no SHA256SUMS, gravado por último;
   mudança das fontes durante exportação aborta conclusão. Três testes adicionados.
   Continua sendo exportador de **rascunho**, não BOM/CPL JLCPCB qualificados.

## Estado observado após a correção

- 263 componentes no netlist; 269 footprints na PCB, incluindo itens board-only.
- 4 camadas, 3.238 segmentos de trilha e 448 vias; cobre preservado nesta revisão.
- ERC: **0** ocorrências. Paridade: **0** divergências.
- DRC: **9 conexões abertas**, **1 aviso `track_dangling` em BST_D**;
  zero violações geométricas de severidade erro não significa placa pronta.
- Nets abertas: LED_RUN_K, CLIP_OTW, FAULT (2), VBG, BST_D, BST_B,
  SPK_N_SNUB e VMID.
- `make check`: **126/127 testes passam**. Falha preexistente em
  `test_documentation_media_evidence_and_task_mirrors_are_current`: hash do
  manifesto de mídia não corresponde à evidência histórica. Não se alterou o
  checksum esperado só para passar o teste. Galeria/evidência devem ser renovadas
  em conjunto após estabilizar os arquivos.
- `make erc`/`make drc` também executados; ver logs. Esses wrappers usam o core
  histórico; não substituem os checks explícitos da candidata acima.

## Bloqueadores de engenharia — ordem de fechamento

### 1. Placement de potência antes de terminar as rotas (PCB-002)

Revisar C16–C19, C9, desacoplamentos, retornos OUT/PVDD/GND e caminhos de potência.
A revisão anterior registrou distâncias retas C16/C17/C18/C19 aos respectivos
pinos de bootstrap de 21,10/45,44/30,80/56,88 mm; C9–VBG de 28,15 mm.
Isso não é resolvido simplesmente passando uma trilha longa nas conexões abertas.
Referência: TI SLASEA8A §12.1/Fig.40, citada na task PCB-002.

Recolocar componentes com base no layout TI e restrições mecânicas, remover apenas
rotas afetadas, revisar laços e então fechar as nove aberturas. Checar largura,
estrangulamentos, vias e retorno de corrente, plano GND cortado por sinais, PWM
perto de áudio, snubber e LC. DRC/paridade por alteração e revisão visual final.
Não promover rota MCP apenas por retorno de sucesso: houve histórico de violação
de keepout pelo roteador. O cobre atual **não foi aprovado nesta revisão**.

### 2. BOM real e montagem (FAB-001/BUY-001)

82 dos 263 componentes do netlist têm MPN ausente ou contendo `TBD` (lista no
relatório JSON). Isso é contagem bruta, antes de separar DNP e itens sem compra.
Nenhum componente tem campo LCSC dedicado; alguns códigos aparecem em prosa.
MPNs não-TBD também precisam normalização: fabricante e código exato separados
não podem ser substituídos por texto como “Diodes Inc./Vishay”.

Para cada referência populada: fabricante, MPN exato, valor/tolerância/tensão/
potência/dielétrico, package e footprint auditado; código de catálogo quando
usado, montagem JLC ou manual, DNP explícito, estoque e data. Separar fusível de
porta-fusível, contatos/housings e acessórios mecânicos. Não deduzir equivalência
pelo tamanho nem tratar test point de cobre como peça comprada.

As incompatibilidades antigas MUR3040/P600, bulk Ø25/Ø30 e housing de quatro vias
não devem ser repetidas como achados atuais: a captura agora declara P600J,
footprint snap-in Ø30 e JST VH B3P. Ainda exigem qualificação final de MPN/ratings.

### 3. Mecânica e térmica (PCB-002/FAB-001)

Conferir gabarito 1:1 contra os suportes originais, alturas/folgas do perfil U,
conectores/chicotes e montagem do dissipador. Fonte local: manual PS28 Rev1 3/2007
em `reference/infinity/ps28-service-manual.pdf`, páginas impressas 14–18, conforme
`mechanical/original-board-reference.md`; medidas do proprietário prevalecem.
TPA3255 DDV tem PowerPAD **superior**: não especificar pad térmico inferior/vias
na pasta como se fosse outro encapsulamento. Documentar interface, pressão,
isolação necessária e vínculo elétrico do dissipador, sem carregar os leads.

A lista de footprints sem modelo 3D contém essencialmente test points e features
mecânicas; ausência de sólido nesses itens não é automaticamente defeito.
Não se criou modelo Blender sem necessidade dimensional demonstrada. A existência
de modelos nos demais componentes não comprova geometria ou fit.

### 4. Documentação e rastreabilidade

- Conciliar README, development-status, schematic e roadmap com D-032: o projeto
  passou a reutilizar preamp/limiter OEM; não repetir como atual o front-end ausente.
- Resolver a afirmação de PCB-001 de “stackup confirmado na cotação”: FAB-001
  registra cotação pendente. Exigir documento datado antes de assumir confirmação.
- Fechar desenho de fabricação com contorno/furos NPTH/PTH, dimensões/tolerâncias,
  espessura, sequência das quatro camadas, cobre externo/interno, máscara,
  acabamento, tratamento de vias e requisitos de montagem. Capacidade/serviço
  escolhido deve ser confirmado na cotação, não inferido de “1 oz”.
- Esquema legível por função, revisão/cartucho; assembly drawings frente/verso,
  pin 1, polaridades, DNP, peças manuais e sequência mecânica; BOM de acessórios.
- Gerbers/drill inspecionados em visualizador independente, CPL confrontado com
  a visualização de montagem do fornecedor, PDF/gabarito sem escala automática.
- Release final de árvore limpa/commit ou tag, manifesto cobrindo todos os arquivos,
  relatório ERC/DRC/paridade e lista de desvios justificados. Atualizar mídia e CI.
- Registrar G2/G3 humanos e limites de BENCH-002. Ensaios de bancada permanecem
  em BENCH-002, não são resultados fictícios nem impedem terminar o projeto.

## Requisitos JLCPCB consultados diretamente

Consulta em 2026-10-15 (UTC−03), páginas oficiais atualizadas em 2026-09-08:

- [BOM](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly):
  `Comment`, `Designator`, `Footprint`; comentário com especificação/tolerância.
  CSV/XLS/XLSX recomendados; designators tratados em maiúsculas. MPN exato e
  código LCSC são nossa exigência de rastreabilidade/seleção, não afirmar que a
  página exige campo LCSC universal para importar qualquer BOM.
- [CPL](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly):
  `Designator`, `Mid X`, `Mid Y` em **mm**, `Layer` Top/Bottom e `Rotation` em graus,
  positiva anti-horária. Centro, origem, face e orientação precisam de conferência;
  não aplicar deslocamento/espelhamento global sem validar cada encapsulamento.

O `bom.csv`/`cpl.csv` nativo atual não é entrega JLCPCB final: falta seleção de
peças/montagem e normalização dos campos. CSV aceito não comprova polaridade.
Serviço THT, dupla face, disponibilidade e preço dependem da cotação real.
Sem upload, pedido, compra ou energização nesta revisão.

## Próximo ponto de decisão

Continuar por **placement local do TPA/bootstrap**, não por fechamento cego de
rotas ou renderização. Após essa revisão, fechar conectividade, BOM/CPL e pacote.
Quantidade de placas, quantidade montada e destino de entrega só são necessários
para a cotação; não bloqueiam as correções de engenharia acima.
