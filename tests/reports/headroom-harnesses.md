# Headroom por projeto — validação local

Data: 2026-10-09. Workspace: `ps28-modern-amp-starter` neste host.
Escopo autorizado: diagnosticar Headroom/Pi, instalar ferramentas opcionais
ausentes e compartilhar acesso Headroom entre os harnesses deste projeto.

## Resultado medido

Todos os clientes usam `.headroom/memory.db` e o mesmo usuário local, por stdio.
O banco tem zero registros após a validação; buscas foram somente leitura.
Nenhuma memória de outro projeto foi importada. Integrações existentes e
configurações de modelo/provedor foram preservadas.

| Cliente | Validação efetiva | Resultado |
|---|---|---|
| Claude Code | `claude mcp get headroom` e `headroom_memory`, registros locais deste checkout | Ambos Connected, sem aprovação pendente |
| Codex | app-server `config/read` com cwd deste projeto | Dois servidores habilitados; memória com banco explícito e startup de 60 s |
| Pi | carregador nativo do adapter e `applyProjectServerTrust`; sessão nova em PTY por 18 s | Dois servidores do projeto, nenhum bloqueado; proxy online e ferramentas diretas atualizadas |
| Hermes | runtime nativo Python 3.14.7 + `hermes_bootstrap`, discovery e seleção `_get_platform_tools(..., 'cli')` | Ambos Connected; as cinco ferramentas disponíveis na seleção CLI |
| MCP | initialize, list_tools e `memory_search` pelas quatro definições efetivas | Quatro consultas sem erro; `memory_search` e `memory_save` anunciadas |
| Compressão MCP | initialize, list_tools e `headroom_stats` | Três ferramentas anunciadas; stats sem erro |

O Pi mantém retrieve na extensão e compress/stats no adapter, evitando registrar
`headroom_retrieve` duas vezes. A sessão nova indicou `Headroom: on`, proxy 0.40.0;
não foi observado warning de desconexão nem de ferramenta duplicada.
Isso não identifica retrospectivamente a causa de uma desconexão anterior.

Os testes não consumiram uma resposta paga de modelo. A disponibilidade foi
verificada no carregamento/configuração, registro de ferramentas e protocolo MCP;
não foi inferida de uma resposta simulada do provedor.

`make check`: validação estrutural com **0 erros**; suíte com **75/76 testes
aprovados**. A única falha é preexistente em
`test_native_export_files_exist_and_match_source`: o checksum de
`docs/images/analog-protected/analog-protected.svg` diverge do manifest.
O arquivo atual tem o mesmo SHA-256 da versão em HEAD; não foi alterado por
este trabalho. O manifest/artifact de hardware não foi atualizado para ocultar
a falha. `git diff --check` passou.

## Doctor e instalação

`headroom doctor --json` após os ajustes: **0 falhas, 2 warnings, 1 skip**.
Exit code 1 corresponde aos warnings. Proxy/readiness/versão, integração Claude,
Codex, hooks de ambos neste projeto, TLS e quatro deployments passaram.

| Warning restante | Causa e limite |
|---|---|
| Budget ausente | Gasto ilimitado configurado; não foi imposto limite financeiro novo |
| Claude Desktop | Desktop sobrescreve ANTHROPIC_BASE_URL; esta versão não suporta rotear suas sessões pelo proxy |

`wrap_marker` foi skip: ausência de wrapper temporário, sem falha associada.
O warning anterior sobre hook Codex ausente neste projeto foi resolvido.

Ferramentas opcionais ausentes foram instaladas pelo instalador Headroom com
verificação de checksum: `difft 0.64.0`, `scc 3.5.0` e
`codebase-memory-mcp 0.8.1`. `ast-grep 0.50.0` já estava presente.
Os comandos de versão e `headroom tools doctor` passaram no diagnóstico.
A instalação do binário de grafo não criou um índice nem ativou outro MCP.

## Evidências e recuperação

Logs locais em `build/headroom/`, ignorados pelo Git:

- `codex-effective.json`, `codex-appserver.log`;
- `pi-effective.json`, `pi-trust.json`, `pi-startup.log`;
- `hermes-effective.json`, `hermes-discovery.json`, `hermes-cli-tools.json`;
- `mcp-connections.json`, `mcp-stderr.log`, `doctor.json`;
- `make-check.log` para a validação do repositório.

Snapshot privado anterior às alterações:
`~/.cache/headroom/project-config-backups/20261009-155035-ps28/`, com manifest
de arquivos preexistentes. Inclui registros globais necessários aos carregadores;
configurações/banco deste host permanecem fora do Git.

Instruções: [docs/headroom.md](../../docs/headroom.md).
Sessões existentes precisam reiniciar para carregar as definições.
As APIs de todos os provedores não foram exercitadas; o modelo precisa suportar
ferramentas. Execução remota exige instalação/banco no ambiente remoto.
Hardware, simulação e EDA não foram modificados nem validados por este trabalho.
