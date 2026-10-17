# Estado do projeto

Atualizado em **2026-10-17**. Fonte de verdade das tasks: [backlog](../.tasks/project-backlog.md).

## Onde estamos

Placa única `kicad/system-candidate/` **roteada e conectada**, ainda não liberada
para fabricação.

| Item | Valor |
|---|---|
| Contorno | 154 × 81 mm, furação e perfil U OEM |
| Footprints / segmentos / vias | 269 / 3.535 / 500 |
| ERC · DRC · aberturas · paridade | 0 · 0 · 0 · 0 |
| BOM | 235 posições com fabricante e MPN ([fechamento](bom-closeout-2026-10-16.md)) |
| Requisitos | Rev.B aprovada no G0 ([baseline](sys002-baseline.md)) |
| Térmica | Fit nominal em CAD e orçamento calculado ([bloco](../mechanical/thermal-block.md)) |
| Testes automatizados | `make check` |

## O que falta até a placa funcionar

1. **PCB-002 / G2** — revisão global de layout: correntes, retornos, EMI, DFM.
2. **ELEC-003 / G1** — auditoria de pinagem, MPN e footprint.
3. **MECH-002** — gabarito impresso 1:1 conferido na unidade OEM (único passo físico antes do pedido).
4. **FAB-001 / G3** — pacote JLCPCB, estoque, cotação e "ok" do proprietário.
5. **BENCH-002 / G4** — montagem no gabinete e primeira energização com lâmpada-série, sem woofer.

Ensaios de bancada saíram do plano (D-037): limites de requisito são cobertos por
análise, simulação e CAD; ver [matriz de aceitação](../tests/acceptance.md).

## Riscos abertos

- PVDD tem ramais finos (0,2–0,6 mm) além do ramo de 1,2 mm; PCB-002 decide.
- Caminho perfil→ambiente não medido; aceito por comparação com o classe AB OEM (D-037).
- Modelos 3D genéricos em alguns componentes; renders não comprovam fit físico.

## Histórico

Decisões em [decisions.md](decisions.md); mudanças em [CHANGELOG](../CHANGELOG.md).
Revisões anteriores da placa ficam só no histórico Git (D-038).
