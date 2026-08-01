---
house: tech
domain: skills
type: index
updated: 2026-07-29
---

# Índice — Linguagens e Ferramentas

## Bancos de dados — `tech/01-skills/databases/`

| Nota | O que responde | Nível |
|---|---|---|
| [[postgresql]] | Usar Postgres além do CRUD: escolher entre B-tree, GIN, GiST e BRIN, escrever CTE recursiva e window function, particionar tabela, decidir quando JSONB substitui uma tabela e quando é preguiça. Cobre as extensões que evitam um banco especializado (pgvector, TimescaleDB), LISTEN/NOTIFY e replicação lógica, as views `pg_stat` para diagnóstico — e as três armadilhas que derrubam produção: bloat por VACUUM mal ajustado, escalada de lock em migration e o teto de conexões. | advanced |
| [[database-optimization]] | Diagnosticar uma query lenta antes de reescrevê-la: ler `EXPLAIN (ANALYZE, BUFFERS)`, montar a estratégia de índice, ajustar autovacuum e statistics target, e dimensionar PgBouncer sabendo o que o transaction mode quebra. Traz detecção e correção de N+1, roteamento para réplicas de leitura, as camadas de cache e o cache hit ratio como SLO. A regra que abre a nota é o método: nunca otimize sem medir primeiro — o instinto sobre onde está o gargalo costuma estar errado. | advanced |
| [[redis]] | Escolher a estrutura de dados certa (string, hash, set, sorted set, stream) e saber onde Redis para de ser cache: pub/sub que perde mensagem sem subscriber contra streams que persistem, script Lua para atomicidade, Redlock para lock distribuído e seus limites. Decide RDB contra AOF pelo risco de perda aceitável, explica as políticas de eviction e por que `KEYS` em produção trava o servidor. Traz cache-aside com TTL jitter contra thundering herd. | advanced |
| [[mongodb]] | Modelar documento em vez de tabela e pagar o preço certo: aggregation pipeline, índices compostos, replica sets e — a decisão irreversível — o shard key, que não se altera depois. Cobre transações multi-documento, change streams para CDC, Atlas Search, o teto de 16 MB por documento e por que `$lookup` em coleção shardada é caro. | advanced |
| [[supabase]] | Construir backend sobre Postgres gerenciado sem cair nos furos de segurança do modelo: RLS (desabilitada por padrão, e o que a service role key ignora), Auth com JWT e OAuth, Realtime por canais, Edge Functions em Deno e Storage com policies. Traz migrations, queries avançadas via PostgREST, geração automática de tipos TypeScript e os cold starts que aparecem em produção. | advanced |
| [[planetscale]] | Decidir se o workflow de branching de banco compensa as restrições do Vitess: deploy requests com análise de impacto, migração sem bloqueio de tabela, revert window de 30 minutos. O ponto que decide a adoção é o que se perde — **sem foreign keys**, integridade referencial vira responsabilidade da aplicação — mais o custo de scatter queries e o desenho de schema exigido pelo sharding. Registra que o free tier acabou em 2024. | advanced |
| [[vector-dbs]] | Escolher e operar o armazenamento de embeddings de um sistema RAG: métricas de similaridade (cosine, L2, dot product) e quando cada uma vale, HNSW e IVF com o trade-off entre tempo de build e latência de query, filtragem por metadado e busca híbrida densa+esparsa. Traz a tabela comparando Pinecone, Qdrant, Weaviate, Chroma e pgvector por hosting, dimensões e controle de índice — pgvector limitado a 2.000 dimensões é o corte que elimina candidatos. Avisa que trocar de modelo de embedding obriga a reindexar tudo, e que chunking pesa mais na qualidade que a escolha do banco. | advanced |

## Frameworks — `tech/01-skills/frameworks/`

| Nota | O que responde | Nível |
|---|---|---|
| [[fastapi]] | Estruturar uma API Python de produção: sistema de injeção de dependência e os escopos que dão erro sutil quando errados, Pydantic v2, lifespan events, organização em routers, background tasks e a fronteira para Celery. Traz fluxo completo de JWT, SQLAlchemy async e paginação com response model. A armadilha que mais custa: rota `async def` que chama código bloqueante trava o event loop inteiro. | advanced |
| [[django]] | Tirar proveito do ORM em vez de brigar com ele: `Q`, `F`, `Subquery`, e `select_related`/`prefetch_related` para matar o N+1 que o ORM esconde. Decide entre DRF e Django Ninja para a camada de API, cobre signals (e por que mascaram side effects), async views, middleware customizado e migrations com downtime zero. | advanced |
| [[nextjs]] | Trabalhar no App Router sem lutar contra o modelo: Server Components como padrão e `"use client"` como opt-in — que não significa "só no cliente" —, Server Actions com validação dupla obrigatória, e as camadas de cache com `revalidatePath`. Cobre parallel e intercepting routes, streaming com Suspense, middleware, route handlers e otimização de imagem. | advanced |
| [[react]] | Usar React 19 com o modelo mental novo: Server Components, hook `use()`, Actions e o que o React Compiler passa a fazer por você — e o que ele continua não resolvendo. Traz features concorrentes, gerência de estado com Zustand e Jotai, hooks customizados avançados e error boundaries. A armadilha clássica: closure em effect capturando valor velho. | advanced |
| [[svelte]] | Migrar para o sistema de reatividade explícito do Svelte 5: as runes `$state`, `$derived` e `$effect`, incluindo uso fora de componentes para lógica composível, e `$state.raw` para controle fino. Cobre load functions e form actions do SvelteKit, hooks, transições, e a migração de stores para runes. Alerta para `$effect` com dependência circular e para reatividade de array/objeto. | advanced |
| [[astro]] | Decidir por zero JavaScript no cliente por padrão e adicionar interatividade cirúrgica: arquitetura de islands, as client directives e o que `client:only` custa (pula SSR inteiro), content collections. Traz adapters de SSR, renderização híbrida, middleware, view transitions e Astro DB. Restrição prática: props de island precisam ser serializáveis. | advanced |
| [[htmx]] | Construir interação sem escrever JavaScript, devolvendo HTML em vez de JSON: `hx-get`/`hx-post`, estratégias de `hx-swap`, triggers avançados e swaps out-of-band. Traz integração com Django e com FastAPI+Jinja2, response headers, Alpine.js como companheiro e a extensão de WebSocket. Cobre CSRF em Django e o que acontece com o histórico de navegação. | advanced |
| [[langchain]] | Orquestrar LLM com LCEL em vez das chains legadas — e não misturar as duas. Cobre os `Runnable` como primitiva composível, o pipeline RAG canônico (loaders → splitters → embeddings → retriever), agente ReAct, callbacks e tracing com LangSmith, output parsers e LangGraph para agente com estado. Avisa que `k` mal escolhido no retriever degrada a resposta antes de o modelo entrar em cena. | advanced |

## Linguagens — `tech/01-skills/languages/`

| Nota | O que responde | Nível |
|---|---|---|
| [[python]] | Escrever Python de produção com tipagem que sustenta refatoração: `ParamSpec`, `TypeVar`, `Protocol`, padrões de `asyncio` com `gather` e `TaskGroup`, dataclasses contra Pydantic v2, pattern matching estrutural. Cobre o que o GIL impede e como contornar, profiling de memória com `tracemalloc`, empacotamento moderno com `uv` e `pyproject.toml`. Traz as armadilhas que ainda pegam gente experiente: mutável como argumento default e `asyncio.run()` dentro de corrotina. | advanced |
| [[typescript]] | Modelar domínio com precisão em vez de só "adicionar tipos": generics com constraint, conditional types e `infer`, template literal types, mapped types, narrowing por união discriminada, `satisfies`, const assertions e module augmentation. Traz tsconfig estrito para produção e por que `noUncheckedIndexedAccess` quebra código existente — além do custo real de `as`, que desliga o sistema de tipos no ponto exato onde ele importava. | advanced |
| [[rust]] | Decidir se o problema justifica Rust e então escrevê-lo: ownership e borrowing, lifetimes, `dyn` contra `impl` na escolha entre trait object e generic, runtime async com Tokio, tratamento de erro com `thiserror`/`anyhow`, smart pointers e FFI com PyO3 para expor a Python. Cobre abstrações de custo zero, quando `unsafe` se justifica, e os problemas que aparecem em produção: deadlock de mutex em código async, referência circular com `Rc`, e o tempo de compilação. | advanced |

## Ferramentas — `tech/01-skills/tools/`

| Nota | O que responde | Nível |
|---|---|---|
| [[docker]] | Produzir imagem pequena, reproduzível e com pouca superfície de CVE: multi-stage build, ordenação de layers para acerto de cache, BuildKit com mount cache, SSH e secrets. Traz a tabela de imagens base com tamanho e superfície de CVE (`ubuntu` ~78 MB até `scratch`), rootless mode, healthchecks, `STOPSIGNAL` e tini para signal handling, buildx multi-plataforma e scanning. Deixa explícito que `.dockerignore` não é `.gitignore` e que secret em variável de ambiente vaza. | advanced |
| [[git-advanced]] | Reescrever, recuperar e automatizar histórico com segurança: rebase interativo comando a comando, worktrees, `bisect` manual e automatizado para achar o commit que introduziu o bug, e `reflog` para recuperar o que parecia perdido — lembrando que reflog expira. Traz a comparação submodule contra subtree, hooks compartilhados com o time, cherry-pick, sparse checkout para monorepo, `filter-repo` e `rerere`. | advanced |
| [[claude-code]] | Operar o Claude Code além do prompt: comandos e flags do CLI, slash commands, integração com MCP servers, sistema de hooks (e o significado dos exit codes), `settings.json` hierárquico, subagents, o plugin Superpowers, worktrees para trabalho isolado e permission modes. Registra que `CLAUDE.md` entra em todos os tokens — logo, o que se escreve nele tem custo por chamada. | advanced |
