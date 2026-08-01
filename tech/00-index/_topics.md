---
house: tech
type: topic-index
updated: 2026-08-01
---

# Casa Tech — Índice de Temas Transversais

Alguns problemas não moram em um domínio. Gestão de segredos é tratada em cinco dos oito
domínios desta casa — o cofre e a rotação estão em devops, o `--mount=type=secret` em
ferramentas, a service role key que ignora RLS em bancos, o API secret que nunca vai ao frontend
em serviços de nuvem, o `CREDENTIAL_CHAIN` em armazenamento. Para essas perguntas, escolher um
domínio em `_house.md` é escolher errado por construção: qualquer escolha perde material que
está em outro lugar.

Use este arquivo quando a pergunta for sobre **uma preocupação**, não sobre um território. A
coluna **Onde começar** nomeia a nota que trata o tema de forma mais direta: abra só ela e pare,
se responder. A coluna **Também tratado em** existe para o caso de não responder — é a
divulgação honesta de que o tema é distribuído, não uma lista de leitura obrigatória.

Se a pergunta for sobre um território (um banco, um framework, uma linguagem, um broker, um
orquestrador), volte para `_house.md` e desça pelo domínio.

## Temas

| Tema | Onde começar | Também tratado em |
|---|---|---|
| Gestão de segredos e credenciais | [[secrets-management]] | [[docker]] (`--mount=type=secret`, e por que segredo em variável de ambiente vaza), [[github-actions]] (OIDC no lugar de credencial de longa duração), [[kubernetes-basics]] (Secret é base64, não criptografia), [[terraform]] (Secrets Manager como data source), [[git-advanced]] (hook de pre-commit e `filter-repo` para o que já vazou), [[supabase]] (service role key ignora RLS), [[cloudinary]] (API secret só no servidor), [[duckdb]] (`PROVIDER CREDENTIAL_CHAIN` em ambiente efêmero), [[prefect]] (blocks como credencial versionada), [[docker-compose-patterns]] |
| Achar o gargalo antes de otimizar | [[database-optimization]] ("o instinto sobre onde está o problema costuma estar errado") | [[postgresql]] (views `pg_stat`), [[sql-snippets]] e [[spark]] (`EXPLAIN`/`explain("formatted")` confirmando o plano real), [[python]] (`tracemalloc` para vazamento), [[gpu-architecture]] (roofline decide memory-bound contra compute-bound), [[inference-engines]] (TTFT e TBT antes de comparar engine), [[big-o-notation]] (para n pequeno quem decide são as constantes, não a classe) |
| Observabilidade em produção — saber **por quê** quebrou | [[observability]] | [[microservices]] (service mesh tira tracing do código; liveness separado de readiness), [[messaging-patterns]] (envelope com correlation, causation e `trace_id`), [[langchain]] (LangSmith), [[openai-agents-sdk]] (spans e tracing processors), [[kubernetes-basics]] (probes), [[reverse-proxy]] (métricas na borda), [[feature-flags]] (medir a variante ativada) |
| Custo de token e de inferência | [[tokenization]] (fertility rate: português custa 1,72 tokens/palavra contra 1,28 do inglês) | [[claude-api]] (prompt caching e Batches como as duas alavancas), [[prompt-engineering]], [[rag-architecture]] (o pipeline inteiro custa 2-4 s e mais contexto), [[vram-estimation]] e [[quantization]] (o custo quando a inferência é sua), [[fine-tuning-peft]] e [[pretraining]] (Chinchilla e o cálculo de FLOPs), [[autogen]] e [[crewai]] (coordenação multiplica tokens), [[claude-code]] (`CLAUDE.md` entra em todos os tokens), [[claude-code-superpowers]] (cada subagente é chamada separada) |
| Custo de infraestrutura | [[s3-storage-patterns]] (escada de storage classes e três custos escondidos) | [[cloudinary]] (cada transformação única vira derived asset armazenado; invalidação de CDN é cara), [[sqs-sns]] (long polling corta ~99% do custo de requisição), [[deployment-strategies]] (blue/green dobra a infra), [[gitlab-ci]] (`interruptible` para não pagar por pipeline obsoleto), [[data-lake-patterns]] (small files problem), [[planetscale]] (o free tier acabou em 2024), [[specialized-hardware]] (eficiência paga em lock-in) |
| Cache e invalidação | [[redis]] (cache-aside, TTL com jitter contra thundering herd, políticas de eviction) | [[database-optimization]] (camadas de cache e cache hit ratio como SLO), [[nextjs]] (as camadas do App Router e `revalidatePath`), [[dns-and-cdn]] (a cadeia de TTL até o resolver do ISP, e cache poisoning via `Vary`), [[cloudinary]] (versione o `public_id` em vez de invalidar), [[claude-api]] (prompt caching com TTL de 5 min), [[docker]] (ordenação de layer para acerto de cache — outro sentido da palavra, ver o critério abaixo) |
| Idempotência e entrega duplicada | [[messaging-patterns]] (as três semânticas, e por que quase todo sistema real usa at-least-once com idempotência no consumer) | [[event-driven]] (`event_id` marcado na mesma transação do efeito), [[sqs-sns]] (Standard duplica e desordena por projeto), [[kafka]] (`enable.idempotence` e exactly-once transacional), [[nats]], [[rabbitmq]] (`auto_ack=True` perde mensagem), [[flink]] (checkpoint EXACTLY_ONCE), [[apache-airflow]] (toda task idempotente), [[data-lake-patterns]] (bronze é cópia idempotente da fonte), [[argocd]] (reconciliação contínua é a mesma propriedade com outro nome) |
| Evolução de schema sem downtime | [[deployment-strategies]] (expand/contract, e por que blue/green quebra com schema compartilhado) | [[sql-snippets]] (coluna nova → trigger → backfill → `NOT NULL`), [[postgresql]] (escalada de lock em migration), [[django]] (schema migration separada da data migration), [[planetscale]] (deploy request sem bloqueio e revert window de 30 min), [[supabase]], [[event-driven]] (evento é imutável: mudança breaking impede o replay), [[kafka]] (Schema Registry e modos de compatibilidade), [[delta-lake]] (schema enforcement por padrão, `mergeSchema` como opt-in), [[data-lake-patterns]] (schema evolution por formato), [[dbt]] (`on_schema_change`) |
| Input não confiável cruzando a fronteira | [[prompt-engineering]] (técnica sandwich, sanitização de input, validação de output) | [[mcp-servers-guide]] (path traversal e sandbox em Docker), [[media-pipeline]] (valide magic bytes, nunca a extensão), [[supabase]] (RLS vem desabilitada por padrão), [[reverse-proxy]] (`X-Forwarded-For` sem validação é confiança em cabeçalho forjável), [[github-actions]] (self-hosted runner em repo público executa código de fork), [[autogen]] (executor local nunca recebe input não confiável), [[cloudinary]] e [[s3-storage-patterns]] (upload assinado no backend), [[tokenization]] (token especial interpolado sem sanitizar), [[htmx]] (CSRF), [[regex-cheatsheet]] (backtracking catastrófico) |
| Gerenciado contra self-hosted | [[adr-guide]] (a decisão satisfaz os quatro critérios de ADR, e o exemplo trabalhado da nota é exatamente essa escolha) | [[cloudinary]] contra [[media-pipeline]] (a mesma decisão escrita dos dois lados), [[vector-dbs]] (tabela comparativa com coluna de hosting), [[prefect]] (Cloud contra self-hosted: muda só `PREFECT_API_URL`), [[sqs-sns]] contra [[rabbitmq]] e [[nats]], [[supabase]] e [[planetscale]], [[feature-flags]] (LaunchDarkly contra Unleash e Flagsmith), [[github-actions]] (self-hosted runners), [[specialized-hardware]] (lock-in de vendor como o preço da eficiência) |

## Critério de inclusão

Um tema entra aqui quando é tratado **em mais de um domínio** — não quando aparece em muitas
notas. O teste é: existe uma escolha de domínio em `_house.md` que responde a pergunta sozinha?
Se existe, o tema pertence ao índice daquele domínio e não a este arquivo. Índice de temas que
cresce sem esse filtro vira um segundo índice de tudo, e volta a custar o contexto que os três
saltos economizam.

Contagem de notas não é o teste; dispersão entre domínios é. E **a confirmação é por leitura da
nota, nunca por keyword** — nesta casa três candidatos morreram exatamente aí: `custo` acertou
`data-lake-patterns` porque a palavra está dentro de `customers`; `breaking change` acertou
`claude-code-superpowers` dentro de um exemplo de checklist; e uma busca por `RLS` sem
distinguir maiúscula acertou meia dúzia de notas por causa da variável `urls`.

Quatro decisões desta casa que valem registro:

- **"Cache" são quatro conceitos colados por uma palavra**, e a linha acima cobre só um deles:
  dado servido a partir de cópia que pode envelhecer. Cache de layer do Docker, cache de
  dependência do CI e KV cache do attention não são o mesmo problema, e uma linha única mandaria
  o agente para a nota errada. O mesmo raciocínio que a casa finance aplicou a "alavancagem".
- **"Custo" também é dois**, e entrou como duas linhas com hubs distintos. Custo de token cresce
  com o texto e se ataca por caching e por escolha de modelo; custo de infraestrutura cresce com
  recurso provisionado e se ataca por lifecycle, tiering e desligar o que não é usado. Um hub só
  serviria mal aos dois.
- **"Input não confiável" é o único tema desta casa sem nota-hub.** [[prompt-engineering]] entrou
  como porta de entrada por ser a única nota que trata a defesa como disciplina nomeada — as
  outras carregam a regra como gotcha isolada da tecnologia. Isso é um buraco declarado, não uma
  escolha: falta aqui uma nota de segurança de aplicação que valha por si.
- **"Sobreposição entre snippet e nota de tecnologia" ficou de fora, e continua sendo regra de
  manutenção em [[snippets]].** Uma linha aqui responderia a uma pergunta de autor ("onde eu
  escrevo isto?"), não de leitor. Este arquivo roteia quem tem uma pergunta técnica; quem vai
  escrever uma nota lê a regra de manutenção em `_house.md` e o critério de divisão em
  [[snippets]].

Rejeitado pelo critério, apesar de aparecer em quase toda a casa: **"default da ferramenta não é
default de produção"** — RLS desabilitada, Secret em base64, `auto_ack=True`, `catchup=True`,
`spark.sql.shuffle.partitions=200`, Core NATS descartando sem subscriber, DuckDB em 80% da RAM.
É um padrão real e recorrente, mas a linha "Também tratado em" seria a lista de todas as notas
da casa. Tema que aponta para tudo não roteia nada, e transforma este arquivo no segundo índice
de tudo que o critério existe para impedir. Isso pertence à seção **Common Gotchas** de cada
nota, que é onde já está.
