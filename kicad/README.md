# KiCad

- **[`system-candidate/`](system-candidate/system-candidate.kicad_pro)** — a placa do
  produto: esquema, PCB roteada, bibliotecas locais (`libraries/`) e netlist.
- `models/` — modelos 3D: corpos por datasheet (`ps28-bodies/`, incluindo o bloco
  térmico) e CAD Würth licenciado CC BY-SA 4.0 (`vendor-wurth/`, [atribuição](models/vendor-wurth/README.md)).

Edição: um escritor de EDA por vez, snapshot antes de mutação, `make erc` e
`make drc` depois. Não há gerador: a placa é editada direto no KiCad.
Revisões anteriores ficam só no histórico Git (D-038).
