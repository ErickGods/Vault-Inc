---
house: tech
type: house-index
updated: 2026-08-01
---

# Casa Tech — Índice Mestre

Este é o primeiro arquivo a carregar ao trabalhar nesta casa. Ele não contém conhecimento;
contém o mapa. Use assim: identifique na tabela de domínios ativos qual território cobre a
tarefa, carregue o índice daquele domínio, leia a coluna "O que responde" e abra **apenas** as
notas que a tarefa exige. Três saltos, e nada de varrer o vault com Glob.

**Como abrir uma nota.** Wikilinks **dentro desta casa** não carregam caminho — são
identificadores, não paths. O arquivo fica em `<pasta>/<nome-da-nota>.md`, onde `<pasta>` vem da
coluna **Pasta** da tabela abaixo. Exemplo: a nota `big-o-notation`, listada em [[references]], é
o arquivo `tech/07-references/big-o-notation.md`.

**Cinco dos oito domínios desta casa têm subpastas** — [[skills]] (4), [[devops]] (6), [[ai-ml]]
(5), [[architecture]] (4) e [[data-engineering]] (4). Para eles a célula **Pasta** dá apenas a
**raiz do domínio**, e o caminho exato mora nos **títulos de seção do próprio índice de
domínio**: em [[devops]], a seção "Segurança" declara `tech/02-devops/security/`, e é ali que a
nota `secrets-management` mora — não em `tech/02-devops/`. Um agente que parar neste arquivo para
esses cinco domínios vai montar um caminho que não existe, e o fallback natural (`ls -R`) é
exatamente a varredura que a regra proíbe. Desça até o índice do domínio e leia o título da
seção antes de abrir o arquivo.

Só três domínios são planos e resolvem aqui mesmo: [[snippets]], [[references]] e [[templates]].

Os índices de domínio, este arquivo e o `_topics.md` têm pasta fixa em vez de vir da tabela:
ficam sempre em `tech/00-index/`, com o nome do arquivo igual ao do wikilink — [[ai-ml]] é o
arquivo `tech/00-index/ai-ml.md`.

**Link que cruza casa é a exceção e carrega o caminho inteiro.** `_house`, `_topics`,
`templates` e `snippets` agora existem em mais de uma casa, então o basename sozinho é ambíguo —
e isso já causou duas colisões reais. Ao linkar para fora daqui, escreva
`[[quant/06-risk-analytics/sharpe-ratio]]` e não `[[sharpe-ratio]]`. O verificador reporta link
nu para basename ambíguo.

> **Não deduza o caminho.** Os prefixos numéricos **não são deriváveis** do nome do domínio nem
> da ordem em que os domínios aparecem aqui. Leia a coluna Pasta.

## Domínios ativos

| Domínio | Índice | Pasta | Cobre |
|---|---|---|---|
| Linguagens e ferramentas | [[skills]] | `tech/01-skills/` (4 subpastas) | bancos de dados relacionais, documento, chave-valor e vetoriais; frameworks web e de LLM (FastAPI, Django, Next.js, React, Svelte, Astro, htmx, LangChain); Python, TypeScript e Rust; Docker, Git avançado e Claude Code |
| DevOps | [[devops]] | `tech/02-devops/` (6 subpastas) | pipelines de CI/CD, estratégias de substituição de versão, feature flags e GitOps; containers e Kubernetes; infraestrutura como código; observabilidade com SLO e error budget; borda, DNS/CDN e VPN; gestão de segredos |
| IA e Machine Learning | [[ai-ml]] | `tech/03-ai-ml/` (5 subpastas) | fundamentos de LLM (arquitetura, tokenização, embeddings, pré-treino, fine-tuning, alinhamento); inferência e serving (KV cache, quantização, VRAM, engines); hardware e aceleradores; avaliação e benchmarks; frameworks de agente; RAG, prompt engineering e multi-agente; MCP; Claude API |
| Arquitetura | [[architecture]] | `tech/04-architecture/` (4 subpastas) | clean architecture, microsserviços e event-driven; padrões de mensageria com RabbitMQ, SQS/SNS e NATS; object storage, mídia e transformação de imagem na nuvem; registro de decisão arquitetural |
| Engenharia de dados | [[data-engineering]] | `tech/05-data-engineering/` (4 subpastas) | orquestração com Airflow, Dagster e Prefect; lakehouse, medallion, Delta Lake e DuckDB; streaming com Kafka e Flink; transformação com dbt e Spark |
| Snippets | [[snippets]] | `tech/06-snippets/` | código pronto para colar em bash, Docker, Python e SQL — forma exata, não estudo |
| Referências | [[references]] | `tech/07-references/` | tabelas de consulta: complexidade e custo de estruturas de dados, comandos Git, expressões regulares |
| Templates | [[templates]] | `tech/08-templates/` | moldes dos artefatos recorrentes: nota de tecnologia, página de projeto, revisão semanal |

Há ainda três `.canvas` em `tech/09-canvas/` — mapas visuais de stack, de pipeline de dados e de
trilhas de estudo. São material de leitura humana no Obsidian, não fonte de roteamento: um
agente não deve tratá-los como índice.

## Temas transversais

Se a pergunta é sobre uma **preocupação** e não sobre um território — custo de inferência, custo
de infraestrutura, gestão de segredos, idempotência, evolução de schema, cache que envelhece,
observabilidade, gerenciado contra self-hosted — comece por [[_topics]]. Nenhum domínio da tabela
acima responde essas perguntas sozinho: segredo é tratado em cinco domínios, e escolher um deles
aqui perde material que está nos outros quatro. O `_topics.md` diz qual nota abrir primeiro para
cada tema.

## Regra de manutenção

Uma nota nova custa **exatamente uma linha** no índice do seu domínio e **zero edições em
qualquer prompt de agente**. Nenhum agente cita nota por nome: os agentes citam este arquivo, e
este arquivo cita os índices de domínio. Se um prompt de agente começar a listar notas
individuais, a propriedade que faz este desenho escalar foi quebrada. Pelo mesmo motivo, **este
arquivo não lista notas** — ele mapeia domínios. Nota só aparece no índice do seu domínio.

**O teto de tamanho não é contagem de linhas — é se os títulos de subseção nomeiam territórios
que o leitor já tem na cabeça antes de terminar a pergunta.** [[ai-ml]] tem 23 linhas e é
saudável, porque quem chega perguntando "como sirvo esse modelo?" reconhece "inferência e
serving" e pula os outros quatro blocos sem lê-los. O contraexemplo é da própria casa: a pasta
`fundamentals/` estava sob um único título "Fundamentos" com 13 linhas, e foi partida em quatro
subseções — **arquitetura e treino / inferência e serving / hardware / avaliação** — não por
tamanho, mas porque "Fundamentos" é rótulo de prateleira: ninguém formula uma pergunta cuja
resposta é "fundamentos". Título que não é território não filtra nada, e o agente lê o bloco
inteiro para descobrir se interessa.

**Vigie a subseção, não o domínio.** Medido num teste real de cobertura na casa finance: o agente
abriu 13,5% das notas da casa e **67% das notas da subseção onde a tarefa caiu**. O índice
economiza contexto **entre** domínios e quase nada **dentro** da subseção que a tarefa acerta,
porque ali as notas são mutuamente relevantes por construção. Uma subseção que cresce mantendo
essa densidade aumenta o custo por tarefa enquanto o índice continua parecendo funcionar.

> **Prosa que cita contagem defasa, e isso já mordeu a casa finance** — o texto de lá afirmava 16
> e 11 linhas depois que seis notas novas entraram. Confira antes de usar qualquer número acima
> como argumento:
> ```bash
> for f in tech/00-index/*.md; do printf "%-20s %2d\n" "$(basename $f .md)" "$(grep -c '^| \[\[' $f)"; done
> ```

**Nota nova cujo tema já aparece em outro domínio ganha uma linha em [[_topics]].** O teste é
dispersão entre domínios, não contagem de notas: se algum domínio responde a pergunta sozinho, o
tema pertence ao índice daquele domínio. Essa é a única exceção à regra de uma linha em um lugar,
e ela é deliberada — o mapa transversal mora num arquivo só, justamente para não obrigar edição
em N índices quando uma nota nova toca um tema comum.

O campo `Nível` **não é sinal de roteamento, e esta casa é a prova mais crua disso no vault
inteiro: 86 das 89 notas declaram `advanced`.** As três exceções nem são outro nível — são os
templates, que não declaram o campo. Um campo em que 100% dos valores declarados são iguais não
discrimina nada. Roteie pela coluna "O que responde".
