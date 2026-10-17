# Headroom compartilhado neste projeto

Objetivo: qualquer harness local configurado acessa a memória deste projeto
diretamente por MCP. O banco canônico é `.headroom/memory.db`; todos os clientes
usam o mesmo usuário. Claude/OpenAI/Codex são provedores/modelos, enquanto Claude
Code, Codex CLI, Pi e Hermes são os clientes que disponibilizam as ferramentas.
Trocar o provedor não troca o banco nem exige nova instalação do Headroom.

## Configuração local em 2026-10-09

| Harness | Definição efetiva |
|---|---|
| Claude Code | `.mcp.json`; registros locais do mesmo projeto em `~/.claude.json` permitem o acesso direto sem aprovação pendente. |
| Codex | `.codex/config.toml` com `cwd` e `--db` explícitos; confiança registrada somente para este checkout. |
| Pi | `.mcp.json` e overrides em `.pi/mcp-adapter.json`; aprovação dos dois servidores vinculada ao hash das definições deste projeto. |
| Hermes | `~/.hermes/config.yaml`: servidores Headroom, com `${workspaceFolder}` no cwd/banco de memória. |

As definições locais usam a instalação uv existente de `headroom-ai[all]`.
São específicas deste host e estão fora do Git. Ao mover o checkout, atualizar
os caminhos absolutos de Claude/Codex/Pi; Hermes resolve seu workspace ativo.
Iniciar os harnesses com a raiz deste projeto como workspace/cwd. O registro
Hermes é global porque esta versão não descobre `.mcp.json` de projetos;
cada workspace recebe seu próprio banco, não o banco global do Headroom.

Os servidores são:

- `headroom`: `headroom mcp serve`, ferramentas de compressão/recuperação/stats.
- `headroom_memory`: Python da instalação uv, módulo
  `headroom.memory.mcp_server`, com `--user` comum e `--db` deste projeto.

Pi mantém apenas `headroom_compress`/`headroom_stats` como ferramentas diretas
do servidor `headroom`, porque a extensão `pi-headroom` já fornece
`headroom_retrieve`. As ferramentas de memória são diretas/eager.
Definições de servidores de outros serviços/projetos foram preservadas.

## Uso

Abrir uma sessão nova depois de modificar configurações. Usar `memory_search`
para buscar conhecimento persistente e `memory_save` quando o usuário solicitar
registro durável. Prefixos dos nomes variam conforme o harness.
O acesso MCP é independente do provedor desde que o modelo aceite ferramentas.

Para confirmar disponibilidade, usar `/mcp` no Claude Code/Codex,
`/mcp-adapter` e `/headroom-status` no Pi e `hermes mcp list` no Hermes.
`codex mcp get` gerencia a configuração global nesta versão; a configuração
por projeto foi conferida pelo `config/read` do app-server, com cwd explícito.
Consultar a memória sem criar registros por CLI:

```sh
headroom memory stats
```

O banco global de memória anterior fica preservado. Não houve importação de
outros projetos; um banco vazio é válido e passa a reunir apenas registros
deste projeto. Memória e configurações locais não devem ser versionadas.

## Compressão e execução remota

MCP fornece acesso às ferramentas; compressão automática de todas as chamadas
depende da integração de cada harness. O proxy local existente continua em
`http://127.0.0.1:8791`, com serviço `headroom.service`. A extensão do Pi usa esse
proxy; os hooks de Claude/Codex asseguram sua disponibilidade. Trocar provedor
não garante que sua API passe automaticamente pelo proxy.

O MCP permanece local por stdio. Uma execução do Claude Code/Codex em máquina
remota ou container de nuvem precisa da instalação e do banco naquele ambiente;
a nuvem não acessa automaticamente arquivos ou localhost desta máquina.
Não expor MCP à rede nem copiar credenciais para o repositório.

## Evidências e referências

Validação local e limites registrados em
[tests/reports/headroom-harnesses.md](../tests/reports/headroom-harnesses.md).
Logs sanitizados em `build/headroom/`; snapshot privado das configurações
anteriores em `~/.cache/headroom/project-config-backups/`.

Referências de formatos: [Claude Code MCP](https://code.claude.com/docs/en/mcp),
[Codex MCP](https://developers.openai.com/codex/mcp/),
[Pi MCP adapter](https://www.npmjs.com/package/pi-mcp-adapter).
Os carregadores instalados de Pi/Hermes foram conferidos no host.
