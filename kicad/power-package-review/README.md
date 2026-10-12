# D-021 — captura de revisão de encapsulamentos

Abrir `power-package-review.kicad_pro` (captura **incompleta**, não fabricação).
Gerada por `scripts/create_power_package_review.py --output <diretório novo>`.
O gerador recusa sobrescrita. PCB roteada `system-candidate` preservada.

Correções rastreáveis:
- Retirada seleção MUR3040WTG: onsemi MUR3020WT/D Rev.7 p.2, IFSM=150 A
  por junção contra requisito ≥200 A. P.1 identifica retificador duplo TO-247,
  não diodo axial. D301/D302 agora representam apenas os dois ramos funcionais
  CT sem MPN/footprint escolhidos. Não montar símbolo funcional como peça real.
- C301/C302: removido footprint Ø25 mm e seleção não qualificada; conservar
  requisito 4700 µF/≥63 V/105 °C/ripple≥3,5 A até seleção primária válida.
- J301: três vias do chicote mantidas, housing VHR-4N e footprint não qualificados
  retirados. Header precisa ser identificado, não apenas terminal de crimp.
- F301: valor T TBD; removida aparência de seleção 6,3 A. Holder ainda candidato.
- D303: SMCJ51A permanece candidato explícito, não OVP qualificada. Supervisor
  desabilita lógica; não desconecta a alimentação PVDD do TPA.

Todas as nets preservadas em teste de regressão. ERC nativo 0 violações;
footprints ausentes são bloqueadores intencionais, não hardware validado.
Manifesto inclui hashes das fontes. Sem PCB/placement nesta captura: escolher
encapsulamentos corretos e resolver OVP/inrush antes de reconstruir o layout.
