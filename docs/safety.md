# Segurança e gates obrigatórios

36 V reduz risco de choque, mas altas correntes, incêndio, partes quentes e energia
nos capacitores continuam presentes. Rede AC fica fora da PCB nova; fonte certificada
externa fica restrita a bancada/fallback. D-010 seleciona T1 original com novo bloco
secundário; o proprietário informou saúde dos componentes e capacidade técnica
para medições/conexões/testes. Ratings e segurança do conjunto novo ainda exigem
evidência e gates: [D-009/D-010](transformer-reuse.md).
O manual não comprova 34-0-34 VAC. Não ligar a fonte simétrica diretamente ao TPA3255.

## Proibições

- Sem woofer no primeiro bring-up; sem energização sem checklist e limites aprovados.
- SPK± não são GND. Nunca prender garra terra de scope em uma dessas saídas.
  Usar sonda diferencial com limites de common-mode/banda adequados. Nunca remover
  terra de proteção do scope. Medição por canais referenciados exige revisão especializada.
- Não manusear/retrabalhar bulk antes de medir descarga; não curto descarregar capacitores.
- Não insistir em FAULT nem aumentar current limit para contornar falha.
- Não expor circuitos de rede do plate original sem técnico qualificado.

## Registro de riscos

R1: topologia PBTL incorreta → curto/destruição; ELEC-001 e revisão pin-a-pin.
R2: fonte/TVS/fusível incompatíveis → incêndio; PWR-001 e análise transientes/inrush.
R3: swing/bias/VMID incorretos → clipping/DC/pop; ELEC-002 e BENCH-001.
R4: PowerPAD/LC subdimensionados → aquecimento; PCB-001/002 e ensaio térmico.
R5: erro scope → curto/instrumento; BENCH-001 e técnica diferencial aprovada.
R6: excesso de excursão no gabinete → woofer danificado; SYS-001 e ACOU-001.
R7: preço/MPN falsos → retrabalho/fraude; BUY-001 e rastreabilidade de fornecedor.

## Gates (D-030: aprovação = "ok" do proprietário registrado na task/decisão com data e commit)

G0 requisitos e baseline aprovados; G1 captura+SPICE+ERC revisados;
G2 layout+DRC+paridade+fit/térmica revisados; G3 BOM/CPL/DFM+cotação aprovados;
G4 carga resistiva/rails/DC/FAULT/térmica aprovados; G5 teste acústico e integração.
Status inicial: todos PENDENTES. ERC vazio não muda status. IA recomenda, humano aprova.
Gates são marcos curtos, não auditorias: G0–G2 podem ser aprovados juntos na revisão
final do layout; G3 antes do pedido; G4/G5 na bancada.

Registro atual2026-10-17: **G0 Rev.B aprovado pelo proprietário** (“Aprovo o G0
da Rev.B”); baseline/commit em [sys002-baseline.md](sys002-baseline.md).
G1–G5 permanecem pendentes. Esse aceite não autoriza energização/fabricação.
