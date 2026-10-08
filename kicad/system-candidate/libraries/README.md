# Biblioteca local da revisão B

- PS28.kicad_sym: símbolo 44 pinos TPA3255DDV, PowerPAD superior; TI SLASEA8A p.3–4.
- PS28.pretty/WE_HCF2013_7443631000: derivado do footprint oficial KiCad HCF2013,
  ajustado ao land pattern WE rev006.000 p.1. Pad vazio é estabilidade, NÃO GND.
- PS28.pretty/WE_860020575014: derivado do CP_Radial_D10/P5 oficial; hole0,9 mm,
  courtyard aumentado para Dmáx10,5 + margem. WCAP-ATG5 rev1.0 p.1.
- PS28.pretty/WE_WR_TBL_691137710002: desenho local a partir do PDF WE rev001.003,
  pitch5,00 mm, drill1,3, corpo10×7,5, sem substituição por variante5,08 mm.

As fontes, datas/URLs/hashes estão em ../../../reference/manifest.json.
Bibliotecas originais KiCad: CC-BY-SA4.0 com exceção para uso em projetos,
https://gitlab.com/kicad/libraries/kicad-footprints e kicad-symbols.
Preservar atribuição/licenças upstream dos derivados; nenhuma licença nova foi
atribuída automaticamente ao projeto inteiro. Os PDFs têm copyright dos fabricantes.

Modelos3D genéricos não são certificação de dimensões de MPN. Os modelos genéricos
HCF/aux que não comprovam alturas do PN foram omitidos; envelopes dimensionais em
../../../mechanical/ps28-core-envelope.scad, ainda sem render/fit verificados.
PCB/BOM NÃO liberadas. Camada nativa no KiCad: F.CrtYd, não layer Rescue.
