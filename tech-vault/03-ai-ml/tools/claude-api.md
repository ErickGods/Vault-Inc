---
tags: [skill, ai-ml, claude-api]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Claude API, Anthropic API]
---

# Claude API (Anthropic API)

## Overview

A Claude API (Anthropic API) é a interface programática para os modelos Claude. A API segue o padrão Messages, onde cada requisição define uma sequência de mensagens com roles `user` e `assistant`, mais um `system` prompt opcional. Suporta text, imagens, documentos PDF, tool use e streaming via SSE.

O endpoint principal é `POST https://api.anthropic.com/v1/messages`. Autenticação via header `x-api-key`. SDKs oficiais disponíveis para [[python]] e [[typescript]].

> [!important] Versioning
> Sempre inclua o header `anthropic-version: 2023-06-01`. Sem ele, requests podem falhar ou usar comportamentos legados.

Integra-se com [[langchain]], [[mcp-servers-guide]] e é a base de [[claude-code-superpowers]].

## Core Concepts

### Messages API: Roles, Content Blocks, Multi-Turn

```python
import anthropic

client = anthropic.Anthropic()

# Single turn
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system="You are an expert software architect.",
    messages=[
        {"role": "user", "content": "Review this architecture and suggest improvements."}
    ],
)
print(message.content[0].text)

# Multi-turn conversation
conversation = [
    {"role": "user", "content": "Explain CQRS pattern"},
    {"role": "assistant", "content": "CQRS (Command Query Responsibility Segregation)..."},
    {"role": "user", "content": "How does it differ from Event Sourcing?"},
]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=2048,
    messages=conversation,
)
```

**Content blocks permitem múltiplos tipos em uma mensagem:**

```python
message = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this image and this code:"},
                {"type": "image", "source": {"type": "url", "url": "https://..."}},
                {"type": "text", "text": "```python\ndef foo(): pass\n```"},
            ],
        }
    ],
)
```

### Tool Use: Definition, tool_choice, tool_result

```python
tools = [
    {
        "name": "get_stock_price",
        "description": "Get the current stock price for a ticker symbol",
        "input_schema": {
            "type": "object",
            "properties": {
                "ticker": {
                    "type": "string",
                    "description": "Stock ticker symbol (e.g., AAPL, GOOGL)",
                },
                "currency": {
                    "type": "string",
                    "enum": ["USD", "EUR", "BRL"],
                    "default": "USD",
                },
            },
            "required": ["ticker"],
        },
    }
]

# tool_choice controla quando usar ferramentas
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    tools=tools,
    tool_choice={"type": "auto"},          # auto | any | tool | none
    # tool_choice={"type": "tool", "name": "get_stock_price"},  # forçar tool específica
    messages=[{"role": "user", "content": "What's Apple's current stock price?"}],
)

# Processar tool calls
if response.stop_reason == "tool_use":
    tool_use = next(b for b in response.content if b.type == "tool_use")
    result = execute_tool(tool_use.name, tool_use.input)

    # Continuar conversa com tool_result
    final = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        tools=tools,
        messages=[
            {"role": "user", "content": "What's Apple's stock price?"},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": str(result),
                    }
                ],
            },
        ],
    )
```

### Vision: Image Content Blocks

```python
import base64

# Via base64 (arquivos locais)
with open("diagram.png", "rb") as f:
    image_data = base64.standard_b64encode(f.read()).decode("utf-8")

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/png",   # image/jpeg, image/gif, image/webp
                        "data": image_data,
                    },
                },
                {"type": "text", "text": "Describe this architecture diagram."},
            ],
        }
    ],
)

# Via URL (imagens públicas)
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "image", "source": {"type": "url", "url": "https://example.com/img.jpg"}},
                {"type": "text", "text": "What's in this image?"},
            ],
        }
    ],
)
```

## Patterns

### Streaming via SSE

```python
# Python streaming
with client.messages.stream(
    model="claude-opus-4-5",
    max_tokens=4096,
    messages=[{"role": "user", "content": "Write a detailed technical spec"}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)

    # Acessar message final com metadados
    final = stream.get_final_message()
    print(f"\nTokens: {final.usage.input_tokens} in, {final.usage.output_tokens} out")
```

```typescript
// TypeScript streaming
const stream = await client.messages.stream({
  model: "claude-opus-4-5",
  max_tokens: 4096,
  messages: [{ role: "user", content: "Explain quantum entanglement" }],
});

for await (const chunk of stream) {
  if (chunk.type === "content_block_delta" && chunk.delta.type === "text_delta") {
    process.stdout.write(chunk.delta.text);
  }
}

const finalMessage = await stream.finalMessage();
```

### Batches API

Para processar grandes volumes de requisições com desconto de custo:

```python
# Criar batch (até 10.000 requisições por batch)
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"request-{i}",
            "params": {
                "model": "claude-haiku-4-5",
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": item}],
            },
        }
        for i, item in enumerate(documents)
    ]
)

print(f"Batch ID: {batch.id}")

# Verificar status
import time
while True:
    status = client.messages.batches.retrieve(batch.id)
    if status.processing_status == "ended":
        break
    time.sleep(60)

# Recuperar resultados
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        print(f"{result.custom_id}: {result.result.message.content[0].text}")
```

### Prompt Caching

Reduz custo e latência em prompts com contexto grande e reutilizável:

```python
# cache_control: {"type": "ephemeral"} marca o breakpoint de cache
# Tudo ANTES do breakpoint é cacheado

response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=1024,
    system=[
        {
            "type": "text",
            "text": "You are an expert code reviewer.",
        },
        {
            "type": "text",
            "text": entire_codebase_context,   # 50k+ tokens
            "cache_control": {"type": "ephemeral"},   # BREAKPOINT aqui
        },
    ],
    messages=[{"role": "user", "content": "Review the auth module for security issues"}],
)

# Verificar cache hit
print(response.usage.cache_read_input_tokens)      # tokens lidos do cache
print(response.usage.cache_creation_input_tokens)  # tokens criados no cache
```

**Regras do cache:**
- TTL padrão: 5 minutos (ephemeral)
- Custo de escrita: 25% mais caro que tokens normais
- Custo de leitura: 90% mais barato que tokens normais
- Mínimo 1024 tokens para ser cacheado
- Até 4 breakpoints por requisição

### Anthropic SDK Python

```python
# Sync client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
    max_retries=3,
    timeout=60.0,
)

# Async client
async_client = anthropic.AsyncAnthropic()

async def process_batch(prompts: list[str]) -> list[str]:
    tasks = [
        async_client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": p}],
        )
        for p in prompts
    ]
    results = await asyncio.gather(*tasks)
    return [r.content[0].text for r in results]
```

### Anthropic SDK TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
  maxRetries: 3,
  timeout: 60 * 1000,
});

// Token counting antes de enviar
const tokenCount = await client.messages.countTokens({
  model: "claude-opus-4-5",
  system: "You are helpful.",
  messages: [{ role: "user", content: longDocument }],
});
console.log(`Estimated tokens: ${tokenCount.input_tokens}`);
```

### Error Handling e Rate Limits

```python
from anthropic import (
    APIConnectionError,
    RateLimitError,
    APIStatusError,
    BadRequestError,
)

def call_with_retry(prompt: str, max_retries: int = 5) -> str:
    for attempt in range(max_retries):
        try:
            response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text

        except RateLimitError as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt        # exponential backoff
            time.sleep(wait)

        except APIConnectionError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(1)

        except BadRequestError as e:
            # Não retry em erros de validação
            raise ValueError(f"Invalid request: {e.message}") from e

        except APIStatusError as e:
            if e.status_code >= 500:   # retry em erros de servidor
                time.sleep(2 ** attempt)
            else:
                raise
```

### System Prompts Best Practices

```python
# Estrutura recomendada para system prompts complexos
system_prompt = """<role>
You are a senior software engineer specializing in Python and distributed systems.
</role>

<context>
You are reviewing code for a high-traffic e-commerce platform (10M requests/day).
Performance, security, and maintainability are critical.
</context>

<guidelines>
- Prioritize security issues first
- Flag O(n²) or worse complexity
- Suggest specific, actionable improvements
- Include code examples for non-trivial suggestions
</guidelines>

<output_format>
Structure your review as:
1. Critical Issues (must fix)
2. Important Improvements (should fix)
3. Minor Suggestions (nice to have)
</output_format>"""
```

## Gotchas

> [!warning] max_tokens é Obrigatório
> Ao contrário de outras APIs, `max_tokens` é obrigatório na Claude API. Omitir causa erro 400. Use valores adequados ao seu caso de uso.

> [!bug] Tool Results e Content Blocks
> `tool_result` deve ser enviado no role `user`, não `assistant`. E o campo `content` dentro de `tool_result` deve ser uma lista de content blocks, não uma string direta (embora strings funcionem como atalho).

> [!caution] Prompt Caching e Não-Determinismo
> Cache hits podem retornar respostas ligeiramente diferentes devido ao sampling com temperatura > 0. Para outputs determinísticos, use `temperature=0`.

> [!tip] Integração com [[mcp-servers-guide]]
> A Claude API não tem suporte nativo a MCP — isso é gerenciado pelo host (Claude Code, Claude Desktop). Para usar MCP diretamente via API, você precisa implementar o cliente MCP no seu aplicativo.

## Snippets

### Token Counting

```python
# Contar tokens antes de enviar (útil para validar contexto)
response = client.messages.count_tokens(
    model="claude-opus-4-5",
    system="You are helpful.",
    tools=tools,
    messages=messages,
)
print(f"Input tokens: {response.input_tokens}")
```

### Modelos Disponíveis

```
claude-opus-4-5          → máxima capacidade, mais caro
claude-sonnet-4-5        → balanço capacidade/custo (recomendado)
claude-haiku-4-5         → mais rápido e barato (tasks simples)
claude-3-5-sonnet-20241022  → versão estável anterior
```

### Extended Thinking

```python
# Ativa raciocínio profundo (aumenta qualidade em problemas complexos)
response = client.messages.create(
    model="claude-opus-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000,    # tokens reservados para raciocínio
    },
    messages=[{"role": "user", "content": complex_math_problem}],
)

for block in response.content:
    if block.type == "thinking":
        print(f"Reasoning: {block.thinking}")
    elif block.type == "text":
        print(f"Answer: {block.text}")
```

## References

- [Anthropic API Docs](https://docs.anthropic.com/en/api/)
- [Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [TypeScript SDK](https://github.com/anthropics/anthropic-sdk-typescript)
- [Model Cards](https://docs.anthropic.com/en/docs/about-claude/models)

## Related

- [[python]] — SDK Python oficial
- [[typescript]] — SDK TypeScript oficial
- [[prompt-engineering]] — melhores práticas para prompts
- [[langchain]] — integração via LangChain
- [[mcp-servers-guide]] — expandir capacidades via MCP
