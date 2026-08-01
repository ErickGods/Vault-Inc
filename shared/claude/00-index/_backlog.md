---
house: shared
type: backlog
updated: 2026-08-01
---

# Claude Code — Backlog de notas planejadas

Estas são notas que as 13 existentes (e o antigo MOC, agora substituído por [[_house]]) **citam
por wikilink mas que nunca foram escritas**. Não são links quebrados a consertar — são um
**roadmap em forma de link**: o autor esboçou um vault bem maior nos wikilinks antes de escrever
os arquivos. Uma linha aqui fica "planejada" até alguém escrever a nota; nesse momento ela ganha
um arquivo de verdade e migra para uma linha em [[_house]].

Este arquivo existe para que esses alvos sejam um **backlog deliberado e visível**, não sujeira
que passa por rot. O portão `scripts/check_links.py` tolera todos eles pela `baseline.txt` — não
tente resolvê-los aqui.

**Como ler a coluna "Citada por".** Quando uma das 13 notas escritas aponta para o alvo, a nota
está nomeada — é uma promessa concreta que aquela nota faz ao leitor. Quando diz *roadmap*, o
alvo vinha só do esboço do antigo MOC: território que a casa pretendia cobrir, sem nota escrita
ainda apontando para lá.

## Conceitos e uso avançado

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[ultrathink]] | O modo de raciocínio estendido acionado por palavra-chave (`ultrathink`) e quando o custo extra de pensamento compensa. | roadmap · 03-advanced |
| [[prompt-engineering-for-claude]] | Técnicas de engenharia de prompt específicas para os modelos Claude. | roadmap · 03-advanced |
| [[memory-system]] | O sistema de memória do Claude Code — arquivos de memória, `MEMORY.md`, persistência entre sessões. | roadmap · 03-advanced |
| [[plan-mode]] | O modo de planejamento que separa desenhar a solução de executá-la. | roadmap · 03-advanced |

## Configuração

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[claude-md-configuration]] | O CLAUDE.md em profundidade: o que colocar, o que custa contexto e como estruturar por diretório. | [[what-is-claude-code]], [[context-window-management]] |
| [[claude-md-guide]] | Guia completo do CLAUDE.md como instruções de projeto (sobreposto a `claude-md-configuration` — consolidar ao escrever). | roadmap · 03-advanced |
| [[settings-and-config]] | Configuração do Claude Code: `settings.json`, precedência global vs local, variáveis de ambiente. | roadmap · 03-advanced |

## API e SDK

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[messages-api-reference]] | Referência da Messages API — o contrato de request/response que o Claude Code usa por baixo. | [[claude-code-vs-api-vs-chat]], [[claude-models-overview]] |
| [[claude-api-reference]] | Referência ampla da API da Anthropic além do endpoint de mensagens. | roadmap · 04-api-and-sdk |
| [[batch-api]] | A Batch API em profundidade: submissão assíncrona, 50% de desconto, ciclo de status e coleta. | [[claude-code-vs-api-vs-chat]], [[pricing-and-tokens]] |
| [[extended-thinking]] | Extended Thinking em profundidade: budget de tokens, blocos de pensamento e quando ativar. | [[claude-models-overview]] |
| [[prompt-caching-deep-dive]] | Prompt caching em profundidade: pontos de cache, TTL, mínimo de tokens e cálculo de economia. | [[pricing-and-tokens]] |
| [[anthropic-sdk-python]] | O SDK Python: instalação, uso e exemplos. | roadmap · 04-api-and-sdk |
| [[anthropic-sdk-typescript]] | O SDK TypeScript/Node.js: instalação e exemplos. | roadmap · 04-api-and-sdk |
| [[claude-agent-sdk]] | O Agent SDK para construir agentes sobre o Claude. | roadmap · 04-api-and-sdk |

## Workflows e patterns

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[subagents-parallel-execution]] | O padrão completo de subagentes paralelos com contexto isolado, além do mecânico já em [[subagents]]. | [[what-is-claude-code]], [[context-window-management]] |
| [[worktrees-workflow]] | O workflow de ponta a ponta com git worktrees para sessões paralelas isoladas. | [[what-is-claude-code]], [[context-window-management]] |
| [[tdd-with-claude]] | TDD assistido por agentes Claude. | roadmap · 06-patterns |
| [[code-review-with-agents]] | Code review automatizado com agentes. | roadmap · 06-patterns |
| [[debugging-workflow]] | Workflow de debugging sistemático com agentes. | roadmap · 06-patterns |
| [[project-scaffolding]] | Geração de estrutura de projetos com Claude. | roadmap · 06-patterns |
| [[documentation-generation]] | Geração automatizada de documentação. | roadmap · 06-patterns |
| [[financial-analysis-with-claude]] | Análise financeira e de equity assistida por Claude — a ponte da ferramenta para a casa finance. | roadmap · 06-patterns |
| [[pitchbook-generation]] | Geração de pitchbooks e materiais de investimento com Claude. | roadmap · 06-patterns |
| [[ai-for-equity-research]] | IA aplicada a research de equities. | roadmap · 06-patterns |

## Plugins e extensões

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[mcp-catalog]] | Catálogo de servidores MCP prontos para usar. | roadmap · 05-plugins |
| [[ide-integrations]] | Integrações com VS Code, Cursor e JetBrains. | roadmap · 05-plugins |
| [[superpowers-plugin]] | O plugin Superpowers: skills avançadas e cowork. | roadmap · 05-plugins |
| [[third-party-tools]] | Ferramentas de terceiros compatíveis com Claude. | roadmap · 05-plugins |
| [[building-plugins]] | Como construir plugins e extensões para Claude. | roadmap · 05-plugins |

## Snippets

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[skill-snippets]] | Blocos prontos para criar skills. | roadmap · 07-snippets |
| [[hook-snippets]] | Blocos de hooks para `settings.json`. | roadmap · 07-snippets |
| [[mcp-server-snippets]] | Blocos de configuração de servidores MCP. | roadmap · 07-snippets |
| [[api-snippets]] | Blocos de chamadas à API da Anthropic. | roadmap · 07-snippets |
| [[claude-md-snippets]] | Blocos reutilizáveis para o CLAUDE.md. | roadmap · 07-snippets |

## Troubleshooting

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[common-errors]] | Erros comuns do Claude Code e suas soluções. | roadmap · 08-troubleshooting |
| [[performance-tips]] | Dicas de performance e otimização de tokens. | roadmap · 08-troubleshooting |
| [[context-overflow]] | Como lidar com overflow de contexto. | roadmap · 08-troubleshooting |
| [[debugging-agents]] | Técnicas para debugar agentes autônomos. | roadmap · 08-troubleshooting |

## Glossário e índice

| Nota planejada | O que cobriria | Citada por |
|---|---|---|
| [[claude-glossary]] | Glossário do ecossistema Claude/Anthropic. | roadmap · 09-glossary |
| [[claude-code-moc]] | O índice geral do Claude Code — papel hoje cumprido por [[_house]]; as 8 notas de recursos ainda o citam no `Related` e migram quando forem religadas. | as 8 notas de `02-core-features/` |
