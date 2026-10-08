# Galeria 3D nativa — KiCad 10

Estas imagens vêm de **`kicad-cli pcb render`**, não de desenho conceitual,
renderizador CAD alternativo ou rotação artificial de uma foto. Cada GIF contém
16 renders de câmera independentes do KiCad. Pillow somente acrescenta faixas de
status e codifica os GIFs. Saída real: PNG1264×862; GIF784×558,
16frames,140ms/frame, loop. O KiCad ajustou as dimensões solicitadas ao renderizar.

## OEM refinada — candidata de estudo

![OEM refinada — vista isométrica](oem-isometric.png)

![OEM refinada — órbita KiCad](oem-orbit.gif)

[Vista superior](oem-top.png) · [Vista inferior](oem-bottom.png)

## Revisão B — seleção de peças preservada

![Revisão B — vista isométrica](selected-isometric.png)

![Revisão B — órbita KiCad](selected-orbit.gif)

[Vista superior](selected-top.png) · [Vista inferior](selected-bottom.png)

## Limites — não omitir ao compartilhar

- As duas placas estão **sem roteamento**. Galeria não é gerber, prova de fit,
  montagem aprovada, teste térmico, nem evidência de funcionamento.
- C1/J1/J5/L1/L2 não têm modelos associados aos footprints customizados. U1
  referencia um STEP indisponível nesta instalação; por isso seu corpo não aparece.
  J6 é feature de GND, sem modelo: hole/bond na B; pad de trança sem furo na OEM.
- Os40 footprints com modelos disponíveis usam bibliotecas visuais do KiCad.
  Não são CADs específicos dos fabricantes com tolerâncias qualificadas.
- Nenhum componente fictício foi colocado para ocultar essas ausências.
- A OEM utiliza contorno inferido153×79,1mm; furação, fit e contato térmico
  permanecem não verificados. B permanece padrão de validação; OEM é estudo.

## Reprodução e rastreabilidade

```bash
python3 scripts/render_kicad_gallery.py --frames 16
```

Dependências locais: KiCad CLI e modelos de sua biblioteca, Python/Pillow e fonte
DejaVuSans. Não são instaladas automaticamente. Logs e frames brutos ficam em
`build/renders/`, fora do Git. `manifest.json` registra versão KiCad, commit-fonte,
SHA256 das PCBs/imagens, comandos e auditoria de modelos para cada footprint.
O commit-fonte antecede o commit da mídia: é a revisão elétrica/mecânica renderizada.
Ver [operacionalidade](../../functional-readiness.md) para os bloqueios do produto.
