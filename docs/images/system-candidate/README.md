# Candidata integrada — esquema e referências de mídia

Atualização: **2026-10-16**. Uma PCB principal, `kicad/system-candidate/`, com
269 footprints e conectividade fechada. ERC/DRC/paridade/aberturas 0 não são G1/G2/G3.
D-032 reaproveita preamp/limiter OEM; os estudos anteriores não descrevem a candidata atual.

- [Esquema nativo SVG atual](system-candidate.svg), exportado do `.kicad_sch`
  integrado. O cartucho herdado da captura não define o estado de liberação;
  a fonte de estado é [development-status.md](../../development-status.md).
- [Galeria nativa atual](../kicad-3d/README.md): isométrica, topo, base e órbita
  de `system-*`; sem bancos fora do contorno. Modelos genéricos/ausentes constam
  no [manifesto](../kicad-3d/manifest.json); render não valida fit físico.
- [Núcleo com CAD Würth](core-with-vendor-cad.png): **histórico de 2026-10-08**,
  anterior à integração. Não é a placa de produto nem imagem atual da candidata.
- Modelos Würth CC BY-SA 4.0: [atribuição](../../../kicad/models/vendor-wurth/README.md).

Regenerar em diretório isolado e conferir antes de promover:

```sh
kicad-cli sch export svg --output build/system-svg/ kicad/system-candidate/system-candidate.kicad_sch
make render-3d
```

Hashes atuais em `tests/reports/tpa-local-layout-review.json` e
`docs/images/kicad-3d/manifest.json`. O antigo `system-candidate-review.json`
é evidência de snapshot histórico, não de liberação atual.
