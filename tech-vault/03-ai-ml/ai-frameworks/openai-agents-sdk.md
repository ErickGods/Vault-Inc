---
tags: [skill, ai-ml, openai-agents-sdk]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [OpenAI Agents SDK, Agents SDK]
---

# OpenAI Agents SDK

## Overview

O OpenAI Agents SDK (anteriormente Swarm, agora parte do pacote `openai-agents`) é um framework de produção para construir sistemas de agentes com suporte nativo a handoffs, guardrails e tracing. Diferente de frameworks de alto nível como [[crewai]], o SDK mantém controle explícito sobre o fluxo de execução enquanto abstrai a complexidade de gerenciamento de estado entre turnos.

> [!important] Versão
> O SDK foi redesenhado em 2025. A API `openai-agents>=0.1.0` é incompatível com o Swarm original. Sempre verifique a versão instalada.

Integra-se nativamente com [[claude-api]] via compatibilidade OpenAI e suporta os mesmos padrões de [[multi-agent-systems]].

## Core Concepts

### Agent Class

O `Agent` é a unidade fundamental — combina instruções, modelo e ferramentas:

```python
from agents import Agent, function_tool, Runner

agent = Agent(
    name="Research Assistant",
    model="gpt-4o",
    instructions="""You are a research assistant.
    When asked about a topic, search for information and summarize findings.
    Always cite your sources.""",
    tools=[search_tool, summarize_tool],
    model_settings=ModelSettings(
        temperature=0.3,
        max_tokens=4096,
        top_p=0.95,
    ),
)
```

**Instruções dinâmicas** — podem ser callables que recebem contexto:

```python
def dynamic_instructions(context: RunContextWrapper, agent: Agent) -> str:
    user_tier = context.context.get("user_tier", "free")
    return f"You assist {user_tier} tier users. {'Premium features enabled.' if user_tier == 'premium' else 'Suggest upgrades when relevant.'}"

agent = Agent(
    name="Support Agent",
    instructions=dynamic_instructions,
)
```

### Runner: run, run_sync, run_streamed

```python
from agents import Runner

# Async (recomendado para produção)
result = await Runner.run(agent, "Analyze the Q3 sales data")

# Sync (scripts e notebooks)
result = Runner.run_sync(agent, "Quick question")

# Streaming com eventos em tempo real
async for event in Runner.run_streamed(agent, "Long analysis task"):
    if event.type == "text_delta":
        print(event.delta, end="", flush=True)
    elif event.type == "tool_call":
        print(f"\n[Tool: {event.tool_name}]")
```

O `RunResult` contém todo o histórico de mensagens, tool calls e o output final:

```python
result = await Runner.run(agent, input_messages)
print(result.final_output)      # string do output final
print(result.messages)          # lista completa de mensagens
print(result.last_agent)        # agente que produziu o output final
```

### Handoffs: Agent-to-Agent Delegation

Handoffs permitem que um agente delegue para outro especialista:

```python
billing_agent = Agent(
    name="Billing Specialist",
    instructions="Handle billing inquiries, refunds, and subscription changes.",
)

technical_agent = Agent(
    name="Technical Support",
    instructions="Resolve technical issues, bugs, and API problems.",
)

triage_agent = Agent(
    name="Triage",
    instructions="Route customer inquiries to the appropriate specialist.",
    handoffs=[billing_agent, technical_agent],
)
```

**Handoff customizado com filtro de contexto:**

```python
from agents import handoff

def billing_handoff_filter(messages: list) -> list:
    # Remover dados sensíveis antes de passar para billing
    return [m for m in messages if "credit_card" not in str(m)]

billing_handoff = handoff(
    agent=billing_agent,
    input_filter=billing_handoff_filter,
    on_handoff=lambda ctx: log_handoff(ctx.context["user_id"], "billing"),
)
```

## Patterns

### Function Tools com @function_tool

```python
from agents import function_tool
from pydantic import BaseModel

class SearchParams(BaseModel):
    query: str
    max_results: int = 10
    date_range: str | None = None

@function_tool
async def web_search(params: SearchParams) -> str:
    """Search the web for current information.

    Args:
        params: Search parameters including query and filters

    Returns:
        Formatted search results with titles and snippets
    """
    results = await search_api(params.query, params.max_results)
    return format_results(results)
```

O SDK usa Pydantic para validação automática dos parâmetros — erros de tipo são capturados antes de chamar a função.

### Guardrails: Input e Output

**Input guardrails** — validam/transformam input antes de processar:

```python
from agents import input_guardrail, GuardrailFunctionOutput

@input_guardrail
async def pii_detector(
    context: RunContextWrapper,
    agent: Agent,
    input: str | list
) -> GuardrailFunctionOutput:
    has_pii = await detect_pii(input)
    if has_pii:
        return GuardrailFunctionOutput(
            tripwire_triggered=True,
            output_info={"reason": "PII detected in input"},
        )
    return GuardrailFunctionOutput(tripwire_triggered=False)

agent = Agent(
    name="Safe Agent",
    input_guardrails=[pii_detector],
)
```

**Output guardrails** — validam output antes de retornar ao usuário:

```python
@output_guardrail
async def toxicity_filter(context, agent, output) -> GuardrailFunctionOutput:
    score = await check_toxicity(output.final_output)
    return GuardrailFunctionOutput(
        tripwire_triggered=score > 0.8,
        output_info={"toxicity_score": score},
    )
```

### Tracing: Spans e Processors

```python
from agents.tracing import add_trace_processor, TracingProcessor

class CustomProcessor(TracingProcessor):
    def on_trace_start(self, trace) -> None:
        self.start_time = time.time()

    def on_span_start(self, span) -> None:
        log.info(f"Span started: {span.span_data.type}")

    def on_span_end(self, span) -> None:
        duration = time.time() - span.started_at
        metrics.record(f"agent.span.{span.span_data.type}", duration)

    def on_trace_end(self, trace) -> None:
        total = time.time() - self.start_time
        log.info(f"Trace complete: {total:.2f}s, {len(trace.spans)} spans")

add_trace_processor(CustomProcessor())
```

### Multi-Agent Orchestration com Context Variables

```python
from dataclasses import dataclass
from agents import RunContextWrapper

@dataclass
class AppContext:
    user_id: str
    session_id: str
    permissions: list[str]
    conversation_history: list

# Contexto tipado disponível em todas as ferramentas e instruções
async def run_with_context(user_id: str, message: str):
    context = AppContext(
        user_id=user_id,
        session_id=generate_session_id(),
        permissions=await get_user_permissions(user_id),
        conversation_history=[],
    )

    result = await Runner.run(
        orchestrator_agent,
        message,
        context=context,
    )
    return result
```

### Parallel Agent Execution

```python
import asyncio

async def parallel_research(topics: list[str]) -> list[str]:
    tasks = [
        Runner.run(research_agent, f"Research: {topic}")
        for topic in topics
    ]
    results = await asyncio.gather(*tasks)
    return [r.final_output for r in results]
```

## Gotchas

> [!warning] Handoff Loop Detection
> O SDK não detecta loops de handoff nativamente. Se agent A faz handoff para B e B faz handoff para A, você terá recursão infinita. Implemente um contador de handoffs no contexto.

> [!bug] Streaming + Guardrails
> Output guardrails só são executados após o streaming completar. O usuário pode ver output antes do guardrail validar. Use input guardrails para validação em tempo real.

> [!caution] Tool Parallelism
> Por padrão, o modelo pode chamar múltiplas ferramentas em paralelo. Se suas ferramentas têm side effects (escrita em DB, envio de email), adicione `parallel_tool_calls=False` no `ModelSettings`.

> [!tip] Comparação com [[autogen]]
> OpenAI Agents SDK é mais opinativo e produção-ready. AutoGen é mais flexível para pesquisa e experimentação. Para sistemas de produção em escala, prefira este SDK.

## Snippets

### Agent com Retry Logic

```python
from agents import ModelSettings

resilient_agent = Agent(
    name="Resilient",
    model="gpt-4o",
    model_settings=ModelSettings(
        max_retries=3,          # retry automático em falhas de rede
        timeout=30.0,
    ),
    instructions="...",
)
```

### Conversação Multi-Turn

```python
history = []

async def chat(user_message: str) -> str:
    history.append({"role": "user", "content": user_message})
    result = await Runner.run(agent, history)
    history.extend(result.messages)  # preservar histórico completo
    return result.final_output
```

### Inspecionar Tool Calls

```python
result = await Runner.run(agent, "What's the weather in Tokyo?")

for msg in result.messages:
    if msg.get("role") == "assistant" and msg.get("tool_calls"):
        for call in msg["tool_calls"]:
            print(f"Tool: {call['function']['name']}")
            print(f"Args: {call['function']['arguments']}")
```

## References

- [OpenAI Agents SDK Docs](https://openai.github.io/openai-agents-python/)
- [Agents SDK GitHub](https://github.com/openai/openai-agents-python)
- [[prompt-engineering]] — escrever instruções eficazes para agentes

## Related

- [[multi-agent-systems]] — padrões arquiteturais para sistemas multi-agente
- [[crewai]] — alternativa com foco em crews e roles
- [[autogen]] — alternativa Microsoft com foco em conversação
- [[claude-api]] — usar Claude como modelo base nos agentes
- [[prompt-engineering]] — otimizar instruções dos agentes
