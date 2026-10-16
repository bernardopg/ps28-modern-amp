# Roadmap

## Incremento atual — 2026-10-16

**Uma PCB de produto: `kicad/system-candidate/`.** Roteamento conectado, revisão
local do TPA e fit térmico nominal concluídos: 269 footprints, ERC/DRC/paridade e
conexões abertas zerados. [Estado técnico](../docs/development-status.md).

- **Em andamento — PCB-002:** revisão global de potência/retornos/EMI e gate G2.
- **Revisão pendente — ELEC-003:** captura integrada/ERC concluídos; auditoria de
  pinagem/MPNs/footprints e revisão humana G1 não assinadas.
- **Próximo — BUY-001/FAB-001:** qualificar BOM/CPL/DNP/estoque, obter cotação,
  conferir gabarito e preparar pacote rastreável; aprovação G3 pelo proprietário.
- **Bancada — BENCH-001/002:** aprovar limites e instrumentos antes de energia;
  validar montagem/TIM/roscas/folgas e dissipação real em carga artificial.
- **Depois — ACOU-001:** woofer somente após bring-up/proteções aprovados.

O preamp/limiter OEM é reaproveitado (D-032); o front-end novo anterior permanece
histórico. O fit calculado não mede o caminho dissipador→ambiente nem garante
150 W contínuos. Nenhum gate ou sprint foi aprovado automaticamente.

## Milestones e sprints

- **M0 / S01:** infraestrutura e setup.
- **M1 / S02:** requisitos, woofer, T1, mecânica e recursos de bancada.
- **M2 / S03 / G1:** captura, simulações e revisão elétrica independente.
- **M3 / S04 / G2–G3:** revisão de layout, BOM/CPL, cotação e autorização fabril.
- **M4 / S05 / G4–G5:** bring-up resistivo e integração acústica.

Estados oficiais: [backlog](project-backlog.md) e `items/`; WIP máximo 2.
A ordem técnica não ativa sprint nem dispensa dependências/gates. Sequência
verificável em [docs/production-roadmap.md](../docs/production-roadmap.md).

## Fora do compromisso

DSP/PFFB/controle remoto e alterações após a placa validada exigem nova decisão
de escopo. Não criar revisões físicas intermediárias como substituto do fechamento.
