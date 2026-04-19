---
tags: [moc, ai-ml]
status: active
level: advanced
updated: 2026-04-05
aliases: [AI/ML MOC]
created: 2026-04-05
---

# 🤖 AI/ML MOC

## Visão Geral

Este MOC cobre o domínio de Inteligência Artificial e Machine Learning com foco em Large Language Models (LLMs), sistemas multi-agentes, RAG (Retrieval-Augmented Generation) e os frameworks que tornam essas tecnologias acessíveis em produção. É a área de maior crescimento do vault — novas ferramentas e padrões surgem constantemente.

O foco aqui não é ML clássico (sklearn, redes neurais from scratch), mas a camada de aplicação sobre modelos fundacionais: como orquestrar, promover e deployar sistemas de IA úteis e confiáveis.

> [!info] Cobertura
> Esta seção (`03-ai-ml/`) contém 23 arquivos organizados em padrões de LLM, frameworks de IA, MCP e ferramentas de API.

> [!warning] Área em Rápida Evolução
> Esta é a seção de maior volatilidade do vault. Verificar atualidade dos arquivos com frequência maior — o que era estado da arte há 6 meses pode estar obsoleto.

---

## 🔬 Fundamentos — Como LLMs Funcionam

> [!info] Nova Seção — Adicionada em 2026-04-14
> Conhecimento técnico profundo sobre arquitetura, treinamento, inferência e hardware. Base para criar skills e agentes especializados na Vault-Inc.

### Arquitetura & Representação

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[transformer-architecture]] | Self-attention, Multi-head, RoPE, SwiGLU, LayerNorm | ✅ active |
| [[tokenization]] | BPE, WordPiece, SentencePiece, tiktoken, fertility rates | ✅ active |
| [[embeddings]] | Espaço vetorial, cosine similarity, modelos, MRL, anisotropia | ✅ active |

### Treinamento

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[pretraining]] | Next-token loss, scaling laws Chinchilla, data pipelines | ✅ active |
| [[fine-tuning-peft]] | LoRA, QLoRA, PEFT, fine-tuning vs RAG | ✅ active |
| [[rlhf-alignment]] | RLHF, DPO, Constitutional AI, reward hacking | ✅ active |

### Inferência & Otimização

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[kv-cache-attention]] | KV cache, paged attention, GQA, Flash Attention | ✅ active |
| [[quantization]] | INT4/INT8, GPTQ, AWQ, GGUF/llama.cpp | ✅ active |
| [[inference-engines]] | vLLM, TensorRT-LLM, llama.cpp, speculative decoding | ✅ active |

### Hardware

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[gpu-architecture]] | CUDA cores, Tensor Cores, HBM, arithmetic intensity | ✅ active |
| [[specialized-hardware]] | TPU, Groq LPU, Cerebras, Trainium, Apple ANE | ✅ active |
| [[vram-estimation]] | Fórmulas, exemplos práticos, tabela de referência | ✅ active |

### Avaliação

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[benchmarks-evals]] | MMLU, HumanEval, Chatbot Arena, LLM-as-judge | ✅ active |

---

## 📊 Dashboard

```dataview
TABLE status, level, updated
FROM "tech-vault/03-ai-ml"
SORT updated DESC
```

---

## 🗺️ Skills Map

### LLM Patterns — Padrões Arquiteturais

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[prompt-engineering]] | Técnicas avançadas de prompting | ✅ active |
| [[rag-architecture]] | Retrieval-Augmented Generation | ✅ active |
| [[multi-agent-systems]] | Orquestração de agentes autônomos | ✅ active |

### AI Frameworks

| Arquivo | Framework | Status |
|---------|-----------|--------|
| [[langchain]] | LangChain — orquestração de LLMs | ✅ active |
| [[claude-code-superpowers]] | Claude Code — uso avançado e automações | ✅ active |
| [[openai-agents-sdk]] | OpenAI Agents SDK | ✅ active |
| [[crewai]] | CrewAI — agentes colaborativos | 🚧 draft |
| [[autogen]] | AutoGen (Microsoft) — conversação multi-agente | 🚧 draft |
| [[vercel-ai-sdk]] | Vercel AI SDK — IA no frontend/edge | ✅ active |

### MCP — Model Context Protocol

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[mcp-servers-guide]] | Criação e uso de MCP servers | ✅ active |

### APIs

| Arquivo | Conteúdo | Status |
|---------|---------|--------|
| [[claude-api]] | Anthropic Claude API — referência completa | ✅ active |

---

## ⚡ Quick Access

- [[prompt-engineering]] — Base para qualquer trabalho com LLMs
- [[rag-architecture]] — Padrão mais comum para knowledge bases
- [[claude-code-superpowers]] — Maximizar produtividade com Claude Code
- [[mcp-servers-guide]] — Estender capacidades de agentes com ferramentas
- [[claude-api]] — Referência da API Anthropic

---

## 🧠 Padrões Fundamentais

### RAG Architecture

> [!tip] Quando Usar RAG
> Use RAG quando você tem documentos proprietários que o modelo não conhece. É mais simples e confiável que fine-tuning para a maioria dos casos de uso empresariais.

```
Pergunta do usuário
       ↓
Embedding da pergunta
       ↓
Busca vetorial (ver [[vector-dbs]])
       ↓
Context retrieval (top-k documentos)
       ↓
Prompt enriquecido → LLM → Resposta
```

Para implementação detalhada, veja [[rag-architecture]] e [[vector-dbs]] (em [[engineering-moc]]).

### Multi-Agent Systems

```
Orchestrator Agent
├── Research Agent     ← busca informações
├── Analysis Agent     ← processa e analisa
├── Writing Agent      ← gera conteúdo
└── Review Agent       ← valida qualidade
```

Cada agente tem: system prompt especializado, ferramentas específicas e handoff protocol. Ver [[multi-agent-systems]], [[crewai]] e [[autogen]].

---

## 🔧 MCP — Model Context Protocol

> [!info] O que é MCP
> MCP (Model Context Protocol) é o padrão aberto da Anthropic para conectar LLMs a ferramentas e fontes de dados externas. Permite criar "ferramentas" que qualquer modelo compatível pode usar, similar a plugins mas com protocolo padronizado.

```typescript
// Estrutura básica de um MCP server — ver [[mcp-servers-guide]]
const server = new McpServer({
  name: "my-tool-server",
  version: "1.0.0",
});

server.tool("query-database", async (params) => {
  // lógica da ferramenta
  return { result: data };
});
```

---

## 📐 Prompt Engineering Patterns

> [!tip] Técnicas Essenciais
> 1. **Chain of Thought** — peça ao modelo para "pensar passo a passo"
> 2. **Few-shot** — forneça exemplos do formato desejado
> 3. **Role prompting** — defina persona especializada para o modelo
> 4. **Constitutional AI** — regras de comportamento embutidas no prompt
> 5. **ReAct** — intercala raciocínio e ação em agentes

Ver [[prompt-engineering]] para exemplos completos e anti-padrões comuns.

---

## 🔗 Integrações com Outros Domínios

- **Engineering** → [[engineering-moc]] — [[langchain]] e [[vector-dbs]] vivem em `01-skills/`
- **Architecture** → [[architecture-moc]] — padrões como [[event-driven]] aplicados a pipelines de IA
- **Data Engineering** → [[data-engineering-moc]] — ingestão de dados para treino e RAG
- **DevOps** → [[devops-moc]] — observabilidade de sistemas de IA (tracing de chamadas LLM)

---

## 🧪 Avaliação de Sistemas de IA

> [!example] Framework de Avaliação (LLM-as-Judge)
> Para sistemas RAG e agentes, use LLM-as-judge para avaliação automática:
> - **Faithfulness** — resposta é fiel ao contexto recuperado?
> - **Relevance** — contexto recuperado é relevante para a pergunta?
> - **Answer Quality** — resposta é completa e precisa?
>
> Ferramentas: Ragas, LangSmith, Braintrust

---

## 📅 Frameworks — Comparativo Rápido

| Framework | Pontos Fortes | Quando Usar |
|-----------|--------------|-------------|
| [[langchain]] | Ecossistema rico, integrações | Projetos complexos com muitas integrações |
| [[openai-agents-sdk]] | Simples, oficial OpenAI | Agentes baseados em OpenAI |
| [[crewai]] | Agentes colaborativos, roles | Simulação de equipes |
| [[autogen]] | Conversação multi-agente | Pesquisa e exploração |
| [[vercel-ai-sdk]] | Edge-friendly, React hooks | Apps Next.js com streaming |
