# Toolchain e auditoria local

## Complemento verificado — 2026-10-16

KiCad 10.0.7/bibliotecas, ngspice 47 e Blender 5.2.2 LTS disponíveis; MCP Blender
compatível, addon 1.8. Gerbonara 1.6.3 instalado via uv em `build/validation-venv`
(Python 3.13 isolado), sem alterar o sistema. `scripts/verify_gerbers.py` verifica
os rascunhos com parser independente. ReportLab e pypdf já disponíveis para
desenho cotado e inspeção PDF. API IPC KiCad indisponível; KCAA operou em disco.
Instalação/reprodução e todos os avisos em
[revisão final](final-design-review-2026-10-16.md). FreeCAD/KiBot/novos addons não
são necessários para as verificações executadas; não substituem bancada/DFM.

## Snapshot anterior

Snapshot em 2026-10-07 (relógio da máquina); reproduzir com make doctor.

## Verificado

Arch Linux x86_64; KiCad 10.0.7; bibliotecas símbolos/footprints/3D 10.0.7;
ngspice 47; Python 3.14.7; uv 0.12.23; Git e gh autenticado como bernardopg;
poppler/pdftotext, curl, make, gcc, cmake, ninja; numpy/matplotlib disponíveis.
KiCad AI Assistant local VERSION 0.2.6 (release GitHub correspondente).
KiCad API enable_server=true, porém ping IPC retornou Connection refused.
Isso pode significar editor fechado/socket indisponível; não prova falha de instalação.
Abrir PCB, confirmar Preferences → API e testar conexão antes de editar via MCP.

## Seleção enxuta, não ranking universal

- Base obrigatória já instalada: KiCad oficial + libraries + ngspice + Git/CLI.
- IA opcional já presente: paul356/KiCad-AI-Assistant MIT + kcaa da sessão.
  Validar conexão e criar snapshot antes de escrever. Não reinstalar sem necessidade.
- Auditor independente principal: kicad-cli + checklist + humano; outro MCP não
  garante independência porque pode compartilhar parser/regras/modelo.
- obhox/kicad-mcp AGPL-3.0 e oaslananka/kicad-mcp-pro MIT: alternativas consultadas
  via API GitHub (não arquivadas), NÃO instaladas/testadas; sem dois escritores.
- KiBot para exports/CI e InteractiveHtmlBom para bancada: úteis quando EDA/BOM
  existirem; avaliar compatibilidade/licença e fixar versão antes de adotar.
- FreeCAD para painel/dissipador; REW para acústica; sigrok/PulseView somente com
  instrumentos compatíveis. FreeCAD/OpenSCAD/REW não encontrados no PATH.
- scipy/kipy ausentes no Python do sistema; não são necessários aos comandos atuais.
  kcaa pode ter ambiente isolado próprio; ausência sistêmica não prova ausência no plugin.

Não foi feita instalação privilegiada nem atualização global. O setup usa stdlib Python
e ferramentas já presentes. Se precisar opcionais Arch, revisar pacotes atuais e usar
atualização completa de sistema, nunca atualização parcial nem curl|sh cego.

## Lacunas físicas

Fonte de bancada, sonda diferencial, scope, carga, medição térmica, ESD, bancada e
woofer não podem ser auditados por software. BENCH-001/SYS-001 são pré-requisitos.
Documentação/simulação funcionais; containers EDA parseados, mas instalação com ressalva:
`make eda-smoke` registra warnings `PROPERTY_ENUM(): No enum choices defined`
no KiCad 10.0.7. Reproduzidos também com BOARD nativo via pcbnew; export/import
terminaram com exit 0. Causa e impacto ainda não determinados (TOOL-001).
Não suprimir warnings nem declarar toolchain plenamente saudável. Bancada e
arquitetura ainda não liberadas.
