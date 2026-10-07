# Setup KiCad no Arch Linux

## Software principal

**KiCad 10.x** é o EDA principal deste projeto. Em 29/08/2026 o projeto KiCad publicou a versão estável 10.0.6.

Instalação típica no Arch:

```bash
sudo pacman -Syu
sudo pacman -S kicad kicad-library kicad-library-3d ngspice git
```

Confirme os nomes dos pacotes no seu mirror/repositório antes de executar se houver mudanças de empacotamento.

## Ferramentas auxiliares

```bash
# uv para ambientes Python/MCP modernos
curl -LsSf https://astral.sh/uv/install.sh | sh

# opcional: ferramentas de desenvolvimento
sudo pacman -S base-devel python python-pip cmake ninja
```

## Estrutura Git recomendada

```text
ps28-modern-amp/
├── README.md
├── docs/
├── kicad/
│   ├── ps28-modern.kicad_pro
│   ├── ps28-modern.kicad_sch
│   └── ps28-modern.kicad_pcb
├── reference/
│   ├── ti/
│   └── infinity/
├── simulation/
├── bom/
├── manufacturing/
├── tests/
└── skills/
```

## Configuração inicial do KiCad

1. Criar projeto `ps28-modern`.
2. Definir units em mm.
3. Habilitar IPC API quando usar ferramentas MCP que dependam dela.
4. Criar net classes desde o início:
   - `ANALOG`;
   - `LOGIC`;
   - `PVDD`;
   - `SWITCH_NODE`;
   - `SPEAKER`.
5. Criar regras locais para clearance e largura de trilha antes de roteamento.
6. Configurar Git para versionar `.kicad_pro`, `.kicad_sch`, `.kicad_pcb`, bibliotecas customizadas e arquivos de regras.

## `kicad-cli`

Use o CLI para verificações reprodutíveis:

```bash
kicad-cli sch erc kicad/ps28-modern.kicad_sch
kicad-cli pcb drc kicad/ps28-modern.kicad_pcb
```

Consulte `kicad-cli --help` porque opções podem mudar entre releases.

## Simulação

O KiCad integra ngspice. Simular principalmente:

- crossover;
- ganho;
- VMID;
- resposta a degrau do mute/reset quando modelável;
- sensibilidade a tolerâncias.

Não tente validar EMI e comportamento completo do power stage apenas com SPICE simplificado.
