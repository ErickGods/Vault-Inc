---
tags: [claude-code, fundamentals]
aliases: [Claude Interfaces, CLI vs API vs Chat, Quando usar Claude]
house: shared
domain: claude/fundamentals
level: intro
status: active
created: 2026-04-19
updated: 2026-08-01
---

# Claude Code vs API vs Chat

## Overview

A Anthropic oferece múltiplas interfaces para interagir com os modelos Claude, cada uma projetada para casos de uso distintos. Escolher a interface errada é um dos erros mais comuns — usar o chat para tarefas que requerem automação, ou chamar a API diretamente quando o Claude Code resolveria em segundos.

Este documento mapeia cada interface, suas capacidades reais, limitações, e fornece um guia de decisão para escolher a interface certa para cada situação.

> [!info] Quatro interfaces principais
> 1. **Claude Code** — CLI/terminal para desenvolvimento agentico
> 2. **Claude API** (Messages API) — integração programática em aplicações
> 3. **Claude Chat** (claude.ai) — interface web conversacional
> 4. **Claude Desktop** — app nativo com capabilities extras

Integra com [[what-is-claude-code]], [[claude-models-overview]], e [[pricing-and-tokens]].

---

## Claude Code (Terminal / CLI)

### O que é

CLI oficial da Anthropic instalada via `npm install -g @anthropic-ai/claude-code`. Roda no terminal e opera diretamente no ambiente de desenvolvimento do usuário com acesso ao sistema de arquivos, shell, e ferramentas do projeto.

### Quando usar

- Desenvolvimento de software: implementar features, refatorar, debugar
- Tarefas que requerem ler/escrever múltiplos arquivos
- Operações git (commits, branches, PRs)
- Rodar comandos do projeto (testes, builds, linters)
- Automação de tarefas de desenvolvimento repetitivas
- Análise de repositórios completos

### Capabilities

```
✓ Leitura/escrita de arquivos no sistema
✓ Execução de comandos bash
✓ Operações git completas
✓ Navegação em repositórios (glob, grep)
✓ Chamadas HTTP (WebFetch)
✓ Subagentes paralelos
✓ Sessões persistentes com histórico
✓ CLAUDE.md para contexto de projeto
✓ Integração com ferramentas MCP
✓ Worktrees para isolamento
```

### Limitações

```
✗ Sem interface gráfica nativa
✗ Requer terminal e Node.js instalados
✗ Não integra com ferramentas não-CLI nativamente
✗ Contexto reseta entre sessões (sem memória persistente automática)
```

### Pricing

- **Plano Pro**: ~$20/mês — limite de uso mensal incluso
- **Plano Max**: ~$100/mês — limites maiores
- **Plano Team**: ~$25/usuário/mês — colaboração em equipe
- **API Key direta**: pay-as-you-go por token (sem plano necessário)

### Exemplo de uso

```bash
# Implementar uma feature completa
cd /meu-projeto
claude

> Implemente um endpoint POST /api/payments com validação de Pix
> Rode os testes e corrija falhas
> Faça commit com mensagem descritiva
```

---

## Claude API (Messages API)

### O que é

API REST programática para integrar Claude diretamente em aplicações, scripts, e pipelines de dados. Acessada via SDK oficial (Python, TypeScript) ou HTTP direto.

### Quando usar

- Construir produtos e features com Claude embutido
- Pipelines de processamento de dados em escala
- Automações server-side (background jobs, webhooks)
- Aplicações com lógica customizada em torno das respostas
- Quando você precisa controle total sobre o contexto enviado
- Integração em sistemas existentes (CRMs, ERPs, dashboards)
- Streaming de respostas para UI em tempo real

### Capabilities

```
✓ Controle total sobre mensagens e contexto
✓ Streaming de tokens
✓ Prompt caching (economia de custo)
✓ Batch API (50% desconto, processamento async)
✓ Tool use / function calling
✓ Extended thinking
✓ Vision (análise de imagens)
✓ Files API (upload de documentos)
✓ Multi-turn conversations
✓ Rate limits configuráveis
✓ Qualquer linguagem com HTTP
```

### Limitações

```
✗ Sem acesso ao sistema de arquivos do servidor (você gerencia)
✗ Sem estado entre requests (você mantém histórico)
✗ Configuração e manutenção de infra é sua responsabilidade
✗ Rate limits por tier de conta
✗ Custo pode escalar inesperadamente sem monitoramento
```

### Rate Limits (por tier)

| Tier | RPM | TPM | TPMD |
|------|-----|-----|------|
| Free | 5 | 25K | 300K |
| Tier 1 ($5 gasto) | 50 | 50K | 1M |
| Tier 2 ($50 gasto) | 1000 | 100K | 10M |
| Tier 3 ($500 gasto) | 2000 | 200K | 100M |
| Tier 4 ($5K gasto) | 4000 | 400K | — |

*RPM = Requests por minuto, TPM = Tokens por minuto, TPMD = Tokens por dia*

### Snippets básicos

**Python:**
```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

# Request básico
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{
        "role": "user",
        "content": "Explique dependency injection em Python"
    }]
)
print(response.content[0].text)

# Streaming
with client.messages.stream(
    model="claude-sonnet-4-6",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Gere um README para meu projeto"}]
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)
```

**TypeScript:**
```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// Request básico
const response = await client.messages.create({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Analise este código" }],
});

// Streaming
const stream = await client.messages.stream({
  model: "claude-sonnet-4-6",
  max_tokens: 1024,
  messages: [{ role: "user", content: "Explique o código" }],
});

for await (const chunk of stream) {
  if (chunk.type === "content_block_delta" && chunk.delta.type === "text_delta") {
    process.stdout.write(chunk.delta.text);
  }
}
```

---

## Claude Chat (claude.ai)

### O que é

Interface web conversacional acessada pelo browser em [claude.ai](https://claude.ai). Projetada para uso humano direto — conversação, exploração de ideias, criação de documentos.

### Quando usar

- Exploração e ideação sem estrutura definida
- Perguntas rápidas sem necessidade de código
- Rascunho de documentos, emails, apresentações
- Aprendizado de conceitos novos
- Quando você não quer configurar nada
- Brainstorming e discussões abertas
- Upload e análise de documentos PDF (plano Pro)

### Capabilities

```
✓ Interface amigável, sem setup
✓ Upload de arquivos (PDF, imagens, código)
✓ Análise de imagens
✓ Projects — contexto persistente entre conversas
✓ Artifacts — geração de HTML/React interativo no browser
✓ Memória (quando habilitada)
✓ Modelos mais recentes disponíveis
✓ Grátis (com limites) ou Pro ($20/mês)
```

### Limitações

```
✗ Sem acesso ao sistema de arquivos local
✗ Sem execução de código (apenas sugestões)
✗ Sem automação — você copia e cola manualmente
✗ Contexto entre sessões depende de Projects/Memória
✗ Rate limits mais restritivos no plano grátis
✗ Não escalável para volume
```

### Quando NÃO usar

- Quando você precisa que o Claude modifique arquivos reais → use Claude Code
- Quando você está construindo um produto → use a API
- Quando você tem 100+ documentos para processar → use Batch API
- Quando precisa integrar com seu pipeline → use a API

---

## Claude Desktop App

### O que é

Aplicativo nativo (macOS e Windows) que oferece uma experiência mais integrada que o browser, com capabilities adicionais via MCP (Model Context Protocol).

### Quando usar

- Uso pessoal com integração mais profunda ao OS
- Quando você quer conectar Claude a ferramentas locais via MCP
- Melhor experiência offline (contexto local)
- Integração com apps nativos (Obsidian, arquivos locais, etc.)

### Capabilities extras vs web

```
✓ Servidores MCP locais (acesso a arquivos, databases, APIs)
✓ Integração com apps nativos
✓ Melhor performance que browser
✓ Menos friction que abrir browser
```

> [!tip] Claude Desktop + MCP
> O Claude Desktop é especialmente poderoso com servidores MCP. Por exemplo: conectar ao Obsidian via MCP server e ter o Claude lendo/escrevendo notas diretamente, sem copiar e colar.

---

## Tabela Comparativa Completa

| Feature | Claude Code | Messages API | Claude Chat | Claude Desktop |
|---------|------------|--------------|-------------|----------------|
| **Acesso a arquivos locais** | Sim (total) | Não | Não | Via MCP |
| **Execução de bash** | Sim | Não | Não | Não |
| **Operações git** | Sim | Não | Não | Não |
| **Streaming** | Sim | Sim | Sim | Sim |
| **Tool use** | Sim (built-in) | Sim (configurável) | Parcial | Via MCP |
| **Extended thinking** | Sim | Sim | Sim | Sim |
| **Vision (imagens)** | Sim | Sim | Sim | Sim |
| **Upload PDF** | Via bash | Via Files API | Sim | Via MCP |
| **Multi-turn** | Sim (sessão) | Sim (você gerencia) | Sim | Sim |
| **Contexto persistente** | CLAUDE.md | Você implementa | Projects | Memória |
| **Subagentes paralelos** | Sim | Via código | Não | Não |
| **Automação/script** | Sim (`--print`) | Sim (nativo) | Não | Não |
| **Rate limits** | Pelo plano | Por tier | Por plano | Por plano |
| **Custo base** | $20-100/mês | Pay-as-you-go | Grátis/$20 | Grátis/$20 |
| **Setup necessário** | npm install | SDK + API key | Nenhum | Download |
| **Multimodal output** | Texto + código | Texto + código | Artifacts (HTML/React) | Texto + código |

---

## Fluxograma de Decisão

```
Você tem uma tarefa para Claude. Qual interface usar?

┌─────────────────────────────────────────────┐
│ Você precisa MODIFICAR ou CRIAR arquivos     │
│ no seu projeto?                              │
└─────────────────────────────────────────────┘
         │ SIM                    │ NÃO
         ▼                        ▼
   Claude Code             ┌──────────────────┐
   (CLI terminal)          │ Você está         │
                           │ CONSTRUINDO       │
                           │ UM PRODUTO?       │
                           └──────────────────┘
                              │ SIM     │ NÃO
                              ▼         ▼
                         Messages   ┌───────────────┐
                           API      │ Você precisa   │
                                    │ PROCESSAR      │
                                    │ VOLUME (100+)? │
                                    └───────────────┘
                                       │ SIM   │ NÃO
                                       ▼       ▼
                                   Batch    Claude Chat
                                    API     ou Desktop
                                    
┌─────────────────────────────────────────────────────┐
│ REGRAS RÁPIDAS:                                      │
│ • Modificar arquivos do projeto → Claude Code        │
│ • Construir produto/feature com IA → Messages API    │
│ • Processar 100+ documentos → Batch API              │
│ • Exploração, chat, rascunhos → Claude Chat/Desktop  │
│ • Integrar com apps locais → Claude Desktop + MCP   │
└─────────────────────────────────────────────────────┘
```

---

## Exemplos Concretos por Interface

### Cenário 1: Implementar autenticação OAuth no backend

**Interface correta: Claude Code**
```bash
cd /meu-projeto
claude
> Implemente OAuth 2.0 com Google no endpoint /auth/google
> Use python-social-auth, adicione os testes
> Atualize o .env.example com as variáveis necessárias
```

Por quê: requer ler múltiplos arquivos, escrever código, editar configurações, rodar testes.

### Cenário 2: Classificar 10.000 reviews de produto

**Interface correta: Batch API**
```python
requests = [
    {
        "custom_id": f"review-{i}",
        "params": {
            "model": "claude-haiku-4-5",
            "max_tokens": 20,
            "messages": [{"role": "user", "content": f"Classifique: {review}"}]
        }
    }
    for i, review in enumerate(reviews)
]

batch = client.messages.batches.create(requests=requests)
```

Por quê: volume alto, latência não crítica, custo 50% menor com Batch API.

### Cenário 3: Chatbot de suporte no seu SaaS

**Interface correta: Messages API**
```python
def handle_support_message(user_id: str, message: str, history: list):
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system="Você é o assistente de suporte da MinhaNuvem...",
        messages=history + [{"role": "user", "content": message}]
    )
    return response.content[0].text
```

Por quê: precisa de controle total sobre o sistema prompt, gerenciar histórico por usuário, integrar com banco de dados.

### Cenário 4: Entender o código de um projeto open source

**Interface correta: Claude Chat ou Claude Code**
- Se só quer entender → Claude Chat (cole os trechos relevantes)
- Se quer modificar ou contribuir → Claude Code (navegue o repo real)

### Cenário 5: Gerar relatório semanal de métricas

**Interface correta: Messages API (script agendado)**
```python
# Script Python agendado via cron
def generate_weekly_report():
    metrics = fetch_metrics_from_db()
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"Gere um relatório executivo com estes dados: {metrics}"
        }]
    )
    
    send_email(report=response.content[0].text)
```

### Cenário 6: Brainstorm de naming para nova feature

**Interface correta: Claude Chat**
- Conversa aberta, exploração criativa, sem necessidade de código ou automação.
- Chat é perfeito para isso.

---

## Migrar de Chat para Claude Code

Um padrão comum: você começa explorando no chat e depois quer implementar. Aqui como fazer a transição:

```
1. No chat: "Mostre o código da solução que você descreveu"
2. Copie o código para um arquivo no projeto
3. Abra o terminal: cd /meu-projeto && claude
4. > "Revise o arquivo recém-criado auth.py e integre com o sistema existente"
```

---

## Related

- [[what-is-claude-code]] — Detalhes da CLI do Claude Code
- [[claude-models-overview]] — Modelos disponíveis em cada interface
- [[pricing-and-tokens]] — Custo de cada interface
- [[context-window-management]] — Gerenciar contexto em cada interface
- [[../04-api-and-sdk/messages-api-reference]] — Referência completa da API
- [[../04-api-and-sdk/batch-api]] — Processamento em lote
