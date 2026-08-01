# Reestruturação da Vault Inc Library — Design

**Data:** 2026-07-28
**Status:** aprovado (seções 1–3)
**Autor:** Erick + Claude

---

## 1. Objetivo

Transformar a `Vault-Inc-Library` de uma coleção de notas em uma **base de conhecimento operacional** capaz de sustentar a criação e a escala de agentes em três casas — financeira, quantitativa e de tecnologia — com o objetivo final de estruturar uma casa de análises quant finance, research e wealth management.

O problema não é falta de conteúdo. São 235 arquivos com 2.854 wikilinks. O problema é que o conhecimento não está ligado aos agentes e a estrutura não escala.

---

## 2. Diagnóstico do estado atual

### 2.1 Os "arquivos em branco" não existem

De 235 `.md`, apenas **um** está de fato vazio: `tech-vault/01-skills/devops/docker.md` (0 bytes, duplicata de `01-skills/tools/docker.md`).

O que aparece como nó cinza no grafo do Obsidian são **alvos de link que nunca foram criados**:

| Métrica | Valor |
|---|---|
| Wikilinks totais | 2.854 |
| Alvos distintos | 324 |
| Alvos não resolvidos | **126 distintos / 216 ocorrências** |

~39% dos alvos de link apontam para o vazio.

> **Nota metodológica:** o verificador precisa indexar `.md` **e** `.canvas`. A primeira versão indexava só `.md` e reportou 8 links de canvas como quebrados quando os arquivos existiam. Está incorporado ao `check_links.py` da §12.

### 2.2 O problema real de escala

```
finance-vault/agents/*  →  58 referências ao finance-vault
.claude/agents/*        →   0 referências ao tech-vault
```

Os 10 agentes de tecnologia **não conhecem a própria base de conhecimento**. São prompts genéricos que rodariam em qualquer repositório. Toda a `tech-vault/` está órfã.

Além disso, ambos os orquestradores mandam os agentes escreverem em `vault/projects/`, `vault/reports/qa/`, `vault/clients/` — **diretórios que não existem no repositório**.

### 2.3 Fragmentação estrutural

- `docker.md` em 2 lugares (um deles vazio) — duplicata real
- **A duplicação de templates era em boa parte ilusão de nomenclatura.** Cinco arquivos pareciam duplicados pelo nome; conferido o conteúdo, **só um era**:

| Arquivo | O que realmente é |
|---|---|
| `docs/01-templates/adr-template.md` | Template de ADR — a versão completa, com seções de guia |
| `tech-vault/08-templates/adr-template.md` | **Duplicata real** — mesmo template em sintaxe Templater |
| `tech-vault/04-architecture/decisions/adr-template.md` (11 KB) | **Nota de conhecimento** sobre ADRs — MADR vs Nygard, exemplos, tooling |
| `docs/01-templates/skill-template.md` | Template de **Skill do Claude Code** |
| `tech-vault/08-templates/skill-template.md` | Template de **nota sobre tecnologia** (`# <% technology %>`) — "skill" aqui é habilidade técnica, casa com `01-skills/` |

Consolidar por nome de arquivo teria apagado dois conteúdos distintos. A lição vale para a migração inteira: **nome igual não é conteúdo igual** — conferir estrutura antes de consolidar qualquer par.
- **3 arquivos `CLAUDE.md`** sem hierarquia entre si
- **4 `README.md`**, um deles em `.claude/agents/mnt/user-data/outputs/vault-inc/vault/` — caminho de sandbox vazado e commitado. Havia também um `files.zip` de 18 KB na mesma pasta, esse não versionado (o `.gitignore` já cobria `*.zip`), apenas em disco
- Convenções divergentes: `finance-vault/00-MOC/🗺️ Home.md` vs `tech-vault/00-moc/home.md`
- Um 4º vault (`claude-vault/`) fora do README e de qualquer MOC
- Três campos de frontmatter concorrentes: `level` (106), `complexity` (80), `context` (80)

### 2.4 Erro de conteúdo a corrigir

`claude-vault/02-core-features/subagents.md` documenta `subagent_type` como se recebesse nomes de modelo (`claude-opus-4`, `claude-haiku-4`). Não recebe: `subagent_type` é o **tipo de agente**; o modelo é parâmetro separado. Como essa nota vira conhecimento operacional, ela ensinaria errado.

---

## 3. Decisões de arquitetura

| # | Decisão | Escolha |
|---|---|---|
| D1 | Relação entre os ramos | Linhas de negócio independentes, com colaboração cruzada |
| D2 | Repositórios | Dois: Library (público) + Workspace (privado) |
| D3 | Acesso do agente ao conhecimento | Índice por domínio (A) **+** Skills operacionais (B) |
| D4 | Newsroom / Daily News | Público com staging — **fase 2, fora deste escopo** |
| D5 | Topologia do repo público | Claude-nativo: conhecimento visível no topo, agentes/skills em `.claude/` |
| D6 | Posição da quant | **Terceira casa**, não mesa do financeiro |

### D2 — Por que dois repositórios

O repo público é vitrine institucional (LinkedIn, site) e, na fase 2, redação do Daily News. Entregáveis operacionais — IPS de cliente HNW com patrimônio, reports com posição — não podem coexistir com ele. Separação física, não disciplina.

### D5 — Por que Claude-nativo

O Claude Code só enxerga `.claude/agents/` e `.claude/skills/<nome>/SKILL.md`. As alternativas eram sincronizar (gera drift) ou empacotar como plugin (enterra a vitrine dentro de `plugins/`). A opção nativa não paga imposto nenhum: sem sync, sem instalação, Obsidian abre limpo. Migrar para plugin depois é mover pastas.

### D6 — Por que a quant é casa

Ela traduz em duas direções, e é a única que faz isso:

- **← finance:** tese discricionária → hipótese testável (universo, período, fator, critério de rejeição)
- **→ tech:** hipótese validada → código que roda (engine de backtest, pipeline, execução)

```
finance/  ──tese──▶  quant/  ──especificação──▶  tech/
   ◀──evidência──      ◀──dados / infra / código──
```

Uma mesa dentro do financeiro não teria mandato para o segundo movimento; uma equipe de tech não teria o primeiro.

---

## 4. Topologia final

### 4.1 Vault-Inc-Library (público)

```
Vault-Inc-Library/
├── CLAUDE.md                    # orquestrador raiz + convenções globais
├── README.md                    # vitrine institucional
├── finance/
│   ├── CLAUDE.md                # regras da casa financeira
│   ├── 00-index/
│   │   ├── _house.md            # índice mestre — o que o agente carrega
│   │   ├── investments.md
│   │   ├── analysis.md
│   │   ├── accounting.md
│   │   ├── markets.md
│   │   └── personal-finance.md
│   ├── 01-fundamentals/
│   ├── 02-investments/          # equities, fixed-income, funds, derivatives, alternatives
│   ├── 03-analysis/             # fundamental, technical, macro
│   ├── 04-personal-finance/
│   ├── 05-accounting/
│   ├── 06-markets/
│   ├── 07-psychology/
│   ├── 08-frameworks/           # o que sobrar após migração para quant/
│   └── 09-glossary/
├── quant/
│   ├── CLAUDE.md
│   ├── 00-index/
│   ├── 01-math-foundations/     # probabilidade, álgebra linear, estocástico, otimização
│   ├── 02-time-series/          # estacionariedade, cointegração, GARCH, regime switching
│   ├── 03-factor-models/        # CAPM, Fama-French, construção de fatores, risk premia
│   ├── 04-strategies/           # momentum, mean-reversion, carry, stat arb
│   ├── 05-backtesting/          # survivorship, look-ahead, custos, PBO, deflated Sharpe
│   ├── 06-risk-analytics/       # VaR, ES, stress testing, drawdown, Kelly / sizing
│   ├── 07-execution/            # microestrutura, slippage, impacto, TCA
│   ├── 08-ml-finance/           # features, walk-forward, overfitting
│   └── 09-market-data/          # point-in-time, corporate actions, vendors, B3 vs US
├── tech/
│   ├── CLAUDE.md
│   ├── 00-index/
│   ├── 01-skills/               # languages, frameworks, databases, tools
│   ├── 02-devops/
│   ├── 03-ai-ml/
│   ├── 04-architecture/
│   ├── 05-data-engineering/
│   ├── 06-snippets/
│   └── 07-references/
├── shared/
│   ├── claude/                  # ex claude-vault — como operar o Claude Code
│   ├── templates/               # fonte única de templates
│   └── conventions.md
├── .claude/
│   ├── agents/
│   │   ├── finance/
│   │   ├── quant/
│   │   ├── tech/
│   │   └── shared/
│   └── skills/
├── newsroom/                    # reservado — fase 2
├── scripts/
│   ├── check_links.py
│   └── migrate_house.py
└── docs/
```

### 4.2 Vault-Inc-Workspace (privado)

```
Vault-Inc-Workspace/
├── library/                     # submódulo git → Vault-Inc-Library
├── clients/
│   └── <cliente>/
│       └── IPS-<YYYY-MM-DD>.md
├── reports/
│   ├── equity/                  # <ticker>-<YYYY-MM-DD>.md
│   ├── macro/
│   ├── quant/
│   ├── risk/
│   └── pe/
├── cross-desk/                  # CDRs
├── projects/
├── .claude/                     # sincronizado de library/.claude — gitignored
├── scripts/
│   └── sync-agents.ps1
└── .gitignore
```

O submódulo dá caminhos estáveis e relativos (`library/finance/...`) e versiona qual estado do conhecimento produziu cada entregável — o que importa para auditoria de research.

`sync-agents.ps1` copia `library/.claude/{agents,skills}` → `.claude/` do Workspace, que é gitignored. Direção única, fonte de verdade sempre na Library, sem drift e sem symlink (que no Windows exigiria modo desenvolvedor).

---

## 5. Mecanismo A — Índice como interface

Cada domínio ganha um `_index.md` que é **tabela, não prosa**:

```markdown
---
house: finance
domain: analysis/fundamental
---
# Índice — Análise Fundamentalista

| Nota | O que responde | Nível |
|---|---|---|
| [[dcf-valuation]] | Projetar FCF e descontar à WACC | advanced |
| [[multiples-valuation]] | P/E e EV/EBITDA — quando cada um mente | intermediate |
| [[moats]] | Identificar e testar vantagem competitiva durável | intermediate |
```

O agente faz **três saltos com contexto controlado**:

1. carrega `<casa>/00-index/_house.md` (~2 KB)
2. escolhe o domínio e carrega o `_index.md` correspondente
3. lê apenas as notas que a tarefa exige

Nunca varre o vault às cegas.

**Propriedade que resolve a escala: nota nova = uma linha no índice.** Nenhum prompt de agente é editado. Hoje, `equity-research-analyst.md` cita 23 arquivos direto no prompt — cada nota nova exigiria editar N agentes à mão.

A coluna **"O que responde"** é o mecanismo inteiro: ela existe para o agente decidir **não** abrir a nota. Uma entrada vaga ("explica CAPM") obriga a leitura para descobrir se é relevante, o que anula a economia de contexto. Escrever cada linha como *a pergunta que a nota responde*, não como o tópico dela.

### Índice de temas transversais — correção vinda da validação em E1

Construir a casa quant revelou um limite do roteamento por domínio. Nas 7 notas da quant, **custos de transação aparecem em todas as 7** e atravessam os quatro domínios. Um agente que pergunta "como trato custos num backtest de momentum na B3" precisa escolher um domínio, e qualquer escolha perde material.

Por isso cada casa ganha também um `00-index/_topics.md`:

```markdown
| Tema | Onde começar | Também tratado em |
|---|---|---|
| Custos de transação | [[backtesting-basics]] | [[momentum-strategies]], [[position-sizing]] |
```

A coluna **"Onde começar"** dá ao agente um padrão — a nota que trata o tema mais diretamente — e a terceira coluna revela honestamente que o tema é distribuído. Fica em **um arquivo por casa**, não espalhado como referência cruzada em cada índice de domínio: espalhar quebraria a propriedade de "uma linha, um lugar", já que uma nota nova sobre custos exigiria editar N índices.

**Critério de inclusão: dispersão entre domínios, não contagem de notas.** O teste é — existe uma escolha de domínio em `_house.md` que responde a pergunta sozinha? Se existe, o tema pertence ao índice daquele domínio. Look-ahead bias aparece em apenas 2 notas da quant, mas em 2 domínios distintos, e por isso entra; um tema concentrado num domínio não entra por mais notas que ocupe. Sem esse filtro o índice de temas vira um segundo índice de tudo e devolve o custo de contexto que os três saltos economizam.

> **Armadilha ao montar o índice de temas: confirmar o hit lendo, não contando.** Na quant, três alegações minhas derivadas de `grep` eram artefato. "Viés de sobrevivência em 6 notas" era 4 — o hit em `position-sizing` é uma citação de Van Tharp ("sobrevive e capitaliza") e o de `factor-investing` é "não sobrevive a testes out-of-sample", que é overfitting. Todos os hits de `correla` em `sharpe-ratio` são *autocorrelação*, preocupação diferente de correlação instável em crise. Em 235 arquivos um mapa de temas derivado por palavra-chave produz esses erros em silêncio.

### O índice mestre precisa carregar o caminho da pasta

Descoberto testando o mecanismo de ponta a ponta com um agente real: **os índices acertavam em decidir o que ler e falhavam em abrir o que foi decidido.**

Wikilink não carrega caminho. O agente sabia que precisava de `[[momentum-strategies]]`, mas não onde o arquivo mora — e a numeração das pastas não é derivável: `quant/` tem `03-factor-models`, `04-strategies`, `05-backtesting`, `06-risk-analytics`, sem `01` nem `02`, porque esses números estão reservados para domínios planejados que não existem em disco. O campo `domain: strategies` do frontmatter também não carrega o prefixo.

O agente adivinhou o caminho, errou duas vezes, e caiu num `ls -R` — **exatamente a varredura que a regra da casa proíbe**. O desenho induzia o comportamento que ele proibia.

Correção: a tabela de domínios ativos do `_house.md` ganha uma coluna **`Pasta`**.

```markdown
| Domínio | Índice | Pasta | Cobre |
|---|---|---|---|
| Estratégias | [[strategies]] | `quant/04-strategies/` | momentum, trend following |
```

Fica no `_house.md` e não nos índices de domínio porque é **uma célula por domínio**, não por nota — domínios nascem raramente, notas o tempo todo. A propriedade "uma linha por nota nova" fica intacta. A tabela de planejados também ganha a coluna, com `—`, para deixar visível que o número está reservado mas a pasta não existe.

O `_house.md` precisa ainda declarar a convenção (`<pasta>/<nome-da-nota>.md`) e avisar explicitamente que os prefixos **não são sequenciais nem deriváveis do nome do domínio** — quem inferir em vez de ler a tabela erra.

### `Related` compete com o índice

As notas herdadas do vault têm seções `## Related`. Elas são um segundo caminho de navegação, e o segundo teste de ponta a ponta pegou um agente usando-o: ele abriu duas notas de `factor-models` pelas seções `Related` de notas já lidas, **sem nunca abrir o índice daquele domínio**.

O agente declarou o risco que assumiu, e a formulação dele é a melhor descrição do problema:

> se o domínio contiver uma nota que não é citada por nenhum `Related` das notas que li, ela seria diretamente relevante e eu não a vi. Não fui checar, porque checar era abrir o índice, que é justamente o passo que pulei.

**`Related` mostra o que foi linkado; o índice mostra o que existe.** Os links de saída de uma nota são o que o autor dela por acaso lembrou; o índice é o inventário completo. A lacuna entre os dois é invisível de dentro da nota.

Repetir a regra com mais ênfase não resolve — o agente conhecia o protocolo e escolheu contorná-lo. O que faltava era o *motivo*. Os quatro agentes da quant agora dizem: chegar por `Related` é legítimo quando você quer *aquela* nota; quando o motivo é **territorial** (cobertura do domínio, não um fato pontual), abra o índice mesmo que o `Related` já tenha citado candidatos.

### A propriedade de filtro, medida — e o resultado tem duas metades

E1 não conseguiu testar isso: com 7 notas o agente leu 100% do corpus, e o valor demonstrado do índice foi resolver caminho, não filtrar leitura.

E2 mediu, com 74 notas em 11 domínios. Um `equity-research-analyst` recebeu uma cobertura real de concessionária de energia e reportou o rastro exato:

| Recorte | Abertas / existentes | % |
|---|---|---|
| Casa inteira | 10 / 74 | **13,5%** |
| Domínios em que entrou | 10 / 40 | 25% |
| `investments` | 3 / 17 | 18% |
| **`analysis/fundamental`** | **4 / 6** | **67%** |

**O índice economiza contexto entre domínios e quase nada dentro da subseção onde a tarefa cai.** O agente nunca precisou saber que existiam domínios de psicologia, glossário ou finanças pessoais — isso é o mecanismo pagando por si. Mas dentro de `analysis/fundamental` ele abriu 4 de 6, porque ali as notas são **mutuamente relevantes por construção**: a coluna "O que responde" o ajudou a *ordenar* as 6, não a *descartar* 5.

Consequência operacional: **vigie a subseção, não o domínio.** Se uma subseção crescer para 12–15 notas mantendo essa densidade de relevância mútua, o custo por tarefa cresce junto e o índice continua parecendo funcionar — porque continua existindo e sendo lido — enquanto já não filtra nada. É o modo de falha silenciosa que a regra de teto descreve, mas medido no nível errado.

E um domínio de 2 notas (`frameworks`) não pode filtrar coisa alguma: abrir 50% dele não foi decisão.

### O mecanismo acha o que existe e não prova o que não existe

Achado do mesmo teste, e é estrutural. O agente precisou afirmar que o vault **não** cobre o regime tarifário da ANEEL. Para verificar, teria de abrir os 7 índices em que não entrou — exatamente o custo que os três saltos existem para evitar. Ele rotulou a afirmação como inferência sobre a coluna "Cobre" em vez de afirmá-la como verificada.

**Ausência não é verificável em três saltos.** Um agente que precise declarar lacuna de conhecimento — e a casa exige isso nos disclosures — está fazendo uma afirmação mais cara do que o índice suporta. Não há correção óbvia; registrar como limitação conhecida e exigir que a incerteza seja rotulada, não escondida.

### O formato foi desenhado sobre um vault de finanças, e a casa tech expôs quatro limites

As três casas têm a mesma forma de índice. Construir a terceira — 89 notas de engenharia — revelou onde o desenho aperta, e nenhum dos quatro casos é defeito de execução.

**1. A coluna "Onde começar" pressupõe que exista uma nota-hub.** Em finanças, preocupação transversal tem dono natural: tributação tem `tax-optimization-br`, custo tem `compound-interest`. Em engenharia, **"input não confiável" é tratado em 11 notas de 5 domínios e nenhuma o possui** — cada uma carrega sua instância como gotcha (magic bytes em `media-pipeline`, path traversal em `mcp-servers-guide`, `X-Forwarded-For` em `reverse-proxy`, RLS em `supabase`). O formato obriga a nomear um hub, e a resposta menos errada roteia mal quem pergunta sobre upload de arquivo.

A causa é estrutural: **conhecimento financeiro concentra em hubs; conhecimento de engenharia distribui em gotchas.** Falta ao formato um slot para "este tema é real e não tem dono".

**2. Não existe eixo de decaimento.** `compound-interest` continua correta em 2040. `planetscale` registra o fim do free tier em 2024, `rabbitmq` registra mirrored queues depreciadas desde a 3.9, `autogen` registra incompatibilidade entre 0.2 e 0.4+. O MOC antigo do ai-ml avisava que a área é "de maior volatilidade — o que era estado da arte há 6 meses pode estar obsoleto", e apagá-lo apagou o único lugar que dizia isso.

A coluna "O que responde" diz o que a nota responde, **nunca por quanto tempo a resposta continua verdadeira**. Um agente que abrir `inference-engines` em 2027 não recebe sinal nenhum de que aquele domínio apodrece dez vezes mais rápido que `big-o-notation`.

**3. Uma linha em um índice força o corte por camada, não por coisa.** `docker` está em `skills/tools` e `docker-compose-patterns` em `devops/containers`. `claude-code` em `skills/tools` e `claude-code-superpowers` em `ai-ml/ai-frameworks`. `kafka` em `data-engineering/streaming` enquanto o problema de semântica de entrega que ele encarna mora em `architecture/messaging`.

Em finanças, uma debênture é uma debênture independente de quem pergunta. Aqui a mesma tecnologia pertence genuinamente a dois domínios, e o `_topics.md` faz trabalho de reparo — 3 das 10 linhas existem sobretudo para reconectar notas que o corte por domínio separou.

**4. `Nível` não é apenas pouco informativo nesta casa, é provadamente morto.** As 3 exceções aos 86 `advanced` não são outro nível: são os templates, que não declaram o campo. **100% dos valores declarados são `advanced`**, impressos em toda linha de 8 índices. Custo de token com zero bit de roteamento. Para a casa tech, o honesto é remover a coluna, não normalizá-la.

### Contagens no índice mestre defasam, e a regra é avaliada contra elas

O `_house.md` afirmava "investments em 16 linhas" e "analysis em 11" ao argumentar que a estrutura ainda cabia. Medido: **17 e 15** — o Estágio B adicionou seis notas e o texto não acompanhou.

Como a regra de teto é avaliada contra esses números, ela estava sendo avaliada contra dados errados. Prosa que cita contagem é dado duplicado, e dado duplicado deriva. O `_house.md` de cada casa deve trazer o comando que confere:

```bash
for f in <casa>/00-index/*.md; do printf "%-20s %2d\n" "$(basename $f .md)" "$(grep -c '^| \[\[' $f)"; done
```

### Colisão de basename entre casas — decisão consciente

Uma casa por pasta **garante** basenames repetidos: `quant/00-index/_house.md` já existe, E2 cria `finance/00-index/_house.md`, E3 cria `tech/00-index/_house.md`. O mesmo vale para `_topics.md`.

Como o Obsidian resolve por basename, `[[_house]]` sem caminho é **ambíguo** — e o `check_links.py` reportava isso como *resolvido*, um falso negativo da mesma família dos que já corrigimos.

Duas saídas foram consideradas:

| Opção | Custo |
|---|---|
| Renomear por casa (`_finance-house.md`) | Desambigua por basename, mas polui o nome e quebra a simetria entre casas |
| Manter `_house.md` e qualificar caminho quando linkar | Exige `[[finance/00-index/_house]]` nos raros links entre casas |

**Escolhida a segunda.** Os agentes não alcançam esses arquivos por wikilink — alcançam por caminho, via a coluna `Pasta` e a convenção `<casa>/00-index/`. A ambiguidade só afeta navegação humana no Obsidian e link entre casas, que é raro.

O que mudou no verificador: `ambiguous_targets()` reporta basenames alcançáveis por mais de um arquivo, e há `--fail-on-ambiguous` (desligado por padrão) para virar portão quando quisermos. A regra operacional é: **link entre casas sempre qualifica o caminho.**

### `docs/superpowers/` nunca é reescrito por migração

O `migrate_house.py` exclui `docs/superpowers/` das reescritas de link. O motivo não é política de pasta: **o spec cita nomes de arquivo antigos como exemplo do problema que a migração corrige** (`🗺️ Home.md` na §2.3). Reescrevê-los apagaria o registro diagnóstico de o que foi feito e por quê.

A exclusão é deliberadamente mais estreita que a allowlist do `check_links.py`: pastas `*templates` **continuam** sendo reescritas, porque template que linka arquivo renomeado passa a emitir link quebrado a cada uso.

### Teto de tamanho por índice — e por que o número é a variável errada

A regra original: um índice além de **15–20 linhas** deixa de ser escaneável e o agente passa a lê-lo como leria uma listagem de diretório.

**Construir a casa finance mostrou que a contagem de linhas mede a coisa errada.** O que torna um índice escaneável é se os títulos de subseção nomeiam **territórios que o agente já tem em mente antes de terminar de ler a pergunta** — não quantas linhas há.

O contraste dentro da mesma casa é a prova:

| Índice | Linhas | Subseções | Saúde |
|---|---|---|---|
| `investments` | 16 (no teto) | equities, fixed-income, funds, derivatives, alternatives | **boa** |
| `analysis` | 11 (folgado) | fundamental, macro, technical | **pior** |

`investments` está no limite e roteia em uma leitura: as 5 subseções são fronteiras de classe de ativo que qualquer analista já pensa, então o agente escaneia 5 títulos e depois 2–4 linhas. O custo é limitado pela subseção, não pela tabela.

`analysis` é menor e é pior estruturado: fundamental, macro e técnica são **três epistemologias incompatíveis arquivadas como se fossem três prateleiras**. Uma pergunta de valuation e uma pergunta de gráfico não têm relação, e o índice não dá sinal de que cruzar entre elas quase sempre é erro.

**A regra corrigida:** o modo de falha de uma tabela plana é o agente ter de ler todas as linhas para rotear. Uma subseção cujo título nomeia um território reconhecível colapsa isso para uma leitura. Logo:

- 24 linhas em 5 subseções nomeadas por território **roteiam em um salto**
- 12 linhas em subseções chamadas "Parte 1 / Parte 2 / Outros" **já estão quebradas**

Ao cruzar o teto, o primeiro movimento é **abrir subseções por território**; separar em índices distintos só quando nem as subseções segurarem. E o lugar onde a estrutura degrada primeiro é a subseção **residual** — a definida pelo que não é. Em `investments`, "Alternativos" (commodities, cripto, private equity) é essa, e é ali que a próxima nota vai cair.

### Pasta fora do índice é invisível — e a disciplina é que a torna invisível

Descoberto ao religar os agentes da casa finance, e é contraintuitivo: **a regra "nunca varra o vault com Glob" transforma toda pasta ausente do índice em pasta inalcançável.**

`finance/11-templates/` existia com 5 arquivos e não era nomeada por nenhum índice, nenhuma linha de `_topics.md`, nem pelo `CLAUDE.md` da casa. Enquanto os agentes citavam arquivos direto no prompt, a citação direta era o caminho. Ao remover as citações — que é o ponto da reestruturação — os templates ficaram sem rota alguma. A reescrita melhorou 21 das 23 citações do `equity-research-analyst` e **regrediu 2**.

O diagnóstico correto é do índice, não do agente. O agente estava obedecendo.

**Regra para E3 e E4: antes de remover citação direta de qualquer agente, confirmar que toda pasta da casa aparece no `_house.md`.** A verificação é mecânica:

```bash
for d in <casa>/*/; do
  grep -q "$(basename $d)" <casa>/00-index/_house.md || echo "ORFA: $d"
done
```

A casa tech tem quatro candidatas ao mesmo erro: `06-snippets`, `07-references`, `08-templates` e `09-canvas`.

O caso dos templates também respondeu a pergunta de fronteira: **template é conhecimento e fica no vault; a instância preenchida é entregável e vai para o repo privado.** A estrutura é durável e revisável; o preenchimento carrega dado de cliente.

### Domínio com subpastas: o caminho mora no título da seção

`finance/02-investments/` tem 5 subpastas e `finance/03-analysis/` tem 3 — a casa quant não tinha nenhuma, então a coluna `Pasta` (um caminho por domínio) não bastava.

Solução: a célula `Pasta` do `_house.md` dá a **raiz do domínio**, e o índice do domínio usa **uma seção por pasta, com o caminho no título**:

```markdown
## Renda fixa — `finance/02-investments/fixed-income/`

| Nota | O que responde | Nível |
```

Mantém um índice por domínio, um caminho inequívoco por seção, e zero manutenção por nota. O `_house.md` precisa **avisar explicitamente** que para esses domínios o caminho exato está no índice — um agente que parar no `_house.md` monta um caminho que não existe.

### O campo `level` não roteia

Medido no vault: **109 notas marcadas `advanced`** contra 20 `intermediate`, 5 `basic` e 2 `intro` — mais quatro vocabulários concorrentes e placeholders de template vazando. Um campo em que 80% das linhas compartilham o mesmo valor não discrimina nada. A coluna permanece no formato (e o vocabulário é normalizado em `intro | intermediate | advanced` durante E2/E3), mas **não deve ser tratada como sinal de roteamento** — quem roteia é "O que responde".

---

## 6. Mecanismo B — Skills

### 6.1 Divisão de responsabilidade

| | Nota do vault (A) | Skill (B) |
|---|---|---|
| Responde | **o quê** e **por quê** | **como**, passo a passo |
| Natureza | didática, estável | operacional, com guardrails |
| Muda quando | o entendimento muda | o processo muda |
| Exemplo | `dcf-valuation.md` explica FCF, WACC, perpetuidade | `dcf-valuation/SKILL.md` executa o valuation |

**A skill cita a nota, nunca a copia.** Fonte única, sempre.

### 6.2 Formato

```markdown
---
name: dcf-valuation
description: Use ao valuar uma empresa por fluxo de caixa descontado —
  projeção de FCF, cálculo de WACC, perpetuidade e tabela de sensibilidade.
---

## Antes de começar
Leia [[dcf-valuation]] e [[wacc]]. Se a empresa for financeira, PARE —
DCF não se aplica a bancos; use [[valuation-bancos]].

## Passos
1. Colete 5 anos de demonstrativos → registre fonte e data
2. Projete FCF explícito 5–10 anos → justifique cada premissa por escrito
3. Calcule WACC → beta, prêmio de risco Brasil, custo de dívida pós-imposto
4. Perpetuidade: g ≤ crescimento nominal do PIB de longo prazo. Sem exceção.
5. Sensibilidade obrigatória: matriz WACC × g
6. Cenário bear com perda máxima estimada

## Critérios de saída
- [ ] Toda premissa tem justificativa rastreável
- [ ] Sensibilidade presente
- [ ] Disclosure de conflito de interesse
- [ ] Notas do vault citadas
```

Skill rígida: valuation sem sensibilidade e sem cenário bear destrói credibilidade de casa de research.

### 6.3 Ordem de nascimento

As skills nascem junto com a casa que as opera (§11.1), não em ondas próprias.

| Etapa | Skill | Função |
|---|---|---|
| **E1** quant | `hypothesis-test` | Tese discricionária → hipótese testável: universo, período, fator, critério de rejeição |
| **E1** quant | `backtest-protocol` | Backtest com guardrails — survivorship, look-ahead, custos, deflated Sharpe |
| **E2** finance | `equity-initiation` | Report de iniciação de cobertura — primeiro entregável ponta a ponta |
| **E2** finance | `dcf-valuation` | O cálculo que sustenta o report |
| **E5** raiz | `vault-note` | Cria nota com frontmatter correto **e atualiza o índice**. Sem ela o vault apodrece de novo. |

**Depois da migração:** `ips-builder`, `risk-report`, `cross-desk-request`.

`vault-note` fica em E5 por depender do formato de índice já validado nas três casas — é a skill que perpetua o padrão, então precisa que o padrão esteja fechado. Até lá, notas novas seguem `shared/conventions.md` à mão.

---

## 7. Roster de agentes

| Casa | Agentes |
|---|---|
| **Finance** | `equity-research-analyst` (existe), `private-banker` (existe), `credit-research-analyst`, `macro-strategist`, `pe-analyst`, `compliance-officer` |
| **Quant** | `quant-researcher`, `quant-developer`, `risk-quant`, `market-data-quant` |
| **Tech** | `lead-engineer`, `backend`, `frontend`, `devops`, `qa`, `security`, `data-engineer`, `ml-engineer`, `ui-ux` — os 9 atuais, religados ao `tech/00-index/` |
| **Shared** | `pm` (intake de qualquer casa) + orquestrador raiz no `CLAUDE.md` |

`risk-quant` sai do financeiro (onde estava previsto como "Risk Manager") e vem para a quant: VaR e stress testing são trabalho quantitativo. `compliance-officer` fica no financeiro — suitability, CVM 30, KYC.

### 7.1 Fronteira `market-data-quant` × `data-engineer`

Precisa estar escrita, senão vira conflito recorrente:

- **`market-data-quant` (quant)** — correção **financeira** do dado: point-in-time, ajuste de proventos, viés de sobrevivência, splits, corporate actions. **Especifica.**
- **`data-engineer` (tech)** — **transporte**: ingestão, orquestração, storage, SLA, custo. **Constrói.**

### 7.2 O bloco de roteamento é duplicado em todo agente — de propósito

Todo agente carrega uma seção `## Como alcançar o conhecimento` idêntica: carregue `_house.md`; se a pergunta é sobre tema transversal e não sobre território, use `_topics.md`; abra o índice do domínio; leia só o que a tarefa exige.

Fatorar isso num arquivo compartilhado e substituir por "siga o procedimento em `_routing.md`" **seria pior**. O arquivo de definição é a única coisa garantidamente no contexto do subagente no primeiro turno; um ponteiro cria um salto *antes* do primeiro salto, e é o salto mais provável de ser pulado — um agente que acredita já saber onde as coisas estão não busca instrução dizendo o que ele acha que já sabe. Pior, a falha é silenciosa e parece sucesso: o agente roda um Glob, acha notas reais, produz resposta plausível, e ninguém vê que a disciplina foi contornada.

A duplicação é barata na dimensão que importa: o bloco não contém conhecimento, contém **três caminhos de arquivo**. Índices se dividem, domínios nascem, notas mudam de nome — nada disso toca essas cópias. Os agentes antigos precisavam de edição a cada nota nova porque fixavam *notas*; estes fixam o *ponto de entrada*, que é justamente o que o desenho promete não mover.

**O risco real é drift** — alguém edita um agente e esquece os outros, e a casa passa a ter dois procedimentos de roteamento sem sinal de erro. Defesa: uma checagem em `scripts/` afirmando que os blocos são idênticos, transformando divergência silenciosa em portão vermelho. Vale implementar quando o roster passar de ~5 agentes por casa; com E2 e E3 somando ~15, entra em E5.

### 7.3 Cascata de CLAUDE.md

Os 3 `CLAUDE.md` atuais viram a cascata nativa do Claude Code:

- `CLAUDE.md` (raiz) — convenções globais, orquestrador, roteamento entre casas
- `finance/CLAUDE.md`, `quant/CLAUDE.md`, `tech/CLAUDE.md` — regras de cada casa

O Claude Code carrega o aninhado automaticamente ao trabalhar dentro da pasta. Mata a duplicação sem inventar mecanismo.

---

## 8. Protocolo de colaboração — Cross-Desk Request

### 8.1 Por que artefato escrito

**Subagentes começam com contexto zero.** Não herdam a conversa nem sabem o que já foi decidido. É a causa número um de multi-agente que produz lixo. O CDR obriga o solicitante a montar um prompt autossuficiente antes de despachar.

### 8.2 Formato

```yaml
---
from: equity-research-analyst
to: quant-researcher
type: hypothesis-test
priority: normal
---
## Pergunta
O prêmio de qualidade se sustenta em industriais da B3 pós-2016?

## Contexto mínimo
Tese de WEGE3 apoiada em ROIC persistente. Preciso saber se é
fator remunerado no mercado local ou idiossincrasia do papel.

## Entregável esperado
Backtest com universo, período, construção do fator e critério de rejeição.

## Já verificado
[[moats]], [[roic]]. Não há nota de fator qualidade no vault.
```

### 8.3 Regras

- CDRs vivem em `cross-desk/` no repo **privado** — são operação, não conhecimento
- O campo `Já verificado` impede a casa de responder três vezes a mesma pergunta
- Resposta que vire conhecimento durável **sobe para o vault público** como nota nova, e o índice ganha uma linha
- Conflito entre casas escala para o orquestrador raiz

---

## 9. Convenções

### 9.1 Nomes

kebab-case, sem emoji, sem espaço. Os `🗺️ Home.md` e `🗺️ Analysis-MOC.md` são causa direta de links que não resolvem, e voltariam a quebrar quando o `newsroom/` virar site.

### 9.2 Frontmatter canônico

```yaml
tags: []
aliases: []          # PT/EN — "fluxo de caixa descontado" → dcf-valuation
house: finance | quant | tech | shared
domain: analysis/fundamental
level: intro | intermediate | advanced
status: draft | active | planned | deprecated
created: YYYY-MM-DD
updated: YYYY-MM-DD
```

`level`, `complexity` e `context` consolidam em `level` + `domain`. `aliases` já existe em 193 arquivos e é o que permite ao agente achar nota por termo em português sem depender do nome do arquivo.

---

## 10. Triagem dos 216 links não resolvidos

Números apurados por varredura, não estimados.

| Balde | Ocorr. | Natureza | Tratamento |
|---|---|---|---|
| **A. Código sem fence** | **19** | `[[ ]]` de teste bash e índices de array lidos como wikilink: `"$file" =~ \.(ts`, `-d "$dir"`, `$code -eq 124`, `:space:`, `"chunk1", "chunk2"` | Cercar os blocos de código. **Não é link.** |
| **B. Sintaxe de template** | **27** | `{{moc-relacionado}}`, `{{nota-essencial-N}}`, `adr-{{NNNN}}`, `<% tp.date.now(...) %>` | Legítimo dentro de template. Allowlist no checker. |
| **C. Pipe escapado em tabela** | **21** | `🗺️ Home\`, `engineering-moc\`, `income-statement\` — **todos os 21 apontam para arquivo que existe** | **Corrigir o verificador, não o conteúdo.** Ver nota abaixo. |
| **D. Conhecimento financeiro faltando** | **43** | 14 notas: `moats` (7), `dcf-valuation` (7), `selic-and-monetary-policy` (5), `capm` (5), `wacc` (4), `hedging-strategies` (4), `sharpe-ratio` (3), `roe-roic` (2), `roic`, `multiples-valuation`, `valuation-bancos`, `jcp`, `order-book`, `gdp-and-growth` | **Criar.** `capm` e `sharpe-ratio` nascem em `quant/`; o resto em `finance/`. |
| **E. Backlog do claude-vault** | **81** | ~42 notas planejadas e nunca escritas: `claude-code-moc` (8), `financial-analysis-with-claude` (7), `hook-snippets` (4), `claude-api-reference` (3), `batch-api` (3), `mcp-catalog` (2)… | **Não é apodrecimento — é build inacabado.** Vira `shared/claude/00-index/_backlog.md` com `status: planned`. |
| **F. Docs órfãos** | **21** | `workflow-*` (5), `python-projections-finance` (2), `fintech-automation` (2), `qa-report-template`, `security-audit-template`, `vault-inc-architecture`, `node`, `mongoose` + 4 links de canvas com nome errado (`tech-stack-canvas` em vez de `tech-stack-overview.canvas`) | Triagem individual: criar, repontar ou remover |
| **G. Resíduo de parsing** | **4** | `adr-{{NNNN}}`, string vazia, fragmento de bloco quebrado | Some com A e B |

**Total: 216.**

> **Correção ao balde C, apurada na revisão de código do `check_links.py`.** A versão anterior deste spec mandava "remover a `\`" dos 21 links. **Isso quebraria as tabelas.** Dentro de uma célula de tabela markdown, `|` é o delimitador de coluna, então o Obsidian exige que o alias de um wikilink seja escapado: `[[tech-vault/00-moc/🗺️ Home\|🖥️ Tech Home]]`. A sintaxe está **correta**; quem erra é o verificador, cujo regex para no `|` e leva a barra junto. O conserto é `rstrip("\\")` no extrator de links. Nenhum arquivo de conteúdo é tocado.

Dois achados que mudam a leitura do problema:

1. **O balde E é 37% do total** — e não é apodrecimento. É o roteiro de construção do `claude-vault`, escrito nos links antes de virar arquivo. Tratar como conserto seria errado; vira backlog catalogado.
2. **Os baldes A + B + C somam 67 ocorrências (31%) que não são links quebrados de verdade** — são código sem fence, sintaxe de template e um bug de escaping. Ou seja, o problema real é menor do que o número bruto sugere: **149 links de fato faltando**, dos quais 81 já são backlog conhecido.

---

## 11. Plano de migração

A migração é organizada **por casa**, não por tipo de tarefa. Cada etapa entrega uma casa inteira e funcional — estrutura, conhecimento, índice, agentes e skills — antes de a próxima começar. **A casa quant vem primeiro**, por ser o foco do projeto.

### 11.0 Estratégia de commit

Durante a execução, cada etapa fecha com um **commit de checkpoint**. Ao final, tudo é **squashed em um único commit** antes do merge.

O motivo: o histórico público deve começar já com as casas organizadas — reestruturação não é narrativa que interessa a quem chega no repo. Mas quebrar por casa só faz sentido se houver rollback entre etapas; sem checkpoint, uma falha na etapa 4 obriga a refazer as três anteriores à mão.

### 11.1 Etapas

| Etapa | Casa | Escopo | Risco |
|---|---|---|---|
| **E0** | — | **Higiene.** Deletar `.claude/agents/mnt/` (5 arquivos), `files.zip`, `docker.md` vazio. Consolidar `adr-template` ×2 → `shared/templates/adr.md` e `skill-template` ×2 (§2.3 — o terceiro `adr-template` é conteúdo, fica para E3). Escrever `scripts/check_links.py` e capturar a linha de base. | nulo |
| **E1** | **Quant** ⭐ | Criar `quant/` com os 9 domínios. Migrar as 5 notas (§11.5). Criar `capm` e `sharpe-ratio`. Escrever `quant/00-index/`. Criar os 4 agentes e `quant/CLAUDE.md`. Skills `hypothesis-test` e `backtest-protocol`. | médio |
| **E2** | **Finance** | `finance-vault/`→`finance/`, emoji→kebab. Frontmatter canônico. Índices. Criar as 12 notas restantes do balde D. Migrar os 2 agentes existentes e criar os 4 previstos. Skills `equity-initiation` e `dcf-valuation`. | **alto** |
| **E3** | **Tech** | `tech-vault/`→`tech/`. Frontmatter e índices. **Religar os 9 agentes ao `tech/00-index/`** — hoje são 0 referências. Cercar os blocos de código do balde A. | médio |
| **E4** | **Shared** | `claude-vault/`→`shared/claude/`. Corrigir `subagents.md` (§2.4). Catalogar o balde E em `_backlog.md` com `status: planned`. Consolidar templates e escrever `conventions.md`. Allowlist do balde B. | baixo |
| **E5** | Raiz | `CLAUDE.md` orquestrador, `README.md` da vitrine, skill `vault-note`, pre-commit hook, `newsroom/` reservado. Balde F (docs órfãos). | baixo |
| **E6** | — | **Repo privado.** Criar `Vault-Inc-Workspace`, submódulo, `sync-agents.ps1`, mover `finance/reports/`. | baixo |

### 11.2 Por que a quant primeiro

Ela é a única casa **construída do zero** — não há renomeação, não há link legado para preservar. Isso a torna o melhor lugar para validar os padrões novos (formato de índice, frontmatter canônico, anatomia de agente e de skill) **antes** de aplicá-los sobre 235 arquivos existentes.

Se o formato de índice estiver errado, descobrir isso em 7 notas custa uma tarde. Descobrir em `finance/` custa a migração inteira.

### 11.3 Dependências entre etapas

- **E0 antes de tudo** — o checker é o critério de aceite de todas as demais
- **E1 antes de E2** — os padrões validados na quant são o contrato das outras casas
- **Dentro de cada casa: renomear → frontmatter → índice → agentes → skills.** Agente não pode referenciar índice que não existe; índice não pode listar arquivo que ainda vai mudar de nome
- **E2 depois de E1, mas os links `quant → finance` só resolvem ao fim de E2** — durante E1 as notas migradas apontam para caminhos antigos. Esperado e verificado, não ignorado: o checker roda com `--baseline` para não acusar regressão em link que a etapa seguinte vai consertar

### 11.4 E2 é a etapa perigosa

Renomear `finance/` mexe em ~90 arquivos e nos wikilinks que apontam para eles de todas as casas. Não pode ser manual.

`scripts/migrate_house.py` recebe tabela `old → new` de uma casa, move os arquivos **e** reescreve os links em todo o repositório no mesmo passo, fechando em um commit de checkpoint.

**Critério de verificação objetivo:** rodar `check_links.py --baseline scripts/baseline.txt` depois de cada etapa. **Nenhum alvo quebrado novo pode aparecer** (§12). Um alvo novo significa mapeamento errado — e o checkpoint torna o rollback trivial.

**Duas linhas de base distintas, não confundir:** 216 é a contagem bruta da §10, que inclui os baldes A e B. O `check_links.py` descarta ambos por design, e sua linha de base medida em 2026-07-29 é **155 ocorrências / 98 distintos**. É esse o número que as etapas perseguem.

**Um fato que reduz muito o risco:** o Obsidian resolve wikilink por **basename**, não por caminho. Mover arquivo de pasta não quebra link; só renomear quebra. Portanto E1 (que apenas move e cria) é segura por construção, e o risco concentra-se nas renomeações emoji→kebab de E2, E3 e E4.

Quebrar por casa reduz o raio de explosão: um erro de mapeamento em E2 não contamina `tech/` nem `shared/`, que ainda não foram tocados.

### 11.5 Migração explícita para `quant/`

Sem ambiguidade sobre o que sai do `finance/`:

| Origem | Destino |
|---|---|
| `03-analysis/quantitative/backtesting-basics.md` | `quant/05-backtesting/` |
| `03-analysis/quantitative/factor-investing.md` | `quant/03-factor-models/` |
| `03-analysis/quantitative/momentum-strategies.md` | `quant/04-strategies/` |
| `08-frameworks/portfolio-theory-mpt.md` | `quant/06-risk-analytics/` |
| `08-frameworks/position-sizing.md` | `quant/06-risk-analytics/` |

**Permanecem em `finance/08-frameworks/`:** `capital-allocation.md` e `investment-checklist.md` — são framework de decisão discricionária, não quantitativa. Com isso `03-analysis/quantitative/` deixa de existir.

---

## 12. O que impede a volta do problema

`scripts/check_links.py` — o mesmo verificador do diagnóstico — vira **hook de pre-commit** com duas asserções:

1. Nenhum alvo de wikilink quebrado **novo** em relação a `scripts/baseline.txt`
2. Toda nota está listada no `_index.md` do seu domínio

### Por que o portão compara conjunto, e não total

A primeira versão deste spec media a **soma** de links não resolvidos e exigia que ela não subisse. Isso é compensável, e de um jeito que acontece naturalmente nesta migração:

```
ANTES:  {falta-1: 1, falta-2: 1}   total = 2
DEPOIS: {capm: 1}                  total = 1   → portão PASSA
```

A fase apagou um arquivo do backlog com 2 links mortos e renomeou `capm.md` sem atualizar `[[capm]]`. Saldo −1, portão verde, vault quebrado. Como **62 das 110 ocorrências são backlog do `claude-vault`** que as fases vão consolidar, o orçamento de mascaramento era grande.

`baseline.txt` guarda a **lista ordenada dos alvos** não resolvidos. A regra é: falha se surgir alvo que não estava na lista. Resolver link é progresso livre; quebrar link é sempre detectado, mesmo com o total caindo.

Requisitos do verificador, apurados na triagem e na revisão de código:

| Requisito | Motivo | Direção do erro |
|---|---|---|
| Indexar `.md` **e** `.canvas` | 8 canvas existentes reportados como quebrados (§2.1) | falso positivo |
| Ignorar wikilink em bloco de código cercado | `[[ -d "$dir" ]]` do bash vira link — **80 ocorrências medidas** (balde A) | falso positivo |
| `rstrip("\\")` no alvo extraído | `\|` é escape obrigatório em célula de tabela — 21 ocorrências (balde C) | falso positivo |
| Allowlist de `shared/templates/` | `{{...}}` e `<% tp... %>` são sintaxe legítima (balde B) | falso positivo |
| Allowlist de `docs/superpowers/` | Specs e planos citam notas como exemplo — **79 ocorrências, a maior fonte isolada** | falso positivo |
| Pular **apenas** `.claude/worktrees/` | O repo principal tem `.claude/worktrees/<nome>/`, uma cópia completa do vault. Um rename que quebra link fica mascarado pela cópia e a contagem não se move | **falso negativo** |
| **Varrer** `.claude/agents/` e `.claude/skills/` como fonte | É onde o agente cita o conhecimento. Excluí-los desliga a verificação exatamente do elo que este projeto existe para garantir | **falso negativo** |
| Normalizar só extensões indexadas | `[[diagrama.png]]` não pode resolver contra `diagrama.md` | **falso negativo** |

Os dois últimos são os perigosos: fazem a contagem parecer boa enquanto o vault está quebrado. Todos os sete estão travados por teste de regressão em `scripts/tests/test_check_links.py`.

É a diferença entre limpar o vault uma vez e mantê-lo limpo.

---

## 13. Fora de escopo

- **Newsroom / Daily News (D4)** — decidido: público com staging (`newsroom/drafts/` gitignored, `newsroom/published/` versionado). Implementação só após volume de análises no repo privado.
- **Empacotamento como plugin do Claude Code** — evolução natural da D5 quando as três casas estabilizarem.
- **Conteúdo das ~42 notas do backlog do `claude-vault`** (balde E) — catalogado, não escrito.

---

## 14. Critérios de sucesso

- [ ] `check_links.py` reporta **0** links não resolvidos fora da allowlist e do backlog `status: planned`
- [ ] Todo agente de tech referencia `tech/00-index/` — hoje são 0 referências
- [ ] Toda nota aparece no `_index.md` do seu domínio
- [ ] Nenhum entregável operacional no repo público
- [ ] Um report de equity produzido ponta a ponta pela skill `equity-initiation`, alimentando o repo privado
- [ ] Nota nova exige editar exatamente **um** índice e **zero** prompts de agente
- [ ] **Um agente real percorre os três saltos sem varredura.** Não basta os índices existirem: é preciso invocar um agente com uma pergunta de verdade e pedir o rastro exato de arquivos abertos. Foi esse teste — e só ele — que revelou que o `_house.md` não permitia resolver wikilink em caminho. Repetir ao fim de cada casa.
