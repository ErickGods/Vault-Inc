---
house: shared
type: house-index
updated: 2026-08-01
---

# Claude Code — Índice

Referência sobre **operar o próprio Claude Code**: fundamentos do modelo e recursos principais
da ferramenta. Não é uma casa com agentes e ninguém roteia para cá em busca de análise — é
conhecimento compartilhado, de que qualquer casa se serve quando a dúvida é sobre a ferramenta
e não sobre finanças, quant ou engenharia. Alcança-se como qualquer índice: leia a célula "O que
responde", abra **apenas** a nota que a tarefa exige, e pare quando tiver o suficiente. As notas
moram em duas pastas — o índice tem uma seção por pasta.

O que este vault ainda **não** tem mora em [[_backlog]]: dezenas de notas que as 13 existentes
citam por wikilink mas que nunca foram escritas. Se você procurou um tema de Claude Code e não o
achou abaixo, confira o backlog antes de concluir que a casa não cobre — pode ser roadmap, não
lacuna.

## Fundamentos — `shared/claude/01-fundamentals/`

| Nota | O que responde | Nível |
|---|---|---|
| [[what-is-claude-code]] | O que é o Claude Code e por que ele **age** em vez de só responder: instalação por OS (npm, Homebrew, WSL), o loop percepção→raciocínio→ação com a Tool Use API, os modos de operação (interativo/REPL, headless `--print`, pipe, subagentes, worktrees), integração com IDEs, comandos e flags do dia a dia, e como se compara a Copilot, Cursor e Aider. | intro |
| [[claude-code-vs-api-vs-chat]] | Qual das quatro interfaces da Anthropic usar para cada tarefa — Claude Code (CLI), Messages API, Claude Chat (claude.ai) e Desktop: capabilities e limitações de cada uma, rate limits da API por tier, tabela comparativa completa e o fluxograma de decisão (modificar arquivos → CLI; construir produto → API; processar volume → Batch; explorar → Chat). | intro |
| [[claude-models-overview]] | Qual modelo Claude escolher: a família Haiku/Sonnet/Opus e o trade-off custo×qualidade×velocidade, os model IDs e versões (3.x e 4.x) e por que fixar o ID completo em produção, quais modelos suportam Extended Thinking e quando ligá-lo, e como selecionar modelo no Claude Code (`--model`, `/model`, settings.json) e via API. | intro |
| [[context-window-management]] | Como não estourar a janela de 200K tokens: o que compõe e o que consome o contexto, auto-compactação, `/compact` vs `/clear`, leitura seletiva (offset/limit, grep antes de ler), subagentes com contexto isolado, os sinais de que o contexto está cheio, e o impacto do CLAUDE.md — cobrado em toda mensagem. | intro |
| [[pricing-and-tokens]] | Quanto custa usar Claude e como reduzir: input vs output tokens, prompt caching (write 25% acima, read 90% abaixo), Batch API (50% off), planos Pro/Max/Team vs API key pay-as-you-go, como contar tokens, e calculadoras de custo por cenário real (chatbot, PDFs em massa, code review em CI). | intro |

## Recursos principais — `shared/claude/02-core-features/`

| Nota | O que responde | Nível |
|---|---|---|
| [[skills-system]] | O que são skills e como escrevê-las: rígidas (processo exato, guardrails) vs flexíveis (estilo, julgamento), o frontmatter e por que o campo `description` decide o matching automático, onde salvar (global `~/.claude/skills/` vs local, com prioridade do local), a estrutura completa de uma skill, e como skill difere de CLAUDE.md, slash command, hook e memory. | intermediate |
| [[hooks-system]] | Como disparar comandos shell automaticamente em eventos do ciclo de vida — PreToolUse, PostToolUse, Notification, Stop, SubagentStop: a configuração em settings.json, as variáveis de ambiente injetadas (`CLAUDE_TOOL_INPUT` etc.), hooks bloqueantes (PreToolUse como guardrail) vs não-bloqueantes com `|| true`, exemplos prontos (auto-lint, auto-format, auditoria, Slack) e debugging. | intermediate |
| [[mcp-servers]] | Como integrar o Claude Code a sistemas externos via Model Context Protocol: a arquitetura cliente/servidor, servidor stdio (local) vs SSE (remoto), como registrar em settings.json e via `claude mcp`, o protocolo JSON-RPC 2.0, a tríade tools/resources/prompts, como escrever um servidor mínimo em TypeScript e em Python, servidores prontos e o que não expor por segurança. | intermediate |
| [[subagents]] | Como o Agent tool despacha subagentes de contexto isolado: os parâmetros (qual agente, modelo, `tools`, `isolation`, `run_in_background`), foreground/síncrono vs background/paralelo, como devolvem resultado (texto, JSON, arquivo), os patterns research/implementation/review/coordinator, o custo que multiplica, quando **não** usar, e a regra do prompt self-contained. | intermediate |
| [[agent-teams]] | Como orquestrar um time de agentes especializados: a estrutura de `.claude/agents/`, o formato do system prompt de um agente, o case study dos 10 agentes da Vault Inc, como o orquestrador lê os arquivos e despacha, a ordem de dependência entre eles (PM→UI/UX→Frontend; Lead→Backend; QA valida), e a comunicação mediada por relatório escrito. | intermediate |
| [[worktrees]] | O que são git worktrees e por que isolam trabalho paralelo sem conflito de arquivo: como o Claude Code os usa com `isolation: "worktree"`, o setup manual (`add`/`list`/`merge`/`remove`), as ferramentas EnterWorktree/ExitWorktree, a combinação com subagentes em background, quando usar ou não, e os gotchas (uma branch por worktree, `.env` não copiado, `node_modules` duplicado). | intermediate |
| [[slash-commands]] | Os comandos que se digitam com `/`: os built-in (`/help`, `/clear`, `/compact`, `/model`, `/cost`, `/status`, `/init`, `/review`, `/doctor`, `/pr-comments`…), como criar custom commands em `.claude/commands/` com `$ARGUMENTS`, a diferença entre command (ação pontual que termina) e skill (comportamento contínuo), os keyboard shortcuts, e global vs local. | intermediate |
| [[permissions-and-safety]] | Como calibrar o que o Claude executa sem pedir permissão: os modos ask/auto-accept/deny, os arrays `allow`/`deny` em settings.json e a sintaxe glob, `allowedTools`/`disallowedTools` (nível de ferramenta) vs `permissions` (nível de comando), sandbox mode, permissões por projeto vs global, o que **nunca** auto-aprovar (git destrutivo, `rm -rf`, deploy, DROP), e auditoria via hook. | intermediate |
