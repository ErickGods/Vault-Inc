---
tags: [moc, home, claude-vault]
status: active
complexity: basic
context: global
updated: 2026-04-19
created: 2026-04-19
aliases: [Claude Home, Claude Code MOC]
---

# 🗺️ Claude Vault — Ecossistema Anthropic & Claude Code

## Visão Geral

Este vault é o repositório central de conhecimento sobre o ecossistema Anthropic e Claude Code. Cobre desde os fundamentos do Claude como modelo de linguagem até o uso avançado do Claude Code CLI, API, agentes autônomos, skills, MCP (Model Context Protocol), padrões de uso em desenvolvimento de software e pesquisa financeira. O vault serve como referência prática para extrair o máximo do ecossistema Claude no dia a dia da Vault Inc.

> [!info] Para Humanos e Agentes
> Este vault é referência tanto para humanos quanto para agentes de IA da Vault Inc. Os arquivos de patterns e recipes descrevem workflows que agentes podem seguir autonomamente. Os snippets fornecem código reutilizável. O glossário padroniza terminologia usada em prompts e instruções.

> [!tip] Vaults Relacionados
> - [[finance/00-index/_house|Finance Vault]] — Conhecimento financeiro, valuation, análise de mercado
> - [[🗺️ Tech-Home|Tech Vault]] — Engenharia de software, IA/ML, infraestrutura

---

## 📊 Dashboard — Notas Recentes

```dataview
TABLE status, level, updated
FROM "claude-vault"
WHERE file.name != "🗺️ Claude-Home"
SORT updated DESC
```

---

## 📁 01 — Fundamentos

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[what-is-claude-code]] | O que é Claude Code, arquitetura e posicionamento | — |
| [[claude-models-overview]] | Família de modelos: Opus, Sonnet, Haiku | — |
| [[claude-code-vs-api-vs-chat]] | Diferenças entre Claude Code CLI, API e chat web | — |
| [[context-window-management]] | Gerenciamento de contexto e janela de tokens | — |
| [[pricing-and-tokens]] | Precificação, tokens de entrada/saída, cache | — |

---

## 📁 02 — Funcionalidades Principais

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[skills-system]] | Sistema de skills: criação, ativação e uso | — |
| [[hooks-system]] | Hooks de ciclo de vida: pre/post tool, stop | — |
| [[mcp-servers]] | Model Context Protocol: servidores e integração | — |
| [[subagents]] | Subagentes: Task tool e paralelismo | — |
| [[agent-teams]] | Times de agentes: coordenação e orquestração | — |
| [[worktrees]] | Git worktrees para isolamento de tarefas | — |
| [[slash-commands]] | Comandos slash nativos e customizados | — |
| [[permissions-and-safety]] | Sistema de permissões, allowlist e segurança | — |

---

## 📁 03 — Avançado

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[ultrathink]] | Modo de raciocínio estendido: ultrathink | — |
| [[prompt-engineering-for-claude]] | Técnicas de engenharia de prompt para Claude | — |
| [[claude-md-guide]] | Guia completo do CLAUDE.md: instruções de projeto | — |
| [[memory-system]] | Sistema de memória: arquivos, MEMORY.md, persistência | — |
| [[plan-mode]] | Modo de planejamento antes da execução | — |
| [[settings-and-config]] | Configuração: settings.json, variáveis de ambiente | — |

---

## 📁 04 — API e SDK

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[claude-api-reference]] | Referência completa da API Anthropic | — |
| [[anthropic-sdk-python]] | SDK Python: instalação, uso e exemplos | — |
| [[anthropic-sdk-typescript]] | SDK TypeScript/Node.js: instalação e exemplos | — |
| [[claude-agent-sdk]] | Agent SDK: construção de agentes com Claude | — |
| [[batch-api]] | Batch API: processamento em lote de requisições | — |

---

## 📁 05 — Plugins e Extensões

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[mcp-catalog]] | Catálogo de servidores MCP disponíveis | — |
| [[ide-integrations]] | Integrações com VS Code, Cursor, JetBrains | — |
| [[superpowers-plugin]] | Plugin Superpowers: skills avançadas e cowork | — |
| [[third-party-tools]] | Ferramentas de terceiros compatíveis com Claude | — |
| [[building-plugins]] | Como construir plugins e extensões para Claude | — |

---

## 📁 06 — Patterns e Recipes

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[tdd-with-claude]] | TDD assistido por agentes Claude | — |
| [[code-review-with-agents]] | Code review automatizado com agentes | — |
| [[project-scaffolding]] | Geração de estrutura de projetos com Claude | — |
| [[financial-analysis-with-claude]] | Análise financeira e de equity com Claude | — |
| [[debugging-workflow]] | Workflow de debugging sistemático com agentes | — |
| [[documentation-generation]] | Geração automatizada de documentação | — |
| [[pitchbook-generation]] | Geração de pitchbooks e materiais de investimento | — |
| [[ai-for-equity-research]] | IA aplicada a research de equities | — |

---

## 📁 07 — Snippets

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[skill-snippets]] | Snippets de código para criação de skills | — |
| [[hook-snippets]] | Snippets de hooks para settings.json | — |
| [[mcp-server-snippets]] | Snippets de configuração de servidores MCP | — |
| [[api-snippets]] | Snippets de chamadas à API Anthropic | — |
| [[claude-md-snippets]] | Snippets de blocos para CLAUDE.md | — |

---

## 📁 08 — Troubleshooting

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[common-errors]] | Erros comuns e suas soluções | — |
| [[performance-tips]] | Dicas de performance e otimização de tokens | — |
| [[context-overflow]] | Como lidar com overflow de contexto | — |
| [[debugging-agents]] | Técnicas para debugar agentes autônomos | — |

---

## 📁 09 — Glossário

| Arquivo | Conteúdo | Status |
|---------|----------|--------|
| [[claude-glossary]] | Glossário completo do ecossistema Claude/Anthropic | — |

---

## ⚡ Quick Access — Arquivos Essenciais

1. [[what-is-claude-code]] — Ponto de entrada: o que é, como funciona, arquitetura
2. [[skills-system]] — Como criar e usar skills para automatizar workflows
3. [[mcp-servers]] — Integração com ferramentas externas via MCP
4. [[agent-teams]] — Orquestração de múltiplos agentes em paralelo
5. [[claude-api-reference]] — Referência da API para integrações programáticas

---

## 🔗 Conexões com Outros Vaults

- [[finance/00-index/_house|🏦 Finance Vault]] — Para análise financeira assistida por Claude, ver [[financial-analysis-with-claude]] e [[pitchbook-generation]]
- [[🗺️ Tech-Home|💻 Tech Vault]] — Para padrões de engenharia de software com IA, ver [[tdd-with-claude]] e [[debugging-workflow]]

---

*Vault criado em 2026-04-19. Referência viva — atualizar conforme o ecossistema Claude evolui.*
