# Revisão do starter original
Todos os 15 documentos de raiz e cinco skills originais foram lidos e preservados
em docs/archive/chatgpt; primeiro commit conserva paths e conteúdo exatos.

Correções:
- Markdown truncado: tabelas BOM/requisitos, títulos e passos de segurança foram
  reescritos; fragmentos não foram reconstruídos como fatos sem evidência.
- Baseline virou proposta; potência/custo/woofer/fonte não são validações reais.
- M1/M2/M3 foi corrigido: TPA3255 tem M1/M2; SLASEA8A §10.2.4 fornece os estados.
- LC simplificado não define todos os OUTs/paralelamento: separar datasheet e EVM.
- 1500 µF atribuído genericamente à EVM foi removido como receita; SLAR130A
  contém C31/C46 4700 µF/80 V. Escolha real depende do baseline/inrush/ripple.
- NE5532/VMID/volume em 12 V exigem headroom e estabilidade; não são circuito fechado.
- Rampas de alimentação e limites de bancada passaram a exigir sequencing/Vin válidos.
- Cupons, preço de montagem e versões datadas foram retirados como premissas.
- KiCad MCP Pro resolve hoje para oaslananka/kicad-mcp-pro; comparação não foi
  tratada como prova de qualidade ou validação independente.
- Skills sem frontmatter/passos/saída foram reestruturadas; testes de comportamento
  fornecidos, mas ainda não há benchmark independente nem sign-off técnico.

Esta revisão é documental; não substitui revisão elétrica completa dos PDFs e circuito.
