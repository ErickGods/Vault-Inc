---
tags: [claude-code, fundamentals]
status: active
level: basic
updated: 2026-04-19
created: 2026-04-19
aliases: [Context Window, Gerenciamento de Contexto, Tokens Claude Code]
---

# Context Window Management

## Overview

Context window é o "espaço de trabalho" de memória de curto prazo do Claude — a quantidade máxima de informação que ele pode processar e manter em mente simultaneamente durante uma interação. Quando esse espaço se esgota, o modelo não pode "ver" o início da conversa, perde referências a arquivos lidos anteriormente e pode começar a cometer erros ou omissões.

No Claude Code, gerenciar contexto eficientemente é uma competência crítica: uma sessão mal gerenciada em um projeto grande pode esgotar o contexto em minutos, forçando `/compact` ou reinício de sessão. Uma sessão bem gerenciada mantém o Claude focado e eficiente por horas.

> [!info] Tokens: a unidade de contexto
> Tudo que entra e sai do Claude é medido em tokens. Aproximadamente **1 token ≈ 4 caracteres** em inglês, ou **3-3.5 caracteres** em português (por causa de palavras mais longas). Uma página de texto (~500 palavras) ≈ 700-800 tokens.

Integra com [[what-is-claude-code]], [[claude-models-overview]], [[pricing-and-tokens]].

---

## O que é Context Window

### Definição técnica

O context window é a janela de atenção do transformer — o número máximo de tokens que o modelo processa em uma única forward pass. Ao contrário de um humano que pode consultar memórias antigas, o Claude só "vê" o que está dentro desta janela.

O contexto é composto por:

```
┌────────────────────────────────────────────────────┐
│                  CONTEXT WINDOW                    │
│                                                    │
│  System Prompt (CLAUDE.md + instruções internas)  │
│  ─────────────────────────────────────────────    │
│  Histórico da conversa                             │
│   • Suas mensagens                                 │
│   • Respostas do Claude                            │
│   • Tool calls e resultados (arquivos lidos, etc.) │
│  ─────────────────────────────────────────────    │
│  Mensagem atual (input)                            │
│  ─────────────────────────────────────────────    │
│  Espaço para resposta (output)                     │
└────────────────────────────────────────────────────┘
```

### Por que é um recurso limitado

1. **Custo computacional**: processar mais tokens = mais compute = mais custo e latência
2. **Limite arquitetural**: transformers têm limite físico de atenção (mesmo com técnicas de extensão)
3. **Degradação de qualidade**: modelos tendem a "esquecer" informações do início do contexto quando próximos ao limite

---

## Limites por Modelo

| Modelo | Context Window | Max Output Tokens |
|--------|---------------|-------------------|
| claude-3-haiku-20240307 | 200.000 tokens | 4.096 tokens |
| claude-3-5-haiku-20241022 | 200.000 tokens | 8.192 tokens |
| claude-haiku-4-5 | 200.000 tokens | 8.192 tokens |
| claude-3-5-sonnet-20241022 | 200.000 tokens | 8.192 tokens |
| claude-sonnet-4-5 | 200.000 tokens | 64.000 tokens |
| claude-sonnet-4-6 | 200.000 tokens | 64.000 tokens |
| claude-3-opus-20240229 | 200.000 tokens | 4.096 tokens |
| claude-opus-4-5 | 200.000 tokens | 32.000 tokens |
| claude-opus-4-6 | 200.000 tokens | 32.000 tokens |

> [!info] 200K tokens em perspectiva
> 200.000 tokens ≈ 150.000 palavras ≈ 500 páginas de texto. Parece imenso, mas um repositório médio com histórico de conversa, arquivos lidos e tool results pode atingir esse limite mais rápido do que você imagina.

---

## Como Claude Code Gerencia Contexto

### Auto-compactação

O Claude Code monitora o uso de contexto e, quando se aproxima do limite, realiza **auto-compactação automática**: resume o histórico da conversa em uma versão comprimida que preserva os pontos essenciais. Isso acontece transparentemente — você pode não perceber que ocorreu.

O trigger de auto-compactação é configurável e geralmente ativa em ~80-90% do limite.

### CLAUDE.md incluído automaticamente

O arquivo `CLAUDE.md` na raiz do projeto (e em subdiretórios) é injetado no início de toda sessão como parte do system prompt. Isso significa que ele **sempre** consome tokens — o CLAUDE.md de 5.000 tokens custa esses tokens em cada mensagem da sessão.

```bash
# Verificar tamanho do CLAUDE.md em tokens (aproximado)
wc -w CLAUDE.md  # palavras ÷ 0.75 ≈ tokens
```

### Tool results no contexto

Cada vez que o Claude executa uma ferramenta (lê arquivo, roda bash, etc.), o resultado é adicionado ao contexto:

```
Claude: [lê app/models.py — 500 linhas]
→ +~2.500 tokens adicionados ao contexto

Claude: [roda pytest — output de 100 linhas]
→ +~500 tokens adicionados ao contexto

Claude: [lê 5 arquivos de config]
→ +~1.000 tokens adicionados ao contexto
```

---

## O que Consome Tokens

### Breakdown típico de uma sessão

| Componente | Tokens típicos | Percentual |
|-----------|----------------|------------|
| System prompt interno do Claude Code | ~2.000 | 1% |
| CLAUDE.md do projeto | 500-5.000 | 0.25-2.5% |
| Histórico de conversa | Cresce com o tempo | variável |
| Arquivos lidos (Read tool) | 500-10.000 por arquivo | maior custo |
| Output de comandos bash | 100-5.000 por execução | variável |
| Resposta do Claude | 200-4.000 por mensagem | variável |

### Os maiores consumidores

**1. Arquivos grandes lidos inteiros:**
```bash
# Ler um arquivo de 1.000 linhas ≈ 5.000-8.000 tokens
# Ler 10 arquivos assim = 50.000-80.000 tokens = 25-40% do contexto
```

**2. Output de comandos verbosos:**
```bash
# git log --all --oneline (repositório com 1000 commits)
# → pode gerar 5.000+ tokens de output
```

**3. Stack traces e logs longos:**
```bash
# pytest com verbose output em um projeto grande
# → facilmente 2.000-10.000 tokens
```

**4. Histórico acumulado de conversa:**
```bash
# Cada round-trip (pergunta + resposta + tool calls) ≈ 1.000-5.000 tokens
# Sessão longa de 2h → pode acumular 50.000-100.000 tokens
```

---

## Estratégias de Otimização

### 1. Leitura seletiva de arquivos

Em vez de ler arquivos inteiros, use offset e limit:

```bash
# Ruim: lê o arquivo inteiro (10.000 tokens)
> Leia app/models.py e encontre a classe User

# Bom: o Claude vai usar Read com offset/limit
> Encontre onde está definida a classe User em app/models.py
# → Claude usa grep primeiro, depois lê apenas as linhas relevantes
```

Quando usando a API diretamente:
```python
# Ler apenas linhas 100-200 de um arquivo grande
with open("app/models.py") as f:
    lines = f.readlines()
    relevant_section = "".join(lines[100:200])
```

### 2. Usar grep antes de ler

O Claude Code usa Grep internamente (via ripgrep), que retorna apenas linhas que fazem match — muito mais eficiente que ler arquivos completos:

```
> Onde está implementada a autenticação JWT neste projeto?
# → Claude usa grep para localizar, lê apenas os arquivos relevantes
```

### 3. Subagentes com contexto isolado

Para tarefas que envolvem muitos arquivos independentes, use subagentes paralelos — cada um com seu próprio contexto limpo:

```bash
# Em vez de uma sessão que lê 20 arquivos e esgota o contexto:
# Lance 4 subagentes, cada um processando 5 arquivos independentes

claude --print "Refatore apenas src/auth/*.py para usar type hints" &
claude --print "Refatore apenas src/api/*.py para usar type hints" &
claude --print "Refatore apenas src/models/*.py para usar type hints" &
claude --print "Refatore apenas src/utils/*.py para usar type hints" &
wait
```

### 4. /compact — Compactação manual

Quando o contexto está alto mas você quer continuar a sessão:

```bash
> /compact
# → Claude cria um resumo denso do histórico atual
# → Contexto reduz significativamente
# → Sessão continua com o contexto comprimido
```

> [!warning] Perda de informação no /compact
> O `/compact` comprime — inevitavelmente perde alguns detalhes. Depois de compactar, verifique se o Claude ainda tem acesso às informações que você considerou importantes.

### 5. Sessões focadas em vez de sessões longas

```bash
# Ruim: uma sessão monstruosa que faz tudo
> Implemente auth, refatore models, adicione testes, gere docs, faça PR...
# → contexto estoura, qualidade degrada no final

# Bom: sessões focadas com objetivos claros
claude --print "Implemente JWT auth em src/auth/"  # sessão 1
claude --print "Adicione testes para src/auth/"     # sessão 2
claude --print "Atualize a documentação de auth"    # sessão 3
```

### 6. CLAUDE.md enxuto

O CLAUDE.md é lido em toda sessão. Mantenha-o conciso:

```markdown
# RUIM — CLAUDE.md de 500 linhas com exemplos extensos
## Tech Stack
[5 parágrafos descrevendo cada tecnologia em detalhe...]
## Comandos
[lista de 50 comandos com descrições longas...]
## Histórico do projeto
[timeline completo do projeto...]

# BOM — CLAUDE.md de 50 linhas, só o essencial
## Stack: FastAPI + PostgreSQL + Next.js
## Test: `make test` | Lint: `make lint` | Dev: `make dev`
## Convenções: Conventional Commits, branches feat/fix/chore
## DB: SQLAlchemy async, sempre usar migrations Alembic
```

---

## Sinais de que o Contexto Está Cheio

### Comportamentos do modelo

**1. Respostas inconsistentes com o início da sessão:**
```
Você no início: "use sempre type hints em Python"
Claude depois de muitas mensagens: gera código sem type hints
→ Sinal: o início da conversa foi "empurrado para fora" do contexto
```

**2. Claude "esquece" arquivos que leu:**
```
Você: "Lembre-se do arquivo config.py que você leu?"
Claude: "Não tenho acesso ao conteúdo de config.py no momento..."
→ Sinal: o resultado da leitura foi comprimido/perdido
```

**3. Respostas mais genéricas e menos contextualizadas:**
```
Respostas iniciais: específicas ao seu projeto, conhece as convenções
Respostas tardias: genéricas, como se não conhecesse o projeto
→ Sinal: o contexto do projeto foi perdido
```

**4. Aviso explícito do Claude Code:**
```
⚠️ Context window is 85% full. Consider using /compact or starting a new session.
```

**5. Truncamento de tool results:**
O Claude Code pode começar a truncar resultados de ferramentas para economizar espaço.

---

## Soluções Quando o Contexto Estoura

### Opção 1: /compact (continuar a sessão)

```bash
> /compact
# Comprime histórico, continua a sessão
# Melhor quando: no meio de uma tarefa complexa que não pode reiniciar
```

### Opção 2: Novo chat com contexto selecionado

```bash
# Feche a sessão atual
# Abra nova sessão com informações essenciais
claude

> Contexto: estou implementando JWT auth. 
> Já criei src/auth/middleware.py (código: [cole aqui]).
> Próximo passo: integrar com os endpoints em src/api/routes.py
```

### Opção 3: Subagentes para tarefas restantes

```bash
# A sessão atual está com contexto alto
# Lance subagente para a próxima tarefa com contexto fresco
claude --print "
  Dado que src/auth/middleware.py já existe com JWT auth implementado,
  integre este middleware nos endpoints em src/api/routes.py.
  O middleware deve ser aplicado em todas as rotas exceto /health e /auth/login.
"
```

### Opção 4: Worktrees para isolamento completo

```bash
# Para trabalho de longa duração em diferentes features simultaneamente
git worktree add ../feature-payments feat/payments
git worktree add ../feature-auth feat/auth

# Cada worktree tem sua própria sessão do Claude Code com contexto isolado
cd ../feature-payments && claude &
cd ../feature-auth && claude &
```

---

## Técnicas Avançadas

### Chunking — Processamento em partes

Para arquivos muito grandes, processe em chunks:

```python
def process_large_file_with_claude(filepath: str, chunk_size: int = 200):
    """Processa arquivo grande em chunks para evitar esgotar contexto."""
    with open(filepath) as f:
        lines = f.readlines()
    
    results = []
    for i in range(0, len(lines), chunk_size):
        chunk = "".join(lines[i:i + chunk_size])
        
        response = client.messages.create(
            model="claude-haiku-4-5",  # modelo barato para cada chunk
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": f"Analise este trecho de código (linhas {i}-{i+chunk_size}):\n\n{chunk}"
            }]
        )
        results.append(response.content[0].text)
    
    # Síntese final com modelo mais capaz
    synthesis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": f"Sintetize estas análises parciais:\n\n" + "\n\n---\n\n".join(results)
        }]
    )
    return synthesis.content[0].text
```

### Summarization hierárquica

Para sessões longas, crie summaries intermediários:

```bash
# A cada 30 minutos de trabalho intenso
> Faça um resumo em bullet points das mudanças que fizemos até agora nesta sessão
# → Salve o resumo
> /clear
# → Cole o resumo no início da nova sessão
> Continuando de onde paramos: [cole o resumo]
```

### Read com offset/limit explícito

Na API, ao passar arquivos para o contexto, use leitura seletiva:

```python
def read_file_section(filepath: str, start_line: int, end_line: int) -> str:
    """Lê apenas a seção relevante de um arquivo."""
    with open(filepath) as f:
        lines = f.readlines()
    return "".join(lines[start_line:end_line])

# Ao invés de passar o arquivo inteiro:
relevant_code = read_file_section("app/models.py", 150, 200)
# → passa para o Claude apenas as linhas 150-200
```

### Contexto dinâmico — incluir só o necessário

```python
def build_context_for_task(task: str, project_root: str) -> str:
    """Constrói contexto mínimo necessário para a tarefa."""
    context_parts = []
    
    # 1. Sempre inclui CLAUDE.md
    claude_md = read_file(f"{project_root}/CLAUDE.md")
    context_parts.append(f"# Contexto do projeto\n{claude_md}")
    
    # 2. Inclui só os arquivos mencionados na tarefa
    mentioned_files = extract_file_mentions(task)  # regex para encontrar paths
    for filepath in mentioned_files:
        if os.path.exists(f"{project_root}/{filepath}"):
            content = read_file(f"{project_root}/{filepath}")
            context_parts.append(f"# {filepath}\n```\n{content}\n```")
    
    return "\n\n".join(context_parts)
```

---

## CLAUDE.md e seu Impacto no Contexto

### Análise de custo por tamanho

| Tamanho do CLAUDE.md | Tokens aprox. | Custo por mensagem (Sonnet) | Custo por 1000 mensagens |
|---------------------|---------------|---------------------------|--------------------------|
| 1 KB (~250 palavras) | ~300 tokens | $0.0009 | $0.90 |
| 5 KB (~1.250 palavras) | ~1.500 tokens | $0.0045 | $4.50 |
| 20 KB (~5.000 palavras) | ~6.000 tokens | $0.018 | $18 |
| 50 KB (~12.500 palavras) | ~15.000 tokens | $0.045 | $45 |

### Boas práticas para CLAUDE.md

```markdown
# Regra 1: Apenas informações que afetam DECISÕES do Claude
## Stack: FastAPI/Python 3.11, PostgreSQL 15, Next.js 14
## DB: async SQLAlchemy, todas queries via session.execute()
## Auth: JWT via python-jose, sempre verificar em middleware

# Regra 2: Comandos exatos, sem explicação
## make test → pytest com coverage
## make lint → ruff + mypy  
## make migrate → alembic upgrade head

# Regra 3: Convenções que o Claude pode violar por default
## Commits: Conventional Commits em inglês
## APIs: sempre retornar {data: ..., error: null} ou {data: null, error: ...}
## Logs: usar structlog, nunca print()

# Regra 4: NÃO incluir
## História do projeto
## Explicações pedagógicas
## Código de exemplo longo
## Links e referências
```

---

## Exemplos Práticos com Código

### Verificar uso de contexto via API

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=1000,
    messages=[{"role": "user", "content": "Olá, como você está?"}]
)

# Verificar uso de tokens
print(f"Input tokens: {response.usage.input_tokens}")
print(f"Output tokens: {response.usage.output_tokens}")
print(f"Cache read tokens: {response.usage.cache_read_input_tokens}")
print(f"Cache creation tokens: {response.usage.cache_creation_input_tokens}")

# Calcular % do contexto usado
context_limit = 200_000
used_percent = (response.usage.input_tokens / context_limit) * 100
print(f"Contexto usado: {used_percent:.1f}%")
```

### Monitor de contexto para sessões longas

```python
class ContextMonitor:
    def __init__(self, model: str = "claude-sonnet-4-6", limit: int = 200_000):
        self.model = model
        self.limit = limit
        self.history = []
        self.client = anthropic.Anthropic()
    
    def chat(self, message: str) -> str:
        self.history.append({"role": "user", "content": message})
        
        response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=self.history
        )
        
        assistant_message = response.content[0].text
        self.history.append({"role": "assistant", "content": assistant_message})
        
        # Monitorar uso
        used = response.usage.input_tokens
        percent = (used / self.limit) * 100
        
        if percent > 80:
            print(f"⚠️  CONTEXTO {percent:.0f}% CHEIO — considere compactar")
        elif percent > 60:
            print(f"ℹ️  Contexto {percent:.0f}% usado")
        
        return assistant_message
    
    def compact(self):
        """Compacta o histórico mantendo apenas o essencial."""
        summary_prompt = "Faça um resumo conciso em bullet points desta conversa, preservando decisões técnicas e código relevante."
        
        summary_response = self.client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=self.history + [{"role": "user", "content": summary_prompt}]
        )
        
        summary = summary_response.content[0].text
        
        # Reinicia histórico com o resumo como contexto
        self.history = [{
            "role": "user",
            "content": f"[Resumo da conversa anterior]\n{summary}\n\n[Continuando a partir daqui]"
        }, {
            "role": "assistant",
            "content": "Entendido, vou continuar com base no resumo da nossa conversa anterior."
        }]
        
        print(f"✓ Contexto compactado. Tokens anteriores preservados em resumo.")
```

---

## Related

- [[what-is-claude-code]] — Como o Claude Code gerencia contexto internamente
- [[claude-models-overview]] — Context window de cada modelo
- [[pricing-and-tokens]] — Custo por token e estratégias de economia
- [[claude-code-vs-api-vs-chat]] — Diferenças de contexto entre interfaces
- [[../02-core-features/claude-md-configuration]] — CLAUDE.md em profundidade
- [[../03-advanced/subagents-parallel-execution]] — Subagentes para contexto isolado
- [[../03-advanced/worktrees-workflow]] — Worktrees para sessões paralelas isoladas
