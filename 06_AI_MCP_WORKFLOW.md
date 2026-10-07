# IA, MCP e Skills para desenvolvimento

## Recomendação principal

Use IA como **copiloto e revisor**, não como autoridade de sign-off.

### Opção A — KiCad AI Assistant

Projeto `paul356/KiCad-AI-Assistant`:

- plugin para KiCad 10;
- testado em Linux;
- painel LLM dentro do KiCad;
- pode trabalhar com schematic, PCB, DRC e skills em Markdown;
- possui MCP server embutido.

É a opção mais direta para edição assistida dentro do KiCad.

### Opção B — Konnect

Projeto `obhox/kicad-mcp`:

- plugin/MCP nativo para KiCad 10;
- usa IPC API do KiCad para PCB;
- suporta schematic, layout, ERC/DRC, JLCPCB part search e manufacturing export;
- está marcado como **beta**.

Use apenas com Git e snapshots frequentes.

### Opção C — KiCad MCP Pro

Projeto `oaslananka/kicad-mcp` / pacote `kicad-mcp-pro`:

- orientado a revisão, ERC/DRC, DFM, BOM e fabricação;
- bom como segunda linha de auditoria;
- o próprio projeto afirma que não substitui sign-off humano, SI/PI/EMC/thermal avançados.

## Estratégia recomendada

```text
KiCad 10 + Git
      │
      ├─ KiCad AI Assistant: edição interativa
      │
      ├─ kicad-cli: ERC / DRC / exports
      │
      └─ KiCad MCP Pro: auditoria independente
```

Não mantenha dois agentes com escrita irrestrita no mesmo projeto ao mesmo tempo.

## Política de permissões

- **read-only** para revisão e primeira análise;
- habilitar escrita somente em branch separada;
- commit antes de cada sessão de IA;
- nunca aceitar automaticamente:
  - mudança de footprint do TPA3255;
  - alteração de valores de bootstrap/desacoplamento;
  - alteração de modo PBTL;
  - mudança de net class de PVDD/SPEAKER;
  - export final para fabricação.

## Fluxo de Git

```bash
git checkout -b feat/schematic-core
# trabalho assistido
git diff
git commit -am "Add TPA3255 PBTL core"

# outra branch para layout
git checkout -b feat/power-layout
```

## Prompt base para o agente

```text
Você está trabalhando no projeto PS28 Modern Amp Rev. A.
A golden reference é a documentação oficial TI TPA3255 + TPA3255EVM.
Não altere valores críticos da aplicação de referência sem explicar a razão e citar o item do datasheet/EVM.
Não libere fabricação.
Antes de qualquer alteração, informe: objetivo, nets afetadas, riscos e validação necessária.
Depois da alteração, execute/recomende ERC/DRC e mostre o diff conceitual.
```

## Skills deste pacote

Veja `skills/`:

- `reference_design_guardrails.md`;
- `schematic_review.md`;
- `class_d_layout_review.md`;
- `bom_dfm_review.md`;
- `bringup_review.md`.

## ChatGPT / plugins

No diretório de plugins atual não foi localizado um plugin ChatGPT específico para KiCad que eu recomendaria como substituto do MCP local. Portanto, para controle real do KiCad, prefira um MCP local/IPC API e mantenha o projeto em Git.
