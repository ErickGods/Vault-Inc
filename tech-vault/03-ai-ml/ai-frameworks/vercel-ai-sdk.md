---
tags: [skill, ai-ml, vercel-ai-sdk]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Vercel AI SDK, AI SDK]
---

# Vercel AI SDK

## Overview

O Vercel AI SDK é o framework [[typescript]] de referência para integrar LLMs em aplicações web, com suporte nativo a [[react]], [[nextjs]] e qualquer runtime JavaScript. Sua proposta central é unificar a interface de múltiplos provedores (OpenAI, Anthropic, Google, etc.) enquanto fornece primitivas de streaming, structured outputs e tool calling prontas para produção.

O SDK divide-se em três camadas:
- **AI SDK Core** — funções de servidor: `generateText`, `streamText`, `generateObject`, `streamObject`
- **AI SDK UI** — hooks de cliente: `useChat`, `useCompletion`, `useObject`
- **AI SDK RSC** — integração com React Server Components via `streamUI`

> [!important] Provider Registry
> Cada provedor é um pacote separado: `@ai-sdk/openai`, `@ai-sdk/anthropic`, `@ai-sdk/google`. Isso permite tree-shaking e atualizações independentes.

Ideal para integrar [[claude-api]] em aplicações [[nextjs]] com streaming em tempo real.

## Core Concepts

### useChat Hook

```typescript
"use client";
import { useChat } from "ai/react";

export function ChatInterface() {
  const {
    messages,
    input,
    handleInputChange,
    handleSubmit,
    isLoading,
    error,
    reload,
    stop,
    append,
  } = useChat({
    api: "/api/chat",
    initialMessages: [],
    onFinish: (message) => {
      analytics.track("chat_message_complete", {
        role: message.role,
        tokens: message.usage?.totalTokens,
      });
    },
    onError: (error) => console.error("Chat error:", error),
  });

  return (
    <div>
      {messages.map((m) => (
        <div key={m.id} data-role={m.role}>
          {m.content}
          {m.toolInvocations?.map((tool) => (
            <ToolResult key={tool.toolCallId} invocation={tool} />
          ))}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} />
        <button type="submit" disabled={isLoading}>Send</button>
        {isLoading && <button type="button" onClick={stop}>Stop</button>}
      </form>
    </div>
  );
}
```

### streamText no Servidor

```typescript
// app/api/chat/route.ts
import { streamText } from "ai";
import { anthropic } from "@ai-sdk/anthropic";

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = await streamText({
    model: anthropic("claude-opus-4-5"),
    system: "You are a helpful assistant.",
    messages,
    maxTokens: 4096,
    temperature: 0.7,
    onFinish: async ({ text, usage, finishReason }) => {
      await db.conversations.create({
        content: text,
        inputTokens: usage.promptTokens,
        outputTokens: usage.completionTokens,
      });
    },
  });

  return result.toDataStreamResponse();
}
```

### generateObject: Structured Output com Zod

Elimina a necessidade de parsear JSON manualmente:

```typescript
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { z } from "zod";

const productSchema = z.object({
  name: z.string(),
  category: z.enum(["electronics", "clothing", "food", "other"]),
  price: z.number().positive(),
  features: z.array(z.string()).min(3),
  inStock: z.boolean(),
  metadata: z.object({
    sku: z.string(),
    weight: z.number().optional(),
  }),
});

const { object } = await generateObject({
  model: openai("gpt-4o"),
  schema: productSchema,
  prompt: "Extract product information from: MacBook Pro M4 - $2499 - In Stock",
  mode: "json",    // json | tool | auto
});

// object é tipado como z.infer<typeof productSchema>
console.log(object.category);  // "electronics"
console.log(object.price);     // 2499
```

**streamObject para outputs parciais em tempo real:**

```typescript
import { streamObject } from "ai";

const { partialObjectStream } = await streamObject({
  model: anthropic("claude-sonnet-4-5"),
  schema: reportSchema,
  prompt: "Generate a detailed market analysis report",
});

for await (const partial of partialObjectStream) {
  // partial é atualizado incrementalmente
  updateUI(partial);
}
```

## Patterns

### Tool Calling Server-Side

```typescript
import { streamText, tool } from "ai";
import { z } from "zod";

const result = await streamText({
  model: openai("gpt-4o"),
  tools: {
    getWeather: tool({
      description: "Get current weather for a location",
      parameters: z.object({
        location: z.string().describe("City name or coordinates"),
        unit: z.enum(["celsius", "fahrenheit"]).default("celsius"),
      }),
      execute: async ({ location, unit }) => {
        const data = await weatherApi.fetch(location, unit);
        return {
          temperature: data.temp,
          condition: data.condition,
          humidity: data.humidity,
        };
      },
    }),

    searchDatabase: tool({
      description: "Search internal knowledge base",
      parameters: z.object({
        query: z.string(),
        limit: z.number().min(1).max(20).default(5),
      }),
      execute: async ({ query, limit }) => {
        return await vectorDb.search(query, limit);
      },
    }),
  },
  maxSteps: 5,    // permite múltiplos ciclos de tool calling
  messages,
});
```

### Multi-Step Tool Calls

Com `maxSteps > 1`, o modelo pode chamar ferramentas múltiplas vezes:

```typescript
// O modelo pode: search → analyze → search again → summarize
const result = await generateText({
  model: anthropic("claude-opus-4-5"),
  tools: { search: searchTool, calculate: calcTool },
  maxSteps: 10,
  onStepFinish: ({ text, toolCalls, toolResults, stepType }) => {
    console.log(`Step: ${stepType}, Tools used: ${toolCalls.length}`);
  },
  prompt: "Research the ROI of renewable energy vs fossil fuels in 2025",
});

console.log(result.steps.length);      // quantos steps foram necessários
console.log(result.text);              // output final consolidado
```

### Provider Registry

```typescript
import { createProviderRegistry } from "ai";
import { anthropic } from "@ai-sdk/anthropic";
import { openai } from "@ai-sdk/openai";
import { google } from "@ai-sdk/google";

export const registry = createProviderRegistry({
  anthropic,
  openai,
  google,
});

// Usar qualquer modelo via string
const result = await generateText({
  model: registry.languageModel("anthropic:claude-opus-4-5"),
  prompt: "Hello",
});

// Ou via variável de ambiente
const model = registry.languageModel(process.env.AI_MODEL ?? "openai:gpt-4o");
```

### Middleware: Guardrails, Logging, Caching

```typescript
import { wrapLanguageModel, extractReasoningMiddleware } from "ai";

const modelWithMiddleware = wrapLanguageModel({
  model: anthropic("claude-opus-4-5"),
  middleware: {
    // Interceptar e modificar parâmetros antes da chamada
    transformParams: async ({ params }) => {
      return {
        ...params,
        system: `${params.system}\nAlways respond in the user's language.`,
      };
    },

    // Interceptar response para logging
    wrapGenerate: async ({ doGenerate, params }) => {
      const start = Date.now();
      const result = await doGenerate();
      metrics.record("llm.latency", Date.now() - start);
      return result;
    },

    // Cache de respostas determinísticas
    wrapStream: async ({ doStream, params }) => {
      const cacheKey = hashParams(params);
      const cached = await cache.get(cacheKey);
      if (cached) return createCachedStream(cached);

      const result = await doStream();
      await cache.set(cacheKey, result, { ttl: 3600 });
      return result;
    },
  },
});
```

### AI RSC: Server Components Integration

```typescript
// lib/actions.ts
"use server";
import { streamUI } from "ai/rsc";
import { openai } from "@ai-sdk/openai";

export async function generateDashboard(query: string) {
  const result = await streamUI({
    model: openai("gpt-4o"),
    prompt: query,
    text: ({ content }) => <p>{content}</p>,
    tools: {
      showChart: {
        description: "Display a chart with data",
        parameters: z.object({
          type: z.enum(["bar", "line", "pie"]),
          data: z.array(z.object({ label: z.string(), value: z.number() })),
        }),
        generate: async ({ type, data }) => (
          <ChartComponent type={type} data={data} />
        ),
      },
    },
  });
  return result.value;
}
```

### Streaming Protocols

O SDK suporta dois protocolos de streaming:

```typescript
// Data Stream Protocol (padrão) — para useChat
return result.toDataStreamResponse({
  headers: { "X-Custom-Header": "value" },
  sendUsage: true,            // envia token usage ao cliente
  sendReasoning: true,        // envia thinking tokens (Claude)
});

// Text Stream Protocol — para outputs simples
return result.toTextStreamResponse();

// Consumir manualmente
for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

## Gotchas

> [!warning] useChat e Route Handlers
> `useChat` espera que o endpoint `/api/chat` retorne um Data Stream Response. Retornar JSON simples quebra o parsing do hook. Use sempre `result.toDataStreamResponse()`.

> [!bug] generateObject com Schemas Complexos
> Schemas Zod muito profundos (>4 níveis de aninhamento) podem falhar com alguns modelos. Simplifique ou use `mode: "json"` com validação manual.

> [!caution] maxSteps e Custo
> `maxSteps: 10` pode resultar em 10 chamadas separadas ao LLM se o modelo continuar chamando ferramentas. Defina limites conservadores em produção e monitore via `onStepFinish`.

> [!tip] [[prompt-engineering]] com streamText
> Use o parâmetro `system` em vez de adicionar uma system message no array `messages`. O SDK otimiza o posicionamento do system prompt por provedor.

## Snippets

### useCompletion para One-Shot

```typescript
const { completion, complete, isLoading } = useCompletion({
  api: "/api/complete",
});

await complete("Summarize this document: ...");
```

### Embed com AI SDK

```typescript
import { embed, embedMany } from "ai";
import { openai } from "@ai-sdk/openai";

const { embedding } = await embed({
  model: openai.embedding("text-embedding-3-small"),
  value: "Document text to embed",
});

const { embeddings } = await embedMany({
  model: openai.embedding("text-embedding-3-small"),
  values: ["Doc 1", "Doc 2", "Doc 3"],
});
```

### Token Counting

```typescript
const result = await generateText({ model, prompt });
console.log(result.usage.promptTokens);
console.log(result.usage.completionTokens);
console.log(result.usage.totalTokens);
```

## References

- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs)
- [AI SDK GitHub](https://github.com/vercel/ai)
- [AI SDK Examples](https://github.com/vercel/ai/tree/main/examples)

## Related

- [[nextjs]] — framework principal de integração
- [[react]] — hooks de cliente (useChat, useCompletion)
- [[typescript]] — linguagem base
- [[claude-api]] — provedor Anthropic via @ai-sdk/anthropic
- [[prompt-engineering]] — otimizar prompts no SDK
