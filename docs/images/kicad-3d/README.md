# Galeria 3D nativa — KiCad 10

Atualizada em **2026-10-16**, após a revisão local TPA e fechamento das conexões.
Imagens de **`kicad-cli pcb render`**; cada GIF contém 16 renders independentes de
câmera. Pillow apenas acrescenta faixas de estado e codifica os GIFs. Não são
imagens conceituais nem rotação artificial de uma fotografia.

## Placa única atual — candidata de sistema

![Candidata integrada — vista isométrica](system-isometric.png)

![Candidata integrada — órbita KiCad](system-orbit.gif)

[Vista superior](system-top.png) · [Vista inferior](system-bottom.png)

`kicad/system-candidate/`: contorno OEM medido **154 × 81 mm**, **269 footprints**,
fonte/analógico protegido/sequenciador/isolamento integrados, interfaces com o
preamp/limiter OEM (D-032). Não há bancos de importação fora do contorno.
Bootstrap e desacoplamentos locais foram reposicionados; o cobre está conectado.
**ERC 0, DRC 0, aberturas 0, paridade 0** — isso não equivale a aprovação G2/G3.
[Revisão e limites](../../tpa-local-layout-review.md).
O modelo do bloco foi corrigido para os furos OEM a 23,65 mm e para a posição
mundial em H5; [fit nominal, cortes e orçamento térmico](../../../mechanical/thermal-block.md).
Não representa fit físico ou dissipação medidos.

## OEM refinada — estudo histórico do núcleo

![Núcleo OEM histórico — vista isométrica](oem-isometric.png)

![Núcleo OEM histórico — órbita KiCad](oem-orbit.gif)

[Vista superior](oem-top.png) · [Vista inferior](oem-bottom.png)

## Revisão B — seleção histórica do núcleo

![Núcleo B histórico — vista isométrica](selected-isometric.png)

![Núcleo B histórico — órbita KiCad](selected-orbit.gif)

[Vista superior](selected-top.png) · [Vista inferior](selected-bottom.png)

B/OEM são referências históricas separadas, não três produtos a fabricar. Não
possuem a integração e o roteamento da candidata atual. A captura separada
`kicad/analog-protected/` continua como referência de 32 componentes/80 pinos;
seus 13 footprints pendentes não significam ausência desses blocos na candidata.

## Limites ao compartilhar

- Render não é Gerber, aprovação de montagem, fit, térmica, EMI ou funcionamento.
- Na candidata, os itens sem modelo são test points e features H6/J6;
  a lista exata está no manifesto. B/OEM históricos também não mostram os corpos
  de C1/J1/J5/J6/L1/L2/U1 por ausência de modelos associados/disponíveis.
- Corpos disponíveis podem ser modelos genéricos/envelopes de estudo. A presença
  visual não qualifica tolerâncias, acesso, dissipação nem contato do PowerPAD.
- Não foram adicionados componentes fictícios para preencher ausências.
- Fixações, placa original e dissipação OEM são interfaces preservadas, não
  autorização para cortar gabinete ou mudar suportes. Fit final ainda exige gabarito.
- BOM/CPL devem refletir as novas faces e rotações. Produção continua não liberada.

## Reprodução e rastreabilidade

```bash
make render-3d
```

Requer KiCad CLI/modelos, Python/Pillow e DejaVuSans já instalados; não instala
nada automaticamente. Logs e frames brutos ficam em `build/renders/`.
`manifest.json` registra hashes das PCBs, imagens, gerador, comandos e auditoria
por footprint, incluindo hashes dos arquivos 3D efetivamente disponíveis.
O contexto distingue referências históricas da candidata atual
verificada e recusa rotular uma PCB cujo hash difere da evidência nativa.

Publicação em staging com manifesto por último; uma falha não publica sucesso.
A anotação dos renders não modifica a geometria da PCB. O commit-fonte pode
anteceder o commit das imagens; os hashes, e não apenas o nome do commit, vinculam
esta árvore de trabalho aos renders.

Evidência atual: `tests/reports/tpa-local-layout-review.json`. O registro de
2026-10-08 em `tests/reports/documentation-media-refresh.json` permanece histórico,
com seus hashes originais e um apontamento explícito para a evidência atual.
