# Candidata D-020 — mídia nativa, incompleta

- [Schematic nativo SVG](system-candidate.svg): 204 componentes na mesma captura
  (D-023/D-024: blocos D-021, D-020 e D-019 à direita); ponte de sinal só via relé;
  front-end de áudio (RCA/crossover/volume) ainda incompleto. Nets AUX_RAW/GND
  compartilhadas não significam roteamento; saída de sinal permanece aberta.
- Render 3D completo da candidata, com bancos fora do contorno:
  [galeria](../kicad-3d/README.md) (`system-*`).
- [Núcleo com CAD Würth](core-with-vendor-cad.png) (2026-10-08, anterior a D-023): render nativo KiCad, pixels
  preservados e faixa de status acrescentada. O enquadramento mostra o núcleo;
  os29 footprints analógicos estão FORA do contorno/recorte, não escondidos como
  se integrados fisicamente. Não representa layout completo nem fit OEM.
- Modelos oficiais nominal WCAP-ATG5/HCF2013 CC BY-SA4.0, atribuição/avisos em
  [kicad/models/vendor-wurth](../../../kicad/models/vendor-wurth/README.md).
  Bornes/U1 continuam sem modelos; J6 é pad de trança sem corpo comprado.
  Demais corpos genéricos não são CAD qualificados do fabricante.

Regenerar nativamente (arquivos atuais preservados antes de mutação):

```sh
kicad-cli sch export svg --output build/system-svg/ kicad/system-candidate/system-candidate.kicad_sch
kicad-cli pcb render --output build/system-native.png --width 1600 --height 1200 --perspective --rotate 325,0,25 kicad/system-candidate/system-candidate.kicad_pcb
```

Cadeia de hashes/reportes em `tests/reports/system-candidate-review.json`.
Imagens/ferramentas/regressões não aprovam fabricação, compra ou energização.
