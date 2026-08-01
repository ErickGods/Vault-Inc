# Vault Inc Library

Base de conhecimento aberta da **Vault Inc** — uma casa de análises quant finance, research e
wealth management. Vault do [Obsidian](https://obsidian.md) que serve como fonte de verdade para
agentes de IA construídos sobre o [Claude Code](https://claude.com/claude-code).

Não é uma coleção de notas. É a camada de conhecimento de três casas que produzem trabalho real.

## As três casas

| Casa | Mandato |
|---|---|
| **`finance/`** | Research fundamentalista, wealth management e crédito — a casa que fala com o cliente |
| **`quant/`** | Traduz tese discricionária em hipótese testável, e hipótese validada em código |
| **`tech/`** | Engenharia de software, infraestrutura e dados — a casa que constrói |

A **quant** é o eixo do projeto, e a razão é estrutural: ela traduz nos dois sentidos. Pega uma
tese de research ("esta empresa tem vantagem competitiva") e a transforma em hipótese com
universo, período e critério de rejeição. Depois pega a hipótese validada e a transforma em código
que roda. Nenhuma das outras duas casas faria os dois movimentos.

```
finance/  ──tese──▶  quant/  ──especificação──▶  tech/
   ◀──evidência──      ◀──dados / infra / código──
```

## O problema que este repositório resolve

Uma base de conhecimento grande é inútil para um agente se ele não consegue achar o que precisa
sem ler tudo. A abordagem ingênua — listar arquivos no prompt do agente — não escala: um agente
desta casa chegou a citar 23 arquivos diretamente, e cada nota nova exigia editar o prompt à mão.

A solução aqui são **três saltos com custo controlado**:

1. o agente carrega o índice mestre da casa e vê os domínios
2. abre o índice do domínio, cuja coluna **"O que responde"** existe para ele decidir *não* abrir
   uma nota
3. lê apenas o que a tarefa exige

**Nota nova custa uma linha em um índice e zero edição em qualquer prompt de agente.**

Medido num teste real: um agente de equity research, diante de uma cobertura de concessionária de
energia, abriu **10 de 74 notas** da casa financeira — e nunca precisou saber que existiam
domínios de psicologia ou glossário.

## O que tem dentro

```
├── finance/          74 notas — fundamentos, investimentos, análise, contabilidade,
│                     mercados, psicologia, frameworks, glossário
├── quant/             7 notas — fatores, estratégias, backtesting, risco e performance
├── tech/             89 notas — linguagens e frameworks, DevOps, IA/ML,
│                     arquitetura, engenharia de dados
├── shared/           templates e convenções
├── .claude/
│   ├── agents/       20 agentes, organizados por casa
│   └── skills/       rotinas operacionais com guarda-corpos
└── scripts/          verificador de integridade do vault
```

Conteúdo em **português**, com termos técnicos em inglês preservados. Cobre mercado brasileiro
(B3, Tesouro Direto, CDB/LCI/LCA, JCP, tributação do investidor PF) e americano.

## Agentes e skills

Os agentes ficam em `.claude/agents/<casa>/` e são descobertos nativamente pelo Claude Code ao
abrir este repositório. As skills são rotinas operacionais rígidas — passos numerados, critérios
de saída, e uma seção `Nunca`:

| Skill | O que executa |
|---|---|
| `hypothesis-test` | Transforma uma tese de mercado em hipótese testável, com critério de rejeição escrito **antes** do teste |
| `backtest-protocol` | Roda backtest com guarda-corpos: viés de sobrevivência, look-ahead, custos, Deflated Sharpe |
| `equity-initiation` | Produz relatório de início de cobertura ponta a ponta |
| `dcf-valuation` | Executa valuation por fluxo de caixa descontado com sensibilidade obrigatória |

A divisão entre nota e skill é deliberada: **a nota explica o quê e o porquê; a skill executa o
como.** A skill cita a nota, nunca a copia.

## Integridade

O vault tem um verificador próprio, com 66 testes:

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt
```

Ele falha se surgir qualquer link quebrado novo — comparação por conjunto de alvos, não por
total, porque comparar totais permite que uma quebra nova seja compensada por progresso em outro
lugar. Ignora corretamente wikilinks dentro de blocos de código, placeholders de template e a
sintaxe `[[ ]]` do bash.

## Como usar

**Como vault do Obsidian:** clone e abra a pasta raiz. Navegue a partir do `_house.md` de cada
casa.

**Com o Claude Code:** abra o repositório e os 20 agentes e 4 skills são descobertos
automaticamente. Comece pelo `CLAUDE.md` da raiz, que roteia entre as casas.

Os entregáveis operacionais — report de equity, IPS de cliente, backtest — **não moram aqui**.
Eles vão para um repositório privado que monta este como submódulo.

## Estado

As casas **quant** e **finance** estão completas — índices, agentes, skills, e ambas validadas
contra agentes reais executando tarefas de verdade.

A casa **tech** tem as 89 notas migradas e normalizadas, mas apenas 2 dos 8 índices de domínio
escritos, e seus 9 agentes ainda não foram religados ao índice. Trabalho em andamento.

## Licença

[MIT](LICENSE)

---

Construído por [Vault Inc](https://github.com/ErickGods)
