---
tags: [skill, ai-ml, autogen]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [AutoGen, AG2]
---

# AutoGen (AG2)

## Overview

AutoGen (rebrandeado como AG2 pela comunidade) é o framework da Microsoft Research para sistemas de agentes conversacionais. Sua filosofia central é que **agentes se comunicam via mensagens de chat**, tornando o fluxo de trabalho auditável e debugável como uma conversa humana. Diferente de [[crewai]] (roles declarativos) ou [[openai-agents-sdk]] (handoffs estruturados), AutoGen é maximamente flexível — qualquer padrão de comunicação é possível.

O framework [[python]] suporta execução de código segura, memória persistente via Teachability, e padrões avançados como swarms e nested conversations.

> [!important] AG2 vs AutoGen v0.2
> A versão 0.4+ (AG2) tem API incompatível com v0.2. O pacote foi renomeado para `autogen-agentchat`. Verifique qual versão o seu projeto usa antes de copiar exemplos.

## Core Concepts

### ConversableAgent

O `ConversableAgent` é a classe base para todos os agentes:

```python
from autogen import ConversableAgent

agent = ConversableAgent(
    name="AssistantAgent",
    system_message="""You are a helpful AI assistant.
    When you solve a problem, explain your reasoning step by step.
    Always verify your answers before responding.""",
    llm_config={
        "model": "gpt-4o",
        "temperature": 0.1,
        "api_key": os.environ["OPENAI_API_KEY"],
        "cache_seed": 42,       # reproducibilidade
    },
    human_input_mode="NEVER",  # NEVER | ALWAYS | TERMINATE
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)
```

**human_input_mode controla quando o agente solicita input humano:**

```
NEVER    → agente totalmente autônomo
ALWAYS   → solicita input após cada mensagem
TERMINATE → solicita input quando a conversa deveria terminar
```

### UserProxyAgent

`UserProxyAgent` representa o humano e executa código:

```python
from autogen import UserProxyAgent

user_proxy = UserProxyAgent(
    name="UserProxy",
    human_input_mode="TERMINATE",
    code_execution_config={
        "executor": LocalCommandLineCodeExecutor(
            work_dir="./coding",
            timeout=60,
        ),
    },
    max_consecutive_auto_reply=5,
)
```

### GroupChat e GroupChatManager

Para orquestrar 3+ agentes:

```python
from autogen import GroupChat, GroupChatManager

# Agentes especializados
coder = ConversableAgent(name="Coder", system_message="Write Python code.")
reviewer = ConversableAgent(name="Reviewer", system_message="Review code for bugs and performance.")
tester = ConversableAgent(name="Tester", system_message="Write tests for the code.")

group_chat = GroupChat(
    agents=[user_proxy, coder, reviewer, tester],
    messages=[],
    max_round=20,
    speaker_selection_method="auto",  # auto | round_robin | random | custom
    allow_repeat_speaker=False,
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"model": "gpt-4o"},
)

# Iniciar conversa
user_proxy.initiate_chat(
    manager,
    message="Build a REST API endpoint for user authentication with JWT",
)
```

**Speaker selection customizada:**

```python
def custom_speaker_selection(last_speaker, groupchat):
    """Sempre alterna entre coder e reviewer."""
    if last_speaker == coder:
        return reviewer
    elif last_speaker == reviewer:
        return tester
    return coder

group_chat = GroupChat(
    agents=[coder, reviewer, tester],
    speaker_selection_method=custom_speaker_selection,
)
```

## Patterns

### Code Execution: Docker vs Local

**Docker (recomendado para produção):**

```python
from autogen.coding import DockerCommandLineCodeExecutor

docker_executor = DockerCommandLineCodeExecutor(
    image="python:3.12-slim",
    timeout=120,
    work_dir="./sandbox",
    auto_remove=True,           # remove container após execução
    stop_container_on_exit=True,
)

user_proxy = UserProxyAgent(
    name="SafeProxy",
    code_execution_config={"executor": docker_executor},
)
```

**Local (desenvolvimento/testes):**

```python
from autogen.coding import LocalCommandLineCodeExecutor

local_executor = LocalCommandLineCodeExecutor(
    work_dir="./coding",
    timeout=30,
    functions=[],               # funções Python pré-importadas
    virtual_env_context=venv,   # virtualenv isolado
)
```

### Nested Conversations

Nested conversations permitem que um agente inicie uma sub-conversa para resolver um subproblema:

```python
def research_nested(recipient, messages, sender, config):
    """Inicia conversa aninhada para pesquisa profunda."""
    research_agent = ConversableAgent(
        name="Researcher",
        system_message="You are a research specialist.",
        llm_config=config,
    )

    # Sub-conversa dedicada à pesquisa
    result = research_agent.initiate_chat(
        web_agent,
        message=f"Research this topic thoroughly: {messages[-1]['content']}",
        max_turns=5,
        summary_method="reflection_with_llm",
    )
    return True, result.summary

orchestrator.register_nested_chats(
    [{"recipient": research_agent, "summary_method": "last_msg"}],
    trigger=lambda sender: sender.name == "UserProxy",
)
```

### Teachability: Memória Persistente

```python
from autogen.agentchat.contrib.capabilities.teachability import Teachability

teachability = Teachability(
    verbosity=1,
    reset_db=False,                     # preservar memória entre sessões
    path_to_db_dir="./memory/agent_db",
    recall_threshold=1.5,               # similaridade mínima para recall
)

agent = ConversableAgent(name="TutorAgent", llm_config=llm_config)
teachability.add_to_agent(agent)

# Após a conversa, o agente memoriza fatos importantes
# e os recupera em conversas futuras
```

### Two-Agent Chat

O padrão mais simples — dois agentes conversam até terminar:

```python
assistant = ConversableAgent(
    name="Assistant",
    system_message="You solve math problems step by step.",
    llm_config=llm_config,
)

user = ConversableAgent(
    name="User",
    human_input_mode="NEVER",
    llm_config=False,       # sem LLM — só executa código
    code_execution_config={"executor": local_executor},
)

result = user.initiate_chat(
    assistant,
    message="Calculate the eigenvalues of [[1,2],[3,4]]",
    max_turns=8,
    summary_method="reflection_with_llm",
)
print(result.summary)
```

### Sequential Chat (Pipeline)

```python
# Pipeline de processamento em sequência
results = user_proxy.initiate_chats([
    {
        "recipient": data_agent,
        "message": "Load and clean the dataset",
        "summary_method": "last_msg",
        "max_turns": 3,
    },
    {
        "recipient": analysis_agent,
        "message": "Perform statistical analysis on: {carryover}",
        "carryover": "",    # preenchido com summary da chat anterior
        "summary_method": "reflection_with_llm",
        "max_turns": 5,
    },
    {
        "recipient": report_agent,
        "message": "Generate report based on: {carryover}",
        "max_turns": 3,
    },
])
```

### Swarm Pattern

O swarm permite que agentes se passem o contexto dinamicamente:

```python
from autogen.agentchat.contrib.swarm_agent import (
    SwarmAgent,
    initiate_swarm_chat,
    AFTER_WORK,
    ON_CONDITION,
)

def route_to_billing(context_variables):
    return context_variables.get("issue_type") == "billing"

sales_agent = SwarmAgent(
    name="SalesAgent",
    system_message="Handle sales inquiries.",
    llm_config=llm_config,
    after_work=ON_CONDITION(billing_agent, route_to_billing),
)

chat_result, context, last_agent = initiate_swarm_chat(
    initial_agent=triage_agent,
    agents=[triage_agent, sales_agent, billing_agent, tech_agent],
    messages="I have a billing question about my subscription",
    context_variables={"user_id": "user-123"},
    max_rounds=20,
)
```

### Custom Agents com register_reply

```python
class ValidatorAgent(ConversableAgent):
    def __init__(self, schema: dict, **kwargs):
        super().__init__(**kwargs)
        self.schema = schema
        self.register_reply(
            trigger=ConversableAgent,
            reply_func=self._validate_and_reply,
            position=0,         # prioridade máxima
        )

    def _validate_and_reply(self, recipient, messages, sender, config):
        last_msg = messages[-1]["content"]
        try:
            validated = validate_json(last_msg, self.schema)
            return True, f"VALID: {validated}"
        except ValidationError as e:
            return True, f"INVALID: {e.message}. Please fix and retry."
```

## Gotchas

> [!warning] Cache e Reproducibilidade
> `cache_seed` no `llm_config` armazena respostas em disco. Em testes, isso é ótimo. Em produção, pode retornar respostas desatualizadas. Defina `cache_seed=None` em produção.

> [!bug] GroupChat com Muitos Agentes
> Com 6+ agentes em um GroupChat, o `speaker_selection_method="auto"` fica caro (o LLM manager decide quem fala a cada turno). Use `round_robin` ou uma função customizada.

> [!caution] Code Execution e Segurança
> `LocalCommandLineCodeExecutor` executa código na máquina host. Nunca use com código de usuários não confiáveis. Docker executor é obrigatório para inputs externos.

> [!tip] Comparação com [[crewai]]
> AutoGen é melhor para fluxos exploratórios onde a conversa dita a direção. CrewAI é melhor para pipelines com outputs bem definidos. Considere ambos ao projetar [[multi-agent-systems]].

## Snippets

### LLM Config com Fallback

```python
llm_config = {
    "config_list": [
        {"model": "gpt-4o", "api_key": os.environ["OPENAI_API_KEY"]},
        {"model": "claude-3-5-sonnet-20241022", "api_key": os.environ["ANTHROPIC_API_KEY"]},
    ],
    "temperature": 0.1,
    "timeout": 120,
    "cache_seed": None,
}
```

### Extrair Código dos Outputs

```python
from autogen.coding.utils import extract_code_from_string

for msg in chat_result.chat_history:
    if msg["role"] == "assistant":
        code_blocks = extract_code_from_string(msg["content"])
        for lang, code in code_blocks:
            print(f"Language: {lang}\n{code}\n")
```

## References

- [AutoGen Docs](https://microsoft.github.io/autogen/)
- [AG2 GitHub](https://github.com/ag2ai/ag2)
- [AutoGen Paper](https://arxiv.org/abs/2308.08155)
- [[prompt-engineering]] — system messages eficazes

## Related

- [[python]] — linguagem base
- [[multi-agent-systems]] — padrões arquiteturais
- [[crewai]] — alternativa com roles declarativos
- [[openai-agents-sdk]] — alternativa com handoffs estruturados
- [[prompt-engineering]] — otimizar system messages
