---
tags: [skill, frameworks, langchain]
status: active
level: advanced
updated: 2026-04-05
created: 2026-04-05
aliases: [LangChain]
---

# LangChain

## Overview

LangChain é o framework [[python]] dominante para orquestração de LLMs. Evoluiu de uma API orientada a chains para o modelo LCEL (LangChain Expression Language), que trata cada componente como um `Runnable` componível. A integração com [[rag-architecture]] é central: loaders → splitters → embeddings → [[vector-dbs]] → retrievers formam o pipeline padrão. Para modelos, integra com [[claude-api]] e dezenas de outros provedores com interface uniforme.

> [!info] LCEL é o padrão moderno
> Classes legadas como `LLMChain`, `RetrievalQA` e `ConversationalRetrievalChain` são deprecated. Use LCEL com `|` operator para compor runnables. É mais transparente, mais testável e suporta streaming nativo.

O ecossistema inclui LangSmith para observabilidade/tracing (essencial em produção) e LangGraph para workflows stateful com agentes. [[prompt-engineering]] avançado é aplicado diretamente nos templates de prompt encadeados nos pipelines.

---

## Core Concepts

### LCEL — LangChain Expression Language

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# Every component is a Runnable: .invoke(), .stream(), .batch(), .ainvoke()
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Context:\n{context}"),
    ("human", "{question}"),
])
parser = StrOutputParser()

# Composition with | operator
chain = prompt | model | parser

# Invoke
response = chain.invoke({"context": "...", "question": "What is RAG?"})

# Stream
for chunk in chain.stream({"context": "...", "question": "Explain LCEL"}):
    print(chunk, end="", flush=True)

# Async batch
results = await chain.abatch([
    {"context": "...", "question": "Q1"},
    {"context": "...", "question": "Q2"},
])
```

### Runnables — Core Primitives

```python
from langchain_core.runnables import (
    RunnableParallel,
    RunnableLambda,
    RunnablePassthrough,
    RunnableBranch,
)

# Parallel execution
parallel_chain = RunnableParallel(
    summary=summary_chain,
    keywords=keyword_chain,
    sentiment=sentiment_chain,
)
# Returns {"summary": ..., "keywords": ..., "sentiment": ...}

# Lambda for custom transforms
clean_text = RunnableLambda(lambda x: x.strip().lower())

# PassThrough — forward input unchanged (useful for merging)
full_chain = (
    RunnableParallel(question=RunnablePassthrough(), context=retriever)
    | prompt
    | model
    | parser
)

# Branch — conditional routing
router = RunnableBranch(
    (lambda x: "code" in x["type"], code_chain),
    (lambda x: "summary" in x["type"], summary_chain),
    default_chain,  # fallback
)
```

---

## Patterns

### RAG Pipeline

```python
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough

# 1. Load
loader = PyPDFLoader("document.pdf")
docs = loader.load()

# 2. Split
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ".", " "],
)
splits = splitter.split_documents(docs)

# 3. Embed + Store
vectorstore = Chroma.from_documents(
    documents=splits,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db",
)

# 4. Retrieve
retriever = vectorstore.as_retriever(
    search_type="mmr",  # Maximal Marginal Relevance
    search_kwargs={"k": 5, "fetch_k": 20, "lambda_mult": 0.5},
)

# 5. RAG Chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

### ReAct Agent

```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.tools import tool
from langchain import hub

@tool
def search_database(query: str) -> str:
    """Search the product database for information about products."""
    results = db.search(query)
    return str(results)

@tool
def calculate_price(product_id: str, quantity: int) -> float:
    """Calculate the total price for a given product and quantity."""
    product = db.get_product(product_id)
    return product.price * quantity

tools = [search_database, calculate_price]
prompt = hub.pull("hwchase17/react")

agent = create_react_agent(model, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    max_iterations=10,
    handle_parsing_errors=True,
)

result = agent_executor.invoke({"input": "Find the cheapest laptop and calculate price for 3 units"})
```

### Callbacks and Tracing with LangSmith

```python
import os
from langsmith import Client
from langchain_core.tracers import LangChainTracer

os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "ls__..."
os.environ["LANGCHAIN_PROJECT"] = "production-rag"

# LangSmith traces automatically when env vars are set
# For manual control:
tracer = LangChainTracer(project_name="my-project")

result = chain.invoke(
    {"question": "What is LangChain?"},
    config={"callbacks": [tracer]},
)

# Custom callback
from langchain_core.callbacks import BaseCallbackHandler

class TokenCounterCallback(BaseCallbackHandler):
    def __init__(self):
        self.total_tokens = 0

    def on_llm_end(self, response, **kwargs):
        self.total_tokens += response.llm_output.get("token_usage", {}).get("total_tokens", 0)
```

### Output Parsers

```python
from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from pydantic import BaseModel, Field

class ProductAnalysis(BaseModel):
    sentiment: str = Field(description="positive, negative, or neutral")
    score: float = Field(description="confidence score 0-1")
    key_points: list[str] = Field(description="main points extracted")

parser = PydanticOutputParser(pydantic_object=ProductAnalysis)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Analyze the review.\n{format_instructions}"),
    ("human", "{review}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser
result: ProductAnalysis = chain.invoke({"review": "Great product, fast delivery!"})
```

---

## Gotchas

> [!danger] LegacyChain vs LCEL — não misture
> `LLMChain`, `RetrievalQA` e similares não se compõem bem com LCEL. Evite misturar os dois paradigmas no mesmo pipeline — o comportamento de callbacks e tracing pode divergir.

> [!warning] Retriever `k` inadequado degrada qualidade
> Um `k` muito baixo perde contexto relevante; muito alto polui o contexto e aumenta custo. Use MMR (`search_type="mmr"`) para diversidade e um reranker (Cohere, cross-encoder) para qualidade.

```python
# RUIM — k fixo sem considerar query complexity
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# MELHOR — MMR + reranker pipeline
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

compressor = CohereRerank(model="rerank-english-v3.0", top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=compressor,
    base_retriever=vectorstore.as_retriever(search_kwargs={"k": 20}),
)
```

> [!warning] Tokens de contexto em agentes
> Agentes com histórico longo podem facilmente exceder o context window. Use `ConversationSummaryBufferMemory` ou implemente compressão manual de histórico.

---

## Snippets

### Streaming com async generator

```python
async def stream_rag_response(question: str):
    async for chunk in rag_chain.astream(question):
        yield chunk

# FastAPI endpoint
from fastapi.responses import StreamingResponse

@router.get("/chat/stream")
async def chat_stream(q: str):
    return StreamingResponse(
        stream_rag_response(q),
        media_type="text/event-stream",
    )
```

### LangGraph — Stateful Agent

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    messages: Annotated[list, operator.add]
    next: str

def should_continue(state: AgentState) -> str:
    last_msg = state["messages"][-1]
    return "tools" if last_msg.tool_calls else END

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", execute_tools)
graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue)
graph.add_edge("tools", "agent")
app = graph.compile()
```

---

## References

- [LangChain LCEL Docs](https://python.langchain.com/docs/expression_language/)
- [LangSmith Tracing](https://docs.smith.langchain.com/)
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [RAG from Scratch](https://github.com/langchain-ai/rag-from-scratch)

---

## Related

- [[python]]
- [[rag-architecture]]
- [[vector-dbs]]
- [[claude-api]]
- [[prompt-engineering]]
