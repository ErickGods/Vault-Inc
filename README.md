# Vault Inc Library

Base de conhecimento aberta da **Vault Inc** — uma casa de análises quant finance, research e
wealth management. É um vault do [Obsidian](https://obsidian.md) que serve como **fonte de verdade
para agentes de IA** construídos sobre o [Claude Code](https://claude.com/claude-code).

Não é uma coleção de notas. É a **camada de conhecimento** de três casas que produzem trabalho
real — e, principalmente, é um jeito de organizar esse conhecimento para que um agente **ache o que
precisa sem ler tudo.**

> **Comece por aqui, conforme quem você é:**
> - **Só quero ler o conteúdo** → abra a pasta no Obsidian e navegue pelo `_house.md` de cada casa.
> - **Vou rodar os agentes** → abra o repositório no Claude Code e comece pelo [`CLAUDE.md`](CLAUDE.md) da raiz.
> - **Quero entender o desenho** → siga lendo. A seção [Como funciona](#como-funciona) é o coração.

---

## As três casas

Todo conhecimento é dividido em **casas**. Cada casa tem um mandato, um índice mestre e seus
próprios agentes.

| Casa | Mandato | A pergunta que responde |
|---|---|---|
| **`finance/`** | Research fundamentalista, wealth management e crédito. A casa que **fala com o cliente**. | "Esta empresa vale o preço? Isso cabe na carteira deste cliente?" |
| **`quant/`** | Traduz tese discricionária em hipótese testável, e hipótese validada em código. | "Este padrão de mercado funciona mesmo? Quanto se pode perder?" |
| **`tech/`** | Engenharia de software, infraestrutura e dados. A casa que **constrói**. | "Como isso vira código que roda? Como vira infraestrutura?" |

Há ainda uma casa de apoio, **`shared/claude/`**, com o conhecimento sobre operar o próprio Claude
Code (hooks, MCP, subagentes, skills, janela de contexto).

**A quant é o eixo do projeto**, e a razão é estrutural: ela traduz nos dois sentidos. Pega uma
tese de research ("esta empresa tem vantagem competitiva") e a transforma em hipótese com universo,
período e critério de rejeição. Depois pega a hipótese validada e a transforma em código que roda.
Nenhuma das outras duas casas faria os dois movimentos.

```
finance/  ──tese──▶  quant/  ──especificação──▶  tech/
   ◀──evidência──      ◀──dados / infra / código──
```

### A regra que decide para onde vai cada pergunta

Afirmação sobre **uma empresa** é finance; afirmação sobre **uma população de empresas** é quant.

- *"O ROIC desta empresa foi 18%"* — observação verificável na demonstração → **finance**.
- *"Empresas com ROIC de 18% superam o índice"* — hipótese estatística → **quant**, sempre.

---

## Como funciona

Uma base de conhecimento grande é inútil para um agente se ele precisa **ler tudo** para achar o
que importa. A abordagem ingênua — listar os arquivos no prompt do agente — não escala: um agente
desta casa chegou a citar 23 arquivos direto no prompt, e **cada nota nova exigia editar o prompt à
mão.**

A solução aqui são **três saltos com custo controlado.** O agente nunca varre o vault; ele desce
por índices, decidindo a cada passo o que **não** precisa abrir:

```
1. _house.md  ──▶  2. índice do domínio  ──▶  3. a(s) nota(s) que a tarefa exige
   (o mapa da casa)     (a coluna "O que responde"       (lê só o necessário e para)
                         existe para ele decidir
                         NÃO abrir uma nota)
```

1. **Índice mestre** (`<casa>/00-index/_house.md`) — não contém conhecimento, contém o **mapa**:
   lista os domínios ativos e onde cada um mora.
2. **Índice do domínio** — cada nota aparece com uma coluna **"O que responde"**. Ela existe para o
   agente decidir, sem abrir o arquivo, se aquela nota serve à tarefa.
3. **A nota** — ele abre **apenas** o que a tarefa exige e para quando tem o suficiente.

Para preocupações **transversais** (custo, liquidez, tributação, viés, correlação em crise), o
salto 2 usa `<casa>/00-index/_topics.md` em vez de um domínio — porque nenhum domínio sozinho
responde a essas.

**O ganho que faz o desenho escalar:** nota nova custa **uma linha** em um índice e **zero edição**
em qualquer prompt de agente.

> **Exemplo medido, num teste real.** Um agente de equity research, diante de uma cobertura de
> concessionária de energia, abriu **10 notas** da casa financeira — e nunca precisou saber que
> existiam os domínios de psicologia ou de glossário. Ele desceu pelos índices, leu a coluna "O que
> responde" e ignorou o resto.

A regra de ouro para os agentes: **nunca use `Glob`, `Grep`, `ls` ou `find` para localizar uma
nota.** Se o caminho não sai do índice, o defeito é do índice — e precisa ser reportado, não
contornado.

---

## O que tem dentro

```
├── finance/          ~75 notas — fundamentos, investimentos, análise, contabilidade,
│                     mercados, psicologia, frameworks, glossário
├── quant/            ~10 notas — fatores, estratégias, backtesting, risco e performance
├── tech/             ~90 notas — linguagens e frameworks, DevOps, IA/ML,
│                     arquitetura, engenharia de dados
├── shared/claude/    ~13 notas — operar o Claude Code (hooks, MCP, subagentes, skills)
├── docs/             templates, workflows e canvas do Obsidian
├── .claude/
│   ├── agents/       20 agentes, organizados por casa
│   └── skills/        4 skills — rotinas operacionais com guarda-corpos
└── scripts/          verificador de integridade do vault
```

Conteúdo em **português**, com termos técnicos em inglês preservados. Cobre mercado brasileiro (B3,
Tesouro Direto, CDB/LCI/LCA, JCP, tributação do investidor PF) e americano.

**Entregáveis não moram aqui.** Report de equity, IPS de cliente, backtest e memo de PE vão para o
repositório privado `Vault-Inc-Workspace`, que monta este aqui como submódulo em `library/`.

---

## Agentes e skills

Os **agentes** ficam em `.claude/agents/<casa>/` e são descobertos nativamente pelo Claude Code ao
abrir este repositório. Cada agente carrega o **bloco de roteamento** que o ensina a navegar pelos
três saltos — ele não cita notas por nome, aprende a **achá-las** pelo índice da casa.

As **skills** são rotinas operacionais rígidas — passos numerados, critérios de saída e uma seção
`Nunca`:

| Skill | O que executa |
|---|---|
| `hypothesis-test` | Transforma uma tese de mercado em hipótese testável, com critério de rejeição escrito **antes** do teste |
| `backtest-protocol` | Roda backtest com guarda-corpos: viés de sobrevivência, look-ahead, custos, Deflated Sharpe |
| `equity-initiation` | Produz relatório de início de cobertura de uma ação, ponta a ponta |
| `dcf-valuation` | Executa valuation por fluxo de caixa descontado com matriz de sensibilidade obrigatória |

A divisão entre nota e skill é deliberada: **a nota explica o quê e o porquê; a skill executa o
como.** A skill cita a nota, nunca a copia.

---

## Integridade

O vault tem um verificador próprio, coberto por **66 testes**:

```bash
# o portão: falha se surgir qualquer link quebrado que não estava na linha de base
python -B scripts/check_links.py . --baseline scripts/baseline.txt

# a suíte de testes do próprio verificador
python -B -m unittest discover -s scripts/tests
```

A comparação é **por conjunto de alvos, não por total** — comparar totais deixaria uma quebra nova
ser compensada por progresso em outro lugar. O verificador ignora corretamente wikilinks dentro de
blocos de código, placeholders de template e a sintaxe `[[ ]]` do bash.

Migração que renomeia arquivo usa `scripts/migrate_house.py`, que emite um plano, hasheia o estado
do repositório e só aplica preso àquele hash — se algo mudou entre planejar e aplicar, aborta antes
de escrever.

---

## Como usar

**Como vault do Obsidian:** clone e abra a pasta raiz. Navegue a partir do `_house.md` de cada
casa — é o mapa de tudo que existe ali.

**Com o Claude Code:** abra o repositório e os 20 agentes e 4 skills são descobertos
automaticamente. Comece pelo [`CLAUDE.md`](CLAUDE.md) da raiz, que roteia entre as casas e explica
os três saltos. Depois, é só pedir a tarefa — o agente certo se vira para achar o conhecimento.

---

## Estado

As **três casas estão religadas e navegáveis**: índice mestre, índice de temas transversais e
índices de domínio completos (com a coluna "O que responde"), e os **20 agentes carregam o bloco de
roteamento**.

- **quant** e **finance** — completas e **validadas contra agentes reais** executando tarefas de
  verdade. O teste é invocar um agente com uma demanda concreta e exigir o rastro exato de arquivos
  abertos; ele já revelou dois defeitos que nenhuma verificação estática pegaria.
- **tech** — 89 notas migradas e normalizadas, índices escritos e os 9 agentes religados. Falta o
  passo de **validação contra agente real** — a mesma prova que fechou as outras duas casas.
- **shared/claude** — conteúdo escrito e índice montado; integração final à estrutura de casas em
  andamento.

---

## Licença

[MIT](LICENSE)

---

Construído por [Vault Inc](https://github.com/ErickGods)
