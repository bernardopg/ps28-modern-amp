---
id: TOOL-001
title: Investigar warnings PROPERTY_ENUM da instalação KiCad
status: To Do
milestone: M1
sprint: backlog
depends_on: none
updated: 2026-10-07
---

# TOOL-001 — Warnings KiCad

## Objetivo

Entender warnings da instalação antes de confiar em sessões prolongadas de EDA.

## Critérios de aceite

- [ ] Reproduzir em make eda-smoke e arquivo nativo mínimo, guardar versão/logs.
- [ ] Comparar pacote/ambiente limpo com upstream sem alterar instalação global automaticamente.
- [ ] Determinar impacto, correção/mitigação e repetir checks com evidência.

## Evidência

Em 2026-10-07, KiCad 10.0.7 emitiu `PROPERTY_ENUM(): No enum choices defined`
em export CLI e import pcbnew/BOARD gerado nativamente. Os comandos terminaram
com exit 0 e produziram arquivos. Reproduzível, mas causa/impacto não determinados.
Logs em build/\*-smoke.log e build/native-container.log (locais).

## Risco / aprovação

Não esconder assert nem interpretar exit 0 como instalação plenamente saudável.
Atualização/rebuild do sistema exige avaliação e autorização separadas.
