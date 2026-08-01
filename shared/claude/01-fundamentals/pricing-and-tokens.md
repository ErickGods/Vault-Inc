---
tags: [claude-code, fundamentals]
aliases: [Pricing Claude, Tokens Claude, Custo Claude, Prompt Caching]
house: shared
domain: claude/fundamentals
level: intro
status: active
created: 2026-04-19
updated: 2026-08-01
---

# Pricing e Tokens

## Overview

Entender o modelo de pricing da Anthropic é essencial para usar Claude de forma sustentável — seja no Claude Code pessoal, em aplicações para usuários, ou em pipelines de processamento em massa. O custo pode variar em **10-100x** dependendo das decisões tomadas: qual modelo, se usa cache, se usa batch API, e o ratio de input vs output tokens.

Este documento cobre desde o básico de como tokens são cobrados até calculadoras práticas para estimar custo de casos de uso reais.

> [!info] Preços sujeitos a alteração
> Os preços neste documento refletem abril de 2026. Sempre verifique os preços atuais em [anthropic.com/pricing](https://anthropic.com/pricing) antes de planejar orçamentos de produção.

Integra com [[claude-models-overview]], [[context-window-management]], e [[what-is-claude-code]].

---

## Modelo de Pricing: Fundamentos

### Input vs Output tokens

A Anthropic cobra separadamente por tokens de **entrada** (input) e **saída** (output):

- **Input tokens**: tudo que você envia para o modelo — system prompt, histórico de conversa, arquivos, ferramentas disponíveis
- **Output tokens**: tudo que o modelo gera — a resposta, raciocínio (thinking), tool calls

Os output tokens custam tipicamente **3-5x mais** que input tokens. Isso reflete o custo computacional maior de gerar tokens vs processá-los.

```
Exemplo de uma request típica:
─────────────────────────────────────────
Input: system prompt (500 tok) + histórico (2000 tok) + mensagem (200 tok) = 2.700 tok
Output: resposta do Claude (800 tok)

Custo com claude-sonnet-4-6:
Input:  2.700 × ($3.00 / 1.000.000) = $0.0081
Output:   800 × ($15.00 / 1.000.000) = $0.012
TOTAL: $0.0201 por essa interação
```

### Cache tokens

Quando você usa **Prompt Caching**, tokens que já foram processados e estão em cache custam muito menos:

- **Cache write**: custo 25% acima do input normal (para criar o cache)
- **Cache read**: custo 90% abaixo do input normal (para reutilizar)

```
Sem cache, 1000 requests com system prompt de 10.000 tokens (Sonnet):
10.000 × $3.00 / 1M × 1000 = $30.00

Com cache, após a primeira request:
Cache write (1x): 10.000 × $3.75/M = $0.0375
Cache reads (999x): 10.000 × $0.30/M × 999 = $2.997
TOTAL: ~$3.03 (economia de 90%)
```

---

## Tabela de Preços por Modelo

### Claude 3.x Series

| Modelo | Input | Output | Cache Write | Cache Read |
|--------|-------|--------|-------------|------------|
| claude-3-haiku-20240307 | $0.25/MTok | $1.25/MTok | $0.30/MTok | $0.03/MTok |
| claude-3-5-haiku-20241022 | $0.80/MTok | $4.00/MTok | $1.00/MTok | $0.08/MTok |
| claude-3-sonnet-20240229 | $3.00/MTok | $15.00/MTok | $3.75/MTok | $0.30/MTok |
| claude-3-5-sonnet-20241022 | $3.00/MTok | $15.00/MTok | $3.75/MTok | $0.30/MTok |
| claude-3-opus-20240229 | $15.00/MTok | $75.00/MTok | $18.75/MTok | $1.50/MTok |

### Claude 4.x Series

| Modelo | Input | Output | Cache Write | Cache Read |
|--------|-------|--------|-------------|------------|
| claude-haiku-4-5 | $0.80/MTok | $4.00/MTok | $1.00/MTok | $0.08/MTok |
| claude-sonnet-4-5 | $3.00/MTok | $15.00/MTok | $3.75/MTok | $0.30/MTok |
| claude-sonnet-4-6 | $3.00/MTok | $15.00/MTok | $3.75/MTok | $0.30/MTok |
| claude-opus-4-5 | $15.00/MTok | $75.00/MTok | $18.75/MTok | $1.50/MTok |
| claude-opus-4-6 | $15.00/MTok | $75.00/MTok | $18.75/MTok | $1.50/MTok |

*MTok = Milhão de tokens. Batch API: 50% de desconto em input e output.*

> [!tip] Regra de bolso
> Para a maioria dos projetos com Sonnet: estime **$3/MTok de entrada** e **$15/MTok de saída**. Com caching bem implementado, o custo real de input cai para ~$0.30/MTok na maioria das requests recorrentes.

---

## Como Contar Tokens

### Regra prática

- **1 token ≈ 4 caracteres** (inglês)
- **1 token ≈ 3-3.5 caracteres** (português)
- **1 token ≈ 0.75 palavras** (inglês)
- **1 página de texto** (~500 palavras) ≈ 700 tokens
- **1 KB de código Python** ≈ 250-400 tokens
- **1 KB de JSON** ≈ 300-500 tokens

### Referências práticas

| Conteúdo | Tokens aproximados |
|----------|-------------------|
| Este arquivo CLAUDE.md (1 KB) | ~300-500 |
| Arquivo Python médio (200 linhas) | ~1.000-2.000 |
| Arquivo TypeScript grande (500 linhas) | ~2.500-4.000 |
| Resposta curta do Claude | ~100-300 |
| Resposta longa com código | ~500-2.000 |
| System prompt típico | ~500-2.000 |
| Página de PDF (texto) | ~500-700 |

### Tokenizador oficial

A Anthropic disponibiliza o tokenizador `claude-tokenizer` para contar tokens exatos:

```python
import anthropic

client = anthropic.Anthropic()

# Contar tokens antes de enviar
token_count = client.messages.count_tokens(
    model="claude-sonnet-4-6",
    messages=[{"role": "user", "content": "Seu texto aqui..."}]
)

print(f"Tokens: {token_count.input_tokens}")
```

```bash
# Via CLI (aproximação)
echo -n "seu texto" | wc -c  # bytes / 4 ≈ tokens em inglês
```

---

## Claude Code Pricing: Planos

### Plano Pro — $20/mês

- Acesso ao Claude Code
- Limites de uso mensais generosos para desenvolvimento individual
- Acesso a todos os modelos Claude (Haiku, Sonnet, Opus)
- Inclui claude.ai Pro (interface web)
- Ideal para: desenvolvedor individual, uso moderado

### Plano Max — $100/mês (5x Pro)

- Limites de uso 5x maiores que o Pro
- Para desenvolvedores que usam o Claude Code intensamente
- Ideal para: uso pesado o dia todo, projetos grandes

### Plano Team — $25/usuário/mês (mín. 5 usuários)

- Para equipes de desenvolvimento
- Colaboração e contexto compartilhado
- Administração centralizada
- Ideal para: equipes de 5+ pessoas

### API Key (Pay-as-you-go)

Sem plano — paga exatamente pelo que usa:
- Melhor para: automações, aplicações, volume variável
- Não tem limites de sessão do Claude Code
- Custo pode ser menor ou maior que plano, dependendo do uso
- Requer monitoramento de custo ativo

> [!example] Quando usar API Key vs Plano
> **Use plano Pro/Max** se você usa o Claude Code interativamente por 2+ horas por dia — o custo por token em uso intenso superaria $20-100/mês rapidamente.
> 
> **Use API Key** se você tem automações com volume previsível e baixo, ou se precisa mais controle sobre gastos.

---

## Batch API: 50% de Desconto

### Como funciona

A Batch API aceita até 10.000 requests em um único batch e as processa de forma assíncrona, retornando resultados em até 24 horas. Em troca da latência maior, você paga **50% menos** em todos os tokens (input e output).

### Quando vale a pena

```
✓ Análise de 1000+ documentos
✓ Processamento de datasets
✓ Geração de embeddings em massa
✓ Testes de qualidade em massa
✓ Qualquer tarefa onde latência não importa
```

```
✗ Chatbots e interfaces interativas
✗ Quando precisa do resultado em < 5 minutos
✗ Respostas a eventos em tempo real
```

### Exemplo com custo calculado

```python
import anthropic
import time

client = anthropic.Anthropic()

# 1000 documentos para classificar
documents = load_documents()  # lista de 1000 strings

# Criar batch
batch = client.messages.batches.create(
    requests=[
        {
            "custom_id": f"doc-{i}",
            "params": {
                "model": "claude-haiku-4-5",
                "max_tokens": 50,
                "messages": [{
                    "role": "user",
                    "content": f"Classifique em positivo/negativo/neutro: {doc}"
                }]
            }
        }
        for i, doc in enumerate(documents)
    ]
)

print(f"Batch criado: {batch.id}")
# → Custo estimado: 1000 × (média 200 tokens input + 10 tokens output)
# → Sem batch: 200K × $0.80/M + 10K × $4.00/M = $0.16 + $0.04 = $0.20
# → Com batch (50% off): $0.10 ← metade do preço

# Verificar status (pode demorar até 24h)
while True:
    batch_result = client.messages.batches.retrieve(batch.id)
    if batch_result.processing_status == "ended":
        break
    time.sleep(60)  # verificar a cada minuto

# Coletar resultados
results = {}
for result in client.messages.batches.results(batch.id):
    if result.result.type == "succeeded":
        results[result.custom_id] = result.result.message.content[0].text
```

---

## Prompt Caching: Como Funciona

### Mecanismo

O Prompt Caching armazena partes do contexto no servidor da Anthropic. Quando a mesma parte do contexto é enviada novamente em uma request posterior, o servidor reutiliza o resultado processado em cache — sem recalcular.

Para ativar, adicione `cache_control: {"type": "ephemeral"}` nos blocos que deseja cachear.

**Condições para hit de cache:**
1. O conteúdo cacheado deve ser **idêntico** (byte por byte)
2. O cache tem TTL de **5 minutos** por padrão
3. Mínimo de **1.024 tokens** para caching ser ativado
4. Máximo de **4 pontos de cache** por request

### Quando cachear

```
✓ System prompt longo (instruções, personas)
✓ Documentação incluída em todas as requests
✓ Código de referência (schema do DB, modelos)
✓ Few-shot examples repetidos em todas as requests
✗ Mensagens do usuário (sempre diferentes)
✗ Conteúdo curto (< 1024 tokens)
✗ Dados que mudam frequentemente
```

### Implementação Python

```python
import anthropic

client = anthropic.Anthropic()

# System prompt longo (ex: 5000 tokens de instruções)
SYSTEM_PROMPT = """
Você é um assistente especializado em análise de contratos jurídicos brasileiros.
[... 5000 tokens de instruções detalhadas ...]
"""

def analyze_contract(contract_text: str) -> str:
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"}  # ← cachear system prompt
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Analise este contrato:\n\n{contract_text}"
            }
        ]
    )
    
    # Verificar se houve cache hit
    usage = response.usage
    if hasattr(usage, 'cache_read_input_tokens') and usage.cache_read_input_tokens > 0:
        print(f"✓ Cache hit: {usage.cache_read_input_tokens} tokens do cache")
    
    return response.content[0].text

# 1ª chamada: cache write (25% mais caro)
result1 = analyze_contract(contrato1)

# 2ª+ chamadas: cache read (90% mais barato)
result2 = analyze_contract(contrato2)  # ← economia de 90% no system prompt
result3 = analyze_contract(contrato3)
```

### Implementação TypeScript

```typescript
import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

const LARGE_CONTEXT = "... documentação de 10.000 tokens ...";

async function analyzeWithCache(userQuery: string) {
  const response = await client.messages.create({
    model: "claude-sonnet-4-6",
    max_tokens: 1000,
    system: [
      {
        type: "text",
        text: LARGE_CONTEXT,
        cache_control: { type: "ephemeral" }, // ← cachear contexto grande
      },
    ],
    messages: [{ role: "user", content: userQuery }],
  });

  const { cache_read_input_tokens, cache_creation_input_tokens } =
    response.usage as any;

  if (cache_read_input_tokens > 0) {
    console.log(`Cache hit: ${cache_read_input_tokens} tokens economizados`);
  }

  return response.content[0].type === "text" ? response.content[0].text : "";
}
```

---

## Estratégias para Reduzir Custo

### 1. Usar Haiku para tasks simples

```python
def route_to_model(task: str) -> str:
    """Roteamento baseado na complexidade da tarefa."""
    simple_patterns = ["classif", "extrai", "list", "convert", "format"]
    complex_patterns = ["arquitet", "design", "analise profunda", "refator"]
    
    task_lower = task.lower()
    
    if any(p in task_lower for p in complex_patterns):
        return "claude-opus-4-5"  # $15/MTok input
    elif any(p in task_lower for p in simple_patterns):
        return "claude-haiku-4-5"  # $0.80/MTok input — 20x mais barato
    else:
        return "claude-sonnet-4-6"  # $3/MTok input — default
```

### 2. Batch para volume

```
Sem batch: 10.000 requests × $0.003/request = $30
Com batch: 10.000 requests × $0.0015/request = $15
Economia: $15 (50%)
```

### 3. Caching para system prompts repetidos

```
Sem cache: 1.000 requests × 5.000 tokens × $3/MTok = $15
Com cache: cache write ($18.75) + 999 reads × $1.50 = $20.24
↑ Neste caso, cache não compensou (contexto pequeno + poucas requests)

Sem cache: 10.000 requests × 50.000 tokens × $3/MTok = $1.500
Com cache: cache write ($187.50) + 9.999 reads × $150 = $337.45
Economia: $1.162.55 (77%)
← Com volume e contexto grande, cache compensa muito
```

### 4. Limitar max_tokens ao necessário

```python
# Ruim: sempre usa o máximo
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=8192,  # ← sempre gera o máximo
    ...
)

# Bom: calibra ao uso real
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=500,  # ← para uma classificação simples
    ...
)
```

### 5. Leitura seletiva de arquivos

```python
# Ruim: passa o arquivo inteiro
with open("app/models.py") as f:
    full_file = f.read()  # 10.000 tokens

# Bom: passa apenas a seção relevante
relevant_section = extract_relevant_lines("app/models.py", keyword="class User")
# → 200 tokens, 98% de economia
```

---

## Calculadora Prática de Custo

### Cenário 1: Chatbot de suporte para SaaS

```
Parâmetros:
- 1.000 conversas/dia
- Média 5 trocas por conversa
- Média 500 tokens input + 300 tokens output por troca
- Modelo: claude-haiku-4-5
- System prompt: 2.000 tokens (cacheado)

Sem otimização:
- Input: 1000 × 5 × (2000 + 500) × $0.80/M = $10/dia = $300/mês
- Output: 1000 × 5 × 300 × $4.00/M = $6/dia = $180/mês
- Total sem cache: $480/mês

Com prompt caching:
- Cache write: 1 × 2.000 × $1.00/M = $0.002/dia
- Cache reads: 1000 × 5 × 2.000 × $0.08/M = $0.80/dia
- User input: 1000 × 5 × 500 × $0.80/M = $2/dia
- Output: 1000 × 5 × 300 × $4.00/M = $6/dia
- Total com cache: ($0.80 + $2 + $6) × 30 = $264/mês
- Economia: 45%
```

### Cenário 2: Processar 1.000 PDFs

```
Parâmetros:
- 1.000 PDFs, média 10 páginas cada
- ~700 tokens por página = 7.000 tokens por PDF
- Extração estruturada: max_tokens=500 por PDF
- Modelo: claude-haiku-4-5 + Batch API

Custo:
- Input: 1.000 × 7.000 × $0.40/M (batch) = $2.80
- Output: 1.000 × 500 × $2.00/M (batch) = $1.00
- TOTAL: $3.80 para processar 1.000 PDFs

Com Sonnet (sem batch):
- Input: 1.000 × 7.000 × $3.00/M = $21
- Output: 1.000 × 500 × $15.00/M = $7.50
- TOTAL: $28.50 (7.5x mais caro)
```

### Cenário 3: Code review automático em CI/CD

```
Parâmetros:
- 50 PRs por dia
- Média 500 linhas de diff ≈ 2.500 tokens
- Review detalhado: max_tokens=1.000
- Modelo: claude-sonnet-4-6

Custo diário:
- Input: 50 × 2.500 × $3.00/M = $0.375
- Output: 50 × 1.000 × $15.00/M = $0.75
- Total: $1.125/dia = $33.75/mês

Com sistema prompt cacheado (1.000 tokens):
- Cache savings: 50 × 1.000 × ($3.00 - $0.30)/M = $0.135/dia economizados
- Total com cache: ~$30/mês
```

### Cenário 4: Geração de testes automatizados

```
Parâmetros:
- 200 funções para gerar testes
- Média 100 linhas de código por função ≈ 500 tokens
- Testes gerados: max_tokens=1.000
- Modelo: claude-sonnet-4-6

Custo:
- Input: 200 × (500 + 500 system) × $3.00/M = $0.60
- Output: 200 × 1.000 × $15.00/M = $3.00
- TOTAL: $3.60 para gerar testes de 200 funções
```

---

## Comparativo com Competidores

| Modelo | Input | Output | Context |
|--------|-------|--------|---------|
| **claude-haiku-4-5** | **$0.80/MTok** | **$4.00/MTok** | 200K |
| **claude-sonnet-4-6** | **$3.00/MTok** | **$15.00/MTok** | 200K |
| **claude-opus-4-6** | **$15.00/MTok** | **$75.00/MTok** | 200K |
| GPT-4o mini | $0.15/MTok | $0.60/MTok | 128K |
| GPT-4o | $2.50/MTok | $10.00/MTok | 128K |
| GPT-4 Turbo | $10.00/MTok | $30.00/MTok | 128K |
| Gemini 1.5 Flash | $0.075/MTok | $0.30/MTok | 1M |
| Gemini 1.5 Pro | $1.25/MTok | $5.00/MTok | 1M |

> [!info] Custo não é tudo
> Gemini Flash é mais barato, GPT-4o mini é mais barato que Haiku. Mas qualidade, seguimento de instruções, e capacidade de raciocínio variam. Claude é consistentemente top-tier em seguimento de instruções complexas e código — o que pode reduzir o número de retries necessários e o custo real end-to-end.

---

## Monitoramento de Custo

### Dashboard Anthropic

Acesse [console.anthropic.com](https://console.anthropic.com) → **Usage**:
- Uso por dia/semana/mês
- Breakdown por modelo
- Tokens input vs output vs cache
- Custo total

### Alertas de custo

Configure limites no console:
1. Console → Settings → Billing
2. Set spending limit (diário ou mensal)
3. Configure alert threshold (ex: 80% do limite)

### Monitoramento programático

```python
import anthropic
from datetime import datetime, timedelta

client = anthropic.Anthropic()

# Verificar uso total (via response.usage em cada request)
def track_session_cost(responses: list) -> dict:
    """Rastreia custo de uma sessão de requests."""
    total = {
        "input_tokens": 0,
        "output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }
    
    for response in responses:
        usage = response.usage
        total["input_tokens"] += usage.input_tokens
        total["output_tokens"] += usage.output_tokens
        if hasattr(usage, "cache_read_input_tokens"):
            total["cache_read_tokens"] += usage.cache_read_input_tokens or 0
        if hasattr(usage, "cache_creation_input_tokens"):
            total["cache_write_tokens"] += usage.cache_creation_input_tokens or 0
    
    # Calcular custo (Sonnet)
    cost = (
        total["input_tokens"] * 3.00 / 1_000_000 +
        total["output_tokens"] * 15.00 / 1_000_000 +
        total["cache_read_tokens"] * 0.30 / 1_000_000 +
        total["cache_write_tokens"] * 3.75 / 1_000_000
    )
    
    return {**total, "estimated_cost_usd": round(cost, 4)}

# Uso:
session_responses = [response1, response2, response3]
cost_report = track_session_cost(session_responses)
print(f"Custo da sessão: ${cost_report['estimated_cost_usd']}")
print(f"Cache savings: {cost_report['cache_read_tokens']} tokens do cache")
```

---

## Related

- [[claude-models-overview]] — Modelos e quando usar cada um
- [[context-window-management]] — Gerenciar contexto para controlar custo
- [[claude-code-vs-api-vs-chat]] — Pricing de cada interface
- [[what-is-claude-code]] — Planos Pro/Max do Claude Code
- [[../04-api-and-sdk/prompt-caching-deep-dive]] — Caching em profundidade
- [[../04-api-and-sdk/batch-api]] — Batch API detalhada
