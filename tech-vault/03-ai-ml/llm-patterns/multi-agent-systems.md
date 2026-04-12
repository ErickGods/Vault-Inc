---
tags: [skill, ai-ml, multi-agent-systems]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [Multi-Agent Systems, MAS, Agentic AI]
---

# Multi-Agent Systems

## Overview

Sistemas multi-agente (MAS) coordenam múltiplos LLMs especializados para resolver tarefas que excedem as capacidades de um único modelo. Cada agente possui papel, ferramentas e contexto definidos — colaboram via message passing, handoffs e memória compartilhada.

Frameworks principais: [[crewai]], [[autogen]], [[openai-agents-sdk]]. Integra com [[prompt-engineering]] para design de system prompts por agente e [[claude-code-superpowers]] para agentes de engenharia de software.

> [!tip] Quando usar MAS?
> Use single-agent quando a tarefa cabe em uma janela de contexto. Use MAS quando há especialização clara, paralelismo natural, ou quando o task graph excede 10+ etapas encadeadas.

---

## Core Concepts

### Topologias de Orquestração

| Topologia | Descrição | Melhor para |
|-----------|-----------|-------------|
| **Supervisor** | Um orquestrador central delega para workers | Tasks com dependências claras |
| **Peer-to-peer** | Agentes se comunicam diretamente via handoffs | Pipelines sequenciais simples |
| **Hierárquica** | Supervisores de supervisores, multi-nível | Empresas complexas com sub-equipes |
| **Blackboard** | Agentes lêem/escrevem em memória compartilhada | Tasks exploratórias/paralelas |

### Tipos de Memória em Agentes

```
┌─────────────────────────────────────────────┐
│              Agent Memory Stack             │
├─────────────────┬───────────────────────────┤
│  In-Context     │  Messages no window atual  │
│  External       │  Vector DB, SQL, files     │
│  Episodic       │  Log de ações passadas     │
│  Semantic       │  Knowledge base do domínio │
└─────────────────┴───────────────────────────┘
```

---

## Patterns

### 1. Supervisor Pattern (LangGraph)

O orquestrador avalia estado e decide qual worker invocar em cada passo:

```python
# supervisor_agent.py com LangGraph
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class AgentState(TypedDict):
    messages: list[dict]
    next_agent: str
    final_answer: str | None

def supervisor_node(state: AgentState) -> AgentState:
    """Decide qual agente especialista invocar."""
    last_message = state["messages"][-1]["content"]

    routing_prompt = f"""Given the task: '{last_message}'
    Route to: researcher | coder | writer | FINISH
    Respond with ONLY the agent name."""

    decision = llm.invoke(routing_prompt).content.strip()
    return {**state, "next_agent": decision}

def should_continue(state: AgentState) -> Literal["researcher", "coder", "writer", END]:
    return END if state["next_agent"] == "FINISH" else state["next_agent"]

graph = StateGraph(AgentState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("researcher", researcher_agent)
graph.add_node("coder", coder_agent)
graph.add_node("writer", writer_agent)

graph.set_entry_point("supervisor")
graph.add_conditional_edges("supervisor", should_continue)
for worker in ["researcher", "coder", "writer"]:
    graph.add_edge(worker, "supervisor")  # todos retornam ao supervisor

app = graph.compile()
```

### 2. Handoffs (OpenAI Agents SDK Pattern)

Handoffs transferem controle de um agente para outro de forma explícita. O agente receptor recebe todo o histórico relevante:

```python
# handoff_pattern.py usando openai-agents-sdk style
from dataclasses import dataclass
from typing import Callable

@dataclass
class Handoff:
    target_agent: str
    context: dict          # dados passados ao próximo agente
    reason: str            # log para debugging

class Agent:
    def __init__(self, name: str, instructions: str, tools: list, handoffs: list["Agent"]):
        self.name = name
        self.instructions = instructions
        self.tools = tools
        self.handoffs = {a.name: a for a in handoffs}

    def run(self, messages: list[dict]) -> tuple[str, Handoff | None]:
        response = llm_call(self.instructions, messages, self.tools)

        # Detecta se o modelo quer fazer handoff
        if response.tool_calls:
            for tc in response.tool_calls:
                if tc.name.startswith("transfer_to_"):
                    target = tc.name.replace("transfer_to_", "")
                    return None, Handoff(
                        target_agent=target,
                        context=tc.arguments,
                        reason=f"Transferred from {self.name}"
                    )

        return response.content, None

def run_swarm(entry_agent: Agent, initial_message: str, max_turns: int = 20):
    """Executa swarm de agentes até conclusão ou limite de turns."""
    current_agent = entry_agent
    messages = [{"role": "user", "content": initial_message}]

    for _ in range(max_turns):
        answer, handoff = current_agent.run(messages)
        if answer:
            return answer
        if handoff:
            messages.append({"role": "system", "content": handoff.reason})
            current_agent = entry_agent.handoffs[handoff.target_agent]

    raise RuntimeError("Max turns exceeded without resolution")
```

### 3. Planning Agent com ReAct Loop

```python
# react_agent.py — Reason + Act pattern
REACT_SYSTEM = """You are a planning agent. Use this format strictly:

Thought: [analyze current state and what to do next]
Action: [tool_name]
Action Input: [tool arguments as JSON]
Observation: [tool result - filled by system]
... (repeat as needed)
Final Answer: [answer when sufficient information gathered]"""

def react_loop(task: str, tools: dict, max_steps: int = 10) -> str:
    scratchpad = f"Task: {task}\n"

    for step in range(max_steps):
        response = llm.invoke(REACT_SYSTEM + "\n\n" + scratchpad)
        scratchpad += response

        if "Final Answer:" in response:
            return response.split("Final Answer:")[-1].strip()

        # Parse e executa action
        action = parse_action(response)  # extrai tool_name e input
        if action:
            result = tools[action.name](**action.args)
            scratchpad += f"Observation: {result}\n"

    raise RuntimeError(f"ReAct loop did not converge in {max_steps} steps")
```

### 4. Reflection Pattern

Um agente critica e refina o output de outro agente (ou de si mesmo):

```python
# reflection_pattern.py
async def generate_with_reflection(task: str, max_iterations: int = 3) -> str:
    generator_prompt = "You are an expert. Solve the task thoroughly."
    critic_prompt = """Review the solution below. Identify specific flaws.
    If the solution is satisfactory, respond with 'APPROVED'.
    Otherwise, provide concrete improvement instructions."""

    solution = await agent_call(generator_prompt, task)

    for i in range(max_iterations):
        critique = await agent_call(critic_prompt, f"Task: {task}\n\nSolution:\n{solution}")

        if "APPROVED" in critique:
            return solution

        # Incorpora critique no próximo generation
        solution = await agent_call(
            generator_prompt,
            f"Task: {task}\n\nPrevious attempt:\n{solution}\n\nCritique:\n{critique}\n\nImprove the solution."
        )

    return solution  # retorna melhor versão mesmo sem APPROVED
```

### 5. Human-in-the-Loop

```python
# hitl_checkpoint.py
from enum import Enum

class CheckpointAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"

async def hitl_checkpoint(
    agent_output: str,
    context: str,
    auto_approve_threshold: float = 0.95,
    confidence_score: float = 0.0
) -> str:
    """Ponto de verificação humana em pipelines de agentes."""

    if confidence_score >= auto_approve_threshold:
        return agent_output  # auto-approve para alta confiança

    # Notifica humano via webhook/UI
    decision = await notify_human_reviewer(
        output=agent_output,
        context=context,
        timeout_seconds=3600
    )

    match decision.action:
        case CheckpointAction.APPROVE:
            return agent_output
        case CheckpointAction.REJECT:
            raise AgentOutputRejected(decision.reason)
        case CheckpointAction.MODIFY:
            return decision.modified_output
```

---

## Gotchas

> [!danger] Agent Loops Infinitos
> Sem limite de turns e deteccao de ciclos, agentes podem loop indefinidamente consumindo tokens e custo. SEMPRE defina `max_turns` e implemente cycle detection via hash do estado.

> [!warning] State Explosion em Hierarquias Profundas
> Em arquiteturas hierárquicas com 3+ níveis, o contexto propagado cresce exponencialmente. Use sumarização seletiva de mensagens para comprimir histórico antes de passar ao próximo nível.

> [!warning] Tool Hallucination
> Modelos podem inventar argumentos para tools que não existem. Use `tool_choice` para forçar uso de tools específicas e valide schemas rigorosamente com Pydantic.

### Error Recovery Strategies

```python
# Estratégia de retry com escalação progressiva
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def resilient_agent_call(agent, messages):
    try:
        return await agent.run(messages)
    except RateLimitError:
        raise  # tenacity vai retry
    except ContextWindowExceeded:
        # Fallback: comprimir histórico e tentar novamente
        compressed = await summarize_messages(messages)
        return await agent.run(compressed)
    except AgentError as e:
        # Escalação: encaminhar para agente supervisor
        return await escalate_to_supervisor(e, messages)
```

---

## Snippets

### Shared Memory com Redis

```python
# shared_memory.py — memória compartilhada entre agentes
import redis
import json
from typing import Any

class AgentSharedMemory:
    def __init__(self, session_id: str):
        self.r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        self.prefix = f"mas:{session_id}"
        self.ttl = 3600  # 1 hora de TTL

    def write(self, key: str, value: Any) -> None:
        full_key = f"{self.prefix}:{key}"
        self.r.setex(full_key, self.ttl, json.dumps(value))

    def read(self, key: str) -> Any | None:
        data = self.r.get(f"{self.prefix}:{key}")
        return json.loads(data) if data else None

    def append_to_log(self, event: dict) -> None:
        """Log imutável de ações para auditoria."""
        self.r.lpush(f"{self.prefix}:event_log", json.dumps(event))
```

### Consensus entre Agentes

```python
# consensus.py — votação majoritária entre N agentes
async def agent_consensus(question: str, agents: list, threshold: float = 0.6) -> str:
    """Retorna resposta apenas se >= threshold dos agentes concordam."""
    answers = await asyncio.gather(*[a.answer(question) for a in agents])

    from collections import Counter
    counts = Counter(answers)
    top_answer, top_count = counts.most_common(1)[0]

    agreement_ratio = top_count / len(agents)
    if agreement_ratio >= threshold:
        return top_answer

    raise ConsensusNotReached(f"Best agreement: {agreement_ratio:.0%} for '{top_answer}'")
```

---

## References

- [OpenAI Swarm / Agents SDK](https://github.com/openai/openai-agents-python)
- [LangGraph Multi-Agent Architectures](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [CrewAI Documentation](https://docs.crewai.com/)
- [AutoGen: Multi-Agent Conversation Framework (Microsoft, 2023)](https://arxiv.org/abs/2308.08155)
- [ReAct: Synergizing Reasoning and Acting in LLMs (Yao et al., 2022)](https://arxiv.org/abs/2210.03629)
- [Reflexion: Language Agents with Verbal Reinforcement (Shinn et al., 2023)](https://arxiv.org/abs/2303.11366)

---

## Related

- [[crewai]] — framework de alto nível para equipes de agentes com roles
- [[autogen]] — framework Microsoft para conversas multi-agente
- [[openai-agents-sdk]] — SDK oficial OpenAI com handoffs e guardrails
- [[claude-code-superpowers]] — agentes especializados em tarefas de engenharia
- [[prompt-engineering]] — design de system prompts por agente especializado
