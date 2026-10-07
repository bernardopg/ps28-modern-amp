---
id: SETUP-002
title: Containers EDA, comandos e CI
status: Done
milestone: M0
sprint: S01
depends_on: SETUP-001
updated: 2026-10-07
---
# SETUP-002 — Containers EDA, comandos e CI
## Objetivo
Containers EDA, comandos e CI, atendendo docs/requirements.md e gates docs/safety.md.
## Critérios de aceite
- [x] Containers KiCad abrem no CLI sem alegar validação
- [x] make check e make simulate executados; gates vazios falham
## Evidência
Ver tests/reports/setup.md; logs gerados em build/.
## Risco / aprovação
Alterações de hardware exigem fonte primária e gate humano; sem pedidos automáticos.
