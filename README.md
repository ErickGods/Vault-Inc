# Vault Inc

**Vault Inc é uma casa de análises financeiras operada por agentes de IA.**

Ela faz o trabalho de uma equipe de research: analisa empresas, monta e revisa carteiras de
clientes, avalia crédito, testa estratégias quantitativas e constrói a tecnologia que sustenta
tudo isso. Só que a equipe é formada por **agentes** construídos sobre o
[Claude Code](https://claude.com/claude-code).

Este repositório é o **cérebro da empresa**: o conhecimento que os agentes consultam, os próprios
agentes e as rotinas de trabalho que eles seguem. Os relatórios e as entregas para clientes ficam
em um repositório privado — **aqui mora o que faz a Vault Inc funcionar, não os produtos que ela
entrega.**

---

## Como a empresa é organizada

A Vault Inc se divide em três **casas**. Cada casa tem um mandato claro e uma equipe de agentes
especialistas — pense em cada agente como um profissional com uma função.

### 🏛️ finance — a casa que fala com o cliente

Research fundamentalista, gestão de patrimônio e crédito. Toda entrega desta casa é uma **decisão
de alocação de capital** — comprar, vender, manter, dimensionar — ou a análise que a sustenta.
Quem assina responde por ela na frente de quem confiou o patrimônio.

> Agentes: `equity-research-analyst`, `private-banker`, `credit-research-analyst`,
> `macro-strategist`, `pe-analyst`, `compliance-officer`.

### 📊 quant — a casa que testa se a ideia funciona

Traduz nas duas direções, e é a única que faz isso: pega uma tese de research ("esta empresa tem
vantagem competitiva") e a transforma em **hipótese testável**; depois pega a hipótese validada e a
transforma em **código que roda**. Toda entrega é uma dessas traduções, ou a evidência que a
sustenta.

> Agentes: `quant-researcher`, `quant-developer`, `risk-quant`, `market-data-quant`.

### 🔧 tech — a casa que constrói

Engenharia de software, infraestrutura e dados. O que sai daqui roda, é deployado e é monitorado.
Toda entrega é código em produção, infraestrutura provisionada ou pipeline de dados em operação.

> Agentes: `backend`, `frontend`, `data-engineer`, `devops`, `ml-engineer`, `lead-engineer`,
> `qa`, `security`, `ui-ux`.

**Uma regra simples separa finance de quant:** afirmação sobre **uma empresa** é finance;
afirmação sobre **uma população de empresas** é quant. "O ROIC desta empresa foi 18%" é finance.
"Empresas com ROIC de 18% superam o índice" é quant.

---

## Como o trabalho acontece

```
você pede uma tarefa
      │
      ▼
o agente certo, da casa certa, assume
      │
      ├─▶ consulta a base de conhecimento (sem ler tudo — ele navega por índices)
      ├─▶ segue uma skill quando a tarefa exige rigor (passos, critérios, guarda-corpos)
      │
      ▼
o entregável final vai para o repositório privado da empresa
```

**A base de conhecimento** é o que cada agente sabe. Em vez de ler o repositório inteiro, o agente
desce por índices: parte do mapa da casa, escolhe o assunto e abre **só** as notas que a tarefa
exige. É isso que permite a base crescer sem deixar os agentes mais lentos.

**As skills** são as rotinas rígidas da casa — passos numerados, critérios de saída e uma seção
`Nunca`. Elas garantem que trabalho sensível saia sempre com o mesmo rigor:

| Skill | O que executa |
|---|---|
| `equity-initiation` | Relatório de início de cobertura de uma ação, ponta a ponta |
| `dcf-valuation` | Valuation por fluxo de caixa descontado, com sensibilidade obrigatória |
| `hypothesis-test` | Transforma uma ideia de mercado em hipótese testável, com critério de rejeição escrito **antes** do teste |
| `backtest-protocol` | Roda backtest com guarda-corpos: viés de sobrevivência, look-ahead, custos, Deflated Sharpe |

---

## O que tem no repositório

```
├── finance/   quant/   tech/    o conhecimento de cada casa, organizado por assunto
├── shared/                       conhecimento comum + operar o próprio Claude Code
├── .claude/
│   ├── agents/                   os 20 agentes da empresa, por casa
│   └── skills/                   as rotinas de trabalho
├── docs/                         templates e fluxos de trabalho
└── scripts/                      verificador que mantém a base íntegra
```

Conteúdo em **português**, com termos técnicos em inglês preservados. Cobre mercado brasileiro
(B3, Tesouro Direto, CDB/LCI/LCA, JCP, tributação do investidor PF) e americano.

---

## Como explorar

- **Só quero ler** — abra a pasta no [Obsidian](https://obsidian.md) e navegue pelo `_house.md`
  de cada casa.
- **Quero colocar os agentes para trabalhar** — abra o repositório no Claude Code. Os 20 agentes e
  as skills são reconhecidos automaticamente; comece pelo [`CLAUDE.md`](CLAUDE.md) da raiz e peça
  uma tarefa.

A base tem um verificador próprio, com 66 testes, que impede links quebrados de entrarem:

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt
```

---

## Estado

As três casas estão **montadas e funcionando**: cada uma tem seus índices completos e seus agentes
prontos para navegar pelo conhecimento.

- **finance** e **quant** — completas e testadas com agentes reais executando tarefas de verdade.
- **tech** — conhecimento e agentes prontos; falta o mesmo teste com agentes reais que fechou as
  outras duas.

---

## Licença

[MIT](LICENSE) · Construído por [Vault Inc](https://github.com/ErickGods)
