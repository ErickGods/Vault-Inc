---
tags: [claude-code, fundamentals]
aliases: [Claude Models, Opus, Sonnet, Haiku, Claude 3.5, Claude 3.7]
house: shared
domain: claude/fundamentals
level: intro
status: active
created: 2026-04-19
updated: 2026-08-01
---

# Claude Models Overview

## Overview

A Anthropic mantém uma família de modelos Claude organizada em três tiers — **Haiku**, **Sonnet** e **Opus** — cada um representando um trade-off diferente entre velocidade, custo e capacidade. Além dos tiers, cada modelo tem versões numeradas que trazem melhorias incrementais significativas.

Entender a família de modelos é essencial para usar Claude Code eficientemente: o modelo certo para a tarefa certa pode reduzir custos em 10-20x sem perda de qualidade para tarefas simples, ou melhorar resultados dramaticamente para tarefas complexas usando o modelo mais capaz.

> [!info] Nomenclatura
> Os model IDs seguem o padrão `claude-{tier}-{versão}-{data}` para modelos mais antigos (ex: `claude-3-5-sonnet-20241022`) e `claude-{tier}-{versão}` para aliases mais recentes (ex: `claude-sonnet-4-5`). Sempre prefira o model ID completo em código de produção.

Integra com [[what-is-claude-code]], [[pricing-and-tokens]], e [[context-window-management]].

---

## A Família de Modelos Claude

### Haiku — Velocidade e Custo

O tier **Haiku** é o modelo mais leve e rápido da família. Projetado para:
- Tarefas simples e bem definidas
- Alto volume de requests (batch processing)
- Latência crítica
- Aplicações com budget limitado

Haiku é surpreendentemente capaz para tarefas estruturadas — classificação, extração de dados, sumarização de textos curtos, geração de código boilerplate. A limitação aparece em raciocínio complexo multi-step, ambiguidade, e tarefas que requerem profundo entendimento de contexto.

### Sonnet — O Ponto Ideal

O tier **Sonnet** representa o sweet spot da família. É o modelo que a maioria dos desenvolvedores deveria usar como padrão porque:
- Excelente equilíbrio entre qualidade e custo
- Velocidade adequada para uso interativo
- Capacidade suficiente para a vasta maioria das tarefas de desenvolvimento
- É o modelo padrão do Claude Code

Sonnet lida bem com: refatoração de código, implementação de features, code review, geração de testes, análise de bugs, escrita técnica.

### Opus — Máxima Capacidade

O tier **Opus** é o modelo mais capaz da Anthropic. Use quando:
- A tarefa requer raciocínio profundo e multi-step
- Análise de código altamente complexa
- Arquitetura de sistemas sofisticada
- Custo não é a restrição primária
- Resultados de alta qualidade são mais importantes que velocidade

Opus é consideravelmente mais lento e caro que Sonnet, então use com critério.

---

## Versões e Model IDs

### Claude 3.x Series (2024)

| Model ID | Tier | Lançamento | Status |
|----------|------|------------|--------|
| `claude-3-haiku-20240307` | Haiku | Mar 2024 | Disponível |
| `claude-3-sonnet-20240229` | Sonnet | Fev 2024 | Disponível (legado) |
| `claude-3-opus-20240229` | Opus | Fev 2024 | Disponível |
| `claude-3-5-haiku-20241022` | Haiku | Out 2024 | Disponível |
| `claude-3-5-sonnet-20240620` | Sonnet | Jun 2024 | Disponível (legado) |
| `claude-3-5-sonnet-20241022` | Sonnet | Out 2024 | **Recomendado (3.x)** |

### Claude 4.x Series (2025-2026)

| Model ID | Tier | Lançamento | Status |
|----------|------|------------|--------|
| `claude-haiku-4-5` | Haiku | 2025 | Disponível |
| `claude-sonnet-4-5` | Sonnet | 2025 | Disponível |
| `claude-opus-4-5` | Opus | 2025 | Disponível |
| `claude-sonnet-4-6` | Sonnet | 2026 | **Atual** |
| `claude-opus-4-6` | Opus | 2026 | Disponível |

> [!tip] Aliases Sem Data
> A Anthropic oferece aliases sem data como `claude-sonnet-4-5` que apontam automaticamente para a versão mais recente daquele tier. Conveniente para desenvolvimento, mas use o model ID completo em produção para evitar mudanças de comportamento inesperadas.

---

## Tabela Comparativa Completa

| Modelo | Context Window | Velocidade | Custo Input | Custo Output | Extended Thinking |
|--------|---------------|------------|-------------|--------------|-------------------|
| claude-3-haiku-20240307 | 200K tokens | Muito rápido | $0.25/MTok | $1.25/MTok | Não |
| claude-3-5-haiku-20241022 | 200K tokens | Muito rápido | $0.80/MTok | $4.00/MTok | Não |
| claude-haiku-4-5 | 200K tokens | Muito rápido | $0.80/MTok | $4.00/MTok | Não |
| claude-3-5-sonnet-20241022 | 200K tokens | Rápido | $3.00/MTok | $15.00/MTok | Não |
| claude-sonnet-4-5 | 200K tokens | Rápido | $3.00/MTok | $15.00/MTok | Sim |
| claude-sonnet-4-6 | 200K tokens | Rápido | $3.00/MTok | $15.00/MTok | Sim |
| claude-3-opus-20240229 | 200K tokens | Lento | $15.00/MTok | $75.00/MTok | Não |
| claude-opus-4-5 | 200K tokens | Lento | $15.00/MTok | $75.00/MTok | Sim |
| claude-opus-4-6 | 200K tokens | Lento | $15.00/MTok | $75.00/MTok | Sim |

*MTok = Milhão de tokens. Preços sujeitos a alteração — verifique [anthropic.com/pricing](https://anthropic.com/pricing).*

> [!info] Cache e Batch
> Todos os modelos suportam **Prompt Caching** (desconto em cache hits) e **Batch API** (50% de desconto com latência maior). Veja [[pricing-and-tokens]] para detalhes.

---

## Quando Usar Cada Modelo

### Guia de Decisão por Tarefa

| Tarefa | Modelo Recomendado | Justificativa |
|--------|-------------------|---------------|
| Autocompletar código boilerplate | Haiku | Simples, volume alto, custo importa |
| Classificar/categorizar textos | Haiku | Tarefa estruturada, sem raciocínio profundo |
| Extrair dados de documentos | Haiku ou Sonnet | Depende da complexidade |
| Gerar testes unitários simples | Sonnet | Contexto de projeto necessário |
| Implementar features novas | Sonnet | **Default** para desenvolvimento |
| Refatoração de código | Sonnet | Bom custo-benefício |
| Code review completo | Sonnet | Contexto amplo, raciocínio adequado |
| Debug de bugs complexos | Sonnet ou Opus | Depende da profundidade |
| Arquitetura de sistemas | Opus | Raciocínio multi-step profundo |
| Análise de segurança profunda | Opus | Casos edge, raciocínio adversarial |
| Geração de código criativo/novel | Opus | Capacidade máxima necessária |
| Processamento em lote (1000+ items) | Haiku + Batch API | Custo mínimo |

### Tabela de Trade-offs

```
CUSTO          ←————————————————————→ QUALIDADE
Haiku    |████░░░░░░░░░░░░░░░░░░| Baixo custo, boa qualidade básica
Sonnet   |████████████░░░░░░░░░░| Custo médio, alta qualidade
Opus     |████████████████████░░| Alto custo, qualidade máxima

VELOCIDADE     ←————————————————————→ THROUGHPUT
Haiku    |████████████████████░░| Muito rápido, ideal para latência
Sonnet   |█████████████░░░░░░░░░| Rápido, adequado para interativo
Opus     |██████░░░░░░░░░░░░░░░░| Lento, use assíncrono
```

---

## Extended Thinking

Extended Thinking é uma capability que permite ao modelo pensar em voz alta antes de responder — um chain-of-thought explícito que melhora significativamente o raciocínio em problemas complexos.

### Quais modelos suportam

- `claude-sonnet-4-5` e posteriores ✓
- `claude-opus-4-5` e posteriores ✓
- Modelos Claude 3.x — **Não suportam**

### Como funciona

Quando ativado, o modelo usa tokens de "thinking" (cobrados como output tokens) para raciocinar antes de responder. Esses tokens de pensamento ficam visíveis na resposta como blocos `<thinking>`.

### Quando usar Extended Thinking

- Problemas matemáticos complexos
- Análise de algoritmos
- Debugging de lógica intrincada
- Decisões de arquitetura com muitas variáveis
- Qualquer tarefa onde você percebe que o modelo erra sem pensar suficientemente

> [!warning] Custo do Extended Thinking
> Os tokens de thinking são cobrados como output tokens — que custam 3-5x mais que input tokens. Para tarefas simples, Extended Thinking pode triplicar o custo sem benefício. Use somente quando a qualidade do raciocínio é crítica.

### Ativar via API (Python)

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=16000,
    thinking={
        "type": "enabled",
        "budget_tokens": 10000  # max tokens para pensar
    },
    messages=[{
        "role": "user",
        "content": "Analise este algoritmo e identifique a complexidade: ..."
    }]
)

# Blocos de thinking e resposta separados
for block in response.content:
    if block.type == "thinking":
        print("THINKING:", block.thinking)
    elif block.type == "text":
        print("RESPONSE:", block.text)
```

### Ativar via API (TypeScript)

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const response = await client.messages.create({
  model: "claude-sonnet-4-5",
  max_tokens: 16000,
  thinking: {
    type: "enabled",
    budget_tokens: 10000,
  },
  messages: [
    {
      role: "user",
      content: "Qual é a complexidade deste algoritmo de sorting?",
    },
  ],
});

for (const block of response.content) {
  if (block.type === "thinking") {
    console.log("Pensamento:", block.thinking);
  } else if (block.type === "text") {
    console.log("Resposta:", block.text);
  }
}
```

---

## Como Usar Modelos no Claude Code

### Flag `--model`

```bash
# Modelo padrão (Sonnet atual)
claude

# Especificar modelo explicitamente
claude --model claude-opus-4-5

# Haiku para tarefas rápidas e baratas
claude --model claude-haiku-4-5

# Sonnet mais recente
claude --model claude-sonnet-4-6

# Modo headless com modelo específico
claude --model claude-opus-4-5 --print "Analise a arquitetura deste sistema"
```

### Configurar modelo padrão

No arquivo de configuração do Claude Code (`~/.claude/settings.json`):

```json
{
  "model": "claude-sonnet-4-6"
}
```

Ou por projeto (`.claude/settings.json`):

```json
{
  "model": "claude-opus-4-5"
}
```

### Mudar modelo durante sessão

```bash
# Dentro do REPL interativo
> /model claude-opus-4-5
Modelo alterado para: claude-opus-4-5

> /model claude-haiku-4-5
Modelo alterado para: claude-haiku-4-5
```

---

## Snippets: Usar Modelos via API

### Python — Trocar de modelo

```python
import anthropic

client = anthropic.Anthropic(api_key="sk-ant-...")

# Haiku para classificação em massa
def classify_text_batch(texts: list[str]) -> list[str]:
    results = []
    for text in texts:
        response = client.messages.create(
            model="claude-haiku-4-5",  # barato para volume
            max_tokens=50,
            messages=[{
                "role": "user",
                "content": f"Classifique em: positivo/negativo/neutro. Texto: {text}"
            }]
        )
        results.append(response.content[0].text.strip())
    return results

# Opus para análise profunda
def analyze_architecture(code: str) -> str:
    response = client.messages.create(
        model="claude-opus-4-5",  # capacidade máxima
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": f"Analise os trade-offs de arquitetura neste código:\n\n{code}"
        }]
    )
    return response.content[0].text
```

### TypeScript — Seleção dinâmica de modelo

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

type TaskComplexity = "simple" | "medium" | "complex";

function selectModel(complexity: TaskComplexity): string {
  const models: Record<TaskComplexity, string> = {
    simple: "claude-haiku-4-5",
    medium: "claude-sonnet-4-6",
    complex: "claude-opus-4-5",
  };
  return models[complexity];
}

async function processTask(task: string, complexity: TaskComplexity) {
  const model = selectModel(complexity);
  
  const response = await client.messages.create({
    model,
    max_tokens: complexity === "complex" ? 4000 : 1000,
    messages: [{ role: "user", content: task }],
  });

  console.log(`Modelo usado: ${model}`);
  return response.content[0].type === "text" ? response.content[0].text : "";
}

// Uso
await processTask("Classifique este email: ...", "simple");
await processTask("Implemente este endpoint REST", "medium");
await processTask("Projete a arquitetura do sistema de pagamentos", "complex");
```

---

## Pricing por Modelo

Veja tabela completa em [[pricing-and-tokens]]. Resumo dos principais:

| Modelo | Input | Output | Cache Read | Cache Write |
|--------|-------|--------|------------|-------------|
| claude-3-haiku-20240307 | $0.25 | $1.25 | $0.03 | $0.30 |
| claude-3-5-haiku-20241022 | $0.80 | $4.00 | $0.08 | $1.00 |
| claude-haiku-4-5 | $0.80 | $4.00 | $0.08 | $1.00 |
| claude-3-5-sonnet-20241022 | $3.00 | $15.00 | $0.30 | $3.75 |
| claude-sonnet-4-5/4-6 | $3.00 | $15.00 | $0.30 | $3.75 |
| claude-3-opus-20240229 | $15.00 | $75.00 | $1.50 | $18.75 |
| claude-opus-4-5/4-6 | $15.00 | $75.00 | $1.50 | $18.75 |

*Preços em USD por Milhão de tokens (MTok)*

---

## Batch API

A Batch API permite processar múltiplas requests de forma assíncrona com **50% de desconto** em troca de latência maior (até 24h).

### Quando usar Batch API

- Processar 100+ documentos
- Análise em massa de código
- Geração de testes para múltiplos arquivos
- Qualquer workload onde latência não é crítica

```python
import anthropic

client = anthropic.Anthropic()

# Criar batch
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"task-{i}",
            "params": {
                "model": "claude-haiku-4-5",
                "max_tokens": 500,
                "messages": [{"role": "user", "content": f"Analise: {code}"}]
            }
        }
        for i, code in enumerate(codes_to_analyze)
    ]
)

print(f"Batch ID: {batch.id}")
print(f"Status: {batch.processing_status}")

# Verificar status depois
batch_status = client.messages.batches.retrieve(batch.id)
```

---

## Related

- [[what-is-claude-code]] — Como usar modelos no contexto da CLI
- [[pricing-and-tokens]] — Preços detalhados e estratégias de custo
- [[context-window-management]] — Context window de cada modelo
- [[claude-code-vs-api-vs-chat]] — Quando usar CLI vs API vs Chat
- [[../04-api-and-sdk/messages-api-reference]] — Referência da Messages API
- [[../04-api-and-sdk/extended-thinking]] — Extended Thinking em profundidade
