---
tags:
  - finance
  - psychology
  - behavioral
aliases:
  - Finanças Comportamentais
  - Behavioral Finance
complexity: intermediate
context: global
created: 2026-04-06
---

# Behavioral Finance

## Overview

Behavioral Finance é o campo que integra psicologia cognitiva com teoria financeira para explicar **por que investidores tomam decisões irracionais** de forma sistemática e previsível. Enquanto a teoria financeira clássica assume que agentes são racionais e maximizam utilidade (Homo Economicus), behavioral finance demonstra que humanos possuem **bounded rationality** — racionalidade limitada por capacidade cognitiva, informação disponível e tempo.

> [!info] Desafio ao EMH
> A **Efficient Market Hypothesis** (Hipótese do Mercado Eficiente) de Eugene Fama assume que preços refletem toda informação disponível. Behavioral finance argumenta que vieses sistemáticos criam **mispricings** exploráveis — anomalias como o *value premium*, *momentum effect* e *post-earnings announcement drift* são evidências contra a forma forte do EMH.

O campo ganhou relevância acadêmica com o trabalho de **Daniel Kahneman e Amos Tversky** nos anos 1970-80, culminando no Nobel de Economia de Kahneman em 2002. Richard Thaler (Nobel 2017) expandiu a aplicação para nudge theory e políticas públicas.

---

## Core Concepts

### Prospect Theory (Teoria da Perspectiva)

Desenvolvida por Kahneman & Tversky (1979), é a pedra angular de behavioral finance. A **value function** possui três características fundamentais:

1. **Reference dependence** — Ganhos e perdas são avaliados relativos a um ponto de referência (geralmente o preço de compra), não em termos absolutos de riqueza
2. **Loss aversion** — Perdas doem aproximadamente **2.5x mais** do que ganhos equivalentes proporcionam prazer
3. **Diminishing sensitivity** — A diferença entre ganhar R$100 e R$200 parece maior que entre R$10.100 e R$10.200

```
Diagrama da Value Function (Prospect Theory):

        Valor (Psicológico)
          |        /
          |      /  ← Ganhos (côncava - risk averse)
          |    /
          |  /
          |/
----------+----------→ Resultado (R$)
         /|
        / |
       /  |
      /   |  ← Perdas (convexa - risk seeking)
     /    |     Inclinação ~2.5x maior
    /     |
```

> [!important] Implicação Prática
> Loss aversion explica o **disposition effect**: investidores vendem winners cedo demais (para "garantir" o ganho) e seguram losers por tempo demais (para evitar a dor de realizar a perda). Ver [[cognitive-biases]].

### Mental Accounting (Contabilidade Mental)

Conceito de Richard Thaler: pessoas criam **"contas mentais"** separadas para dinheiro que é fungível. Exemplos:

- Tratar o 13º salário como "dinheiro extra" para gastar, mesmo sendo parte da remuneração anual
- Manter reserva de emergência rendendo 100% CDI enquanto paga cartão de crédito a 400% a.a.
- Arriscar mais com "dinheiro da casa" (house money effect) — lucros de investimentos são tratados como menos valiosos

### Anchoring Effect (Efeito Ancoragem)

O primeiro número que um investidor vê influencia desproporcionalmente sua avaliação. Exemplos em finanças:

- **IPO pricing** — O preço de lançamento se torna âncora, mesmo sem fundamento econômico
- **Target prices** de analistas criam âncoras que influenciam decisões de compra/venda
- **Preço histórico** — "PETR4 já valeu R$50, então está barata a R$35" (ignorando mudanças fundamentais)
- **P/L médio histórico** — Usar múltiplos passados como âncora sem considerar mudanças estruturais

### Herd Behavior (Comportamento de Manada)

Investidores seguem a multidão por três razões: informational cascade (assumem que outros sabem algo), pressão social e FOMO ([[investor-psychology]]). Exemplos históricos:

| Evento | Período | Resultado |
|--------|---------|-----------|
| Tulip Mania | 1636-1637 | Bulbos valeram mais que casas; crash de 99% |
| South Sea Bubble | 1720 | Newton perdeu £20.000 ("posso calcular o movimento dos astros, mas não a loucura das pessoas") |
| Dot-com Bubble | 1998-2000 | NASDAQ caiu 78% do pico |
| US Housing/Subprime | 2006-2008 | Crise financeira global |
| Crypto Bubble | 2017 e 2021 | Bitcoin caiu 80%+ em ambos ciclos |

### Overconfidence Bias (Viés de Excesso de Confiança)

Investidores sistematicamente superestimam sua habilidade de stock picking e market timing. Estudos mostram que:

- **Barber & Odean (2000)**: Investidores que mais negociam obtêm retornos 6.5% menores que a média
- 74% dos fund managers acreditam estar acima da média (matematicamente impossível)
- Homens negociam 45% mais que mulheres e obtêm retornos líquidos inferiores
- **Illusion of control** — acreditar que pesquisa e esforço eliminam a aleatoriedade do mercado

### Status Quo Bias

Preferência irracional por manter a situação atual. Em investimentos:

- Manter alocação original mesmo quando perfil de risco mudou
- Não rebalancear portfólio por inércia (não por estratégia)
- Manter ações herdadas por apego emocional, não por análise

---

## How to Apply

1. **Reconheça seus vieses** — O primeiro passo é awareness; estude [[cognitive-biases]] sistematicamente
2. **Automatize decisões** — Use rebalanceamento automático, aportes programados (DCA) e stop-loss pré-definidos
3. **Crie um Investment Policy Statement (IPS)** — Documente regras antes de situações emocionais
4. **Mantenha um diário de investimentos** — Registre a tese e emoções de cada decisão
5. **Use checklists** — Evite decisões impulsivas com processo estruturado
6. **Busque opiniões contrárias** — Combata confirmation bias ativamente

---

## Examples

> [!example] Caso Real: Disposition Effect no Brasil
> Investidor comprou MGLU3 a R$25. A ação sobe para R$28 e ele vende "para garantir" (+12%). Depois comprou IRBR3 a R$40. A ação cai para R$8 e ele segura, dizendo "vai voltar." Loss aversion e mental accounting em ação — ele trata cada posição como conta separada em vez de avaliar o portfólio inteiro.

> [!example] Anchoring em Valuation
> Analista projeta preço-alvo de R$50 para uma ação. Outro analista, partindo dos mesmos dados, projeta R$30. A diferença? O primeiro ancorou no preço atual de R$45; o segundo ancorou no valor patrimonial de R$20. Mesmo DCF, premissas diferentes por causa da âncora inicial.

---

## Gotchas

> [!warning] Armadilhas Comuns
> - **Conhecer os vieses não imuniza contra eles** — Até Kahneman admitiu que continua suscetível a loss aversion
> - **Behavioral finance não é desculpa para market timing** — "O mercado está irracional" não significa que você sabe quando vai corrigir
> - **Overcorrection** — Tentar eliminar toda emoção pode levar à paralisia decisória
> - **Confundir paciência com teimosia** — Segurar um investimento ruim "porque Buffett é buy and hold" é sunk cost fallacy, não disciplina

---

## Brazilian Context

- **Cultura do day trade** — Brasil tem proporção altíssima de day traders (estimativas de 97% perdem dinheiro, estudo FGV/B3)
- **Influenciadores financeiros** — Amplificam herd behavior e overconfidence em redes sociais
- **Poupança como âncora** — Muitos brasileiros usam rendimento da poupança como benchmark, criando âncora baixa
- **Volatilidade do Real** — Câmbio volátil intensifica loss aversion em investimentos internacionais
- **CVM e proteção ao investidor** — Regulação de suitability tenta mitigar decisões inadequadas ao perfil ([[risk-tolerance]])

---

## Formulas

$$V(x) = \begin{cases} x^\alpha & \text{se } x \geq 0 \\ -\lambda(-x)^\beta & \text{se } x < 0 \end{cases}$$

Onde tipicamente: $\alpha = \beta \approx 0.88$ e $\lambda \approx 2.25$ (coeficiente de loss aversion).

$$w(p) = \frac{p^\gamma}{(p^\gamma + (1-p)^\gamma)^{1/\gamma}}$$

> [!note] Interpretação
> Pessoas **sobrevalorizam** probabilidades pequenas (loterias, tail risks) e **subvalorizam** probabilidades moderadas a altas. Isso explica por que investidores compram seguros caros E bilhetes de loteria simultaneamente.

---

## References

- Kahneman, D. & Tversky, A. (1979). *Prospect Theory: An Analysis of Decision under Risk*
- Thaler, R. (1999). *Mental Accounting Matters*. Journal of Behavioral Decision Making
- Kahneman, D. (2011). *Thinking, Fast and Slow*
- Thaler, R. & Sunstein, C. (2008). *Nudge*
- Barber, B. & Odean, T. (2000). *Trading Is Hazardous to Your Wealth*
- Shiller, R. (2000). *Irrational Exuberance*
- Ariely, D. (2008). *Predictably Irrational*

---

## Related

- [[cognitive-biases]] — Catálogo detalhado de vieses com contramedidas
- [[investor-psychology]] — Ciclo emocional e disciplina do investidor
- [[risk-tolerance]] — Perfil de risco e como vieses o distorcem
- [[market-cycles]] — Como behavioral finance explica bolhas e crashes
- [[growth-vs-value]] — Vieses que favorecem growth stocks (narrative fallacy, recency bias)
