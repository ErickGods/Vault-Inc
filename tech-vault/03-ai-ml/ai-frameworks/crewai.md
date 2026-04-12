---
tags: [skill, ai-ml, crewai]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [CrewAI]
---

# CrewAI

## Overview

CrewAI é um framework [[python]] para orquestrar agentes de IA colaborativos, modelado sobre o conceito de "crews" (equipes) onde cada agente tem um papel, objetivo e backstory definidos. O design é inspirado em estruturas organizacionais humanas — um Researcher, um Writer e um Editor colaboram como uma equipe real, com divisão clara de responsabilidades.

Diferente de [[autogen]] (conversação livre) ou [[openai-agents-sdk]] (handoffs explícitos), CrewAI abstrai a orquestração através de definições declarativas de agentes e tasks, deixando o framework decidir como coordenar o trabalho.

> [!important] CrewAI vs LangChain
> CrewAI usa [[langchain]] como backend opcional para ferramentas e LLMs, mas não depende dele. Para novas implementações, prefira as abstrações nativas do CrewAI.

## Core Concepts

### Agent: Role, Goal, Backstory

O `Agent` é definido por sua identidade e não por seu código:

```python
from crewai import Agent
from crewai_tools import SerperDevTool, WebsiteSearchTool

researcher = Agent(
    role="Senior Research Analyst",
    goal="Uncover cutting-edge developments in {topic} and provide actionable insights",
    backstory="""You are a veteran analyst with 15 years of experience.
    You have a talent for synthesizing complex information from multiple sources
    and identifying trends before they become mainstream.""",
    tools=[SerperDevTool(), WebsiteSearchTool()],
    llm="gpt-4o",
    verbose=True,
    allow_delegation=True,      # pode delegar subtasks a outros agentes
    max_iter=10,                # limite de iterações por task
    memory=True,                # ativa memória de curto prazo
)
```

**Backstory é parte do system prompt** — não é apenas documentação. Agentes com backstories bem escritos produzem outputs de maior qualidade porque o contexto narrativo influencia o comportamento do LLM.

### Task: Description, Expected Output, Context

```python
from crewai import Task

research_task = Task(
    description="""Conduct comprehensive research on {topic}.
    Focus on:
    1. Latest developments in the past 6 months
    2. Key players and their strategies
    3. Technical challenges and solutions
    4. Market implications""",
    expected_output="""A detailed research report with:
    - Executive summary (3-5 bullet points)
    - Detailed findings (500-800 words)
    - Sources cited (minimum 5)
    - Confidence level for each finding (High/Medium/Low)""",
    agent=researcher,
    output_file="research_report.md",  # salvar output automaticamente
    async_execution=False,
)

# Task com contexto de outra task (dependency)
writing_task = Task(
    description="Transform the research findings into an engaging article.",
    expected_output="A 1000-word article suitable for a tech blog.",
    agent=writer,
    context=[research_task],    # recebe output da research_task
)
```

### Crew: Agents, Tasks, Process

```python
from crewai import Crew, Process

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[research_task, writing_task, editing_task],
    process=Process.sequential,     # ou Process.hierarchical
    verbose=True,
    memory=True,
    embedder={
        "provider": "openai",
        "config": {"model": "text-embedding-3-small"},
    },
    output_log_file="crew_log.txt",
)

# Executar com variáveis de input
result = crew.kickoff(inputs={"topic": "quantum computing in finance"})
print(result.raw)           # output final como string
print(result.token_usage)   # uso de tokens por agente
```

## Patterns

### Process Types: Sequential vs Hierarchical

**Sequential** — tasks executam em ordem, output de cada task é contexto da próxima:

```
Task 1 (Research) → Task 2 (Write) → Task 3 (Edit) → Output
```

**Hierarchical** — um manager agent coordena dinamicamente:

```python
from crewai import Agent

manager = Agent(
    role="Project Manager",
    goal="Coordinate the team to produce excellent content efficiently",
    backstory="Expert project manager who excels at delegation.",
    allow_delegation=True,
)

crew = Crew(
    agents=[researcher, writer, editor],
    tasks=[complex_task],       # uma task abrangente
    process=Process.hierarchical,
    manager_agent=manager,      # ou manager_llm="gpt-4o"
)
```

No modo hierárquico, o manager quebra a task complexa, delega para agentes especialistas e consolida os resultados.

### Custom Tools

```python
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class DatabaseQueryInput(BaseModel):
    sql: str = Field(description="SQL query to execute")
    limit: int = Field(default=100, description="Max rows to return")

class DatabaseTool(BaseTool):
    name: str = "Database Query Tool"
    description: str = "Execute read-only SQL queries against the analytics DB"
    args_schema: type[BaseModel] = DatabaseQueryInput

    def _run(self, sql: str, limit: int = 100) -> str:
        try:
            results = db.execute(sql, limit=limit)
            return format_as_markdown_table(results)
        except Exception as e:
            return f"Query failed: {str(e)}"
```

### Memory System

CrewAI tem três camadas de memória:

```python
# Short-term memory: contexto da conversa atual (RAG-based)
# Long-term memory: SQLite persistido entre execuções
# Entity memory: extrai e armazena entidades (pessoas, empresas, conceitos)

crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,                    # ativa todas as camadas
    long_term_memory=EnhancedLongTermMemory(
        storage=LTMSQLiteStorage(db_path="./crew_memory.db")
    ),
    entity_memory=EntityMemory(
        storage=RAGStorage(
            embedder_config={"provider": "openai"},
            type="short_term",
        )
    ),
)
```

### Async Execution para Tasks Paralelas

```python
# Tasks sem dependência podem rodar em paralelo
data_analysis_task = Task(
    description="Analyze sales data for Q4",
    agent=analyst,
    async_execution=True,       # não bloqueia outras tasks
)

competitor_research_task = Task(
    description="Research top 5 competitors",
    agent=researcher,
    async_execution=True,
)

# Consolidation task espera ambas completarem
synthesis_task = Task(
    description="Synthesize analysis and research into strategy",
    agent=strategist,
    context=[data_analysis_task, competitor_research_task],
    async_execution=False,      # sincroniza aqui
)
```

### Training e Testing

```python
# Training: melhorar crew com feedback humano
crew.train(
    n_iterations=5,
    filename="training_data.pkl",
    inputs={"topic": "AI trends"},
)

# Testing: avaliar crew com métricas
scores = crew.test(
    n_iterations=3,
    openai_model_name="gpt-4o",
    inputs={"topic": "blockchain"},
)
print(f"Average score: {scores.average_score}")
```

### Callbacks para Monitoramento

```python
from crewai.utilities.events import (
    AgentFinishedTaskEvent,
    TaskCompletedEvent,
    crewai_event_bus,
)

@crewai_event_bus.on(AgentFinishedTaskEvent)
def on_agent_done(source, event: AgentFinishedTaskEvent):
    metrics.increment("agent.tasks_completed", tags={
        "agent": event.agent.role,
        "task": event.task.description[:50],
    })

@crewai_event_bus.on(TaskCompletedEvent)
def on_task_done(source, event: TaskCompletedEvent):
    log.info(f"Task done: {event.task_output.description[:50]}")
```

## Gotchas

> [!warning] Delegation Loops
> Com `allow_delegation=True` em múltiplos agentes, pode ocorrer delegação circular. Use `allow_delegation=False` em agentes "leaf" que não devem delegar.

> [!bug] Memory e Multi-instância
> Long-term memory usa SQLite por padrão, o que causa conflitos em deployments multi-processo. Configure um storage externo (Redis, PostgreSQL) para produção.

> [!caution] Token Usage em Hierarchical Mode
> O manager agent faz chamadas adicionais ao LLM para coordenação. Em tasks complexas, o custo pode ser 3-4x maior que sequential. Monitore via `result.token_usage`.

> [!tip] Integração com [[prompt-engineering]]
> A qualidade do `backstory` impacta diretamente a qualidade do output. Use técnicas de few-shot prompting dentro do backstory para calibrar o comportamento do agente.

## Snippets

### Flow para Pipeline Complexo

```python
from crewai.flow.flow import Flow, listen, start

class ContentFlow(Flow):
    @start()
    def research_phase(self):
        result = research_crew.kickoff(inputs=self.state)
        return result.raw

    @listen(research_phase)
    def writing_phase(self, research_output):
        result = writing_crew.kickoff(inputs={
            **self.state,
            "research": research_output,
        })
        return result.raw

    @listen(writing_phase)
    def publish(self, article):
        publish_to_cms(article)
        return {"status": "published"}
```

### Resultado Estruturado com Pydantic

```python
from pydantic import BaseModel

class ResearchReport(BaseModel):
    summary: str
    key_findings: list[str]
    sources: list[str]
    confidence: float

analysis_task = Task(
    description="Research and analyze the topic",
    expected_output="Structured research report",
    output_pydantic=ResearchReport,   # output validado com Pydantic
    agent=researcher,
)

result = crew.kickoff()
report: ResearchReport = result.pydantic
print(report.confidence)
```

## References

- [CrewAI Docs](https://docs.crewai.com/)
- [CrewAI GitHub](https://github.com/crewAIInc/crewAI)
- [[langchain]] — ferramentas compatíveis com CrewAI
- [[prompt-engineering]] — otimizar role/goal/backstory

## Related

- [[python]] — linguagem base do framework
- [[multi-agent-systems]] — padrões arquiteturais gerais
- [[langchain]] — integração de ferramentas e LLMs
- [[autogen]] — alternativa Microsoft
- [[prompt-engineering]] — qualidade dos prompts de agente
