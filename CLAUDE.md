# Vault Inc — Orquestrador

Este repositório é a **base de conhecimento pública** da Vault Inc: uma casa de análises quant
finance, research e wealth management. Ele contém conhecimento, agentes e skills.

**Entregáveis não moram aqui.** Report de equity, IPS de cliente, backtest e memo de PE vão para
o repositório privado `Vault-Inc-Workspace`, que monta este aqui como submódulo em `library/`.

---

## As três casas

| Casa | Mandato | Índice mestre |
|---|---|---|
| **finance** | Research fundamentalista, wealth management e crédito. A casa que fala com o cliente. | `finance/00-index/_house.md` |
| **quant** | Traduz tese discricionária em hipótese testável, e hipótese validada em código. | `quant/00-index/_house.md` |
| **tech** | Engenharia de software, infraestrutura e dados. A casa que constrói. | `tech/00-index/_house.md` |

Cada casa tem seu próprio `CLAUDE.md` com o mandato detalhado e os padrões obrigatórios. O Claude
Code carrega o aninhado automaticamente ao trabalhar dentro da pasta — leia-o antes de agir.

### Para onde vai cada pergunta

| A pergunta é sobre | Casa | Agente típico |
|---|---|---|
| Esta empresa vale o preço? | finance | `equity-research-analyst` |
| Isso cabe na carteira deste cliente? | finance | `private-banker` |
| O spread paga o risco de crédito? | finance | `credit-research-analyst` |
| Em que fase do ciclo estamos? | finance | `macro-strategist` |
| Este padrão de mercado funciona mesmo? | **quant** | `quant-researcher` |
| Quanto se pode perder, e em que cenário? | **quant** | `risk-quant` |
| Este dado está financeiramente correto? | **quant** | `market-data-quant` |
| Como isso vira código que roda? | quant / tech | `quant-developer` / `backend` |
| Como isso vira infraestrutura? | tech | `devops`, `data-engineer` |

**A dúvida mais comum, e a regra que a resolve:** afirmação sobre **uma empresa** é finance;
afirmação sobre **uma população de empresas** é quant. "O ROIC desta empresa foi 18%" é
observação verificável na demonstração. "Empresas com ROIC de 18% superam o índice" é hipótese
estatística — vai para a casa quant, sempre.

---

## Como qualquer agente alcança conhecimento

**Três saltos, nunca uma varredura.**

1. Carregue `<casa>/00-index/_house.md`. Ele não contém conhecimento — contém o mapa, e a coluna
   `Pasta` com o caminho de cada domínio.
2. Se a pergunta é sobre um **território**, escolha o domínio e abra o índice dele. Se é sobre
   uma **preocupação transversal** — custo, liquidez, tributação, viés, correlação em crise —
   abra `<casa>/00-index/_topics.md`: nenhum domínio responde essas sozinho.
3. Abra **apenas** as notas que a tarefa exige. Leia a coluna "O que responde" e pare quando
   tiver o suficiente.

**Nunca use Glob, Grep, `ls` ou `find` para localizar nota.** Se você não conseguiu montar o
caminho pelo índice, isso é defeito do índice e precisa ser reportado — não contornado.

Dois detalhes que já causaram erro:

- **Wikilink não carrega caminho.** O arquivo fica em `<pasta>/<nome>.md`, e `<pasta>` vem da
  coluna `Pasta`. Prefixos numéricos **não são deriváveis** — domínios planejados seguram números
  sem existir em disco.
- **Domínio com subpasta**: a coluna `Pasta` dá só a raiz; o caminho exato mora no **título da
  seção** dentro do índice do domínio.

E uma regra sobre `Related`: chegar a uma nota pelo `Related` de outra é legítimo quando você
quer *aquela* nota. Quando o motivo é **territorial** — cobertura de um domínio, não um fato
pontual — abra o índice mesmo assim. `Related` mostra o que foi linkado; o índice mostra o que
existe.

---

## Colaboração entre casas — Cross-Desk Request

Subagentes começam com **contexto zero**: não herdam a conversa nem sabem o que já foi decidido.
Por isso pedido entre mesas é artefato escrito, não menção de passagem.

```yaml
---
from: equity-research-analyst
to: quant-researcher
type: hypothesis-test
---
## Pergunta
## Contexto mínimo
## Entregável esperado
## Já verificado
```

O campo **Já verificado** impede a casa de responder três vezes a mesma pergunta. CDRs vivem em
`cross-desk/` no repositório privado — são operação, não conhecimento.

**Quando a resposta virar conhecimento durável, ela sobe para este vault** como nota nova, e o
índice do domínio ganha uma linha. Esse passo é o que impede a casa de reaprender o que já sabe.

---

## Convenções

**Nomes de arquivo**: kebab-case, sem emoji, sem espaço.

**Frontmatter canônico** de toda nota:

```yaml
tags: []
aliases: []          # PT/EN — permite achar a nota pelo termo em português
house: finance | quant | tech | shared
domain: analysis/fundamental
level: intro | intermediate | advanced
status: active | draft | planned | deprecated
created / updated: YYYY-MM-DD
```

> `level` **não é sinal de roteamento.** Medido: 86 de 89 notas do tech declaram `advanced`. Um
> campo em que quase tudo compartilha o mesmo valor não discrimina nada. Quem roteia é a coluna
> "O que responde".

**Nota nova custa uma linha** no índice do seu domínio e **zero edição em prompt de agente**. Se
um agente começar a citar notas por nome, a propriedade que faz este desenho escalar foi quebrada.

---

## O portão

`scripts/check_links.py` é o critério objetivo de qualquer mudança estrutural:

```bash
python -B scripts/check_links.py . --baseline scripts/baseline.txt
```

Ele falha se **surgir qualquer alvo quebrado que não estava na linha de base** — comparação por
conjunto, não por total, porque comparar totais deixa quebra nova ser compensada por progresso.

```bash
python -B -m unittest discover -s scripts/tests
```

Migração que renomeia arquivo usa `scripts/migrate_house.py`, que emite um plano, hasheia, e só
aplica preso àquele hash. Se o repositório mudou entre planejar e aplicar, aborta antes de
escrever.

---

## Estado atual

| Casa | Notas | Índices | Agentes | Skills |
|---|---|---|---|---|
| quant | 7 | completos | 4 | `hypothesis-test`, `backtest-protocol` |
| finance | 73 | completos | 6 | `equity-initiation`, `dcf-valuation` |
| tech | 89 | completos | 9, **ainda não religados** | — |

As três casas têm índice mestre, índice de temas transversais e mandato. **As casas quant e
finance foram validadas contra agentes reais** executando tarefas de verdade — o teste é invocar
um agente com uma demanda concreta e exigir o rastro exato de arquivos abertos. Ele já revelou
dois defeitos que nenhuma verificação estática pegaria.

**Os 9 agentes da casa tech ainda não têm o bloco de roteamento** — eles não citam nota nenhuma,
nem por nome nem por índice. Até serem religados, trate trabalho na casa tech como manual.

`shared/claude/` segue pendente: o conteúdo sobre operar o Claude Code está em `claude-vault/`,
fora da estrutura de casas.
