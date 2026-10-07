# Evidências do setup — 2026-10-07
Este relatório valida infraestrutura/documentação, NÃO hardware.

- Originais: commit raiz `3db5124`; 20 arquivos preservados e movidos sem alteração.
- `make check`: validator sem erros e sete testes unittest aprovados.
- `make simulate`: ngspice 47, magnitude 0,5, −6,0206 dB em 80 Hz;
  modelo Sallen-Key com VCVS ideal, sem headroom/VMID físico validado.
- `make doctor`: ferramentas obrigatórias encontradas; relatório em build/doctor.json.
- `make fetch-reference`: quatro PDFs TI baixados/headers PDF verificados, manifesto
  com URLs finais, timestamps e SHA256. Revisão completa do circuito ainda pendente.
- `make eda-smoke`: netlist/SVG gerados com exit 0; warnings de PROPERTY_ENUM
  no KiCad 10.0.7 registrados. Também aparecem com BOARD nativo via pcbnew.
  Causa/impacto abertos em TOOL-001; não são apresentados como saúde completa do EDA.
- `python3 scripts/eda_check.py erc` e `drc`: ambos exit 2 deliberado,
  `BLOCKED: empty EDA container`; comportamento fail-closed esperado.
- KiCad AI Assistant 0.2.6 instalado; API habilitada no config, ping IPC sem conexão.
- Symlinks CLAUDE.md/.claude/skills/.agents/skills verificados pelo validator.
- Skills: nove playbooks e 18 prompts definidos; só estrutura avaliada, não benchmark
  independente de comportamento/qualidade profissional.

G0–G5 pendentes. Instrumentos, dimensões, woofer, MPNs e limites de bancada desconhecidos.
GitHub privado publicado; 18 issues e cinco milestones, com links em .tasks/github-mirror.json.
CI inicial em 1bd8dc7 aprovado: https://github.com/bernardopg/ps28-modern-amp/actions/runs/37654550846
Revisão do proprietário pendente em SETUP-003. Logs de trabalho ficam em build/.
