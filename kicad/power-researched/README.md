# Potência — candidatos pesquisados, não fabricação

Abrir `power-researched.kicad_pro`. Gerador:
`python3 scripts/create_power_researched.py --output <diretório novo>`.
Recusa sobrescrita; nenhuma alteração na candidata roteada.

RHRP1560: candidato elétrico 600 V/15 A/IFSM 200 A; footprint e térmica pendentes.
LGU2A472MELC: 4700 µF/100 V/105 °C/ripple 4,14 A; footprint snap-in local de estudo
com corpo nominal Ø35×50 mm, envelope reservado Ø36,5×52 mm. Fit não aprovado.
J301/fusível/OVP série não resolvidos. Esta captura não possui PCB.

ERC nativo 0; não significa hardware completo. Fontes, limitações, budgets CT e
contraprova OVP: `../../docs/power-remediation.md`.
