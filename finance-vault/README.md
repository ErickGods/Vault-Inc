# Claude Vault

Repositório central de **agentes** e **skills** customizados da Vault Inc., projetados para serem instalados no Claude Code (`~/.claude/agents/` e `~/.claude/skills/`) ou usados como subagentes em projetos específicos.

## Estrutura

```
claude-vault/
├── agents/                          # Agentes (subagent definitions)
│   └── financial-research-house/    # Casa de research financeira
│       ├── CLAUDE.md                # Orquestrador da casa
│       ├── equity-research-analyst.md
│       └── private-banker.md
├── skills/                          # Skills instaláveis (SKILL.md)
├── templates/                       # Templates para criar novos agentes/skills
└── docs/                            # Documentação meta
```

## Conexão com os outros vaults

Cada agente/skill referencia conhecimento de:

- **finance-vault/** — base de conhecimento financeiro (frameworks, glossário, instrumentos, valuation)
- **tech-vault/** — base de conhecimento técnico (linguagens, frameworks, infra)

A conexão é feita via **caminhos absolutos** (`C:/Users/Erick/Documents/Vault-Inc/Vault-Inc-Library/finance-vault/...`) na seção `Knowledge Sources` de cada agente. Os agentes têm `Read/Glob/Grep` no toolset para consultar esses arquivos em runtime.

## Como instalar um agente

### Opção A — Instalação global (`~/.claude/agents/`)

```bash
# Linux/Mac
cp claude-vault/agents/financial-research-house/equity-research-analyst.md \
   ~/.claude/agents/

# Windows
copy "claude-vault\agents\financial-research-house\equity-research-analyst.md" ^
     "%USERPROFILE%\.claude\agents\"
```

### Opção B — Por projeto (`<projeto>/.claude/agents/`)

Copie o arquivo para a pasta `.claude/agents/` do projeto onde o agente deve ser usado.

### Opção C — Symlink (recomendado para desenvolvimento)

```bash
# Mantém o arquivo sincronizado com o vault
ln -s "$(pwd)/claude-vault/agents/financial-research-house/equity-research-analyst.md" \
      ~/.claude/agents/equity-research-analyst.md
```

## Como criar um novo agente

1. Copie `templates/agent-template.md` para o diretório da casa apropriada
2. Preencha o frontmatter (`name`, `description`, `tools`)
3. Defina identidade, responsabilidades, e o que o agente NÃO faz
4. Adicione a seção `Knowledge Sources` com os arquivos relevantes do `finance-vault` ou `tech-vault`
5. Atualize o `CLAUDE.md` da casa para incluir o novo agente na tabela de orquestração

## Casas planejadas

- **financial-research-house** ✅ — research, equity, fixed income, PE, private banking
- *(futuras casas a definir conforme demanda)*
